import time
"""
Servidor Local - Painel de Estudos e Gestão de Concursos Públicos (IA)
Porta padrão: 8095
Recursos:
- Suporte Multi-IA: Google Gemini (1.5 Flash / 2.5 Flash) e OpenAI (GPT-4o-mini)
- Banco de Retenção Curado Offline (fallback instantâneo caso não haja chave de API)
- Deduplicação Semântica Rigorosa para Flashcards e Simulados
- Repetição Espaçada Nativa (Algoritmo SM-2 integrado)
- Modo Simulado Oficial Cebraspe (Cronômetro + Nota Líquida: 1 errada anula 1 certa)
- Caderno de Erros / Revisões Ativas Persistente
- Navegação Dinâmica entre Disciplinas e Tópicos
- Módulo de Criação e Importação de Novas Aulas
- Exportação Direta de Baralhos para Anki
"""

import sys
import os
import re
import json
import shutil
import datetime
import urllib.parse
import urllib.request
import webbrowser
import base64
import io
try:
    import pypdf
except ImportError:
    pypdf = None
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None
try:
    from http.server import ThreadingHTTPServer as HTTPServer, BaseHTTPRequestHandler
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import supabase_client
except Exception:
    supabase_client = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
PROGRESS_FILE = os.path.join(BASE_DIR, "progresso_estudos.json")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

# ==============================================================================
# CONFIGURAÇÕES E GERENCIAMENTO DE CHAVES DE IA E SUPABASE
# ==============================================================================

def load_config():
    default_cfg = {
        "gemini_api_key": "",
        "openai_api_key": "",
        "preferred_provider": "gemini",
        "port": 8095,
        "supabase_url": "",
        "supabase_key": ""
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_cfg.update(data)
        except Exception:
            pass
    return default_cfg

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def get_api_key(provider="gemini"):
    cfg = load_config()
    if provider.lower() == "gemini":
        key = cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
        return key.strip()
    elif provider.lower() == "openai":
        key = cfg.get("openai_api_key") or os.environ.get("OPENAI_API_KEY", "")
        return key.strip()
    return ""

def mask_key(k):
    if not k:
        return ""
    if len(k) <= 8:
        return "********"
    return f"{k[:4]}...{k[-4:]}"

# ==============================================================================
# ALGORITMO DE REPETIÇÃO ESPAÇADA (SM-2 NATIVO) E PROGRESSO
# ==============================================================================

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "cards": {},
        "quiz_history": [],
        "cebraspe_simulados": []
    }

def save_progress(data):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def record_card_sm2(card_key, quality, card_a="", discipline="", subarea=""):
    """
    quality: 1 = Difícil / Errei, 3 = Médio / Bom, 5 = Fácil / Dominado
    """
    data = load_progress()
    card_info = data.get("cards", {}).get(card_key, {
        "repetitions": 0,
        "interval_days": 1,
        "ease_factor": 2.5,
        "next_review": ""
    })
    if card_a:
        card_info["a"] = card_a
    if discipline:
        card_info["discipline"] = discipline
    if subarea:
        card_info["subarea"] = subarea
    
    reps = card_info.get("repetitions", 0)
    interval = card_info.get("interval_days", 1)
    ef = card_info.get("ease_factor", 2.5)
    
    if quality < 3:
        reps = 0
        interval = 1
    else:
        if reps == 0:
            interval = 1 if quality == 3 else 3
        elif reps == 1:
            interval = 3 if quality == 3 else 7
        else:
            interval = max(1, int(interval * ef))
        reps += 1
        
    ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    today = datetime.date.today()
    next_date = (today + datetime.timedelta(days=interval)).isoformat()
    
    card_info["repetitions"] = reps
    card_info["interval_days"] = interval
    card_info["ease_factor"] = round(ef, 2)
    card_info["next_review"] = next_date
    card_info["last_review"] = today.isoformat()
    
    data.setdefault("cards", {})[card_key] = card_info
    save_progress(data)
    return card_info

# ==============================================================================
# CHAMADAS DE IA (GEMINI / OPENAI) COM TRATAMENTO RESILIENTE
# ==============================================================================

def call_gemini_api(system_prompt, user_prompt, json_mode=True, temperature=0.7):
    api_key = get_api_key("gemini")
    if not api_key:
        raise ValueError("Chave GEMINI_API_KEY não configurada.")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    combined_prompt = f"{system_prompt}\n\n[INSTRUÇÃO DO USUÁRIO]:\n{user_prompt}"
    
    payload = {
        "contents": [
            {
                "parts": [{"text": combined_prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature
        }
    }
    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=25) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        try:
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise ValueError("Resposta inesperada da API Gemini.")

def call_openai_api(system_prompt, user_prompt, json_mode=True, temperature=0.7):
    api_key = get_api_key("openai")
    if not api_key:
        raise ValueError("Chave OPENAI_API_KEY não configurada.")
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
        
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def find_subarea_path(discipline, subarea):
    folder = os.path.join(BASE_DIR, discipline, subarea)
    if os.path.exists(folder):
        return folder
    import unicodedata
    def clean(s):
        if not s:
            return ""
        s_norm = ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
        return re.sub(r'[^a-z0-9]', '', s_norm)
    
    t_d = clean(discipline)
    t_s = clean(subarea)
    
    for d in os.listdir(BASE_DIR):
        dp = os.path.join(BASE_DIR, d)
        if os.path.isdir(dp) and (clean(d) == t_d or t_d in clean(d) or clean(d) in t_d):
            # 1. Exact cleaned match
            for s in os.listdir(dp):
                sp = os.path.join(dp, s)
                if os.path.isdir(sp) and clean(s) == t_s:
                    return sp
            # 2. Substring match
            for s in os.listdir(dp):
                sp = os.path.join(dp, s)
                if os.path.isdir(sp):
                    cs = clean(s)
                    if cs and (cs in t_s or t_s in cs):
                        return sp
    return folder

def generate_key_moments_ai(discipline, subarea, banca="Cebraspe", focus=""):
    """
    Gera momentos-chave da aula com minutagem real extraída da transcrição cronometrada.
    Salva em disco e no Supabase (se configurado).
    """
    sub_path = find_subarea_path(discipline, subarea)
    if not sub_path or not os.path.exists(sub_path):
        return []

    # 1. Localizar Transcrição Cronometrada
    timed_file = None
    for f in os.listdir(sub_path):
        if f.lower().startswith("transcricao_cronometrada") and f.endswith(".txt"):
            timed_file = os.path.join(sub_path, f)
            break

    timed_lines = []
    if timed_file and os.path.exists(timed_file):
        with open(timed_file, "r", encoding="utf-8", errors="ignore") as f_in:
            for line in f_in:
                m = re.match(r'\[([\d\.]+)s\]\s*\[(\d{1,2}:\d{2})\]\s*(.*)', line.strip())
                if m:
                    sec = int(float(m.group(1)))
                    t_str = m.group(2)
                    txt = m.group(3).strip()
                    if txt:
                        timed_lines.append((sec, t_str, txt))

    moments = []

    # Se não houver minutagem cronometrada (ex: PDF ou texto), gera momentos estruturados por página/seção
    if not timed_lines:
        md_text = get_subarea_context(discipline, subarea)
        pages_moments = []
        p_idx = 1
        for l in md_text.split('\n'):
            l_str = l.strip()
            if l_str.startswith('### '):
                title_clean = l_str.replace('### ', '').replace('**', '').strip()
                title_clean = re.sub(r'^[A-Z0-9\.\-]+\s*', '', title_clean)
                if title_clean:
                    pages_moments.append({
                        "title": title_clean,
                        "category": "CONCEITO-CHAVE",
                        "sec": p_idx,
                        "time_str": f"Pág. {str(p_idx).zfill(2)}",
                        "page": p_idx,
                        "quote": title_clean,
                        "importance": f"Conceito relevante da Página {p_idx}"
                    })
                    p_idx += 1
        moments = pages_moments[:10]
    else:
        # Preparar amostra estruturada da transcrição para a IA
        sample_corpus = []
        step = max(1, len(timed_lines) // 180)
        for i in range(0, len(timed_lines), step):
            s_sec, s_time, s_txt = timed_lines[i]
            sample_corpus.append(f"[{s_time}] ({s_sec}s): {s_txt}")

        sample_text = "\n".join(sample_corpus[:200])

        sys_prompt = (
            f"Você é um especialista em análise pedagógica de videoaulas e bancas de concursos ({banca}, FGV, FCC, Vunesp).\n"
            "Seu objetivo é analisar a TRANSCRIÇÃO CRONOMETRADA real desta aula e extrair os 6 a 10 MOMENTOS-CHAVE CRÍTICOS com a MINUTAGEM EXATA onde o professor aborda cada conceito ou pegadinha.\n\n"
            "REGRAS OBRIGATÓRIAS:\n"
            "1. USE EXATAMENTE os minutos e segundos da transcrição cronometrada fornecida. NÃO invente horários fictícios como 01:00.\n"
            "2. Identifique o momento exato em que o professor introduz conceitos centrais, regras, exceções e resolução de questões.\n"
            "3. Categorize cada momento em: 'RESUMO & CONCEITO', 'PEGADINHA DE BANCA', ou 'RESOLUÇÃO DE QUESTÃO'.\n"
            "4. O campo 'sec' deve ser um inteiro com os segundos exatos. O campo 'time_str' deve ser no formato 'MM:SS'.\n\n"
            "Retorne EXATAMENTE um array JSON puro (sem markdown ao redor):\n"
            "[\n"
            "  {\n"
            '    "title": "Definição de Proposição Lógica",\n'
            '    "category": "RESUMO & CONCEITO",\n'
            '    "sec": 717,\n'
            '    "time_str": "11:57",\n'
            '    "quote": "Frase curta dita pelo professor nesse minuto",\n'
            '    "importance": "Por que esse trecho é crucial para a banca ' + banca + '"\n'
            "  }\n"
            "]"
        )

        user_prompt = (
            f"Disciplina: {discipline}\n"
            f"Tópico: {subarea}\n"
            f"Banca Alvo: {banca}\n"
            f"Foco solicitado: {focus or 'Conceitos Fundamentais e Pegadinhas de Prova'}\n\n"
            f"TRANSCRIÇÃO CRONOMETRADA DA AULA:\n{sample_text}"
        )

        ai_res, prov = call_ai_service(sys_prompt, user_prompt, json_mode=True, temperature=0.3)

        if ai_res:
            try:
                cleaned = ai_res.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
                    cleaned = re.sub(r"```$", "", cleaned).strip()
                parsed = json.loads(cleaned)
                if isinstance(parsed, list) and len(parsed) > 0:
                    moments = parsed
            except Exception as e_parse:
                print(f"Erro ao decodificar momentos da IA: {e_parse}")

        # Fallback algorítmico inteligente se a IA não retornar
        if not moments:
            concept_patterns = [
                ("Definição e Conceitos Centrais", "RESUMO & CONCEITO", [r'defini[çc][ãa]o', r'conceito', r'o que [ée]', r'princ[íi]pio']),
                ("Regras Gerais e Estrutura", "RESUMO & CONCEITO", [r'regra', r'estrutura', r'requisito', r'caracter[íi]stica']),
                ("Pegadinhas e Armadilhas de Banca", "PEGADINHA DE BANCA", [r'pegadinha', r'cuidado', r'aten[çc][ãa]o', r'n[ãa]o [ée]', r'exce[çc][ãa]o']),
                ("Diferenciações e Comparações", "PEGADINHA DE BANCA", [r'diferen[çc]a', r'ao contr[áa]rio', r'cuidado com']),
                ("Conectivos e Fórmulas Principais", "RESUMO & CONCEITO", [r'conectivo', r'f[óo]rmula', r'tabela', r'classifica[çc]']),
                ("Resolução de Questão de Concurso", "RESOLUÇÃO DE QUESTÃO", [r'quest[ãa]o', r'banca', r'exerc[íi]cio', r'prova'])
            ]
            used_secs = set()
            for title, cat, pats in concept_patterns:
                for s_sec, s_time, s_txt in timed_lines:
                    if any(abs(s_sec - u) < 90 for u in used_secs):
                        continue
                    if any(re.search(p, s_txt, re.I) for p in pats):
                        used_secs.add(s_sec)
                        moments.append({
                            "title": title,
                            "category": cat,
                            "sec": s_sec,
                            "time_str": s_time,
                            "quote": s_txt[:140],
                            "importance": f"Momento identificado na aula ({s_time})"
                        })
                        break

    # Salvar em múltiplos nomes no disco para garantir localização imediata
    if moments:
        folder_base = os.path.basename(sub_path)
        save_file1 = os.path.join(sub_path, f"Momentos_Chave_{subarea}.json")
        save_file2 = os.path.join(sub_path, f"Momentos_Chave_{folder_base}.json")
        try:
            with open(save_file1, "w", encoding="utf-8") as f_out:
                json.dump(moments, f_out, ensure_ascii=False, indent=2)
            if save_file1 != save_file2:
                with open(save_file2, "w", encoding="utf-8") as f_out:
                    json.dump(moments, f_out, ensure_ascii=False, indent=2)
            print(f"Momentos-chave salvos com sucesso em: {save_file1}")
        except Exception as e_save:
            print(f"Erro ao salvar arquivo de momentos: {e_save}")

        # Salvar no Supabase se configurado
        if supabase_client and supabase_client.is_supabase_configured():
            try:
                aula_id = f"{supabase_client.normalize_slug(discipline)}_{supabase_client.normalize_slug(subarea)}"
                supabase_client.upsert_conteudo(aula_id=aula_id, momentos=moments)
            except Exception as e_supa:
                print(f"Erro ao sincronizar momentos com Supabase: {e_supa}")

    return moments

def call_ai_service(system_prompt, user_prompt, json_mode=True, temperature=0.7):
    cfg = load_config()
    pref = cfg.get("preferred_provider", "gemini").lower()
    
    gemini_key = get_api_key("gemini")
    openai_key = get_api_key("openai")
    
    errors = []
    providers = ["gemini", "openai"] if pref == "gemini" else ["openai", "gemini"]
    
    for prov in providers:
        if prov == "gemini" and gemini_key:
            try:
                res = call_gemini_api(system_prompt, user_prompt, json_mode, temperature)
                return res, "gemini"
            except Exception as e:
                errors.append(f"Gemini: {str(e)}")
        elif prov == "openai" and openai_key:
            try:
                res = call_openai_api(system_prompt, user_prompt, json_mode, temperature)
                return res, "openai"
            except Exception as e:
                errors.append(f"OpenAI: {str(e)}")
                
    if not gemini_key and not openai_key:
        return None, "sem_chave"
        
    return None, f"Falha nos provedores: {'; '.join(errors)}"

# ==============================================================================
# BANCO DE ALTA RETENÇÃO (FALLBACK OFFLINE INTELIGENTE)
# ==============================================================================

OFFLINE_CURATED_CARDS = {
    "Excel": [
        {
            "q": "O que ocorre quando o 4º argumento do PROCV é omitido na fórmula =PROCV(\"A\"; A1:B10; 2)?",
            "a": "O Excel assume o padrão 1 (ou VERDADEIRO), que executa a pesquisa APROXIMADA. Para essa pesquisa funcionar corretamente, a primeira coluna da matriz obrigatoriamente deve estar em ordem crescente."
        },
        {
            "q": "Qual a diferença exata de causa entre os erros #N/D e #REF! gerados pela função PROCV?",
            "a": "#N/D (Não Disponível): o valor procurado não foi localizado na 1ª coluna da matriz em busca exata. #REF!: o 3º argumento (núm_índice_coluna) faz referência a uma coluna maior que a quantidade total de colunas da matriz informada."
        },
        {
            "q": "A função PROCV faz distinção entre letras maiúsculas e minúsculas ao comparar textos?",
            "a": "NÃO. A função PROCV é 'case-insensitive'. Pesquisar por 'CONCURSO', 'Concurso' ou 'concurso' retornará o mesmo resultado."
        }
    ],
    "Artigo_5": [
        {
            "q": "Quais são os crimes inafiançáveis e imprescritíveis previstos no Art. 5º da CF/88?",
            "a": "Mnemônico RAÇÃO: RAcismo (inciso XLII) e AÇÃO de grupos armados, civis ou militares, contra a ordem constitucional e o Estado Democrático (inciso XLIV)."
        },
        {
            "q": "Em quais hipóteses é permitido o ingresso em domicílio sem o consentimento do morador durante a NOITE?",
            "a": "Apenas em caso de flagrante delito, desastre, ou para prestar socorro. A determinação judicial só autoriza a entrada durante o DIA."
        }
    ],
    "Atos_Administrativos": [
        {
            "q": "Quais são os 5 requisitos de validade de qualquer ato administrativo?",
            "a": "Mnemônico CO-FI-FO-MO-OB: Competência, Finalidade, Forma, Motivo e Objeto."
        },
        {
            "q": "Qual a diferença de efeitos entre anulação e revogação de ato administrativo?",
            "a": "Anulação extingue ato ilegal com efeitos retroativos (Ex Tunc). Revogação extingue ato válido por conveniência e oportunidade com efeitos prospectivos (Ex Nunc)."
        }
    ],
    "Morfologia_e_Sintaxe": [
        {
            "q": "Quais são os casos facultativos de crase (Mnemônico N-A-P)?",
            "a": "1) Diante de Nome próprio feminino; 2) Após a preposição Até; 3) Diante de Pronome possessivo feminino singular (minha, tua, sua)."
        },
        {
            "q": "Qual a concordância na voz passiva sintética com partícula apassivadora (SE)?",
            "a": "Com VTD/VTDI, o verbo concorda obrigatoriamente com o sujeito paciente (Ex: Vendem-se casas; Aluga-se sala)."
        }
    ]
}

# ==============================================================================
# MANIPULAÇÃO E VARREDURA DO SISTEMA DE ARQUIVOS
# ==============================================================================

def cleanup_legacy_structures():
    old_root_excel = os.path.join(BASE_DIR, "Excel")
    inf_excel = os.path.join(BASE_DIR, "Informatica", "Excel")
    if os.path.exists(old_root_excel) and os.path.isdir(old_root_excel):
        try:
            os.makedirs(inf_excel, exist_ok=True)
            for f in os.listdir(old_root_excel):
                src = os.path.join(old_root_excel, f)
                dst = os.path.join(inf_excel, f)
                if not os.path.exists(dst) and os.path.isfile(src):
                    shutil.copy2(src, dst)
                if os.path.isfile(src):
                    os.remove(src)
            os.rmdir(old_root_excel)
        except Exception:
            pass

def scan_concursos_tree():
    cleanup_legacy_structures()
    
    tree = {}
    total_files = 0
    total_cards = 0
    total_quiz = 0
    
    ignore_dirs = {'.git', '__pycache__', 'scratch', '.system_generated', 'Excel'}
    
    for item in sorted(os.listdir(BASE_DIR)):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path) and item not in ignore_dirs:
            discipline = item
            sub_dict = {}
            for sub in sorted(os.listdir(item_path)):
                sub_path = os.path.join(item_path, sub)
                if os.path.isdir(sub_path):
                    files_list = []
                    sub_cards = 0
                    sub_quiz = 0
                    
                    for f in sorted(os.listdir(sub_path)):
                        fp = os.path.join(sub_path, f)
                        if os.path.isfile(fp):
                            size = os.path.getsize(fp)
                            ext = os.path.splitext(f)[1].lower()
                            file_type = "markdown" if ext == ".md" else ("cards" if "anki" in f.lower() else ("quiz" if "simulado" in f.lower() else "text"))
                            
                            cards_count = 0
                            if file_type == "cards":
                                try:
                                    with open(fp, "r", encoding="utf-8", errors="ignore") as fc:
                                        lines = [l.strip() for l in fc if '\t' in l]
                                        cards_count = len(lines)
                                        sub_cards += cards_count
                                        total_cards += cards_count
                                except Exception:
                                    pass
                                    
                            if file_type == "quiz":
                                try:
                                    with open(fp, "r", encoding="utf-8", errors="ignore") as fq:
                                        q_data = json.load(fq)
                                        if isinstance(q_data, list):
                                            sub_quiz += len(q_data)
                                            total_quiz += len(q_data)
                                except Exception:
                                    pass
                                    
                            files_list.append({
                                "name": f,
                                "size": size,
                                "type": file_type,
                                "cards_count": cards_count
                            })
                            total_files += 1
                            
                    sub_dict[sub] = {
                        "files": files_list,
                        "cards_count": sub_cards,
                        "quiz_count": sub_quiz,
                        "files_count": len(files_list)
                    }
                    
            # Inclui a disciplina no mapa estrutural
            tree[discipline] = sub_dict
                
    return {
        "tree": tree,
        "total_files": total_files,
        "total_cards": total_cards,
        "total_quiz": total_quiz,
        "base_dir": BASE_DIR
    }

def read_file_content(rel_path):
    safe_path = os.path.normpath(os.path.join(BASE_DIR, rel_path))
    if not safe_path.startswith(BASE_DIR):
        return None, "Acesso negado."
    if not os.path.exists(safe_path) or not os.path.isfile(safe_path):
        return None, "Arquivo não encontrado."
    try:
        with open(safe_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content, None
    except Exception as e:
        return None, str(e)

def get_subarea_context(discipline, subarea):
    folder = os.path.join(BASE_DIR, discipline, subarea)
    if not os.path.exists(folder):
        return f"Matéria: {discipline} - Tópico: {subarea}"
    
    context_parts = []
    for f in sorted(os.listdir(folder)):
        fp = os.path.join(folder, f)
        if os.path.isfile(fp) and (f.endswith('.md') or f.endswith('.txt')):
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fc:
                    txt = fc.read()[:15000]
                    context_parts.append(f"--- CONTEÚDO DO ARQUIVO {f} ---\n{txt}")
            except Exception:
                pass
    return "\n\n".join(context_parts) if context_parts else f"Matéria: {discipline}, Tópico: {subarea}"

def get_lesson_metadata(discipline, subarea):
    folder = os.path.join(BASE_DIR, discipline, subarea)
    if not os.path.exists(folder):
        return {
            "title": f"{discipline} • {subarea}",
            "professor": "Não definido",
            "duration": "N/D",
            "category": "Geral",
            "youtube_url": "",
            "markdown_content": "",
            "has_lesson": False
        }
    
    lesson_md = None
    for f in os.listdir(folder):
        if f.startswith("Aula_") and f.endswith(".md"):
            lesson_md = os.path.join(folder, f)
            break
    if not lesson_md:
        r = os.path.join(folder, "README.md")
        if os.path.exists(r):
            lesson_md = r
            
    content = ""
    if lesson_md and os.path.exists(lesson_md):
        try:
            with open(lesson_md, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            pass

    title_m = re.search(r"^#\s+(.*)", content, re.MULTILINE)
    prof_m = re.search(r"\*\*Professor(?:\(a\))?:\*\*\s*(.*)", content)
    dur_m = re.search(r"\*\*(?:Dura[çc][ãa]o|Carga Hor[áa]ria):\*\*\s*(.*)", content)
    link_m = re.search(r"(https?://(?:www\.)?(?:youtube\.com/watch\?[^\s\)\"]+|youtu\.be/[^\s\)\"]+))", content)
    cat_m = re.search(r"\*\*Categoria.*:\*\*\s*(.*)", content)
    
    clean_title = title_m.group(1).strip() if title_m else f"{discipline} • {subarea}"
    has_full_lesson = bool(prof_m and link_m)
    
    return {
        "discipline": discipline,
        "subarea": subarea,
        "title": clean_title,
        "professor": prof_m.group(1).strip() if prof_m else "Prof. Titular",
        "duration": dur_m.group(1).strip() if dur_m else "Conteúdo Programático",
        "category": cat_m.group(1).strip() if cat_m else "Edital de Concursos",
        "youtube_url": link_m.group(1).strip() if link_m else "",
        "markdown_content": content,
        "has_lesson": has_full_lesson
    }

def load_reviews(discipline, subarea):
    folder = os.path.join(BASE_DIR, discipline, subarea)
    rfile = os.path.join(folder, "revisoes_erros.json")
    if os.path.exists(rfile):
        try:
            with open(rfile, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"cards": [], "quiz": []}

def save_reviews(discipline, subarea, data):
    folder = os.path.join(BASE_DIR, discipline, subarea)
    os.makedirs(folder, exist_ok=True)
    rfile = os.path.join(folder, "revisoes_erros.json")
    with open(rfile, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_quiz_questions(discipline, subarea):
    folder = os.path.join(BASE_DIR, discipline, subarea)
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if "simulado" in f.lower() and f.endswith(".json"):
                try:
                    with open(os.path.join(folder, f), "r", encoding="utf-8") as fq:
                        return json.load(fq)
                except Exception:
                    pass
    return []

def save_quiz_questions(discipline, subarea, questions):
    folder = os.path.join(BASE_DIR, discipline, subarea)
    os.makedirs(folder, exist_ok=True)
    target = None
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if "simulado" in f.lower() and f.endswith(".json"):
                target = os.path.join(folder, f)
                break
    if not target:
        target = os.path.join(folder, f"Simulado_{subarea}_Questoes.json")
    with open(target, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)


# ==============================================================================
# MOTOR DOS 4 PILARES DE ALTA RETENÇÃO (MÉTODO CONCURSOS PÚBLICOS)
# ==============================================================================

def extract_text_from_pdf_bytes(pdf_bytes):
    """
    Extrai texto completo de todas as páginas de um PDF em memória usando pypdf.
    """
    if not pypdf:
        return 0, "Biblioteca pypdf não instalada."
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        pages_text = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text() or ""
            if t.strip():
                pages_text.append(f"--- PÁGINA {i+1} ---\n{t.strip()}")
        return num_pages, "\n\n".join(pages_text)
    except Exception as e:
        return 0, f"Erro ao extrair texto do PDF: {str(e)}"

def generate_raiox_content(discipline, subarea, context_text, banca="Cebraspe", focus=""):
    """
    Pilar 2: Raio-X de Banca & Pegadinhas Mais Frequentes (Cebraspe, FGV, FCC, Vunesp).
    """
    sys_prompt = (
        f"Você é um especialista sênior em bancas examinadoras de concursos públicos ({banca}, FGV, FCC, Vunesp).\n"
        f"Seu objetivo é gerar uma análise aprofundada de RAIO-X DE BANCA & PEGADINHAS (Pilar 2) sobre o tema solicitado.\n\n"
        "Estruture a saída EXATAMENTE em Markdown no formato:\n"
        "## 2. Raio-X de Banca & Pegadinhas Mais Frequentes\n\n"
        "### 🚨 Pegadinha 1: [Título Curto e Impactante da Armadilha]\n"
        "- **O que a banca afirma para induzir ao erro:** [Exemplo de afirmativa falaciosa ou pegadinha típica]\n"
        "- **Pegadinha desmascarada (Onde está o erro):** [Explicação técnica direta de por que a banca induz ao erro]\n"
        "- **💡 Regra de Ouro / Mnemônico:** [Mnemônico ou regra definitiva para o candidato gabaritar]\n\n"
        "### 🚨 Pegadinha 2: [Título Curto e Impactante]\n"
        "..."
        "\n\nGere de 4 a 6 pegadinhas críticas e armadilhas clássicas da matéria."
    )
    user_prompt = (
        f"Disciplina: {discipline} | Assunto: {subarea}\n"
        f"Banca examinadora foco: {banca}\n"
        f"Foco específico solicitado: {focus if focus else 'Principais pegadinhas, inversões conceituais, prazos e exceções'}\n\n"
        f"Conteúdo de referência:\n{context_text[:12000]}"
    )
    
    raw_md, prov = call_ai_service(sys_prompt, user_prompt, json_mode=False, temperature=0.7)
    if raw_md and "## 2." in raw_md:
        return raw_md.strip(), prov
        
    topic_clean = subarea.replace('_', ' ')
    fallback_md = (
        f"## 2. Raio-X de Banca & Pegadinhas Mais Frequentes ({banca})\n\n"
        f"### 🚨 Pegadinha 1: Inversão Conceitual em {topic_clean}\n"
        f"- **O que a banca afirma para induzir ao erro:** A banca troca termos essenciais ou inverte a regra geral com a exceção.\n"
        f"- **Pegadinha desmascarada (Onde está o erro):** Atenção a termos restritivos como 'apenas', 'sempre', 'exclusivamente' ou 'vedado'. As bancas criam afirmativas aparentemente perfeitas com uma restrição indevida.\n"
        f"- **💡 Regra de Ouro / Mnemônico:** Memorize os requisitos essenciais e desconfie de generalizações sem amparo expresso.\n\n"
        f"### 🚨 Pegadinha 2: Troca de Prazos e Competências\n"
        f"- **O que a banca afirma para induzir ao erro:** Afirma que prazos legais ou competências vinculadas podem ser prorrogados por simples ato administrativo discricionário.\n"
        f"- **Pegadinha desmascarada (Onde está o erro):** Prazos formais e competências vinculadas exigem expressa autorização legal.\n"
        f"- **💡 Regra de Ouro / Mnemônico:** Competência vinculada é irrenunciável e intransferível, salvo expressa delegação legal.\n\n"
        f"### 🚨 Pegadinha 3: Questão de Caso Concreto Extenso\n"
        f"- **O que a banca afirma para induzir ao erro:** Traz uma historinha longa para cansar o candidato e insere a pegadinha na última linha.\n"
        f"- **Pegadinha desmascarada (Onde está o erro):** Isole o comando do item e verifique a conformidade direta com a lei ou edital.\n"
        f"- **💡 Regra de Ouro / Mnemônico:** Sublinhe os conectivos e o verbo principal da assertiva antes de assinalar.\n"
    )
    return fallback_md, "offline_curated"

def update_lesson_markdown_with_raiox(discipline, subarea, raiox_markdown):
    """
    Atualiza ou insere a seção ## 2. Raio-X de Banca no arquivo Aula_01_[Tema].md
    """
    folder = os.path.join(BASE_DIR, discipline, subarea)
    os.makedirs(folder, exist_ok=True)
    
    lesson_md = None
    for f in os.listdir(folder):
        if f.startswith("Aula_") and f.endswith(".md"):
            lesson_md = os.path.join(folder, f)
            break
    if not lesson_md:
        lesson_md = os.path.join(folder, f"Aula_01_{subarea}.md")
        
    content = ""
    if os.path.exists(lesson_md):
        with open(lesson_md, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
    if not content:
        content = (
            f"# {discipline.replace('_', ' ').upper()} - {subarea.replace('_', ' ')}\n"
            f"**Professor:** Prof. Especialista  \n"
            f"**Duração:** 50 minutos  \n"
            f"**Categoria:** Edital de Concursos Públicos  \n\n---\n\n"
            f"## 1. Resumo Estruturado e Conceitos-Chave\n\n"
            f"Conteúdo em estruturação. Revise os pontos na aba Raio-X e Flashcards.\n\n"
        )
        
    # Verificar se já existe a seção ## 2.
    pilar2_match = re.search(r'(##\s*2\.\s*(?:Raio|Pontos|Pegadinha)[^\n]*\n)([\s\S]*?)(?=\n##\s*3\.|\Z)', content, re.IGNORECASE)
    if pilar2_match:
        new_content = content[:pilar2_match.start()] + raiox_markdown + "\n\n" + content[pilar2_match.end():]
    else:
        pilar1_match = re.search(r'(##\s*1\.\s*[^\n]*\n[\s\S]*?)(?=\n##\s*|\Z)', content)
        if pilar1_match:
            insert_pos = pilar1_match.end()
            new_content = content[:insert_pos] + "\n\n" + raiox_markdown + "\n\n" + content[insert_pos:]
        else:
            new_content = content.rstrip() + "\n\n---\n\n" + raiox_markdown + "\n"
            
    with open(lesson_md, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    return lesson_md

def generate_pilar1_summary(discipline, subarea, title, professor, context_text):
    """
    Pilar 1: Resumo Estruturado com definições, conceitos-chave e tabelas comparativas.
    """
    sys_prompt = (
        "Você é um professor titular e elaborador sênior para concursos públicos de alto nível.\n"
        "Seu objetivo é criar o PILAR 1: RESUMO ESTRUTURADO E CONCEITOS-CHAVE com base no conteúdo fornecido.\n\n"
        "Estruture em Markdown impecável contendo:\n"
        "- Definições formais, regras gerais e requisitos\n"
        "- Subseções lógicas (### A. ..., ### B. ...)\n"
        "- Tabelas comparativas em markdown quando houver termos confrontados\n"
        "- Mnemônicos e destaques em negrito\n\n"
        "Inicie obrigatoriamente em:\n"
        "## 1. Resumo Estruturado e Conceitos-Chave"
    )
    user_prompt = (
        f"Disciplina: {discipline} | Subárea: {subarea} | Título: {title}\n\n"
        f"Conteúdo de Estudo / Transcrição / PDF:\n{context_text[:14000]}"
    )
    raw_md, _ = call_ai_service(sys_prompt, user_prompt, json_mode=False, temperature=0.6)
    if raw_md and "## 1." in raw_md:
        return raw_md.strip()
        
    return (
        f"## 1. Resumo Estruturado e Conceitos-Chave\n\n"
        f"### A. Fundamentos Essenciais de {subarea.replace('_', ' ')}\n"
        f"O estudo de **{subarea.replace('_', ' ')}** na disciplina de **{discipline.replace('_', ' ')}** exige domínio das definições fundamentais, regras de incidência e competências do edital.\n\n"
        f"- **Conceito Primário:** Conjunto de normas e preceitos aplicáveis com incidência recorrente em provas.\n"
        f"- **Aplicação:** Identificação rápida de padrões nas questões das principais bancas examinadoras.\n\n"
        f"{context_text[:3000] if context_text else 'Consulte os tópicos detalhados no material completo.'}"
    )

def generate_flashcards_from_text(discipline, subarea, context_text, count=6):
    """
    Pilar 3: Flashcards de Alta Retenção no padrão Anki.
    """
    sys_prompt = (
        "Você é um especialista em memorização e flashcards Anki para concursos públicos.\n"
        "Crie perguntas e respostas cirúrgicas, focadas em prazos, mnemônicos, exceções e pegadinhas.\n"
        "Retorne SEMPRE um JSON no formato:\n"
        "{\"cards\": [{\"q\": \"Pergunta desafiadora\", \"a\": \"Resposta fundamentada com a regra de prova\"}]}"
    )
    user_prompt = f"Disciplina: {discipline} | Assunto: {subarea}\n\nMaterial de Estudo:\n{context_text[:12000]}\n\nGere exatamente {count} flashcards de alta retenção."
    raw_json, _ = call_ai_service(sys_prompt, user_prompt, json_mode=True)
    cards = []
    if raw_json:
        try:
            data = json.loads(raw_json)
            cards = data.get("cards", [])
        except Exception:
            pass
    if not cards:
        cards = [
            {"q": f"Qual o conceito fundamental de {subarea.replace('_', ' ')} mais cobrado em concursos?", "a": f"É a regra nuclear aplicável a {discipline.replace('_', ' ')}, exigindo atenção às exceções e termos restritivos."},
            {"q": f"Quais são os erros mais comuns de candidatos ao responder questões sobre {subarea.replace('_', ' ')}?", "a": "Confundir regras gerais com hipóteses excepcionais e desconsiderar a jurisprudência das bancas."},
            {"q": f"Como identificar pegadinhas da banca sobre {subarea.replace('_', ' ')}?", "a": "Verificando se há inversão de conceitos, prazos ou atribuições entre órgãos/competências."}
        ]
    return cards

def generate_quiz_from_text(discipline, subarea, context_text, banca="Cebraspe", count=5):
    """
    Pilar 4: Mini-Simulado de Fixação (Cebraspe Certo/Errado ou Múltipla Escolha).
    """
    sys_prompt = (
        f"Você é um examinador de bancas de concursos ({banca}).\n"
        f"Crie {count} questões de fixação inéditas e desafiadoras com base no material fornecido.\n"
        "Se Cebraspe: 'options' DEVE ser estritamente [\"A) CERTO\", \"B) ERRADO\"].\n"
        "Se FGV, FCC ou Vunesp: 'options' com 4 ou 5 alternativas (A, B, C, D, E).\n"
        "Retorne SEMPRE um JSON válido:\n"
        "{\"questions\": [{\"enunciado\": \"...\", \"options\": [...], \"correct_index\": 0, \"comentario\": \"...\"}]}"
    )
    user_prompt = f"Banca: {banca} | Disciplina: {discipline} | Assunto: {subarea}\n\nMaterial:\n{context_text[:12000]}"
    raw_json, _ = call_ai_service(sys_prompt, user_prompt, json_mode=True, temperature=0.7)
    questions = []
    if raw_json:
        try:
            data = json.loads(raw_json)
            questions = data.get("questions", [])
        except Exception:
            pass
    if not questions:
        if banca == "Cebraspe":
            questions = [
                {
                    "enunciado": f"A respeito de {subarea.replace('_', ' ')} em {discipline.replace('_', ' ')}, julgue o item a seguir: A observância dos preceitos legais e jurisprudenciais consolidados é de caráter imperativo e vinculante para a resolução de questões de prova.",
                    "options": ["A) CERTO", "B) ERRADO"],
                    "correct_index": 0,
                    "comentario": "Item CERTO. A assertiva reflete a correta aplicação dos preceitos normativos exigidos em editais de concursos.",
                    "banca": "Cebraspe"
                }
            ]
        else:
            questions = [
                {
                    "enunciado": f"Em relação a {subarea.replace('_', ' ')}, assinale a alternativa correta:",
                    "options": [
                        "A) As regras e princípios aplicam-se com estrita observância das normas regulamentares vigentes.",
                        "B) É dispensável qualquer formalidade legal.",
                        "C) Os prazos prescricionais podem ser alterados unilateralmente sem previsão em lei.",
                        "D) Nenhuma das anteriores."
                    ],
                    "correct_index": 0,
                    "comentario": "Alternativa A correta. Obediência estrita aos preceitos legais e do edital.",
                    "banca": banca
                }
            ]
    for q in questions:
        q["banca"] = q.get("banca", banca)
    return questions

def auto_generate_all_4_pillars(discipline, subarea, title, professor, text_corpus, yt_url="", banca="Cebraspe"):
    """
    Executa a geração completa ponta a ponta dos 4 Pilares de Alta Retenção:
    1. Resumo Estruturado (Aula_01_[Tema].md)
    2. Raio-X de Banca & Pegadinhas (Aula_01_[Tema].md)
    3. Flashcards Anki (Flashcards_[Tema]_Anki.txt)
    4. Mini-Simulado de Fixação (Simulado_[Tema]_Questoes.json)
    """
    folder = os.path.join(BASE_DIR, discipline, subarea)
    os.makedirs(folder, exist_ok=True)
    
    # 1. Resumo Estruturado
    pilar1_text = generate_pilar1_summary(discipline, subarea, title, professor, text_corpus)
    
    # 2. Raio-X de Banca & Pegadinhas
    raiox_text, _ = generate_raiox_content(discipline, subarea, text_corpus, banca=banca)
    
    # Montar e salvar Aula_01_[Tema].md
    aula_md = f"# {discipline.replace('_', ' ').upper()} - {title}\n"
    aula_md += f"**Professor:** {professor}  \n"
    if yt_url:
        aula_md += f"**Link da Aula:** [Assistir no YouTube]({yt_url})  \n"
    aula_md += "**Duração:** 50 minutos  \n"
    aula_md += f"**Categoria:** Edital de Concursos Públicos ({banca})  \n\n---\n\n"
    aula_md += pilar1_text.strip() + "\n\n---\n\n"
    aula_md += raiox_text.strip() + "\n"
    
    lesson_path = os.path.join(folder, f"Aula_01_{subarea}.md")
    with open(lesson_path, "w", encoding="utf-8") as fm:
        fm.write(aula_md)
        
    # 3. Flashcards Anki
    cards = generate_flashcards_from_text(discipline, subarea, text_corpus, count=6)
    anki_path = os.path.join(folder, f"Flashcards_{subarea}_Anki.txt")
    with open(anki_path, "w", encoding="utf-8") as fa:
        for c in cards:
            fa.write(f"{c['q']}\t{c['a']}\n")
            
    # 4. Mini-Simulado de Fixação
    questions = generate_quiz_from_text(discipline, subarea, text_corpus, banca=banca, count=5)
    save_quiz_questions(discipline, subarea, questions)
    
    # Salvar Transcrição Completa / Texto Fonte
    if text_corpus:
        full_text_path = os.path.join(folder, f"Transcricao_Completa_{subarea}.txt")
        with open(full_text_path, "w", encoding="utf-8") as ft:
            ft.write(text_corpus)
            
    # Inicializar Caderno de Erros
    rfile = os.path.join(folder, "revisoes_erros.json")
    if not os.path.exists(rfile):
        with open(rfile, "w", encoding="utf-8") as fr:
            json.dump({"cards": [], "quiz": []}, fr)
            
    return {
        "lesson_path": lesson_path,
        "cards_count": len(cards),
        "quiz_count": len(questions)
    }

# ==============================================================================
# CONTROLADOR HTTP PRINCIPAL
# ==============================================================================

class ConcursosHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Página Inicial SPA
        if path in ("/", "/index.html"):
            if os.path.exists(HTML_FILE):
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.end_headers()
                with open(HTML_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()

        # 2. Árvore Completa e Métricas
        elif path == "/api/structure":
            data = scan_concursos_tree()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

        # 3. Metadados e Conteúdo da Aula Selecionada
        elif path == "/api/lesson":
            disc = query.get("discipline", ["Informatica"])[0]
            sub = query.get("subarea", ["Excel"])[0]
            meta = get_lesson_metadata(disc, sub)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(meta, ensure_ascii=False).encode("utf-8"))

        # 4. Status das Configurações de IA
        elif path == "/api/config":
            cfg = load_config()
            gem_key = get_api_key("gemini")
            oai_key = get_api_key("openai")
            active = "gemini" if gem_key else ("openai" if oai_key else "offline_bank")
            
            res_data = {
                "has_gemini": bool(gem_key),
                "has_openai": bool(oai_key),
                "active_provider": active,
                "preferred_provider": cfg.get("preferred_provider", "gemini"),
                "gemini_masked": mask_key(gem_key),
                "openai_masked": mask_key(oai_key)
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode("utf-8"))

        # 5. Progresso de Repetição Espaçada e Estatísticas
        elif path == "/api/progress":
            prog = load_progress()
            today = datetime.date.today().isoformat()
            due_cards = 0
            for ck, info in prog.get("cards", {}).items():
                nr = info.get("next_review", "")
                if nr and nr <= today:
                    due_cards += 1
                    
            res = {
                "due_today": due_cards,
                "total_studied_cards": len(prog.get("cards", {})),
                "cebraspe_count": len(prog.get("cebraspe_simulados", [])),
                "cebraspe_history": prog.get("cebraspe_simulados", [])[-10:],
                "cards_details": prog.get("cards", {})
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

        # 6. Flashcards do Tópico (Sem duplicatas)
        elif path == "/api/flashcards":
            disc = query.get("discipline", ["Informatica"])[0]
            sub = query.get("subarea", ["Excel"])[0]
            folder = os.path.join(BASE_DIR, disc, sub)
            cards = []
            seen = set()
            
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if "anki" in f.lower() and f.endswith(".txt"):
                        fp = os.path.join(folder, f)
                        try:
                            with open(fp, "r", encoding="utf-8", errors="ignore") as fc:
                                for line in fc:
                                    line = line.strip()
                                    if "\t" in line:
                                        parts = line.split("\t", 1)
                                        q = parts[0].strip()
                                        a = parts[1].strip()
                                        norm_q = q.lower().replace("?", "").strip()
                                        if norm_q not in seen:
                                            seen.add(norm_q)
                                            cards.append({"q": q, "a": a})
                        except Exception:
                            pass
                            
            if not cards:
                key = "Excel" if "excel" in sub.lower() else ("Artigo_5" if "artigo" in sub.lower() else "")
                if key and key in OFFLINE_CURATED_CARDS:
                    cards = OFFLINE_CURATED_CARDS[key]
                    
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(cards, ensure_ascii=False).encode("utf-8"))

        # 7. Questões de Simulado
        elif path == "/api/quiz":
            disc = query.get("discipline", ["Informatica"])[0]
            sub = query.get("subarea", ["Excel"])[0]
            questions = load_quiz_questions(disc, sub)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(questions, ensure_ascii=False).encode("utf-8"))

        # 8. Caderno de Erros / Revisões
        elif path == "/api/reviews":
            disc = query.get("discipline", ["Informatica"])[0]
            sub = query.get("subarea", ["Excel"])[0]
            revs = load_reviews(disc, sub)
            total = len(revs.get("cards", [])) + len(revs.get("quiz", []))
            revs["total"] = total
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(revs, ensure_ascii=False).encode("utf-8"))

        # 9. Momentos-Chave Salvos
        elif path == "/api/moments":
            disc = query.get("discipline", [""])[0]
            sub = query.get("subarea", [""])[0]
            sub_path = find_subarea_path(disc, sub)
            
            moments = []
            has_timed = False

            # 1. Tentar primeiro do Supabase se configurado
            if supabase_client and supabase_client.is_supabase_configured():
                try:
                    full_info = supabase_client.get_aula_full(disc, sub)
                    if full_info and full_info.get("conteudo"):
                        c_moments = full_info["conteudo"].get("momentos_chave")
                        if isinstance(c_moments, list) and len(c_moments) > 0:
                            moments = c_moments
                            has_timed = bool(full_info["conteudo"].get("transcricao_cronometrada"))
                except Exception as e_supa:
                    print(f"Erro ao buscar momentos no Supabase: {e_supa}")

            # 2. Fallback no disco local
            if not moments and sub_path and os.path.exists(sub_path):
                for f in os.listdir(sub_path):
                    if f.lower().startswith("transcricao_cronometrada"):
                        has_timed = True
                    if f.lower().startswith("momentos_chave") and f.endswith(".json"):
                        try:
                            with open(os.path.join(sub_path, f), "r", encoding="utf-8") as f_in:
                                loaded = json.load(f_in)
                                if isinstance(loaded, list) and len(loaded) > 0:
                                    moments = loaded
                        except Exception:
                            pass

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "moments": moments,
                "has_timed_transcript": has_timed
            }, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/supabase/status":
            is_cfg = supabase_client.is_supabase_configured() if supabase_client else False
            ok = False
            msg = "Supabase não configurado"
            url, key = ("", "")
            if is_cfg and supabase_client:
                ok, msg = supabase_client.test_connection()
                url, key = supabase_client.get_supabase_config()
            masked_key = (key[:6] + "..." + key[-4:]) if len(key) > 10 else ("***" if key else "")
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "configured": is_cfg,
                "connected": ok,
                "message": msg,
                "url": url,
                "masked_key": masked_key
            }, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/transcript":
            disc = query.get("discipline", ["Informatica"])[0]
            sub = query.get("subarea", ["Excel"])[0]
            folder = os.path.join(BASE_DIR, disc, sub)
            timed_file = None
            full_file = None
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if "cronometrada" in f.lower() and f.endswith(".txt"):
                        timed_file = os.path.join(folder, f)
                    elif "completa" in f.lower() and f.endswith(".txt"):
                        full_file = os.path.join(folder, f)
            
            timed_lines = []
            full_text = ""
            
            if timed_file and os.path.exists(timed_file):
                try:
                    with open(timed_file, "r", encoding="utf-8", errors="ignore") as ft:
                        for line in ft:
                            line = line.strip()
                            if line:
                                m = re.match(r"\[([\d\.]+)s\]\s*(.*)", line)
                                if m:
                                    sec = float(m.group(1))
                                    txt = m.group(2).strip()
                                    mins = int(sec // 60)
                                    secs = int(sec % 60)
                                    t_fmt = f"{mins:02d}:{secs:02d}"
                                    timed_lines.append({
                                        "seconds": int(sec),
                                        "t": f"{sec:.1f}s",
                                        "time_fmt": t_fmt,
                                        "text": txt
                                    })
                                else:
                                    timed_lines.append({
                                        "seconds": 0,
                                        "t": "",
                                        "time_fmt": "",
                                        "text": line
                                    })
                except Exception:
                    pass

            if full_file and os.path.exists(full_file):
                try:
                    with open(full_file, "r", encoding="utf-8", errors="ignore") as ff:
                        full_text = ff.read()
                except Exception:
                    pass

            if not full_text and os.path.exists(folder):
                for f in os.listdir(folder):
                    if (f.startswith("Aula_") and f.endswith(".md")) or f.lower() == "readme.md":
                        try:
                            with open(os.path.join(folder, f), "r", encoding="utf-8", errors="ignore") as fmd:
                                full_text = fmd.read()
                        except Exception:
                            pass
                        break

            is_video = bool(timed_file and len(timed_lines) > 0)
            
            # Se não for vídeo (PDF ou texto puro), segmentar o texto em páginas estruturadas
            if not is_video and full_text:
                page_matches = list(re.finditer(r"---\s*PÁGINA\s+(\d+)\s*---", full_text, re.IGNORECASE))
                if page_matches:
                    for idx, m_page in enumerate(page_matches):
                        p_num = int(m_page.group(1))
                        start_pos = m_page.end()
                        end_pos = page_matches[idx + 1].start() if idx + 1 < len(page_matches) else len(full_text)
                        page_block = full_text[start_pos:end_pos].strip()
                        paras = [p.strip() for p in page_block.split("\n\n") if p.strip()]
                        for p_txt in paras:
                            if len(p_txt) > 8:
                                timed_lines.append({
                                    "seconds": 0,
                                    "page": p_num,
                                    "t": f"Pág. {p_num:02d}",
                                    "time_fmt": f"Pág. {p_num:02d}",
                                    "text": p_txt
                                })
                else:
                    # Segmentar por parágrafos lógicos com numeração sequencial de páginas
                    raw_paras = [p.strip() for p in full_text.split("\n\n") if p.strip()]
                    current_p = 1
                    char_count = 0
                    for p_txt in raw_paras:
                        # Dividir sub-linhas se necessário
                        lines_in_p = [l.strip() for l in p_txt.split("\n") if len(l.strip()) > 10]
                        for l_txt in lines_in_p:
                            if l_txt.startswith("#") or l_txt.startswith("---") or l_txt.startswith("**Professor:"):
                                continue
                            timed_lines.append({
                                "seconds": 0,
                                "page": current_p,
                                "t": f"Pág. {current_p:02d}",
                                "time_fmt": f"Pág. {current_p:02d}",
                                "text": l_txt
                            })
                            char_count += len(l_txt)
                            if char_count > 450:
                                current_p += 1
                                char_count = 0

            res_data = {
                "total": len(timed_lines),
                "timed": timed_lines,
                "full_text": full_text,
                "is_video": is_video,
                "content_type": "video" if is_video else ("pdf" if "página" in full_text.lower() else "text")
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode("utf-8"))

        # 10. Conteúdo Bruto de Arquivo
        elif path == "/api/content":
            file_param = query.get("file", [""])[0]
            if not file_param:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Parametro 'file' obrigatorio.")
                return
            content, err = read_file_content(file_param)
            if err:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(err.encode("utf-8"))
                return
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        # 11. Exportar Todos os Flashcards para Anki em lote
        elif path == "/api/export-anki":
            all_cards = []
            disc = query.get("discipline", [""])[0]
            sub = query.get("subarea", [""])[0]
            
            tree_data = scan_concursos_tree()["tree"]
            for d_name, subs in tree_data.items():
                if disc and d_name != disc:
                    continue
                for s_name in subs:
                    if sub and s_name != sub:
                        continue
                    folder = os.path.join(BASE_DIR, d_name, s_name)
                    if os.path.exists(folder):
                        for f in os.listdir(folder):
                            if "anki" in f.lower() and f.endswith(".txt"):
                                try:
                                    with open(os.path.join(folder, f), "r", encoding="utf-8", errors="ignore") as fc:
                                        for line in fc:
                                            if "\t" in line:
                                                all_cards.append(line.strip())
                                except Exception:
                                    pass
                                    
            content = "\n".join(all_cards)
            filename = f"Deck_{sub if sub else 'Concursos'}_Anki.txt"
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.send_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))

        # 13. Renomear Disciplina
        elif path == "/api/discipline/rename":
            old_name = payload.get("old_name", "").strip().replace(" ", "_")
            new_name = payload.get("new_name", "").strip().replace(" ", "_")
            
            if not old_name or not new_name:
                self.send_response(400)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Nome antigo e novo nome da matéria são obrigatórios."}, ensure_ascii=False).encode("utf-8"))
                return
                
            if any(".." in x or "/" in x or "\\" in x for x in [old_name, new_name]):
                self.send_response(400)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Caracteres inválidos no nome da matéria."}, ensure_ascii=False).encode("utf-8"))
                return
                
            old_path = os.path.join(BASE_DIR, old_name)
            new_path = os.path.join(BASE_DIR, new_name)
            
            if not os.path.exists(old_path) or not os.path.isdir(old_path):
                self.send_response(404)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": f"Matéria '{old_name}' não encontrada."}, ensure_ascii=False).encode("utf-8"))
                return
                
            if old_name != new_name:
                if old_name.lower() == new_name.lower():
                    # Renomeação apenas de maiúsculas/minúsculas no Windows NTFS
                    temp_path = old_path + "_tmp_case_" + str(int(time.time() * 1000))
                    try:
                        os.rename(old_path, temp_path)
                        os.rename(temp_path, new_path)
                    except Exception as e_ren:
                        self.send_response(500)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Erro ao renomear pasta: {str(e_ren)}"}, ensure_ascii=False).encode("utf-8"))
                        return
                else:
                    if os.path.exists(new_path):
                        self.send_response(400)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Já existe uma matéria com o nome '{new_name.replace('_', ' ')}'."}, ensure_ascii=False).encode("utf-8"))
                        return
                    try:
                        os.rename(old_path, new_path)
                    except Exception as e_ren:
                        self.send_response(500)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Erro ao renomear pasta: {str(e_ren)}"}, ensure_ascii=False).encode("utf-8"))
                        return
                    
                # Atualizar registros em progresso_estudos.json
                try:
                    prog = load_progress()
                    prog_changed = False
                    for ck, cv in prog.get("cards", {}).items():
                        if cv.get("discipline") == old_name:
                            cv["discipline"] = new_name
                            prog_changed = True
                    for q in prog.get("quiz_history", []):
                        if q.get("discipline") == old_name:
                            q["discipline"] = new_name
                            prog_changed = True
                    for s in prog.get("cebraspe_simulados", []):
                        if s.get("discipline") == old_name:
                            s["discipline"] = new_name
                            prog_changed = True
                    if prog_changed:
                        save_progress(prog)
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "old_name": old_name, 
                "new_name": new_name,
                "message": f"Disciplina renomeada para '{new_name.replace('_', ' ')}' com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        # 14. Excluir Disciplina (e todos os seus tópicos)
        elif path == "/api/discipline/delete":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            if not disc:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Nome da disciplina obrigatorio.")
                return
                
            if ".." in disc or "/" in disc or "\\" in disc:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Nome de disciplina invalido.")
                return
                
            disc_path = os.path.join(BASE_DIR, disc)
            if not os.path.exists(disc_path) or not os.path.isdir(disc_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(f"Disciplina '{disc}' nao encontrada.".encode("utf-8"))
                return
                
            try:
                shutil.rmtree(disc_path)
            except Exception as e_del:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Erro ao remover disciplina: {str(e_del)}".encode("utf-8"))
                return
                
            # Atualizar progresso_estudos.json
            try:
                prog = load_progress()
                cards = prog.get("cards", {})
                prog["cards"] = {k: v for k, v in cards.items() if v.get("discipline") != disc}
                prog["quiz_history"] = [q for q in prog.get("quiz_history", []) if q.get("discipline") != disc]
                prog["cebraspe_simulados"] = [s for s in prog.get("cebraspe_simulados", []) if s.get("discipline") != disc]
                save_progress(prog)
            except Exception:
                pass

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "discipline": disc,
                "message": f"Disciplina '{disc.replace('_', ' ')}' excluída com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        # 15. Renomear Tópico / Subárea
        elif path == "/api/subarea/rename":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            old_name = payload.get("old_name", "").strip().replace(" ", "_")
            new_name = payload.get("new_name", "").strip().replace(" ", "_")
            
            if not disc or not old_name or not new_name:
                self.send_response(400)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Matéria, nome antigo e novo nome do tópico são obrigatórios."}, ensure_ascii=False).encode("utf-8"))
                return
                
            if any(".." in x or "/" in x or "\\" in x for x in [disc, old_name, new_name]):
                self.send_response(400)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Caracteres inválidos detectados no nome do tópico."}, ensure_ascii=False).encode("utf-8"))
                return
                
            old_sub_path = os.path.join(BASE_DIR, disc, old_name)
            new_sub_path = os.path.join(BASE_DIR, disc, new_name)
            
            if not os.path.exists(old_sub_path) or not os.path.isdir(old_sub_path):
                self.send_response(404)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": f"Tópico '{old_name}' não encontrado em '{disc}'."}, ensure_ascii=False).encode("utf-8"))
                return
                
            if old_name != new_name:
                if old_name.lower() == new_name.lower():
                    # Renomeação apenas de maiúsculas/minúsculas no Windows NTFS
                    temp_sub_path = old_sub_path + "_tmp_case_" + str(int(time.time() * 1000))
                    try:
                        os.rename(old_sub_path, temp_sub_path)
                        os.rename(temp_sub_path, new_sub_path)
                    except Exception as e_sub_ren:
                        self.send_response(500)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Erro ao renomear tópico: {str(e_sub_ren)}"}, ensure_ascii=False).encode("utf-8"))
                        return
                else:
                    if os.path.exists(new_sub_path):
                        self.send_response(400)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Já existe um tópico com o nome '{new_name.replace('_', ' ')}' nesta matéria."}, ensure_ascii=False).encode("utf-8"))
                        return
                    try:
                        os.rename(old_sub_path, new_sub_path)
                    except Exception as e_sub_ren:
                        self.send_response(500)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Erro ao renomear tópico: {str(e_sub_ren)}"}, ensure_ascii=False).encode("utf-8"))
                        return
                    
                # Renomear arquivos internos que contenham o nome do tópico antigo
                try:
                    for fname in os.listdir(new_sub_path):
                        if old_name in fname:
                            new_fname = fname.replace(old_name, new_name)
                            src_f = os.path.join(new_sub_path, fname)
                            dst_f = os.path.join(new_sub_path, new_fname)
                            if not os.path.exists(dst_f):
                                os.rename(src_f, dst_f)
                except Exception:
                    pass
                    
                # Atualizar em progresso_estudos.json
                try:
                    prog = load_progress()
                    prog_changed = False
                    for ck, cv in prog.get("cards", {}).items():
                        if cv.get("discipline") == disc and cv.get("subarea") == old_name:
                            cv["subarea"] = new_name
                            prog_changed = True
                    for q in prog.get("quiz_history", []):
                        if q.get("discipline") == disc and q.get("subarea") == old_name:
                            q["subarea"] = new_name
                            prog_changed = True
                    for s in prog.get("cebraspe_simulados", []):
                        if s.get("discipline") == disc and s.get("subarea") == old_name:
                            s["subarea"] = new_name
                            prog_changed = True
                    if prog_changed:
                        save_progress(prog)
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "discipline": disc,
                "old_name": old_name, 
                "new_name": new_name,
                "message": f"Tópico renomeado para '{new_name.replace('_', ' ')}' com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        # 16. Excluir Tópico / Subárea
        elif path == "/api/subarea/delete":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            sub = payload.get("subarea", "").strip().replace(" ", "_")
            
            if not disc or not sub:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Disciplina e topico sao obrigatorios.")
                return
                
            if any(".." in x or "/" in x or "\\" in x for x in [disc, sub]):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Caracteres invalidos detectados.")
                return
                
            sub_path = os.path.join(BASE_DIR, disc, sub)
            if not os.path.exists(sub_path) or not os.path.isdir(sub_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(f"Topico '{sub}' nao encontrado em '{disc}'.".encode("utf-8"))
                return
                
            try:
                shutil.rmtree(sub_path)
            except Exception as e_del:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Erro ao excluir topico: {str(e_del)}".encode("utf-8"))
                return
                
            # Atualizar progresso_estudos.json
            try:
                prog = load_progress()
                cards = prog.get("cards", {})
                prog["cards"] = {k: v for k, v in cards.items() if not (v.get("discipline") == disc and v.get("subarea") == sub)}
                prog["quiz_history"] = [q for q in prog.get("quiz_history", []) if not (q.get("discipline") == disc and q.get("subarea") == sub)]
                prog["cebraspe_simulados"] = [s for s in prog.get("cebraspe_simulados", []) if not (s.get("discipline") == disc and s.get("subarea") == sub)]
                save_progress(prog)
            except Exception:
                pass

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "discipline": disc,
                "subarea": sub,
                "message": f"Tópico '{sub.replace('_', ' ')}' excluído com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        # 17. Criar Nova Disciplina
        elif path == "/api/discipline/create":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            if not disc:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Nome da disciplina obrigatorio.")
                return
            if ".." in disc or "/" in disc or "\\" in disc:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Nome de disciplina invalido.")
                return
            disc_path = os.path.join(BASE_DIR, disc)
            os.makedirs(disc_path, exist_ok=True)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "discipline": disc,
                "message": f"Disciplina '{disc.replace('_', ' ')}' criada com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # 1. Salvar Configurações de IA
        if path == "/api/config":
            cfg = load_config()
            if "gemini_api_key" in payload:
                cfg["gemini_api_key"] = payload["gemini_api_key"].strip()
            if "openai_api_key" in payload:
                cfg["openai_api_key"] = payload["openai_api_key"].strip()
            if "preferred_provider" in payload:
                cfg["preferred_provider"] = payload["preferred_provider"].strip()
            save_config(cfg)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Configurações atualizadas!"}).encode("utf-8"))

        # 2. Registrar Avaliação SM-2 de Flashcard
        elif path == "/api/progress/card":
            card_q = payload.get("q", "").strip()
            card_a = payload.get("a", "").strip()
            disc = payload.get("discipline", "")
            sub = payload.get("subarea", "")
            quality = int(payload.get("quality", 3)) # 1 (difícil), 3 (médio), 5 (fácil)
            if not card_q:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Pergunta do cartao obrigatoria.")
                return
            card_res = record_card_sm2(card_q, quality, card_a=card_a, discipline=disc, subarea=sub)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "sm2": card_res}).encode("utf-8"))

        # 3. Registrar Resultado de Simulado Modo Cebraspe
        elif path == "/api/simulado/cebraspe":
            prog = load_progress()
            record = {
                "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "discipline": payload.get("discipline", "Geral"),
                "subarea": payload.get("subarea", "Geral"),
                "certas": payload.get("certas", 0),
                "erradas": payload.get("erradas", 0),
                "em_branco": payload.get("em_branco", 0),
                "nota_liquida": payload.get("certas", 0) - payload.get("erradas", 0),
                "total_questoes": payload.get("total", 0),
                "tempo_segundos": payload.get("tempo_segundos", 0)
            }
            prog.setdefault("cebraspe_simulados", []).append(record)
            save_progress(prog)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "record": record}).encode("utf-8"))

        # 4. Adicionar Item ao Caderno de Revisões (Erros)
        elif path == "/api/reviews/add":
            disc = payload.get("discipline", "Informatica")
            sub = payload.get("subarea", "Excel")
            item_type = payload.get("type", "card")
            item_data = payload.get("item", {})
            
            revs = load_reviews(disc, sub)
            if item_type == "card":
                q = item_data.get("q", "").strip()
                if q and not any(c.get("q") == q for c in revs.get("cards", [])):
                    revs.setdefault("cards", []).append(item_data)
            elif item_type == "quiz":
                enunciado = item_data.get("enunciado", "").strip()
                if enunciado and not any(qz.get("enunciado") == enunciado for qz in revs.get("quiz", [])):
                    revs.setdefault("quiz", []).append(item_data)
            
            save_reviews(disc, sub, revs)
            total = len(revs.get("cards", [])) + len(revs.get("quiz", []))
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "total": total, "reviews": revs}).encode("utf-8"))

        # 5. Resolver / Remover Item de Revisões (Acertou!)
        elif path == "/api/reviews/resolve":
            disc = payload.get("discipline", "Informatica")
            sub = payload.get("subarea", "Excel")
            item_type = payload.get("type", "card")
            identifier = payload.get("id", "").strip()
            
            revs = load_reviews(disc, sub)
            if item_type == "card":
                revs["cards"] = [c for c in revs.get("cards", []) if c.get("q", "").strip() != identifier]
            elif item_type == "quiz":
                revs["quiz"] = [qz for qz in revs.get("quiz", []) if qz.get("enunciado", "").strip() != identifier]
                
            save_reviews(disc, sub, revs)
            total = len(revs.get("cards", [])) + len(revs.get("quiz", []))
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "total": total, "reviews": revs}).encode("utf-8"))

        # 6. Geração de Flashcards com IA + Fallback de Alta Retenção
        elif path == "/api/generate-ai-flashcards":
            disc = payload.get("discipline", "Informatica")
            sub = payload.get("subarea", "Excel")
            count = int(payload.get("count", 4))
            topic_focus = payload.get("focus", "")
            
            folder = os.path.join(BASE_DIR, disc, sub)
            existing_questions = []
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if "anki" in f.lower() and f.endswith(".txt"):
                        try:
                            with open(os.path.join(folder, f), "r", encoding="utf-8", errors="ignore") as fc:
                                for line in fc:
                                    if "\t" in line:
                                        parts = line.split("\t", 1)
                                        existing_questions.append(parts[0].strip())
                        except Exception:
                            pass
            
            existing_prompt_list = "\n".join([f"- {q}" for q in existing_questions]) if existing_questions else "Nenhum cartão anterior."
            context = get_subarea_context(disc, sub)
            
            sys_prompt = (
                "Você é um elaborador sênior de questões e flashcards para concursos públicos de alto nível (Cebraspe, FGV, FCC, Vunesp).\n"
                "Seu objetivo é criar FLASHCARDS CIRÚRGICOS, INÉDITOS e SEM REPETIÇÃO baseados no conteúdo da matéria e aula.\n"
                "REGRA DE OURO: É expressamente proibido repetir ou parafrasear perguntas que constem na lista existente.\n"
                "Retorne SEMPRE um JSON no formato:\n"
                "{\"cards\": [{\"q\": \"Pergunta desafiadora inédita\", \"a\": \"Resposta clara com fundamentação e regra de prova\"}]}"
            )
            
            user_prompt = (
                f"Disciplina: {disc} | Assunto: {sub}\n"
                f"Foco solicitado: {topic_focus if topic_focus else 'Pegadinhas Críticas e Casos Especiais'}\n\n"
                f"LISTA DE FLASHCARDS JÁ EXISTENTES (NÃO REPITA ESTES TEMAS):\n{existing_prompt_list}\n\n"
                f"Gere exatamente {count} NOVOS flashcards inéditos baseando-se no conteúdo da disciplina:\n\n{context[:12000]}"
            )
            
            cards_to_save = []
            provider_used = "offline_bank"
            
            raw_json, prov = call_ai_service(sys_prompt, user_prompt, json_mode=True)
            if raw_json:
                try:
                    data = json.loads(raw_json)
                    candidate_cards = data.get("cards", [])
                    clean_cards = []
                    for c in candidate_cards:
                        q_new = c["q"].strip()
                        q_lower = q_new.lower()
                        is_dup = False
                        for eq in existing_questions:
                            eq_lower = eq.lower()
                            if q_lower == eq_lower:
                                is_dup = True
                                break
                            w_new = set([w for w in re.split(r'\W+', q_lower) if len(w) > 4])
                            w_old = set([w for w in re.split(r'\W+', eq_lower) if len(w) > 4])
                            if w_new and w_old:
                                overlap = len(w_new.intersection(w_old)) / max(len(w_new), len(w_old))
                                if overlap > 0.60:
                                    is_dup = True
                                    break
                        if not is_dup:
                            clean_cards.append(c)
                    cards_to_save = clean_cards if clean_cards else candidate_cards
                    provider_used = prov
                except Exception:
                    pass
                    
            if not cards_to_save:
                key = sub if sub in OFFLINE_CURATED_CARDS else ("Excel" if "excel" in sub.lower() else ("Artigo_5" if "artigo" in sub.lower() else ""))
                bank = OFFLINE_CURATED_CARDS.get(key, [])
                for bcard in bank:
                    if not any(bcard["q"].lower() == eq.lower() for eq in existing_questions):
                        cards_to_save.append(bcard)
                        if len(cards_to_save) >= count:
                            break
                provider_used = "banco_curado"

            if cards_to_save and os.path.exists(folder):
                anki_target = None
                for f in os.listdir(folder):
                    if "anki" in f.lower() and f.endswith(".txt"):
                        anki_target = os.path.join(folder, f)
                        break
                if not anki_target:
                    anki_target = os.path.join(folder, f"Flashcards_{sub}_Anki.txt")
                try:
                    with open(anki_target, "a", encoding="utf-8") as fa:
                        for c in cards_to_save:
                            fa.write(f"\n{c['q']}\t{c['a']}")
                except Exception:
                    pass
                    
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "cards": cards_to_save, 
                "provider": provider_used
            }, ensure_ascii=False).encode("utf-8"))

        # 7. Geração de Novo Simulado com IA + Fallback de Alta Retenção
        elif path == "/api/generate-ai-quiz":
            disc = payload.get("discipline", "Informatica")
            sub = payload.get("subarea", "Excel")
            banca = payload.get("banca", "Cebraspe")
            count = int(payload.get("count", 3))
            client_existing = payload.get("existing_questions", [])
            
            saved_questions = load_quiz_questions(disc, sub)
            all_existing = list(saved_questions)
            
            for cq in client_existing:
                cq_text = cq.get("enunciado", "") if isinstance(cq, dict) else str(cq)
                cq_clean = re.sub(r'^\d+\.\s*', '', cq_text).strip()
                if cq_clean and not any(cq_clean.lower() in eq.get("enunciado", "").lower() for eq in all_existing):
                    all_existing.append(cq if isinstance(cq, dict) else {"enunciado": cq})

            existing_lines = []
            for eq in all_existing:
                enunc = re.sub(r'^\d+\.\s*', '', eq.get("enunciado", "")).strip()
                if enunc:
                    existing_lines.append(f"- [{eq.get('banca', 'Questão')}] {enunc[:180]}")
            existing_prompt_list = "\n".join(existing_lines) if existing_lines else "Nenhuma questão anterior."
            context = get_subarea_context(disc, sub)
            
            sys_prompt = (
                f"Você é um elaborador sênior de questões de concursos públicos de alta complexidade no estilo da banca {banca}.\n"
                "Seu objetivo é criar questões TOTALMENTE INÉDITAS, DESAFIADORAS e SEM NENHUMA DUPLICAÇÃO.\n"
                "REGRA DE OURO: É expressamente proibido repetir ou parafrasear os temas já abordados na lista existente.\n"
                "Formato de opções:\n"
                "Se banca for Cebraspe: 'options' DEVE ser estritamente [\"A) CERTO\", \"B) ERRADO\"].\n"
                "Se for FGV, FCC ou Vunesp: 'options' deve ter 4 ou 5 alternativas estruturadas (A, B, C, D, E).\n"
                "Retorne SEMPRE um JSON válido no formato:\n"
                "{\"questions\": ["
                "  {"
                "    \"enunciado\": \"Texto contextualizado e pergunta clara\","
                "    \"options\": [\"Opção 1\", \"Opção 2\"],"
                "    \"correct_index\": 0,"
                "    \"comentario\": \"Explicação pedagógica detalhada passo a passo de por que está certo ou errado.\""
                "  }"
                "]}"
            )
            user_prompt = (
                f"Banca: {banca} | Disciplina: {disc} | Assunto: {sub}\n\n"
                f"LISTA DE QUESTÕES JÁ EXISTENTES (NÃO REPITA ESTES ENUNCIADOS):\n{existing_prompt_list}\n\n"
                f"Gere exatamente {count} NOVAS questões estritamente INÉDITAS no estilo {banca} baseadas no conteúdo:\n\n{context[:12000]}"
            )
            
            questions_to_return = []
            provider_used = "offline_bank"
            
            raw_json, prov = call_ai_service(sys_prompt, user_prompt, json_mode=True, temperature=0.8)
            if raw_json:
                try:
                    data = json.loads(raw_json)
                    candidate_questions = data.get("questions", [])
                    clean_questions = []
                    for nq in candidate_questions:
                        new_text = nq.get("enunciado", "").strip()
                        new_text_clean = re.sub(r'^\d+\.\s*', '', new_text).lower()
                        new_words = set([w for w in re.split(r'\W+', new_text_clean) if len(w) > 4])
                        
                        is_dup = False
                        for eq in all_existing:
                            old_text = eq.get("enunciado", "").strip()
                            old_text_clean = re.sub(r'^\d+\.\s*', '', old_text).lower()
                            if new_text_clean == old_text_clean:
                                is_dup = True
                                break
                            old_words = set([w for w in re.split(r'\W+', old_text_clean) if len(w) > 4])
                            if new_words and old_words:
                                overlap = len(new_words.intersection(old_words)) / max(len(new_words), len(old_words))
                                if overlap > 0.55:
                                    is_dup = True
                                    break
                        if not is_dup:
                            nq["banca"] = banca
                            clean_questions.append(nq)
                    questions_to_return = clean_questions if clean_questions else candidate_questions
                    provider_used = prov
                except Exception:
                    pass

            if questions_to_return:
                for q in questions_to_return:
                    q["banca"] = q.get("banca", banca)
                    q_clean = re.sub(r'^\d+\.\s*', '', q.get("enunciado", "")).strip().lower()
                    if not any(re.sub(r'^\d+\.\s*', '', sq.get("enunciado", "")).strip().lower() == q_clean for sq in saved_questions):
                        saved_questions.append(q)
                save_quiz_questions(disc, sub, saved_questions)

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "questions": questions_to_return, 
                "provider": provider_used
            }, ensure_ascii=False).encode("utf-8"))

        # 8. Salvar Flashcard Manual
        elif path == "/api/add-manual-card":
            disc = payload.get("discipline", "Informatica")
            sub = payload.get("subarea", "Excel")
            q = payload.get("q", "").strip()
            a = payload.get("a", "").strip()
            if not q or not a:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Pergunta e resposta sao obrigatorias.")
                return
            folder = os.path.join(BASE_DIR, disc, sub)
            os.makedirs(folder, exist_ok=True)
            anki_file = None
            for f in os.listdir(folder):
                if "anki" in f.lower() and f.endswith(".txt"):
                    anki_file = os.path.join(folder, f)
                    break
            if not anki_file:
                anki_file = os.path.join(folder, f"Flashcards_{sub}_Anki.txt")
            with open(anki_file, "a", encoding="utf-8") as fa:
                fa.write(f"\n{q}\t{a}")
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))

        # 9. Criar Novo Tópico / Pasta
        elif path == "/api/create-topic":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            sub = payload.get("subarea", "").strip().replace(" ", "_")
            if not disc or not sub:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Disciplina e Subarea obrigatorias.")
                return
            target_folder = os.path.join(BASE_DIR, disc, sub)
            os.makedirs(target_folder, exist_ok=True)
            readme_path = os.path.join(target_folder, "README.md")
            if not os.path.exists(readme_path):
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(f"# {disc} • {sub}\n\nPasta pronta para receber extrações de aulas e materiais de estudo.\n")
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Tópico criado com sucesso!"}).encode("utf-8"))

                # 10. Importar / Cadastrar Nova Aula com Extração Inteligente de YouTube e Geração dos 4 Pilares
        elif path == "/api/import-lesson":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            sub = payload.get("subarea", "").strip().replace(" ", "_")
            title = payload.get("title", "").strip()
            professor = payload.get("professor", "Prof. Titular").strip()
            content = payload.get("content", "").strip()
            yt_url = payload.get("youtube_url", "").strip()
            banca = payload.get("banca", "Cebraspe").strip()
            
            if not disc or not sub:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Disciplina e Subarea sao obrigatorias.")
                return
            if not title:
                title = sub.replace("_", " ")

            folder = os.path.join(BASE_DIR, disc, sub)
            os.makedirs(folder, exist_ok=True)
            
            # Tentar extrair transcrição do YouTube automaticamente se houver link
            auto_transcript_timed = []
            auto_full_text = ""
            if yt_url and YouTubeTranscriptApi:
                m_yt = re.search(r'(?:v=|youtu\.be\/|embed\/)([0-9A-Za-z_-]{11})', yt_url)
                if m_yt:
                    yt_id = m_yt.group(1)
                    try:
                        api_yt = YouTubeTranscriptApi()
                        tr_data = api_yt.fetch(yt_id, languages=['pt', 'pt-BR', 'en'])
                        snippets_text = []
                        for item in tr_data:
                            start_sec = item.start if hasattr(item, 'start') else item.get('start', 0)
                            txt = item.text if hasattr(item, 'text') else item.get('text', '')
                            clean_t = txt.replace('\n', ' ').strip()
                            mins = int(start_sec // 60)
                            secs = int(start_sec % 60)
                            auto_transcript_timed.append(f"[{start_sec:.1f}s] [{mins:02d}:{secs:02d}] {clean_t}")
                            snippets_text.append(clean_t)
                        auto_full_text = " ".join(snippets_text)
                    except Exception as e_yt:
                        print(f"Aviso: Transcrição automática do YouTube não disponível: {e_yt}")

            # Salvar transcrição cronometrada se disponível
            if auto_transcript_timed:
                timed_file = os.path.join(folder, f"Transcricao_Cronometrada_{sub}.txt")
                with open(timed_file, "w", encoding="utf-8") as ft:
                    ft.write("\n".join(auto_transcript_timed))

            # Corpus de texto de estudo
            text_corpus = content or auto_full_text
            if not text_corpus:
                text_corpus = f"Tópico {sub.replace('_', ' ')} da matéria {disc.replace('_', ' ')}. Estudo direcionado para concursos públicos."

            # Gerar automaticamente todos os 4 Pilares de Alta Retenção
            pillars_result = auto_generate_all_4_pillars(
                discipline=disc,
                subarea=sub,
                title=title,
                professor=professor,
                text_corpus=text_corpus,
                yt_url=yt_url,
                banca=banca
            )

            msg = "Aula cadastrada com sucesso! Todos os 4 Pilares (Resumo, Raio-X & Pegadinhas, Flashcards e Simulado) foram gerados automaticamente."
            if auto_full_text:
                msg += " Transcrição do YouTube extraída e cronometrada!"
                
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "message": msg,
                "cards_count": pillars_result.get("cards_count", 0),
                "quiz_count": pillars_result.get("quiz_count", 0)
            }, ensure_ascii=False).encode("utf-8"))

        # 11. Gerar Momentos-Chave com IA
        elif path == "/api/generate-moments":
            disc = payload.get("discipline", "").strip()
            sub = payload.get("subarea", "").strip()
            banca = payload.get("banca", "Cebraspe").strip()
            focus = payload.get("focus", "").strip()

            if not disc or not sub:
                self.send_response(400)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Disciplina e tópico são obrigatórios."}, ensure_ascii=False).encode("utf-8"))
                return

            moments = generate_key_moments_ai(disc, sub, banca=banca, focus=focus)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "moments": moments,
                "count": len(moments),
                "message": f"{len(moments)} momentos-chave gerados com sucesso com minutagem real!"
            }, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/supabase/config":
            url = payload.get("url", "").strip()
            key = payload.get("key", "").strip()
            cfg = load_config()
            if url:
                cfg["supabase_url"] = url
            if key:
                cfg["supabase_key"] = key
            save_config(cfg)
            
            ok = False
            msg = "Chave ou URL não preenchida."
            if supabase_client:
                ok, msg = supabase_client.test_connection()

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": ok,
                "message": msg
            }, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/supabase/sync-all":
            if not supabase_client:
                self.send_response(500)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Módulo Supabase ausente"}).encode("utf-8"))
                return
            ok, msg = supabase_client.sync_all_local_to_supabase()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": ok,
                "message": msg
            }, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/generate-ai-raiox":
            disc = payload.get("discipline", "Informatica").strip().replace(" ", "_")
            sub = payload.get("subarea", "Excel").strip().replace(" ", "_")
            banca = payload.get("banca", "Cebraspe").strip()
            focus = payload.get("focus", "").strip()
            
            context = get_subarea_context(disc, sub)
            raiox_md, prov = generate_raiox_content(disc, sub, context, banca=banca, focus=focus)
            update_lesson_markdown_with_raiox(disc, sub, raiox_md)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "markdown": raiox_md,
                "banca": banca,
                "provider": prov,
                "message": f"Raio-X & Pegadinhas ({banca}) gerado com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        # 12. Importar Arquivo PDF e Gerar Todos os 4 Pilares Automaticamente
        elif path == "/api/import-pdf":
            try:
                disc = payload.get("discipline", "").strip()
                sub = payload.get("subarea", "").strip()
                title = payload.get("title", "").strip()
                professor = payload.get("professor", "Prof. Especialista").strip()
                banca = payload.get("banca", "Cebraspe").strip()
                pdf_b64 = payload.get("pdf_base64", "").strip()
                pdf_filename = payload.get("pdf_filename", "material.pdf").strip()
                
                if not pdf_b64:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Arquivo PDF obrigatório."}, ensure_ascii=False).encode("utf-8"))
                    return

                # Higienizador seguro para nomes de pastas no Windows NTFS
                def sanitize_fs_name(s: str) -> str:
                    if not s:
                        return ""
                    s = s.replace(":", " - ").replace("/", "_").replace("\\", "_")
                    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', s)
                    s = re.sub(r'[\s_]+', '_', s).strip('_. ')
                    return s

                disc = sanitize_fs_name(disc) or "Concursos_Gerais"
                if not sub:
                    clean_name = os.path.splitext(pdf_filename)[0].strip()
                    sub = sanitize_fs_name(clean_name) or "Nova_Prova"
                else:
                    sub = sanitize_fs_name(sub)
                    
                pdf_filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', pdf_filename).strip() or "material.pdf"

                if not title:
                    title = sub.replace("_", " ")

                # Decodificar Base64
                if "," in pdf_b64:
                    pdf_b64 = pdf_b64.split(",", 1)[1]
                try:
                    pdf_bytes = base64.b64decode(pdf_b64)
                except Exception as e_b64:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": f"Erro ao decodificar arquivo PDF: {str(e_b64)}"}, ensure_ascii=False).encode("utf-8"))
                    return

                folder = os.path.join(BASE_DIR, disc, sub)
                os.makedirs(folder, exist_ok=True)

                # Salvar arquivo PDF original
                pdf_save_path = os.path.join(folder, pdf_filename)
                try:
                    with open(pdf_save_path, "wb") as f_pdf:
                        f_pdf.write(pdf_bytes)
                except Exception:
                    pass

                # Extrair texto das páginas usando pypdf
                num_pages, extracted_text = extract_text_from_pdf_bytes(pdf_bytes)

                # Gerar automaticamente todos os 4 Pilares
                pillars_result = auto_generate_all_4_pillars(
                    discipline=disc,
                    subarea=sub,
                    title=title,
                    professor=professor,
                    text_corpus=extracted_text,
                    yt_url="",
                    banca=banca
                )

                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "discipline": disc,
                    "subarea": sub,
                    "num_pages": num_pages,
                    "chars_count": len(extracted_text),
                    "cards_count": pillars_result.get("cards_count", 0),
                    "quiz_count": pillars_result.get("quiz_count", 0),
                    "message": f"PDF importado com sucesso ({num_pages} páginas)! Todos os 4 Pilares foram gerados."
                }, ensure_ascii=False).encode("utf-8"))
            except Exception as e_pdf_top:
                print(f"Erro ao processar PDF: {traceback.format_exc()}")
                self.send_response(500)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": f"Falha no processamento do PDF: {str(e_pdf_top)}"
                }, ensure_ascii=False).encode("utf-8"))

        

        # 13. Renomear Disciplina
        elif path == "/api/discipline/rename":
            old_name = payload.get("old_name", "").strip().replace(" ", "_")
            new_name = payload.get("new_name", "").strip().replace(" ", "_")
            
            if not old_name or not new_name:
                self.send_response(400)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Nome antigo e novo nome da matéria são obrigatórios."}, ensure_ascii=False).encode("utf-8"))
                return
                
            if any(".." in x or "/" in x or "\\" in x for x in [old_name, new_name]):
                self.send_response(400)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Caracteres inválidos no nome da matéria."}, ensure_ascii=False).encode("utf-8"))
                return
                
            old_path = os.path.join(BASE_DIR, old_name)
            new_path = os.path.join(BASE_DIR, new_name)
            
            if not os.path.exists(old_path) or not os.path.isdir(old_path):
                self.send_response(404)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": f"Matéria '{old_name}' não encontrada."}, ensure_ascii=False).encode("utf-8"))
                return
                
            if old_name != new_name:
                if old_name.lower() == new_name.lower():
                    # Renomeação apenas de maiúsculas/minúsculas no Windows NTFS
                    temp_path = old_path + "_tmp_case_" + str(int(time.time() * 1000))
                    try:
                        os.rename(old_path, temp_path)
                        os.rename(temp_path, new_path)
                    except Exception as e_ren:
                        self.send_response(500)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Erro ao renomear pasta: {str(e_ren)}"}, ensure_ascii=False).encode("utf-8"))
                        return
                else:
                    if os.path.exists(new_path):
                        self.send_response(400)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Já existe uma matéria com o nome '{new_name.replace('_', ' ')}'."}, ensure_ascii=False).encode("utf-8"))
                        return
                    try:
                        os.rename(old_path, new_path)
                    except Exception as e_ren:
                        self.send_response(500)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Erro ao renomear pasta: {str(e_ren)}"}, ensure_ascii=False).encode("utf-8"))
                        return
                    
                # Atualizar registros em progresso_estudos.json
                try:
                    prog = load_progress()
                    prog_changed = False
                    for ck, cv in prog.get("cards", {}).items():
                        if cv.get("discipline") == old_name:
                            cv["discipline"] = new_name
                            prog_changed = True
                    for q in prog.get("quiz_history", []):
                        if q.get("discipline") == old_name:
                            q["discipline"] = new_name
                            prog_changed = True
                    for s in prog.get("cebraspe_simulados", []):
                        if s.get("discipline") == old_name:
                            s["discipline"] = new_name
                            prog_changed = True
                    if prog_changed:
                        save_progress(prog)
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "old_name": old_name, 
                "new_name": new_name,
                "message": f"Disciplina renomeada para '{new_name.replace('_', ' ')}' com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        # 14. Excluir Disciplina (e todos os seus tópicos)
        elif path == "/api/discipline/delete":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            if not disc:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Nome da disciplina obrigatorio.")
                return
                
            if ".." in disc or "/" in disc or "\\" in disc:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Nome de disciplina invalido.")
                return
                
            disc_path = os.path.join(BASE_DIR, disc)
            if not os.path.exists(disc_path) or not os.path.isdir(disc_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(f"Disciplina '{disc}' nao encontrada.".encode("utf-8"))
                return
                
            try:
                shutil.rmtree(disc_path)
            except Exception as e_del:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Erro ao remover disciplina: {str(e_del)}".encode("utf-8"))
                return
                
            # Atualizar progresso_estudos.json
            try:
                prog = load_progress()
                cards = prog.get("cards", {})
                prog["cards"] = {k: v for k, v in cards.items() if v.get("discipline") != disc}
                prog["quiz_history"] = [q for q in prog.get("quiz_history", []) if q.get("discipline") != disc]
                prog["cebraspe_simulados"] = [s for s in prog.get("cebraspe_simulados", []) if s.get("discipline") != disc]
                save_progress(prog)
            except Exception:
                pass

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "discipline": disc,
                "message": f"Disciplina '{disc.replace('_', ' ')}' excluída com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        # 15. Renomear Tópico / Subárea
        elif path == "/api/subarea/rename":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            old_name = payload.get("old_name", "").strip().replace(" ", "_")
            new_name = payload.get("new_name", "").strip().replace(" ", "_")
            
            if not disc or not old_name or not new_name:
                self.send_response(400)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Matéria, nome antigo e novo nome do tópico são obrigatórios."}, ensure_ascii=False).encode("utf-8"))
                return
                
            if any(".." in x or "/" in x or "\\" in x for x in [disc, old_name, new_name]):
                self.send_response(400)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Caracteres inválidos detectados no nome do tópico."}, ensure_ascii=False).encode("utf-8"))
                return
                
            old_sub_path = os.path.join(BASE_DIR, disc, old_name)
            new_sub_path = os.path.join(BASE_DIR, disc, new_name)
            
            if not os.path.exists(old_sub_path) or not os.path.isdir(old_sub_path):
                self.send_response(404)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": f"Tópico '{old_name}' não encontrado em '{disc}'."}, ensure_ascii=False).encode("utf-8"))
                return
                
            if old_name != new_name:
                if old_name.lower() == new_name.lower():
                    # Renomeação apenas de maiúsculas/minúsculas no Windows NTFS
                    temp_sub_path = old_sub_path + "_tmp_case_" + str(int(time.time() * 1000))
                    try:
                        os.rename(old_sub_path, temp_sub_path)
                        os.rename(temp_sub_path, new_sub_path)
                    except Exception as e_sub_ren:
                        self.send_response(500)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Erro ao renomear tópico: {str(e_sub_ren)}"}, ensure_ascii=False).encode("utf-8"))
                        return
                else:
                    if os.path.exists(new_sub_path):
                        self.send_response(400)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Já existe um tópico com o nome '{new_name.replace('_', ' ')}' nesta matéria."}, ensure_ascii=False).encode("utf-8"))
                        return
                    try:
                        os.rename(old_sub_path, new_sub_path)
                    except Exception as e_sub_ren:
                        self.send_response(500)
                        self.send_header("Content-type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": f"Erro ao renomear tópico: {str(e_sub_ren)}"}, ensure_ascii=False).encode("utf-8"))
                        return
                    
                # Renomear arquivos internos que contenham o nome do tópico antigo
                try:
                    for fname in os.listdir(new_sub_path):
                        if old_name in fname:
                            new_fname = fname.replace(old_name, new_name)
                            src_f = os.path.join(new_sub_path, fname)
                            dst_f = os.path.join(new_sub_path, new_fname)
                            if not os.path.exists(dst_f):
                                os.rename(src_f, dst_f)
                except Exception:
                    pass
                    
                # Atualizar em progresso_estudos.json
                try:
                    prog = load_progress()
                    prog_changed = False
                    for ck, cv in prog.get("cards", {}).items():
                        if cv.get("discipline") == disc and cv.get("subarea") == old_name:
                            cv["subarea"] = new_name
                            prog_changed = True
                    for q in prog.get("quiz_history", []):
                        if q.get("discipline") == disc and q.get("subarea") == old_name:
                            q["subarea"] = new_name
                            prog_changed = True
                    for s in prog.get("cebraspe_simulados", []):
                        if s.get("discipline") == disc and s.get("subarea") == old_name:
                            s["subarea"] = new_name
                            prog_changed = True
                    if prog_changed:
                        save_progress(prog)
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "discipline": disc,
                "old_name": old_name, 
                "new_name": new_name,
                "message": f"Tópico renomeado para '{new_name.replace('_', ' ')}' com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        # 16. Excluir Tópico / Subárea
        elif path == "/api/subarea/delete":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            sub = payload.get("subarea", "").strip().replace(" ", "_")
            
            if not disc or not sub:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Disciplina e topico sao obrigatorios.")
                return
                
            if any(".." in x or "/" in x or "\\" in x for x in [disc, sub]):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Caracteres invalidos detectados.")
                return
                
            sub_path = os.path.join(BASE_DIR, disc, sub)
            if not os.path.exists(sub_path) or not os.path.isdir(sub_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(f"Topico '{sub}' nao encontrado em '{disc}'.".encode("utf-8"))
                return
                
            try:
                shutil.rmtree(sub_path)
            except Exception as e_del:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Erro ao excluir topico: {str(e_del)}".encode("utf-8"))
                return
                
            # Atualizar progresso_estudos.json
            try:
                prog = load_progress()
                cards = prog.get("cards", {})
                prog["cards"] = {k: v for k, v in cards.items() if not (v.get("discipline") == disc and v.get("subarea") == sub)}
                prog["quiz_history"] = [q for q in prog.get("quiz_history", []) if not (q.get("discipline") == disc and q.get("subarea") == sub)]
                prog["cebraspe_simulados"] = [s for s in prog.get("cebraspe_simulados", []) if not (s.get("discipline") == disc and s.get("subarea") == sub)]
                save_progress(prog)
            except Exception:
                pass

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True, 
                "discipline": disc,
                "subarea": sub,
                "message": f"Tópico '{sub.replace('_', ' ')}' excluído com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        # 17. Criar Nova Disciplina
        elif path == "/api/discipline/create":
            disc = payload.get("discipline", "").strip().replace(" ", "_")
            if not disc:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Nome da disciplina obrigatorio.")
                return
            if ".." in disc or "/" in disc or "\\" in disc:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Nome de disciplina invalido.")
                return
            disc_path = os.path.join(BASE_DIR, disc)
            os.makedirs(disc_path, exist_ok=True)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "discipline": disc,
                "message": f"Disciplina '{disc.replace('_', ' ')}' criada com sucesso!"
            }, ensure_ascii=False).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    cfg = load_config()
    start_port = cfg.get("port", 8095)
    httpd = None
    actual_port = start_port
    
    for p in range(start_port, start_port + 10):
        try:
            httpd = HTTPServer(("", p), ConcursosHandler)
            actual_port = p
            break
        except OSError:
            continue
            
    if not httpd:
        print(f"Não foi possível abrir o servidor nas portas {start_port}-{start_port+9}.")
        return

    url = f"http://localhost:{actual_port}"
    print(f"\n==========================================================")
    print(f"🚀 PAINEL DE CONCURSOS IA EM EXECUÇÃO: {url}")
    print(f"• Disciplinas ativas: {len(scan_concursos_tree()['tree'])}")
    print(f"• Motor SM-2 (Repetição Espaçada) & Modo Cebraspe Ativos")
    print(f"• Para encerrar, pressione CTRL+C.")
    print(f"==========================================================\n")
    
    try:
        webbrowser.open(url)
    except Exception:
        pass
        
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado com sucesso.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
