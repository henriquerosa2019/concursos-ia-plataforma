"""
Gerenciador CLI do Repositório de Concursos Públicos
Uso:
  python gerenciador.py status             -> Diagnóstico completo e métricas do repositório
  python gerenciador.py export-anki        -> Exporta todos os flashcards de todas as matérias para o Anki
  python gerenciador.py cleanup            -> Limpeza de pastas obsoletas e validação de regras
  python gerenciador.py test-ai            -> Testa as chaves e conectividade das IAs configuradas
  python gerenciador.py add-topic <Materia> <Topico> -> Cria novo tópico no padrão 4 Pilares
"""

import os
import sys
import json
import re

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def cmd_status():
    print("\n" + "="*70)
    print(" 📊 DIAGNÓSTICO DO REPOSITÓRIO: CONCURSOS PÚBLICOS (IA)")
    print("="*70)
    print(f"Diretório Raiz: {BASE_DIR}\n")
    
    total_disciplines = 0
    total_topics = 0
    total_files = 0
    total_cards = 0
    total_quiz = 0
    total_errors = 0
    
    ignore_dirs = {'.git', '__pycache__', 'scratch', '.system_generated', 'Excel'}
    
    disciplines = []
    for item in sorted(os.listdir(BASE_DIR)):
        ipath = os.path.join(BASE_DIR, item)
        if os.path.isdir(ipath) and item not in ignore_dirs:
            disciplines.append(item)
            
    total_disciplines = len(disciplines)
    
    for disc in disciplines:
        dpath = os.path.join(BASE_DIR, disc)
        subs = [s for s in sorted(os.listdir(dpath)) if os.path.isdir(os.path.join(dpath, s))]
        print(f"📁 DISCIPLINA: {disc.replace('_', ' ')} ({len(subs)} tópicos)")
        
        for sub in subs:
            total_topics += 1
            spath = os.path.join(dpath, sub)
            files = os.listdir(spath)
            
            cards_count = 0
            quiz_count = 0
            errors_count = 0
            has_lesson = False
            
            for f in files:
                total_files += 1
                fp = os.path.join(spath, f)
                if "anki" in f.lower() and f.endswith(".txt"):
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as fc:
                            cards_count += len([l for l in fc if '\t' in l])
                    except Exception:
                        pass
                elif "simulado" in f.lower() and f.endswith(".json"):
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as fq:
                            qdata = json.load(fq)
                            if isinstance(qdata, list):
                                quiz_count += len(qdata)
                    except Exception:
                        pass
                elif f == "revisoes_erros.json":
                    try:
                        with open(fp, "r", encoding="utf-8") as fe:
                            edata = json.load(fe)
                            errors_count += len(edata.get("cards", [])) + len(edata.get("quiz", []))
                    except Exception:
                        pass
                elif f.startswith("Aula_") and f.endswith(".md"):
                    has_lesson = True
                    
            total_cards += cards_count
            total_quiz += quiz_count
            total_errors += errors_count
            
            status_icon = "🟢 Completo" if (has_lesson and cards_count > 0) else "🟡 Estruturado"
            print(f"   └── 🏷️  {sub.replace('_', ' '):<28} | {status_icon} | Cards: {cards_count:2d} | Quiz: {quiz_count:2d} | Erros: {errors_count:2d}")
        print()
        
    print("-"*70)
    print(" 📈 RESUMO GERAL DO SISTEMA:")
    print(f" • Total de Disciplinas: {total_disciplines}")
    print(f" • Total de Tópicos/Subáreas: {total_topics}")
    print(f" • Total de Flashcards Anki no Deck: {total_cards}")
    print(f" • Total de Questões de Simulado Salvas: {total_quiz}")
    print(f" • Itens Pendentes no Caderno de Erros: {total_errors}")
    print(f" • Total de Arquivos de Estudo: {total_files}")
    
    # Status de IA
    cfg = load_config()
    gem = bool(cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY"))
    oai = bool(cfg.get("openai_api_key") or os.environ.get("OPENAI_API_KEY"))
    print("\n 🤖 PROVEDORES DE IA:")
    print(f" • Google Gemini: {'✅ Configurado' if gem else '⚪ Não configurado'}")
    print(f" • OpenAI GPT:    {'✅ Configurado' if oai else '⚪ Não configurado'}")
    print(f" • Provedor Ativo: {'Gemini' if gem else ('OpenAI' if oai else 'Banco Curado Offline')}")
    print("="*70 + "\n")

def cmd_export_anki():
    out_file = os.path.join(BASE_DIR, "Baralho_Geral_Concursos_Anki.txt")
    cards = []
    seen = set()
    
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if "anki" in f.lower() and f.endswith(".txt") and f != "Baralho_Geral_Concursos_Anki.txt":
                fp = os.path.join(root, f)
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as fc:
                        for line in fc:
                            line = line.strip()
                            if "\t" in line:
                                norm = line.split("\t")[0].strip().lower()
                                if norm not in seen:
                                    seen.add(norm)
                                    cards.append(line)
                except Exception:
                    pass
                    
    with open(out_file, "w", encoding="utf-8") as out:
        out.write("\n".join(cards))
        
    print(f"\n✅ Baralho consolidado exportado com sucesso!")
    print(f"📄 Arquivo: {out_file}")
    print(f"🃏 Total de flashcards únicos exportados: {len(cards)}\n")

def cmd_cleanup():
    print("\n🧹 Executando rotina de limpeza preventiva...")
    old_root_excel = os.path.join(BASE_DIR, "Excel")
    inf_excel = os.path.join(BASE_DIR, "Informatica", "Excel")
    
    if os.path.exists(old_root_excel) and os.path.isdir(old_root_excel):
        os.makedirs(inf_excel, exist_ok=True)
        count = 0
        for f in os.listdir(old_root_excel):
            src = os.path.join(old_root_excel, f)
            dst = os.path.join(inf_excel, f)
            if not os.path.exists(dst) and os.path.isfile(src):
                import shutil
                shutil.copy2(src, dst)
            if os.path.isfile(src):
                os.remove(src)
                count += 1
        os.rmdir(old_root_excel)
        print(f"✅ Pasta legada 'Excel' na raiz foi fundida e removida ({count} arquivos migrados).")
    else:
        print("✅ Nenhuma estrutura legada encontrada. O repositório está limpo!")
    print()

def cmd_add_topic(disc, sub):
    target = os.path.join(BASE_DIR, disc.replace(" ", "_"), sub.replace(" ", "_"))
    os.makedirs(target, exist_ok=True)
    readme = os.path.join(target, "README.md")
    if not os.path.exists(readme):
        with open(readme, "w", encoding="utf-8") as f:
            f.write(f"# {disc} • {sub}\n\nPasta pronta para receber materiais no padrão dos 4 Pilares de Alta Retenção.\n")
    print(f"\n✅ Tópico criado: {target}\n")

if __name__ == "__main__":
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    
    if action == "status":
        cmd_status()
    elif action in ("export-anki", "export"):
        cmd_export_anki()
    elif action == "cleanup":
        cmd_cleanup()
    elif action == "add-topic":
        if len(sys.argv) >= 4:
            cmd_add_topic(sys.argv[2], sys.argv[3])
        else:
            print("Uso: python gerenciador.py add-topic <Disciplina> <Topico>")
    else:
        print("Comandos disponíveis: status, export-anki, cleanup, add-topic")
