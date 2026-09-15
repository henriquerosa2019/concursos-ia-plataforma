"""
Módulo de Integração com Banco de Dados Supabase
Permite persistência centralizada na nuvem de todas as aulas, transcrições,
os 4 pilares (Resumo, Raio-X, Flashcards, Simulado) e Momentos-Chave.
Implementado com urllib nativo do Python (zero dependências adicionais).
"""

import os
import json
import re
import urllib.request
import urllib.parse
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def normalize_slug(s):
    if not s:
        return ""
    s_norm = ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '_', s_norm).strip('_')

def get_supabase_config():
    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    
    url = os.environ.get("SUPABASE_URL", cfg.get("supabase_url", "")).strip()
    url = re.sub(r'/rest/v1/?$', '', url).rstrip("/")
    key = os.environ.get("SUPABASE_KEY", os.environ.get("SUPABASE_ANON_KEY", cfg.get("supabase_key", ""))).strip()
    return url, key

def is_supabase_configured():
    url, key = get_supabase_config()
    return bool(url and key and url.startswith("http"))

def supabase_request(endpoint, method="GET", data=None, params=None):
    """
    Executa chamadas REST autenticadas para a API PostgREST do Supabase.
    """
    url_base, key = get_supabase_config()
    if not url_base or not key:
        return None, "Supabase não configurado (URL ou chave ausente)."

    query_str = f"?{urllib.parse.urlencode(params)}" if params else ""
    full_url = f"{url_base}/rest/v1/{endpoint}{query_str}"
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation,resolution=merge-duplicates"
    }

    req_data = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(full_url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = resp.read().decode("utf-8")
            if body:
                return json.loads(body), None
            return True, None
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        return None, f"HTTP {e.code}: {err_msg}"
    except Exception as e:
        return None, str(e)

def test_connection():
    """Testa a conexão com o Supabase verificando a tabela disciplinas."""
    if not is_supabase_configured():
        return False, "Supabase não configurado em config.json."
    res, err = supabase_request("disciplinas", method="GET", params={"limit": "1"})
    if err:
        return False, f"Falha na conexão: {err}"
    return True, "Conexão com o Supabase estabelecida com sucesso!"

def upsert_aula(disciplina_id, subarea, titulo="", professor="", tipo="video", youtube_url=""):
    """Cria ou atualiza uma aula no Supabase."""
    slug = normalize_slug(subarea)
    aula_id = f"{normalize_slug(disciplina_id)}_{slug}"
    
    # 1. Garantir que a disciplina existe
    supabase_request("disciplinas", method="POST", data={
        "id": disciplina_id,
        "nome": disciplina_id.replace("_", " "),
        "icone": "📚"
    }, params={"on_conflict": "id"})

    # 2. Upsert da aula
    payload = [{
        "id": aula_id,
        "disciplina_id": disciplina_id,
        "subarea": subarea,
        "subarea_slug": slug,
        "titulo": titulo or f"Aula - {subarea}",
        "professor": professor or "Não informado",
        "tipo": tipo,
        "youtube_url": youtube_url or "",
        "updated_at": "now()"
    }]
    res, err = supabase_request("aulas", method="POST", data=payload, params={"on_conflict": "id"})
    return (res, err)

def upsert_conteudo(aula_id, pilar1="", pilar2="", flashcards=None, simulado=None, momentos=None, timed_trans=None, full_trans="", paginas=None):
    """Atualiza os 4 pilares e transcrições da aula no Supabase."""
    data = {
        "aula_id": aula_id,
        "updated_at": "now()"
    }
    if pilar1 is not None:
        data["pilar1_resumo"] = pilar1
    if pilar2 is not None:
        data["pilar2_raiox"] = pilar2
    if flashcards is not None:
        data["pilar3_flashcards"] = flashcards
    if simulado is not None:
        data["pilar4_simulado"] = simulado
    if momentos is not None:
        data["momentos_chave"] = momentos
    if timed_trans is not None:
        data["transcricao_cronometrada"] = timed_trans
    if full_trans:
        data["transcricao_completa"] = full_trans
    if paginas is not None:
        data["leitura_paginas"] = paginas

    res, err = supabase_request("conteudos_aulas", method="POST", data=[data], params={"on_conflict": "aula_id"})
    return (res, err)

def get_aula_full(disciplina_id, subarea):
    """Busca aula e seu conteúdo completo diretamente do Supabase."""
    slug = normalize_slug(subarea)
    aula_id = f"{normalize_slug(disciplina_id)}_{slug}"
    
    res_aula, err_a = supabase_request("aulas", method="GET", params={"id": f"eq.{aula_id}"})
    if not res_aula or not isinstance(res_aula, list) or len(res_aula) == 0:
        return None
        
    aula = res_aula[0]
    res_cont, err_c = supabase_request("conteudos_aulas", method="GET", params={"aula_id": f"eq.{aula_id}"})
    conteudo = res_cont[0] if (res_cont and isinstance(res_cont, list) and len(res_cont) > 0) else {}
    
    return {
        "aula": aula,
        "conteudo": conteudo
    }

def sync_all_local_to_supabase():
    """
    Varre todas as disciplinas e tópicos locais e faz upload completo para o Supabase.
    Isso migra todo o material do PC para a nuvem de uma só vez!
    """
    if not is_supabase_configured():
        return False, "Configure o Supabase primeiro nas Configurações."
        
    synced_count = 0
    errors = []

    ignore_dirs = {'.git', '__pycache__', 'scratch', '.system_generated', 'node_modules'}
    
    for d in os.listdir(BASE_DIR):
        dp = os.path.join(BASE_DIR, d)
        if not os.path.isdir(dp) or d.startswith('.') or d in ignore_dirs:
            continue
            
        for s in os.listdir(dp):
            sp = os.path.join(dp, s)
            if not os.path.isdir(sp) or s.startswith('.'):
                continue
                
            # Identificar arquivos locais
            md_file = None
            flashcards_file = None
            quiz_file = None
            moments_file = None
            timed_file = None
            full_file = None

            for f in os.listdir(sp):
                fl = f.lower()
                fp = os.path.join(sp, f)
                if fl.startswith("aula_") and fl.endswith(".md"):
                    md_file = fp
                elif fl.startswith("flashcards_") and fl.endswith(".txt"):
                    flashcards_file = fp
                elif fl.startswith("simulado_") and fl.endswith(".json"):
                    quiz_file = fp
                elif fl.startswith("momentos_chave") and fl.endswith(".json"):
                    moments_file = fp
                elif fl.startswith("transcricao_cronometrada") and fl.endswith(".txt"):
                    timed_file = fp
                elif fl.startswith("transcricao_completa") and fl.endswith(".txt"):
                    full_file = fp

            # Ler conteúdos
            titulo = s
            prof = ""
            pilar1 = ""
            yt_url = ""
            tipo = "video"

            if md_file and os.path.exists(md_file):
                try:
                    with open(md_file, "r", encoding="utf-8", errors="ignore") as f_in:
                        pilar1 = f_in.read()
                        m_t = re.search(r'^#\s*(.*)', pilar1)
                        if m_t:
                            titulo = m_t.group(1).strip()
                        m_p = re.search(r'Professor[a]?:\s*([^\n\r]+)', pilar1, re.IGNORECASE)
                        if m_p:
                            prof = m_p.group(1).strip()
                        m_yt = re.search(r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w\-]+)', pilar1)
                        if m_yt:
                            yt_url = m_yt.group(0)
                        if "PDF" in titulo or "Apostila" in titulo or not yt_url:
                            if not yt_url:
                                tipo = "pdf"
                except Exception:
                    pass

            # Flashcards
            flashcards = []
            if flashcards_file and os.path.exists(flashcards_file):
                try:
                    with open(flashcards_file, "r", encoding="utf-8", errors="ignore") as f_in:
                        for line in f_in:
                            if "\t" in line:
                                parts = line.strip().split("\t")
                                if len(parts) >= 2:
                                    flashcards.append({"front": parts[0].strip(), "back": parts[1].strip()})
                except Exception:
                    pass

            # Simulado
            quiz = []
            if quiz_file and os.path.exists(quiz_file):
                try:
                    with open(quiz_file, "r", encoding="utf-8", errors="ignore") as f_in:
                        q_data = json.load(f_in)
                        if isinstance(q_data, list):
                            quiz = q_data
                        elif isinstance(q_data, dict) and "questions" in q_data:
                            quiz = q_data["questions"]
                except Exception:
                    pass

            # Momentos-Chave
            moments = []
            if moments_file and os.path.exists(moments_file):
                try:
                    with open(moments_file, "r", encoding="utf-8", errors="ignore") as f_in:
                        moments = json.load(f_in)
                except Exception:
                    pass

            # Transcrições
            timed_trans = []
            if timed_file and os.path.exists(timed_file):
                try:
                    with open(timed_file, "r", encoding="utf-8", errors="ignore") as f_in:
                        for line in f_in:
                            m = re.match(r'\[([\d\.]+)s\]\s*\[(\d{1,2}:\d{2})\]\s*(.*)', line.strip())
                            if m:
                                timed_trans.append({
                                    "sec": int(float(m.group(1))),
                                    "time_str": m.group(2),
                                    "text": m.group(3).strip()
                                })
                except Exception:
                    pass

            full_trans = ""
            if full_file and os.path.exists(full_file):
                try:
                    with open(full_file, "r", encoding="utf-8", errors="ignore") as f_in:
                        full_trans = f_in.read()
                except Exception:
                    pass

            # Realizar Upsert no Supabase
            aula_id = f"{normalize_slug(d)}_{normalize_slug(s)}"
            res_a, err_a = upsert_aula(d, s, titulo=titulo, professor=prof, tipo=tipo, youtube_url=yt_url)
            if err_a:
                errors.append(f"{d}/{s} (aula): {err_a}")
                continue

            res_c, err_c = upsert_conteudo(
                aula_id=aula_id,
                pilar1=pilar1,
                flashcards=flashcards,
                simulado=quiz,
                momentos=moments,
                timed_trans=timed_trans,
                full_trans=full_trans
            )
            if err_c:
                errors.append(f"{d}/{s} (conteudo): {err_c}")
            else:
                synced_count += 1

    return (True, f"{synced_count} tópicos/aulas sincronizados com o Supabase com sucesso!") if not errors else (False, f"Sincronizados: {synced_count}. Erros: {'; '.join(errors[:3])}")

def supabase_auth_signup(email, password, nome=""):
    """
    Registra novo usuário no Supabase Auth (/auth/v1/signup).
    """
    url_base, key = get_supabase_config()
    if not url_base or not key:
        return None, "Supabase não configurado."
    signup_url = f"{url_base}/auth/v1/signup"
    headers = {
        "apikey": key,
        "Content-Type": "application/json"
    }
    payload = {
        "email": email.strip().lower(),
        "password": password,
        "data": {"nome": nome.strip() if nome else email.split("@")[0]}
    }
    try:
        req = urllib.request.Request(signup_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, None
    except urllib.error.HTTPError as e:
        return None, e.read().decode("utf-8")
    except Exception as ex:
        return None, str(ex)

def supabase_auth_login(email, password):
    """
    Autentica usuário existente no Supabase Auth (/auth/v1/token?grant_type=password).
    """
    url_base, key = get_supabase_config()
    if not url_base or not key:
        return None, "Supabase não configurado."
    login_url = f"{url_base}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": key,
        "Content-Type": "application/json"
    }
    payload = {
        "email": email.strip().lower(),
        "password": password
    }
    try:
        req = urllib.request.Request(login_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, None
    except urllib.error.HTTPError as e:
        return None, e.read().decode("utf-8")
    except Exception as ex:
        return None, str(ex)
