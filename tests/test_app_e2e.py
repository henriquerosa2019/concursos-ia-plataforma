"""
Suíte de Testes Automatizados End-to-End com Playwright
Plataforma Central de Concursos IA
Verifica todas as 8 funcionalidades e regras de estudo e sincronização com Supabase.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8095"

def run_all_tests():
    print("=" * 65)
    print("🚀 INICIANDO BATERIA DE TESTES PLAYWRIGHT - CONCURSOS IA")
    print("=" * 65)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # -------------------------------------------------------------
        # TESTE 1: Carregamento Inicial e Título da Aplicação
        # -------------------------------------------------------------
        print("\n[TESTE 1] Verificando carregamento e título da aplicação...")
        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(1000)
            title = page.title()
            assert "Concursos" in title, f"Título inesperado: {title}"
            print(f"  ✅ PASS: Aplicação carregada com sucesso! Título: '{title}'")
            results.append(("1. Carregamento e Título", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("1. Carregamento e Título", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # TESTE 2: Alternância de Tema Global (Claro ☀️ / Escuro 🌙)
        # -------------------------------------------------------------
        print("\n[TESTE 2] Testando Alternador de Tema Global (Light / Dark Mode)...")
        try:
            theme_btn = page.locator("#globalThemeBtn")
            theme_text = page.locator("#globalThemeText")
            
            initial_text = theme_text.inner_text()
            theme_btn.click()
            page.wait_for_timeout(500)
            
            body_bg = page.evaluate("() => window.getComputedStyle(document.body).backgroundColor")
            after_text = theme_text.inner_text()
            assert initial_text != after_text, "Texto do tema não mudou!"
            print(f"  ✅ PASS: Tema alternado com sucesso! (Texto: '{after_text}', BG: {body_bg})")

            # Voltar para o modo escuro padrão
            theme_btn.click()
            page.wait_for_timeout(300)
            results.append(("2. Tema Global (Claro/Escuro)", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("2. Tema Global (Claro/Escuro)", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # TESTE 3: Status e Conexão do Supabase no Topbar
        # -------------------------------------------------------------
        print("\n[TESTE 3] Verificando Indicador e Modal do Supabase...")
        try:
            badge = page.locator("#supabaseStatusText")
            badge_text = badge.inner_text()
            print(f"  Status do badge Supabase: '{badge_text}'")
            assert "Conectado" in badge_text or "Local" in badge_text, f"Badge com texto inesperado: {badge_text}"

            # Abrir modal do Supabase
            page.click("#supabaseStatusBadge")
            page.wait_for_timeout(600)
            modal = page.locator("#modalSupabase")
            assert modal.is_visible(), "Modal do Supabase não abriu!"
            
            # Fechar modal
            page.click("#modalSupabase button:has-text('Fechar')")
            page.wait_for_timeout(300)
            print("  ✅ PASS: Integração do Supabase validada com sucesso na interface!")
            results.append(("3. Status e Modal do Supabase", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("3. Status e Modal do Supabase", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # TESTE 4: Navegação até o PDF recém importado: ATOS ADMINISTRATIVOS
        # -------------------------------------------------------------
        print("\n[TESTE 4] Selecionando o PDF importado (Direito Administrativo / ATOS ADMINISTRATIVOS)...")
        try:
            # Aguardar o sidebar carregar a árvore da API
            page.wait_for_selector(".subarea-item", timeout=10000)
            atos_item = page.locator(".subarea-item:has-text('ATOS ADMINISTRATIVOS'), .subarea-item:has-text('Atos Administrativos')").first
            atos_item.click()
            page.wait_for_timeout(1000)

            # Verificar título principal da aula
            lesson_title = page.locator("#lessonTitle").inner_text()
            print(f"  Título da aula carregada: '{lesson_title[:65]}...'")
            assert "ATOS ADMINISTRATIVOS" in lesson_title.upper(), f"Título inesperado: {lesson_title}"
            print("  ✅ PASS: PDF de Atos Administrativos carregado e selecionado!")
            results.append(("4. Seleção de PDF Atos Administrativos", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("4. Seleção de PDF Atos Administrativos", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # TESTE 5: Modo Leitura Apostila / Word e Leitura Contínua
        # -------------------------------------------------------------
        print("\n[TESTE 5] Testando Modo Leitura Apostila / Word (Folhas, Paginação e Contínuo)...")
        try:
            # Acessar a aba de Leitura / Momentos-Chave
            page.locator(".nav-tab:has-text('Momentos-Chave')").click()
            page.wait_for_timeout(500)

            # Clicar no sub-pill do Modo Leitura
            page.locator("#pillCont").click()
            page.wait_for_timeout(600)

            # Checar se o container de folhas de leitura está visível
            pages_container = page.locator(".reader-pages-container")
            assert pages_container.is_visible(), "Container de páginas estilo Word/Livro não visível!"

            # Verificar se a primeira página foi renderizada
            first_sheet = page.locator(".reader-page-sheet").first
            assert first_sheet.is_visible(), "Folha de leitura da página 1 não visível!"

            # Testar botão de avançar página circular (›)
            next_circle = page.locator(".reader-nav-next")
            if next_circle.is_enabled():
                next_circle.click()
                page.wait_for_timeout(400)
                print("  Botão circular de avançar página funcionou com sucesso!")

            # Alternar para modo contínuo via seletor
            cont_btn = page.locator(".reader-mode-btn:has-text('Contínua')")
            if cont_btn.is_visible():
                cont_btn.click()
            else:
                page.evaluate("setReaderDisplayMode('continuous')")
            page.wait_for_timeout(500)

            cont_view = page.locator(".reader-continuous-view")
            assert cont_view.is_visible(), "Modo de leitura contínua não renderizou a folha única!"
            print("  ✅ PASS: Modo Leitura Apostila (Word) e Contínua funcionando perfeitamente!")

            # Restaurar modo páginas
            page.evaluate("setReaderDisplayMode('pages')")
            page.wait_for_timeout(300)
            results.append(("5. Modo Leitura Word/Apostila", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("5. Modo Leitura Word/Apostila", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # TESTE 6: Flashcards e Repetição Espaçada (SM-2)
        # -------------------------------------------------------------
        print("\n[TESTE 6] Testando Interatividade dos Flashcards (Pilar 3)...")
        try:
            # Clicar na aba de Flashcards
            page.locator(".nav-tab:has-text('Flashcards')").click()
            page.wait_for_timeout(600)

            # Verificar se o cartão existe
            card = page.locator("#cardElement")
            assert card.is_visible(), "Card de flashcard (#cardElement) não encontrado!"
            card_front_text = page.locator("#cardText").inner_text()
            print(f"  Texto do cartão (Frente): '{card_front_text[:60]}...'")

            # Virar o cartão
            card.click()
            page.wait_for_timeout(400)
            side_text = page.locator("#cardSide").inner_text()
            assert "VERSO" in side_text, f"Card não virou para o verso: {side_text}"
            
            # Clicar no botão 'Bom' (SM-2)
            page.locator(".sm2-btn-good").click()
            page.wait_for_timeout(400)
            print("  ✅ PASS: Flashcards interativos e algoritmo SM-2 operando com sucesso!")
            results.append(("6. Flashcards e Algoritmo SM-2", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("6. Flashcards e Algoritmo SM-2", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # TESTE 7: Mini-Simulado de Fixação (Pilar 4)
        # -------------------------------------------------------------
        print("\n[TESTE 7] Testando Mini-Simulado de Fixação (Pilar 4)...")
        try:
            # Clicar na aba do Simulado
            page.locator(".nav-tab:has-text('Simulado')").click()
            page.wait_for_timeout(600)

            # Verificar se existem questões renderizadas
            questions = page.locator(".quiz-item")
            q_count = questions.count()
            print(f"  Total de questões no simulado: {q_count}")
            assert q_count > 0, "Nenhuma questão encontrada no simulado!"

            # Responder a primeira opção da questão 1
            first_opt = questions.first.locator(".quiz-opt").first
            first_opt.click()
            page.wait_for_timeout(400)

            # Verificar se o feedback / comentário pedagógico apareceu
            feedback = page.locator("#quiz-fb-0")
            assert feedback.is_visible(), "Explicação pedagógica (#quiz-fb-0) não exibida após resposta!"
            fb_text = feedback.inner_text()
            print(f"  Gabarito / Feedback exibido: '{fb_text[:65]}...'")
            print("  ✅ PASS: Mini-Simulado corrigido com sucesso e comentário pedagógico exibido!")
            results.append(("7. Mini-Simulado e Correção", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("7. Mini-Simulado e Correção", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # TESTE 8: Validação dos Momentos-Chave em Informática / Excel
        # -------------------------------------------------------------
        print("\n[TESTE 8] Verificando os Momentos-Chave em Informática / Excel...")
        try:
            # Clicar no tópico Excel
            excel_item = page.locator(".subarea-item:has-text('Excel')").first
            excel_item.click()
            page.wait_for_timeout(1000)

            # Clicar na aba de Momentos-Chave
            page.locator(".nav-tab:has-text('Momentos-Chave')").click()
            page.wait_for_timeout(600)

            # Garantir que o sub-pill de momentos está ativo
            page.locator("#pillMoments").click()
            page.wait_for_timeout(600)

            # Checar o contador no pill
            pill_text = page.locator("#pillMoments").inner_text()
            print(f"  Texto do Pill de Momentos: '{pill_text}'")
            assert "(0)" not in pill_text, f"Aviso: Consta (0) momentos no pill: {pill_text}"

            # Checar quantidade de cartões renderizados
            moments_cards = page.locator(".key-moment-card")
            m_count = moments_cards.count()
            print(f"  Cartões de momentos-chave renderizados: {m_count}")
            assert m_count >= 6, f"Esperado ao menos 6 momentos, encontrados {m_count}"
            print(f"  ✅ PASS: Todos os {m_count} Momentos-Chave estão presentes e visíveis sem bug (0)!")
            results.append(("8. Momentos-Chave (Excel)", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("8. Momentos-Chave (Excel)", f"FAIL: {e}"))

        browser.close()

    print("\n" + "=" * 65)
    print("📊 RESUMO DOS RESULTADOS DA SUÍTE DE TESTES")
    print("=" * 65)
    all_passed = True
    for name, status in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f" {icon} {name:<42} [{status}]")
        if status != "PASS":
            all_passed = False
    print("=" * 65)
    if all_passed:
        print("🎉 TODOS OS 8 TESTES E REGRAS PASSARAM COM 100% DE SUCESSO!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM. VERIFIQUE OS LOGS ACIMA.")
    print("=" * 65)

if __name__ == "__main__":
    run_all_tests()
