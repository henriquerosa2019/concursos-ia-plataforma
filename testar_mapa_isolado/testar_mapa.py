# -*- coding: utf-8 -*-
"""
===============================================================================
TESTADOR ISOLADO DE MAPA MENTAL PARA CONCURSOS PÚBLICOS (ESTILO NOTEBOOKLM)
===============================================================================
- Extração de texto de qualquer PDF com demarcação de páginas.
- Reconstrução de blocos lógicos (elimina quebras duras de linhas e truncamentos).
- Parser semântico estrito (Regra 13 do AGENTS.md):
  * Nível 0: Raiz (título do documento)
  * Nível 1: De 5 a 8 macro-categorias estruturantes
  * Nível 2 e 3: Subconceitos, regras, súmulas, distinções e pegadinhas
  * Fórmula de Compressão: Rótulos curtos (máx. 4-6 palavras) no formato
    "CONCEITO + essência em poucas palavras"
  * Resumo substantivo integral em frases completas (sem cortes)
- Visualizador interativo em HTML:
  * Árvore horizontal com conectores SVG (curvas de Bézier suaves)
  * Nós em formato de pill coloridos por tipo semântico
  * Botões de expandir/recolher nós (+ / -)
  * Painel lateral de detalhes (Drawer) ao clicar no nó
  * Zoom, Pan, Ajustar à Tela, Tela Cheia e Filtro de busca em tempo real
===============================================================================
"""

import os
import sys
import re
import io
import json
import time
import unicodedata
import webbrowser

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import pypdf
except ImportError:
    pypdf = None


def resolve_file_path(path_str):
    """
    Resolve com segurança o caminho de arquivos no Windows, lidando com:
    1. Aspas simples/duplas inseridas pelo terminal ou drag-and-drop
    2. Diferenças de normalização Unicode (NFC vs NFD)
    3. Case-insensitivity no sistema de arquivos
    """
    if not path_str:
        return None
    raw = path_str.strip().strip('"').strip("'")
    if not raw:
        return None

    # Tenta caminho direto
    if os.path.exists(raw):
        return os.path.abspath(raw)

    # Tenta normalização NFC
    p_nfc = unicodedata.normalize('NFC', raw)
    if os.path.exists(p_nfc):
        return os.path.abspath(p_nfc)

    # Tenta normalização NFD
    p_nfd = unicodedata.normalize('NFD', raw)
    if os.path.exists(p_nfd):
        return os.path.abspath(p_nfd)

    # Tenta encontrar no diretório pai ignorando diferenças de encoding/case
    parent = os.path.dirname(os.path.abspath(raw))
    base = os.path.basename(raw)
    if os.path.isdir(parent):
        norm_target = unicodedata.normalize('NFC', base).lower()
        for f in os.listdir(parent):
            if unicodedata.normalize('NFC', f).lower() == norm_target:
                return os.path.join(parent, f)

    return None


def slugify(text):
    """Gera um slug seguro para nome de arquivos."""
    s = unicodedata.normalize('NFKD', text or "").encode('ascii', 'ignore').decode('utf-8')
    s = re.sub(r'[^a-zA-Z0-9]+', '_', s).strip('_').lower()
    return s[:40] or "mapa"


# ============================================================================
# 1. EXTRAÇÃO DE TEXTO DO PDF
# ============================================================================

def extract_text_from_pdf(pdf_path):
    """Extrai texto com demarcação de páginas a partir de um PDF."""
    resolved = resolve_file_path(pdf_path)
    if not resolved:
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
    pdf_path = resolved

    pages_text = []
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    if pypdf:
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            for i, page in enumerate(reader.pages):
                t = page.extract_text() or ""
                if t.strip():
                    clean_t = re.sub(r'[^a-zA-Z0-9\u00C0-\u017F\s.,;:?!/()\'\\"%-]', '', t)
                    if len(clean_t) / (len(t) or 1) >= 0.70:
                        pages_text.append(f"--- PÁGINA {i+1} ---\n{t.strip()}")
        except Exception as e:
            print(f"[Aviso pypdf]: {e}")

    # Fallback para zlib streams nativo caso pypdf retorne vazio
    if not pages_text:
        try:
            import zlib
            pos = 0
            page_idx = 1
            while pos < len(pdf_bytes):
                stream_idx = pdf_bytes.find(b"stream", pos)
                if stream_idx == -1:
                    break
                start_data = stream_idx + 6
                if start_data < len(pdf_bytes) and pdf_bytes[start_data:start_data+2] == b"\r\n":
                    start_data += 2
                elif start_data < len(pdf_bytes) and pdf_bytes[start_data:start_data+1] in (b"\n", b"\r"):
                    start_data += 1
                end_stream = pdf_bytes.find(b"endstream", start_data)
                if end_stream == -1:
                    break
                raw_stream = pdf_bytes[start_data:end_stream].strip()
                try:
                    decomp = zlib.decompress(raw_stream)
                    strings = re.findall(rb'\((?:[^()\\]|\\.)*\)', decomp)
                    chunk_text = ""
                    for s in strings:
                        inner = s[1:-1].replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
                        try:
                            t_str = inner.decode('utf-8', errors='ignore')
                            if not t_str.strip():
                                t_str = inner.decode('latin-1', errors='ignore')
                            chunk_text += t_str + " "
                        except Exception:
                            pass
                    if len(chunk_text.strip()) > 60:
                        pages_text.append(f"--- PÁGINA {page_idx} ---\n{chunk_text.strip()}")
                        page_idx += 1
                except Exception:
                    pass
                pos = end_stream + 9
        except Exception as e:
            print(f"[Aviso fallback streams]: {e}")

    return "\n\n".join(pages_text).strip()


# ============================================================================
# 2. SANITIZAÇÃO DE TÍTULO E FORMATAÇÃO DE TEXTO
# ============================================================================

def sanitize_mindmap_title(raw_str, default_name="Concurso Público"):
    """Limpa o nome de arquivos para produzir o título central do mapa."""
    s = (raw_str or "").replace(".pdf", "").replace(".PDF", "").replace("_", " ")
    s = re.sub(r'^Transcricao\s+(?:Completa|Cronometrada)\s+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^Aula\s+\d+\s+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^Flashcards?\s+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'kverna\s*\d*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'carreiras', '', s, flags=re.IGNORECASE)
    s = re.sub(r'noite|manh[ãa]|tarde', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bteoria\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bSG\b|\bPF\b|\bPRF\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\b20\d\d\b', '', s)
    s = re.sub(r'[-–—]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()

    cleaned_no_prefix = re.sub(r'^direito\s+\w+\s*', '', s, flags=re.IGNORECASE).strip()
    if len(cleaned_no_prefix) >= 5:
        s = cleaned_no_prefix

    if not s or len(s) < 3:
        s = default_name

    minor_words = {"de", "da", "do", "das", "dos", "e", "em", "por", "com", "na", "no", "à", "ao", "a", "o", "os", "as"}
    words = s.split()
    clean_words = []
    for i, w in enumerate(words):
        if w.lower() in minor_words and i > 0:
            clean_words.append(w.lower())
        else:
            clean_words.append(w.capitalize())
    return " ".join(clean_words)


def to_title_case(text):
    """Converte qualquer texto (ALL CAPS, lowercase ou misto) para Title Case inteligente, preservando siglas jurídicas consagradas."""
    if not text:
        return text
    alpha_chars = [c for c in text if c.isalpha()]
    if not alpha_chars:
        return text

    minor_words = {"de", "da", "do", "das", "dos", "e", "em", "por", "com", "na", "no",
                   "à", "ao", "a", "o", "os", "as", "vs", "entre", "sobre", "sob"}
    acronyms = {"CF", "STF", "STJ", "PCD", "ME", "EPP", "EIRELI", "CLT", "DF", "OAB",
                "PF", "PRF", "TCU", "TI", "TIC", "CP", "CPP", "CC"}
    words = text.split()
    result = []
    for i, w in enumerate(words):
        w_clean = re.sub(r'[^\w]', '', w)
        w_lower = w_clean.lower()
        if w_clean.upper() in acronyms:
            result.append(w.upper())
        elif w_lower in minor_words and i > 0:
            result.append(w.lower())
        else:
            result.append(w.capitalize())
    return " ".join(result)


def compress_label(concept, essence="", max_words=6):
    """Fórmula de Compressão Semântica (Regra 13): CONCEITO + essência em poucas palavras"""
    c = concept.strip()
    e = essence.strip()
    if not e or "(" in c:
        return c
    label = f"{c} ({e})"
    words = label.split()
    if len(words) > max_words:
        c_words = c.split()
        avail = max(1, max_words - len(c_words))
        e_short = " ".join(e.split()[:avail]).rstrip(",;:.- ")
        label = f"{c} ({e_short})"
    return label


def clean_summary_text(text):
    """Limpa e formata o resumo garantindo frases completas sem cortes no meio de palavras."""
    t = (text or "").strip()
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'^[•\-\*►▪▸✓✔\uf0d8\uf0fc\+>\s]+', '', t)
    t = t.replace('**', '').strip()
    t = re.sub(r'[,;:\-–—\s]+$', '', t)
    if t and not t.endswith(('.', '!', '?', '"', ')', ']')):
        t += '.'
    return t


def make_didactic_pegadinha_title(phrase, max_words=6):
    """Gera título didático para pegadinha sem cortar palavras e sem preposições soltas."""
    phrase = re.sub(r'^[!:\s,;.\-–—]+', '', phrase).strip()
    phrase = re.sub(r'^(?:ao|à|a|o|os|as|do|da|dos|das|de|em|na|no|com|por|que|sobre|para)\s+', '', phrase, flags=re.IGNORECASE).strip()
    words = phrase.split()
    if not words:
        return "Pegadinha de Prova"
    if len(words) == 1 and words[0].lower() in ("princípio", "principio", "regra", "exceção", "prazo", "limite"):
        words.append("Aplicável")
    chosen = words[:max_words]
    title_str = " ".join(chosen).rstrip(',;:-–—.')
    return f"Pegadinha: {to_title_case(title_str)}"


def extract_didactic_title_from_clause(marker, text):
    """
    Traduz cláusulas legais (incisos, alíneas, itens) em conceitos didáticos autoexplicativos.
    Elimina nós estéreis contendo apenas algarismos romanos (ex: 'VIII', 'XII') e gera títulos substantivos.
    """
    t = text.strip().rstrip(';.,')
    t_low = t.lower()

    # 1. Fases do Processo Licitatório
    if "preparatória" in t_low or "planejamento" in t_low:
        return f"Fase 1: Preparatória ({marker})"
    if "divulgação do edital" in t_low:
        return f"Fase 2: Divulgação do Edital ({marker})"
    if "apresentação de propostas" in t_low:
        return f"Fase 3: Apresentação de Propostas ({marker})"
    if "julgamento" in t_low and len(t) < 70:
        return f"Fase 4: Julgamento das Propostas ({marker})"
    if "habilitação" in t_low and len(t) < 70:
        return f"Fase 5: Habilitação ({marker})"
    if "recursal" in t_low and len(t) < 70:
        return f"Fase 6: Fase Recursal ({marker})"
    if "homologação" in t_low:
        return f"Fase 7: Homologação ({marker})"

    # 2. Critérios de Julgamento
    if "menor preço" in t_low:
        return f"Critério: Menor Preço ({marker})"
    if "maior desconto" in t_low:
        return f"Critério: Maior Desconto ({marker})"
    if "melhor técnica" in t_low or "conteúdo artístico" in t_low:
        return f"Critério: Melhor Técnica ({marker})"
    if "técnica e preço" in t_low:
        return f"Critério: Técnica e Preço ({marker})"
    if "maior lance" in t_low:
        return f"Critério: Maior Lance ({marker})"
    if "maior retorno" in t_low:
        return f"Critério: Maior Retorno ({marker})"

    # 3. Modalidades Licitatórias
    if "diálogo competitivo" in t_low:
        return f"Modalidade: Diálogo Competitivo ({marker})"
    if "concorrência" in t_low and len(t) < 120:
        return f"Modalidade: Concorrência ({marker})"
    if "concurso" in t_low and len(t) < 120:
        return f"Modalidade: Concurso ({marker})"
    if "leilão" in t_low and len(t) < 120:
        return f"Modalidade: Leilão ({marker})"
    if "pregão" in t_low and len(t) < 120:
        return f"Modalidade: Pregão ({marker})"

    # 4. Hipóteses Clássicas de Inexigibilidade e Dispensa de Licitação
    # Importante: artista/artístico antes de fornecedor exclusivo pois Art. 74, II contém ambos os termos
    if "artístico" in t_low or "artista" in t_low or "setor artístico" in t_low:
        return f"Profissional Artístico Consagrado ({marker})"
    if "fornecedor" in t_low or "exclusivo" in t_low or "produtor" in t_low:
        return f"Fornecedor Exclusivo ({marker})"
    if "notória especialização" in t_low or "técnico-profissionais" in t_low:
        return f"Serviços Técnicos Especializados ({marker})"
    if "credenciamento" in t_low:
        return f"Credenciamento de Objetos ({marker})"
    if "emergência" in t_low or "calamidade" in t_low:
        return f"Emergência ou Calamidade ({marker})"
    if "pesquisa" in t_low and ("ensino" in t_low or "instituição" in t_low or "desenvolvimento" in t_low):
        return f"Instituição de Pesquisa e Ensino ({marker})"
    if "transferência de tecnologia" in t_low:
        return f"Transferência de Tecnologia ({marker})"
    if "deficiência" in t_low or "pcd" in t_low:
        return f"Associação de PCD ({marker})"
    if "catadores" in t_low or "recicláveis" in t_low:
        return f"Associação de Catadores ({marker})"
    if "deserta" in t_low or "fracassada" in t_low or "não surgiram licitantes" in t_low:
        return f"Licitação Deserta ou Fracassada ({marker})"
    if "diários oficiais" in t_low or "imprensa" in t_low:
        return f"Impressão de Diários Oficiais ({marker})"
    if "valores inferiores" in t_low or "valor inferior" in t_low or "baixo valor" in t_low:
        if "obras" in t_low or "engenharia" in t_low:
            return f"Dispensa por Baixo Valor: Obras ({marker})"
        return f"Dispensa por Baixo Valor: Compras ({marker})"
    if "imóvel" in t_low or "locação" in t_low:
        return f"Locação ou Compra de Imóvel ({marker})"

    # Extração genérica inteligente para qualquer outro estatuto / dispositivo
    cleaned = re.sub(
        r'^(?:nos casos de|na contratação de|na hipótese de|para a contratação de|'
        r'para a aquisição de|para aquisição de|para a|para o|para|em caso de|'
        r'aquisição de|prestação de|quando houver|quando|que tenha por objeto|'
        r'destinado a|no caso de|de|a)\s+',
        '', t, flags=re.IGNORECASE
    )
    parts = re.split(r'[,;:\(\.]', cleaned)
    first_part = parts[0].strip()
    words = first_part.split()
    if len(words) > 5:
        first_part = " ".join(words[:5])
    words_title = [w.capitalize() for w in first_part.split()]
    title = " ".join(words_title)
    if not title or len(title) < 3:
        title = "Regra Específica"
    return f"{title} ({marker})"


# ============================================================================
# 3. MOTOR SEMÂNTICO ESTILO NOTEBOOKLM (COM FILTRAGEM TEÓRICA & RECONSTRUÇÃO)
# ============================================================================

def generate_semantic_mindmap_from_text(pdf_filename, full_text):
    base_name = os.path.splitext(os.path.basename(pdf_filename))[0]
    # Se o nome for genérico como 'material', 'teoria', 'aula', 'apostila', busca o nome da pasta temática
    if base_name.lower() in ("material", "aula", "apostila", "teoria", "documento", "pdf", "livro", "slides"):
        parent_dir = os.path.basename(os.path.dirname(os.path.abspath(pdf_filename)))
        if parent_dir and len(parent_dir) >= 3 and parent_dir.lower() not in ("downloads", "desktop", "temp", "tmp", "concursos"):
            base_name = parent_dir
    clean_root_title = sanitize_mindmap_title(base_name)

    # Limpeza de quebras de palavras causadas por hifenização
    clean_corpus = re.sub(r'(\w+)\s*[-–—]\s*\n\s*(\w+)', r'\1\2', full_text)

    # 1. Mapeamento de Páginas
    raw_pages = re.split(r'---\s*P[ÁA]GINA\s*(\d+)\s*---', clean_corpus, flags=re.IGNORECASE)
    page_map = {}
    if len(raw_pages) > 1:
        for idx in range(1, len(raw_pages), 2):
            pnum = int(raw_pages[idx])
            page_map[pnum] = (raw_pages[idx + 1] or "").lower()
    else:
        page_map[1] = clean_corpus.lower()
    total_pages = max(page_map.keys()) if page_map else 1

    def find_page_for_term(term_str, default_page=1):
        t_clean = (term_str or "").lower().strip()
        t_words = [w for w in re.findall(r'\b[a-zà-ÿ]{4,}\b', t_clean)
                   if w not in {"para", "com", "como", "sobre", "pela", "pelo",
                                "pegadinha", "uma", "entre", "são", "regra", "prova",
                                "inciso", "artigo", "fase", "item"}]
        if not t_words:
            return default_page
        best_page, max_matches = default_page, 0
        for pnum in sorted(page_map.keys()):
            ptxt = page_map[pnum]
            matches = sum(1 for w in t_words if w in ptxt)
            if matches > max_matches:
                max_matches = matches
                best_page = pnum
        return best_page

    # 2. FILTRAGEM ESTRITA DE QUESTÕES E EXERCÍCIOS (Pilar 4 separado do Mapa)
    # Impede terminantemente alternativas (ex: 'B) I, II, III e IV') de virarem categorias
    QUESTION_HEADER_REGEX = re.compile(
        r'(?:J[ÁA]\s+CAIU\s+EM\s+PROVA|'
        r'\(\s*[A-Z0-9\s/–-]{3,60}\s*/\s*(?:20\d\d|[A-Z\s]{3,30})\s*/\s*(?:20\d\d|[A-Z\s]{3,30})\s*\)|'
        r'^\s*\d{1,3}\s*[\.\)]\s*\([A-Z]|'
        r'^\s*\d{2}\s+(?:O\b|A\b|Em\b|No\b|Na\b|De\b|Com\b|Segundo\b|Acerca\b|Julgue\b|Assinale\b|Ocorre\b|Considerando\b))',
        re.IGNORECASE
    )
    OPTION_REGEX = re.compile(r'^\s*(?:\(?[A-Ea-e]\)[\s\w,–-]|(?:[A-E]\s+[A-Za-z\u00C0-\u017F]))')
    ANSWER_REGEX = re.compile(r'^\s*(?:GABARITO|RESPOSTA|COMENT[ÁA]RIO)\b', re.IGNORECASE)

    NON_HEADING_TERMS = {
        "cebraspe", "fgv", "fcc", "vunesp", "ibfc", "aocp", "quadrix",
        "gabarito", "comentário", "comentario", "questão", "questao",
        "certo", "errado", "assinale", "julgue", "item",
        "exercício", "exercicio", "exercícios", "exercicios"
    }

    def is_true_theoretical_heading(s):
        s_strip = s.strip()
        if len(s_strip) < 5 or len(s_strip) > 75:
            return False
        if s_strip.endswith((';', ',', ':', '.')):
            return False
        if re.match(r'^\(?[A-Ea-e]\)', s_strip):
            return False
        if any(t in s_strip.lower() for t in NON_HEADING_TERMS):
            return False
        if re.match(r'^[IVXLCDM]+\s*[-–—.]?\s*$', s_strip):
            return False
        if "(VETADO)" in s_strip.upper():
            return False
        if re.match(r'^[IVXLCDM]+\s*[-–—.]\s*(?:apenas|somente|estão|está|são)', s_strip, re.IGNORECASE):
            return False
        
        alpha = [c for c in s_strip if c.isalpha()]
        if not alpha or len(alpha) < 4:
            return False
        upper_ratio = sum(1 for c in alpha if c.isupper()) / len(alpha)
        if upper_ratio >= 0.75:
            words = [w for w in re.findall(r'\b[A-Za-z\u00C0-\u017F]+\b', s_strip) if len(w) >= 3]
            if len(words) >= 1:
                return True
        return False

    lines = clean_corpus.split('\n')
    clean_lines = []
    in_question = False

    for l in lines:
        s = l.strip()
        if not s:
            continue
        if s.startswith('---'):
            clean_lines.append(s)
            in_question = False
            continue

        if QUESTION_HEADER_REGEX.search(s):
            in_question = True
            continue
        if OPTION_REGEX.match(s) or ANSWER_REGEX.match(s):
            continue

        if in_question:
            if is_true_theoretical_heading(s):
                in_question = False
            else:
                continue
        clean_lines.append(s)

    # 3. RECONSTRUÇÃO DE PARÁGRAFOS LÓGICOS (Evita cortes de frases pelo PDF)
    bullet_syms = r'^[•\-\*►▪▸✓✔\uf0d8\uf0fc\+]\s*'
    noise_keywords = ["RODRIGO MOTTA", "KAVERNA", "YOUTUBE", "INSTAGRAM", "WWW.",
                      "PROF.", "@PROF", "GABARITO", "DIREITO ADMINISTRATIVO – PROF",
                      "DIREITO CONSTITUCIONAL – PROF", "DIREITO PENAL – PROF"]

    def is_noise(s):
        su = s.strip().upper()
        if not su or len(su) < 3:
            return True
        if any(nk in su for nk in noise_keywords):
            return True
        if re.match(r'^\d{1,3}\s*$', su):
            return True
        return False

    def is_terminal_line(s):
        s = s.strip()
        return s.endswith(('.', '!', '?', ':', '---', ';')) or (s.isupper() and len(s) > 4)

    def is_new_item_line(s):
        s = s.strip()
        if re.match(bullet_syms, s):
            return True
        if is_true_theoretical_heading(s):
            return True
        if re.match(r'^(?:Art\.|Súmula|ATENÇÃO|IMPORTANTE|OBS|[IVXLCDM]+\s*[-–—])', s, re.IGNORECASE):
            return True
        if re.match(r'^[A-Z\u00C0-\u017F][A-Za-z\u00C0-\u017F\s\(\)/]{2,40}\s+[-–—]\s+[A-Za-z\u00C0-\u017F]', s):
            return True
        return False

    reconstructed_lines = []
    for l in clean_lines:
        s = l.strip()
        if is_noise(s):
            continue
        if s.startswith('---'):
            reconstructed_lines.append(s)
            continue
        if (reconstructed_lines and 
            not is_new_item_line(s) and 
            not is_terminal_line(reconstructed_lines[-1]) and 
            not reconstructed_lines[-1].startswith('---')):
            reconstructed_lines[-1] += " " + s
        else:
            reconstructed_lines.append(s)

    # 4. Extrair Seções Estruturais a partir dos blocos lógicos
    raw_sections = []
    current_sec = None
    current_page = 1

    for s in reconstructed_lines:
        m_page = re.match(r'^---\s*P[ÁA]GINA\s*(\d+)\s*---$', s, re.IGNORECASE)
        if m_page:
            current_page = int(m_page.group(1))
            continue

        if is_true_theoretical_heading(s):
            clean_h = to_title_case(s.rstrip(':. '))
            clean_h = re.sub(r'^(?:Observação\s+Importante[!:]?|Atenção[!:]?|Cuidado[!:]?)\s*', '', clean_h, flags=re.IGNORECASE).strip()
            if "não confunda modalidade com critério de julgamento" in clean_h.lower():
                clean_h = "Critérios de Julgamento"
            if clean_h.lower() not in clean_root_title.lower() and clean_root_title.lower() not in clean_h.lower():
                if clean_h not in ("Importante", "Atenção", "Cuidado", "Obs", "Reflexão"):
                    if current_sec:
                        raw_sections.append(current_sec)
                    current_sec = {
                        "heading": clean_h,
                        "page": current_page,
                        "lines": []
                    }
                    continue

        if current_sec:
            current_sec["lines"].append(s)

    if current_sec:
        raw_sections.append(current_sec)

    # Agrupar seções menores e normalizar
    grouped_sections = []
    seen_h = set()
    for s in raw_sections:
        h_norm = s["heading"].lower()
        if h_norm in seen_h:
            if grouped_sections:
                grouped_sections[-1]["lines"].extend(s["lines"])
            continue
        useful_l = [l for l in s["lines"] if l.strip() and not is_noise(l)]
        if len(useful_l) < 2 and grouped_sections:
            grouped_sections[-1]["lines"].extend(s["lines"])
            continue
        seen_h.add(h_norm)
        grouped_sections.append(s)

    # Limitar entre 5 e 8 categorias principais (Regra 13)
    if len(grouped_sections) > 8:
        scored = sorted(enumerate(grouped_sections), key=lambda x: -len(x[1]["lines"]))
        top_idx = sorted([idx for idx, _ in scored[:8]])
        selected_sections = [grouped_sections[i] for i in top_idx]
    else:
        selected_sections = grouped_sections

    nodes = [{
        "id": "root",
        "titulo": clean_root_title,
        "tipo": "root",
        "pagina": 1,
        "resumo": f"Estrutura esquematizada das unidades conceituais essenciais de {clean_root_title} para provas de concursos públicos."
    }]
    edges = []
    seen_node_keys = set([clean_root_title.lower()])
    node_id_seq = 0

    for c_idx, sec in enumerate(selected_sections):
        cat_id = f"cat_{c_idx + 1}"
        cat_page = find_page_for_term(sec["heading"], sec["page"])
        cat_title = sec["heading"]

        # Resumo substantivo da categoria (primeiro parágrafo denso)
        cat_summary_lines = []
        for l in sec["lines"]:
            ls = l.strip()
            if ls and not is_noise(ls) and len(ls) >= 20 and not ls.isupper():
                cat_summary_lines.append(ls)
                if len(cat_summary_lines) >= 2:
                    break
        cat_summary = clean_summary_text(" ".join(cat_summary_lines)) if cat_summary_lines else f"Regras e fundamentos de {cat_title.lower()} para concursos públicos."

        nodes.append({
            "id": cat_id,
            "titulo": cat_title,
            "tipo": "category",
            "pagina": cat_page,
            "resumo": cat_summary
        })
        edges.append({"source": "root", "target": cat_id})
        seen_node_keys.add(cat_title.lower())

        # Extrair conceitos específicos da seção (máx 10 por categoria para visual límpido)
        sec_lines = sec["lines"]
        sec_items_count = 0

        for line_i, line_str in enumerate(sec_lines):
            if sec_items_count >= 10:
                break
            l = line_str.strip()
            if not l or is_noise(l):
                continue

            # Caso A: Inciso, Alínea ou Artigo (ex: VIII - nos casos de emergência...)
            m_inciso = re.match(r'^([IVXLCDM]+|\d{1,2}|[a-z])\s*[-–—.]\s*(.{4,})$', l)
            if m_inciso:
                raw_marker = m_inciso.group(1).upper()
                marker_str = f"Inciso {raw_marker}" if re.match(r'^[IVXLCDM]+$', raw_marker) else f"Item {raw_marker}"
                didactic_title = extract_didactic_title_from_clause(marker_str, m_inciso.group(2))
                def_raw = clean_summary_text(m_inciso.group(2))
                if didactic_title.lower() not in seen_node_keys:
                    seen_node_keys.add(didactic_title.lower())
                    node_id_seq += 1
                    sec_items_count += 1
                    nid = f"item_{node_id_seq}"
                    nodes.append({
                        "id": nid,
                        "titulo": didactic_title,
                        "tipo": "rule",
                        "pagina": find_page_for_term(didactic_title, cat_page),
                        "resumo": def_raw
                    })
                    edges.append({"source": cat_id, "target": nid})
                continue

            # Caso B: Linha com travessão "Termo – Definição"
            m_dash = re.match(r'^(?:' + bullet_syms + r')?([A-Za-z\u00C0-\u017F\s\(\)/]{3,45})\s+[-–—]\s+(.{12,})$', l)
            if m_dash and not l.startswith('Art.') and not l.startswith('*'):
                candidate_term = m_dash.group(1).strip()
                # Se o termo for apenas algarismo romano ou número, usa extrator didático
                if re.match(r'^(?:[IVXLCDM]+|\d+|[A-Z])$', candidate_term, re.IGNORECASE):
                    marker_str = f"Inciso {candidate_term.upper()}"
                    didactic_title = extract_didactic_title_from_clause(marker_str, m_dash.group(2))
                    def_raw = clean_summary_text(m_dash.group(2))
                    if didactic_title.lower() not in seen_node_keys:
                        seen_node_keys.add(didactic_title.lower())
                        node_id_seq += 1
                        sec_items_count += 1
                        nid = f"item_{node_id_seq}"
                        nodes.append({
                            "id": nid,
                            "titulo": didactic_title,
                            "tipo": "rule",
                            "pagina": find_page_for_term(didactic_title, cat_page),
                            "resumo": def_raw
                        })
                        edges.append({"source": cat_id, "target": nid})
                    continue

                term_raw = to_title_case(candidate_term)
                def_raw = clean_summary_text(m_dash.group(2).strip())
                essence_match = re.search(r'^(?:pessoas jurídicas de|ocorre quando|são|não possuem|com criação|dotada de|modalidade de licitação para|critério de julgamento)\s+([^,.;]{5,30})', def_raw, re.IGNORECASE)
                essence = essence_match.group(1).strip() if essence_match else ""
                short_label = compress_label(term_raw, essence, max_words=5)

                if term_raw.lower() not in seen_node_keys and len(term_raw) >= 3:
                    seen_node_keys.add(term_raw.lower())
                    node_id_seq += 1
                    sec_items_count += 1
                    nid = f"item_{node_id_seq}"
                    p_num = find_page_for_term(term_raw, cat_page)
                    is_comp = any(k in term_raw.lower() for k in ["desconcentração", "descentralização", "versus", "outorga", "delegação", "sociedades", "dispensada", "dispensável"])
                    nodes.append({
                        "id": nid,
                        "titulo": short_label,
                        "tipo": "comparison" if is_comp else "concept",
                        "pagina": p_num,
                        "resumo": def_raw
                    })
                    edges.append({"source": cat_id, "target": nid})
                continue

            # Caso C: Marcador bullet com termo na linha atual e definição na próxima
            m_bullet_only = re.match(r'^' + bullet_syms + r'([A-Za-z\u00C0-\u017F\s\(\)/]{4,45})$', l)
            if m_bullet_only:
                term_raw = to_title_case(m_bullet_only.group(1).strip())
                next_desc = []
                for nxt in sec_lines[line_i + 1: line_i + 4]:
                    ns = nxt.strip()
                    if ns and not is_noise(ns) and not re.match(r'^' + bullet_syms, ns) and not ns.isupper():
                        next_desc.append(ns)
                def_raw = clean_summary_text(" ".join(next_desc)) if next_desc else f"Regime jurídico e características de {term_raw.lower()}."
                essence_match = re.search(r'^(?:diretamente|subordinados|possuem|são aqueles|aqueles que|formados por)\s+([^,.;]{5,30})', def_raw, re.IGNORECASE)
                essence = essence_match.group(1).strip() if essence_match else ""
                short_label = compress_label(term_raw, essence, max_words=5)

                if term_raw.lower() not in seen_node_keys and len(term_raw) >= 3:
                    seen_node_keys.add(term_raw.lower())
                    node_id_seq += 1
                    sec_items_count += 1
                    nid = f"item_{node_id_seq}"
                    p_num = find_page_for_term(term_raw, cat_page)
                    nodes.append({
                        "id": nid,
                        "titulo": short_label,
                        "tipo": "concept",
                        "pagina": p_num,
                        "resumo": def_raw
                    })
                    edges.append({"source": cat_id, "target": nid})
                continue

            # Caso D: Súmula ou Artigo importante
            m_sumula = re.match(r'^(Súmula\s+n?º?\s*\d+\s+[A-Z]{3}|Art\.\s*\d+[^–—:]*)\s*[-–—:]\s*(.{15,})$', l, re.IGNORECASE)
            if m_sumula:
                s_name = m_sumula.group(1).strip()
                s_desc = clean_summary_text(m_sumula.group(2).strip())
                short_label = compress_label(to_title_case(s_name), "Regra Legal", max_words=5)
                if s_name.lower() not in seen_node_keys:
                    seen_node_keys.add(s_name.lower())
                    node_id_seq += 1
                    sec_items_count += 1
                    nid = f"item_{node_id_seq}"
                    nodes.append({
                        "id": nid,
                        "titulo": short_label,
                        "tipo": "rule",
                        "pagina": find_page_for_term(s_name, cat_page),
                        "resumo": s_desc
                    })
                    edges.append({"source": cat_id, "target": nid})
                continue

            # Caso E: Alertas de Prova (ATENÇÃO / IMPORTANTE)
            m_alert = re.search(r'(?:ATENÇÃO|IMPORTANTE|CUIDADO)[!:]?\s*([^.\n]{15,100})', l, re.IGNORECASE)
            if m_alert:
                short_label = make_didactic_pegadinha_title(m_alert.group(1))
                full_alert = clean_summary_text(l)
                if short_label.lower() not in seen_node_keys:
                    seen_node_keys.add(short_label.lower())
                    node_id_seq += 1
                    sec_items_count += 1
                    nid = f"item_{node_id_seq}"
                    nodes.append({
                        "id": nid,
                        "titulo": short_label,
                        "tipo": "trap",
                        "pagina": cat_page,
                        "resumo": full_alert
                    })
                    edges.append({"source": cat_id, "target": nid})
                continue

    # 5. Adicionar Categoria Permanente de Pegadinhas Reais (Pilar 2)
    trap_cat_id = f"cat_{len(selected_sections) + 1}"
    trap_nodes = []

    for pnum in sorted(page_map.keys()):
        ptxt = page_map[pnum]
        for line_p in ptxt.split('\n'):
            lp = line_p.strip()
            m_tr = re.search(r'(?:não\s+confunda|não\s+há\s+hierarquia|banca\s+costuma|pegadinha|cuidado\s+com|atenção)[!:\s]+([^.\n]{12,100})', lp, re.IGNORECASE)
            if m_tr:
                t_title = make_didactic_pegadinha_title(m_tr.group(1))
                if t_title.lower() not in seen_node_keys:
                    seen_node_keys.add(t_title.lower())
                    trap_nodes.append({
                        "titulo": t_title,
                        "pagina": pnum,
                        "resumo": clean_summary_text(lp)
                    })
            if len(trap_nodes) >= 6:
                break
        if len(trap_nodes) >= 6:
            break

    if trap_nodes:
        nodes.append({
            "id": trap_cat_id,
            "titulo": "Raio-X de Pegadinhas da Banca",
            "tipo": "category",
            "pagina": trap_nodes[0]["pagina"],
            "resumo": "Principais armadilhas, inversões conceituais e assertivas com palavras absolutas recorrentes nas bancas examinadoras."
        })
        edges.append({"source": "root", "target": trap_cat_id})

        for tn in trap_nodes:
            node_id_seq += 1
            nid = f"item_{node_id_seq}"
            nodes.append({
                "id": nid,
                "titulo": tn["titulo"],
                "tipo": "trap",
                "pagina": tn["pagina"],
                "resumo": tn["resumo"]
            })
            edges.append({"source": trap_cat_id, "target": nid})

    return {"titulo": clean_root_title, "nodes": nodes, "edges": edges}


# ============================================================================
# 4. GERADOR DE VISUALIZADOR INTERATIVO HTML (ÁRVORE BÉZIER ESTILO NOTEBOOKLM)
# ============================================================================

def generate_interactive_html(mindmap_dict, output_html_path):
    nodes_json = json.dumps(mindmap_dict["nodes"], ensure_ascii=False)
    edges_json = json.dumps(mindmap_dict["edges"], ensure_ascii=False)
    title = mindmap_dict["titulo"]

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>Mapa Mental: {title}</title>
  <style>
    :root {{
      --bg: #090d16;
      --surface: #111827;
      --surface-border: #1f2937;
      --text: #f9fafb;
      --text-muted: #9ca3af;
      --primary: #3b82f6;
      --primary-light: #60a5fa;
      --accent: #10b981;
      --rule: #f59e0b;
      --trap: #ef4444;
      --mnemonic: #a855f7;
      --comparison: #8b5cf6;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      user-select: none;
    }}

    /* Top Toolbar */
    .toolbar {{
      position: absolute;
      top: 14px;
      left: 18px;
      right: 18px;
      height: 56px;
      background: rgba(17, 24, 39, 0.88);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      z-index: 50;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    }}
    .toolbar-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .logo-badge {{
      font-size: 20px;
    }}
    .map-title {{
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      letter-spacing: -0.2px;
    }}
    .stats-tag {{
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.35);
      color: #93c5fd;
      font-size: 11px;
      font-weight: 600;
      padding: 3px 9px;
      border-radius: 20px;
    }}
    .toolbar-right {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .search-input {{
      background: rgba(31, 41, 55, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 8px;
      padding: 6px 12px;
      font-size: 12px;
      color: #fff;
      outline: none;
      width: 190px;
      transition: all 0.2s;
    }}
    .search-input:focus {{
      width: 250px;
      border-color: var(--primary-light);
      box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
    }}
    .btn-tool {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #d1d5db;
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s;
    }}
    .btn-tool:hover {{
      background: rgba(255, 255, 255, 0.14);
      color: #fff;
      transform: translateY(-1px);
    }}

    /* Viewport & Canvas */
    #viewport {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      cursor: grab;
      background-image: 
        radial-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px);
      background-size: 24px 24px;
    }}
    #viewport:active {{
      cursor: grabbing;
    }}
    #canvas {{
      position: absolute;
      top: 0;
      left: 0;
      transform-origin: 0 0;
      pointer-events: none;
    }}
    #svg-lines {{
      position: absolute;
      top: 0;
      left: 0;
      width: 12000px;
      height: 12000px;
      pointer-events: none;
      z-index: 1;
    }}
    #nodes-container {{
      position: absolute;
      top: 0;
      left: 0;
      z-index: 10;
      pointer-events: auto;
    }}

    /* Mind Map Nodes */
    .mm-node {{
      position: absolute;
      border-radius: 24px;
      padding: 8px 16px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
      transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
      white-space: nowrap;
      border-width: 1.5px;
      border-style: solid;
      user-select: none;
    }}
    .mm-node:hover {{
      transform: scale(1.05);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
      z-index: 30;
    }}
    .mm-node.selected {{
      transform: scale(1.08);
      box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.4), 0 10px 30px rgba(0,0,0,0.7);
      z-index: 35;
    }}
    .mm-node.dimmed {{
      opacity: 0.2;
      filter: grayscale(80%);
    }}
    .mm-node.matched {{
      animation: pulseMatch 1.5s infinite alternate;
      z-index: 25;
    }}
    @keyframes pulseMatch {{
      from {{ transform: scale(1); box-shadow: 0 0 8px rgba(56, 189, 248, 0.5); }}
      to {{ transform: scale(1.06); box-shadow: 0 0 20px rgba(56, 189, 248, 0.9); }}
    }}

    /* Types of Nodes */
    .mm-node.type-root {{
      background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
      border-color: #60a5fa;
      color: #ffffff;
      font-size: 15px;
      font-weight: 700;
      padding: 12px 24px;
      border-radius: 30px;
      box-shadow: 0 0 28px rgba(37, 99, 235, 0.45);
    }}
    .mm-node.type-category {{
      background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
      border-color: #34d399;
      color: #ecfdf5;
      font-size: 13.5px;
      padding: 9px 18px;
    }}
    .mm-node.type-concept {{
      background: #1f2937;
      border-color: #4b5563;
      color: #f3f4f6;
    }}
    .mm-node.type-rule {{
      background: rgba(245, 158, 11, 0.15);
      border-color: #f59e0b;
      color: #fef3c7;
    }}
    .mm-node.type-trap {{
      background: rgba(239, 68, 68, 0.18);
      border-color: #ef4444;
      color: #fee2e2;
    }}
    .mm-node.type-comparison {{
      background: rgba(139, 92, 246, 0.18);
      border-color: #8b5cf6;
      color: #ede9fe;
    }}
    .mm-node.type-mnemonic {{
      background: rgba(168, 85, 247, 0.2);
      border-color: #a855f7;
      color: #f3e8ff;
    }}

    .node-icon {{
      font-size: 14px;
    }}
    .page-tag {{
      background: rgba(0, 0, 0, 0.35);
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 10px;
      color: rgba(255, 255, 255, 0.75);
      font-weight: 700;
    }}

    .node-toggle {{
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.3);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 700;
      color: #fff;
      margin-left: 4px;
      transition: background 0.15s;
    }}
    .node-toggle:hover {{
      background: rgba(255, 255, 255, 0.35);
    }}

    /* Side Drawer for Full Details */
    #drawer {{
      position: fixed;
      top: 0;
      right: -420px;
      width: 400px;
      height: 100vh;
      background: #111827;
      border-left: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: -10px 0 35px rgba(0, 0, 0, 0.6);
      z-index: 100;
      padding: 28px 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      transition: right 0.28s cubic-bezier(0.16, 1, 0.3, 1);
      overflow-y: auto;
    }}
    #drawer.open {{
      right: 0;
    }}
    .drawer-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 14px;
    }}
    .drawer-badges {{
      display: flex;
      gap: 8px;
      align-items: center;
    }}
    .drawer-type-badge {{
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .drawer-page-badge {{
      font-size: 10.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
    }}
    .btn-close-drawer {{
      background: none;
      border: none;
      color: #9ca3af;
      font-size: 18px;
      cursor: pointer;
      padding: 4px;
    }}
    .btn-close-drawer:hover {{
      color: #fff;
    }}
    .drawer-title {{
      font-size: 17px;
      font-weight: 800;
      color: #fff;
      line-height: 1.35;
    }}
    .drawer-card {{
      background: #1f2937;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      padding: 16px;
    }}
    .drawer-label {{
      font-size: 11px;
      font-weight: 700;
      color: #9ca3af;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      margin-bottom: 8px;
    }}
    .drawer-text {{
      font-size: 13.5px;
      line-height: 1.6;
      color: #e5e7eb;
      white-space: pre-line;
      word-break: break-word;
    }}
    .drawer-tip {{
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: 8px;
      padding: 12px 14px;
      font-size: 12.5px;
      color: #fde68a;
      line-height: 1.5;
    }}

    .hint-bar {{
      position: absolute;
      bottom: 16px;
      left: 18px;
      background: rgba(17, 24, 39, 0.75);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      padding: 6px 14px;
      font-size: 11.5px;
      color: #9ca3af;
      z-index: 40;
      pointer-events: none;
    }}
  </style>
</head>
<body>

  <!-- Top Toolbar -->
  <div class="toolbar">
    <div class="toolbar-left">
      <span class="logo-badge">🧠</span>
      <span class="map-title">{title}</span>
      <span class="stats-tag" id="stats-badge">Carregando...</span>
    </div>
    <div class="toolbar-right">
      <input type="text" class="search-input" id="search-input" placeholder="🔍 Filtrar no mapa..." title="Filtre nós por palavra-chave">
      <button class="btn-tool" onclick="zoom(0.12)" title="Aumentar Zoom">➕ Zoom</button>
      <button class="btn-tool" onclick="zoom(-0.12)" title="Diminuir Zoom">➖ Zoom</button>
      <button class="btn-tool" onclick="resetView()" title="Tamanho Real (100%)">100%</button>
      <button class="btn-tool" onclick="fitView()" title="Ajustar Mapa à Tela">🔲 Ajustar</button>
      <button class="btn-tool" onclick="toggleAllBranches()" id="btn-toggle-all">↕ Recolher</button>
      <button class="btn-tool" onclick="toggleFullscreen()" title="Tela Cheia">🗖</button>
    </div>
  </div>

  <!-- Interactive Canvas -->
  <div id="viewport">
    <div id="canvas">
      <svg id="svg-lines"></svg>
      <div id="nodes-container"></div>
    </div>
  </div>

  <div class="hint-bar">
    💡 Arraste para mover o mapa • Role o mouse para Zoom • Clique no nó para ler a explicação completa
  </div>

  <!-- Side Details Drawer -->
  <div id="drawer">
    <div class="drawer-header">
      <div class="drawer-badges">
        <span class="drawer-type-badge" id="d-type-badge">CONCEITO</span>
        <span class="drawer-page-badge" id="d-page-badge">Pág. 1</span>
      </div>
      <button class="btn-close-drawer" onclick="closeDrawer()" title="Fechar">✖</button>
    </div>
    <div class="drawer-title" id="d-title">Título do Nó</div>
    <div class="drawer-card">
      <div class="drawer-label">💡 Explicação Pedagógica & Regra de Prova:</div>
      <div class="drawer-text" id="d-summary">Resumo completo...</div>
    </div>
    <div class="drawer-tip" id="d-tip">
      🎯 <b>Dica de Retenção:</b> Estude a diferenciação exata e atente-se às palavras absolutas das bancas examinadoras.
    </div>
  </div>

  <script>
    const data = {{
      nodes: {nodes_json},
      edges: {edges_json}
    }};

    const typeIcons = {{
      root: '🎯',
      category: '📁',
      concept: '💡',
      rule: '⚖️',
      trap: '🚨',
      comparison: '⚖️',
      mnemonic: '🧠',
      definition: '📖',
      example: '🔍',
      exception: '⚠️'
    }};

    const typeBadges = {{
      root: {{ text: '🎯 TÓPICO CENTRAL', bg: 'rgba(37, 99, 235, 0.25)', color: '#93c5fd' }},
      category: {{ text: '📁 CATEGORIA ESTRUTURANTE', bg: 'rgba(5, 150, 105, 0.25)', color: '#6ee7b7' }},
      concept: {{ text: '💡 CONCEITO ESSENCIAL', bg: 'rgba(75, 85, 99, 0.4)', color: '#e5e7eb' }},
      rule: {{ text: '⚖️ REGRA VINCULANTE', bg: 'rgba(245, 158, 11, 0.25)', color: '#fcd34d' }},
      trap: {{ text: '🚨 PEGADINHA DE BANCA', bg: 'rgba(239, 68, 68, 0.25)', color: '#fca5a5' }},
      comparison: {{ text: '⚖️ DISTINÇÃO PRÁTICA', bg: 'rgba(139, 92, 246, 0.25)', color: '#c4b5fd' }},
      mnemonic: {{ text: '🧠 MNEMÔNICO DO AUTOR', bg: 'rgba(168, 85, 247, 0.25)', color: '#d8b4fe' }},
      definition: {{ text: '📖 DEFINIÇÃO FORMAL', bg: 'rgba(6, 182, 212, 0.25)', color: '#67e8f9' }},
      exception: {{ text: '⚠️ EXCEÇÃO DA LEI', bg: 'rgba(239, 68, 68, 0.25)', color: '#fca5a5' }}
    }};

    // Build hierarchy
    const nodeMap = {{}};
    data.nodes.forEach(n => {{
      nodeMap[n.id] = {{ ...n, children: [], parents: [], level: 0, x: 0, y: 0, w: 0, h: 0, collapsed: false }};
    }});
    data.edges.forEach(e => {{
      if (nodeMap[e.source] && nodeMap[e.target]) {{
        nodeMap[e.source].children.push(nodeMap[e.target]);
        nodeMap[e.target].parents.push(nodeMap[e.source]);
      }}
    }});

    let root = data.nodes.find(n => n.tipo === 'root') || data.nodes[0];
    const rootNode = nodeMap[root.id];

    // BFS for levels
    rootNode.level = 0;
    const q = [rootNode];
    const visited = new Set([rootNode.id]);
    while (q.length > 0) {{
      const cur = q.shift();
      cur.children.forEach(ch => {{
        if (!visited.has(ch.id)) {{
          visited.add(ch.id);
          ch.level = cur.level + 1;
          q.push(ch);
        }}
      }});
    }}

    // State
    let zoomLevel = 0.92;
    let panX = 60;
    let panY = 80;
    let isPanning = false;
    let startX = 0, startY = 0;
    let selectedNodeId = null;
    let allCollapsed = false;

    const viewport = document.getElementById('viewport');
    const canvas = document.getElementById('canvas');
    const nodesContainer = document.getElementById('nodes-container');
    const svgLines = document.getElementById('svg-lines');

    viewport.addEventListener('mousedown', e => {{
      if (e.target.closest('.mm-node') || e.target.closest('.btn-tool') || e.target.closest('#drawer')) return;
      isPanning = true;
      startX = e.clientX - panX;
      startY = e.clientY - panY;
    }});
    window.addEventListener('mousemove', e => {{
      if (!isPanning) return;
      panX = e.clientX - startX;
      panY = e.clientY - startY;
      applyTransform();
    }});
    window.addEventListener('mouseup', () => {{ isPanning = false; }});

    viewport.addEventListener('wheel', e => {{
      e.preventDefault();
      const delta = e.deltaY < 0 ? 0.08 : -0.08;
      const newZoom = Math.min(2.0, Math.max(0.3, zoomLevel + delta));
      const rect = viewport.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      panX -= (mouseX - panX) * (newZoom / zoomLevel - 1);
      panY -= (mouseY - panY) * (newZoom / zoomLevel - 1);
      zoomLevel = newZoom;
      applyTransform();
    }}, {{ passive: false }});

    function applyTransform() {{
      canvas.style.transform = `translate(${{panX}}px, ${{panY}}px) scale(${{zoomLevel}})`;
    }}

    function calculateTreeLayout() {{
      let currentY = 60;
      const gapX = 90;
      const gapY = 24;

      function measureSubtree(node) {{
        if (node.collapsed || node.children.length === 0) {{
          node.y = currentY;
          node.h = 42;
          currentY += node.h + gapY;
          return;
        }}
        const childYs = [];
        node.children.forEach(ch => {{
          measureSubtree(ch);
          childYs.push(ch.y);
        }});
        if (childYs.length > 0) {{
          node.y = (childYs[0] + childYs[childYs.length - 1]) / 2;
        }} else {{
          node.y = currentY;
          currentY += 42 + gapY;
        }}
        node.h = 42;
      }}

      currentY = 60;
      measureSubtree(rootNode);

      Object.values(nodeMap).forEach(n => {{
        n.x = 40 + n.level * (240 + gapX);
      }});
    }}

    function renderMindmap() {{
      calculateTreeLayout();
      nodesContainer.innerHTML = '';
      let paths = '';

      function drawBranches(node) {{
        if (node.collapsed) return;
        node.children.forEach(ch => {{
          const x1 = node.x + (node.actualW || 180);
          const y1 = node.y + 20;
          const x2 = ch.x;
          const y2 = ch.y + 20;
          const dx = Math.max(40, (x2 - x1) * 0.55);

          let strokeColor = '#3b82f6';
          if (ch.tipo === 'trap') strokeColor = '#ef4444';
          else if (ch.tipo === 'rule') strokeColor = '#f59e0b';
          else if (ch.tipo === 'comparison') strokeColor = '#8b5cf6';
          else if (ch.tipo === 'mnemonic') strokeColor = '#a855f7';
          else if (ch.tipo === 'category') strokeColor = '#10b981';

          paths += `<path d="M ${{x1}} ${{y1}} C ${{x1 + dx}} ${{y1}}, ${{x2 - dx}} ${{y2}}, ${{x2}} ${{y2}}"
                          fill="none" stroke="${{strokeColor}}" stroke-width="2.2" stroke-linecap="round" opacity="0.65"/>`;
          drawBranches(ch);
        }});
      }}
      drawBranches(rootNode);
      svgLines.innerHTML = paths;

      function createNodeElements(node) {{
        const el = document.createElement('div');
        el.className = `mm-node type-${{node.tipo || 'concept'}}`;
        if (node.id === selectedNodeId) el.classList.add('selected');
        el.id = `node-${{node.id}}`;
        el.style.left = `${{node.x}}px`;
        el.style.top = `${{node.y}}px`;

        const icon = typeIcons[node.tipo] || '💡';
        const page = node.pagina ? `<span class="page-tag">P.${{node.pagina}}</span>` : '';
        const hasKids = node.children && node.children.length > 0;
        const toggleBtn = hasKids ? `<span class="node-toggle" title="Recolher/Expandir">${{node.collapsed ? '+' : '−'}}</span>` : '';

        el.innerHTML = `
          <span class="node-icon">${{icon}}</span>
          <span class="node-text">${{node.titulo}}</span>
          ${{page}}
          ${{toggleBtn}}
        `;

        el.onclick = (e) => {{
          if (e.target.classList.contains('node-toggle')) {{
            e.stopPropagation();
            node.collapsed = !node.collapsed;
            renderMindmap();
            return;
          }}
          selectNode(node);
        }};

        nodesContainer.appendChild(el);
        node.actualW = el.offsetWidth;

        if (!node.collapsed) {{
          node.children.forEach(createNodeElements);
        }}
      }}
      createNodeElements(rootNode);

      let refinedPaths = '';
      function drawBranchesRefined(node) {{
        if (node.collapsed) return;
        node.children.forEach(ch => {{
          const x1 = node.x + (node.actualW || 180);
          const y1 = node.y + 19;
          const x2 = ch.x;
          const y2 = ch.y + 19;
          const dx = Math.max(35, (x2 - x1) * 0.52);

          let strokeColor = 'rgba(59, 130, 246, 0.7)';
          if (ch.tipo === 'trap') strokeColor = 'rgba(239, 68, 68, 0.75)';
          else if (ch.tipo === 'rule') strokeColor = 'rgba(245, 158, 11, 0.75)';
          else if (ch.tipo === 'comparison') strokeColor = 'rgba(139, 92, 246, 0.75)';
          else if (ch.tipo === 'mnemonic') strokeColor = 'rgba(168, 85, 247, 0.75)';
          else if (ch.tipo === 'category') strokeColor = 'rgba(16, 185, 129, 0.75)';

          refinedPaths += `<path d="M ${{x1}} ${{y1}} C ${{x1 + dx}} ${{y1}}, ${{x2 - dx}} ${{y2}}, ${{x2}} ${{y2}}"
                                fill="none" stroke="${{strokeColor}}" stroke-width="2.2" stroke-linecap="round"/>`;
          drawBranchesRefined(ch);
        }});
      }}
      drawBranchesRefined(rootNode);
      svgLines.innerHTML = refinedPaths;

      document.getElementById('stats-badge').textContent = 
        `${{data.nodes.length}} nós • ${{data.edges.length}} conexões • ${{rootNode.children.length}} categorias`;
    }}

    function selectNode(node) {{
      selectedNodeId = node.id;
      document.querySelectorAll('.mm-node').forEach(el => el.classList.remove('selected'));
      const activeEl = document.getElementById(`node-${{node.id}}`);
      if (activeEl) activeEl.classList.add('selected');

      const drawer = document.getElementById('drawer');
      const bInfo = typeBadges[node.tipo] || {{ text: (node.tipo || 'CONCEITO').toUpperCase(), bg: '#374151', color: '#f3f4f6' }};
      const badgeEl = document.getElementById('d-type-badge');
      badgeEl.textContent = bInfo.text;
      badgeEl.style.background = bInfo.bg;
      badgeEl.style.color = bInfo.color;

      document.getElementById('d-page-badge').textContent = `Página ${{node.pagina || 1}} do PDF`;
      document.getElementById('d-title').textContent = node.titulo;
      document.getElementById('d-summary').textContent = node.resumo || 'Sem descrição cadastrada.';

      drawer.classList.add('open');
    }}

    function closeDrawer() {{
      document.getElementById('drawer').classList.remove('open');
      selectedNodeId = null;
      document.querySelectorAll('.mm-node').forEach(el => el.classList.remove('selected'));
    }}

    function zoom(delta) {{
      zoomLevel = Math.min(2.0, Math.max(0.3, zoomLevel + delta));
      applyTransform();
    }}
    function resetView() {{
      zoomLevel = 1.0;
      panX = 60;
      panY = 80;
      applyTransform();
    }}
    function fitView() {{
      let minY = Infinity, maxY = -Infinity, maxX = -Infinity;
      Object.values(nodeMap).forEach(n => {{
        if (n.y < minY) minY = n.y;
        if (n.y > maxY) maxY = n.y;
        if (n.x + (n.actualW || 200) > maxX) maxX = n.x + (n.actualW || 200);
      }});
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      const mapW = maxX - 40 + 100;
      const mapH = maxY - minY + 160;
      const scaleX = (vw - 120) / mapW;
      const scaleY = (vh - 120) / mapH;
      zoomLevel = Math.min(1.1, Math.max(0.35, Math.min(scaleX, scaleY)));
      panX = 60;
      panY = Math.max(60, (vh - (maxY + minY) * zoomLevel) / 2);
      applyTransform();
    }}

    function toggleAllBranches() {{
      allCollapsed = !allCollapsed;
      Object.values(nodeMap).forEach(n => {{
        if (n.children.length > 0 && n.level > 0) {{
          n.collapsed = allCollapsed;
        }}
      }});
      document.getElementById('btn-toggle-all').textContent = allCollapsed ? '↕ Expandir' : '↕ Recolher';
      renderMindmap();
      setTimeout(fitView, 50);
    }}

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen().catch(() => {{}});
      }} else {{
        document.exitFullscreen().catch(() => {{}});
      }}
    }}

    document.getElementById('search-input').addEventListener('input', e => {{
      const q = e.target.value.toLowerCase().trim();
      document.querySelectorAll('.mm-node').forEach(el => {{
        if (!q) {{
          el.classList.remove('matched', 'dimmed');
          return;
        }}
        const txt = el.textContent.toLowerCase();
        const nid = el.id.replace('node-', '');
        const nData = nodeMap[nid];
        const sum = (nData?.resumo || '').toLowerCase();
        if (txt.includes(q) || sum.includes(q)) {{
          el.classList.add('matched');
          el.classList.remove('dimmed');
        }} else {{
          el.classList.remove('matched');
          el.classList.add('dimmed');
        }}
      }});
    }});

    window.addEventListener('keydown', e => {{
      if (e.key === 'Escape') closeDrawer();
    }});

    renderMindmap();
    setTimeout(fitView, 100);
    window.addEventListener('resize', () => renderMindmap());
  </script>
</body>
</html>"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)


# ============================================================================
# 5. EXECUÇÃO PRINCIPAL
# ============================================================================

def main():
    print("=" * 80)
    print("🚀 TESTADOR ISOLADO DE MAPA MENTAL PARA CONCURSOS PÚBLICOS")
    print("   Método 4 Pilares • Padrão NotebookLM Universal (Regra 13)")
    print("=" * 80)

    # Coleta todos os arquivos passados via argumentos
    input_files = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            clean_arg = arg.strip().strip('"').strip("'")
            if clean_arg:
                input_files.append(clean_arg)
    else:
        user_in = input("👉 Digite ou arraste o caminho do arquivo PDF: ").strip().strip('"').strip("'")
        if user_in:
            input_files.append(user_in)

    if not input_files:
        default_pdf = r"c:\PROJETOS IA\Concursos\Direito_Administrativo\Administracao_Direta_e_Indireta\Transcricao_Completa_ADMINISTRAÇÃO_DIRETA_E_INDIRETA.txt"
        print(f"\n[Info] Nenhum PDF informado. Usando arquivo padrão de teste:\n{default_pdf}\n")
        input_files.append(default_pdf)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    processed_count = 0

    for idx, raw_path in enumerate(input_files, 1):
        print("\n" + "-" * 80)
        print(f"[{idx}/{len(input_files)}] Processando: {raw_path}")
        print("-" * 80)

        resolved_path = resolve_file_path(raw_path)
        if not resolved_path:
            print(f"❌ Erro: O arquivo não foi encontrado no disco:")
            print(f"   Informado: {raw_path}")
            continue

        print(f"📄 Arquivo localizado: {resolved_path}")
        if resolved_path.lower().endswith(".pdf"):
            print("📄 Extraindo texto estruturado do PDF...")
            text_corpus = extract_text_from_pdf(resolved_path)
        else:
            print("📄 Lendo arquivo de texto...")
            with open(resolved_path, "r", encoding="utf-8", errors="ignore") as f:
                text_corpus = f.read()

        if not text_corpus.strip():
            print(f"❌ Erro: Nenhum texto legível pôde ser extraído de {resolved_path}.")
            continue

        print(f"  → {len(text_corpus)} caracteres processados")
        print("🧠 Gerando mapa mental semântico estruturado (Estilo NotebookLM)...")
        mindmap = generate_semantic_mindmap_from_text(resolved_path, text_corpus)

        slug = slugify(mindmap["titulo"])

        # Salva o genérico (compatibilidade) e o exclusivo por tema
        json_path_generic = os.path.join(script_dir, "resultado_mapa.json")
        json_path_slug = os.path.join(script_dir, f"resultado_mapa_{slug}.json")
        with open(json_path_generic, "w", encoding="utf-8") as f:
            json.dump(mindmap, f, ensure_ascii=False, indent=2)
        with open(json_path_slug, "w", encoding="utf-8") as f:
            json.dump(mindmap, f, ensure_ascii=False, indent=2)

        html_path_generic = os.path.join(script_dir, "visualizar_mapa.html")
        html_path_slug = os.path.join(script_dir, f"visualizar_mapa_{slug}.html")
        generate_interactive_html(mindmap, html_path_generic)
        generate_interactive_html(mindmap, html_path_slug)

        print("\n" + "=" * 80)
        print(f"✅ MAPA MENTAL GERADO COM SUCESSO [{idx}/{len(input_files)}]: {mindmap['titulo']}")
        print(f"📊 Total de Nós: {len(mindmap['nodes'])} | Arestas: {len(mindmap['edges'])}")
        print(f"📁 JSON salvo em: {json_path_slug}")
        print(f"🌐 HTML exclusivo: {html_path_slug}")
        print("=" * 80)

        # Abrir no navegador forçando nova aba e URL exclusiva com timestamp
        try:
            ts = int(time.time())
            webbrowser.open(f"file:///{os.path.abspath(html_path_slug)}?v={ts}")
            print(f"🌐 Visualizador aberto em nova aba do navegador!")
        except Exception as e_b:
            print(f"[Aviso navegador]: {e_b}")

        processed_count += 1

    print("\n" + "=" * 80)
    print(f"🎯 Concluído! Total de mapas gerados: {processed_count}/{len(input_files)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
