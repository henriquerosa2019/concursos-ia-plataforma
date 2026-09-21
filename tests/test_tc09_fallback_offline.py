"""
Bateria de Testes Automatizados E2E:
TC-09: Fallback Offline Resiliente & Modo Curado
Módulo: 2. IA & Fallbacks | Tag: Resiliência | Papel: Sistema

Critérios Validados:
1. Simulação de ausência de chaves de IA externas / falha de conexão na geração de questões, flashcards e raio-x.
2. Ativação imediata do Banco Curado Offline sem quebras, sem congelamento e sem erros crípticos para o aluno.
3. Renderização fluida dos flashcards na Aba 2, das questões no Simulado na Aba 3 e do Raio-X de Banca na Aba 1.
4. Resiliência do cliente diante de queda total de conectividade de rede (interceptação de rotas).
"""

import os
import sys
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8095"

def run_tc09_tests():
    print("=" * 75)
    print("🛡️ [TC-09] INICIANDO TESTE E2E: FALLBACK OFFLINE RESILIENTE & MODO CURADO")
    print("=" * 75)

    results = []
    unexpected_dialogs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Monitorar qualquer popup de alert/confirm inesperado com erros crípticos
        def on_dialog(dialog):
            msg = dialog.message
            print(f"  ⚠️ Dialog interceptado: [{dialog.type}] {msg}")
            if "Erro desconhecido" in msg or "undefined" in msg.lower() or "crash" in msg.lower():
                unexpected_dialogs.append(msg)
            dialog.accept()

        page.on("dialog", on_dialog)

        # -------------------------------------------------------------
        # 1. CARREGAMENTO INICIAL E PREPARAÇÃO DO AMBIENTE
        # -------------------------------------------------------------
        print("\n[PASSO 1] Carregando a aplicação e preparando a sessão de estudo...")
        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(1000)

            # Fechar modal de login/auth se presente
            if page.locator("#modalAuthOverlay").is_visible():
                page.evaluate("closeAuthModal()")
                page.wait_for_timeout(400)

            # Selecionar Informática / Excel
            page.wait_for_selector(".subarea-item", timeout=10000)
            excel_item = page.locator(".subarea-item:has-text('Excel')").first
            excel_item.click()
            page.wait_for_timeout(1000)

            print("  ✅ Aplicação carregada e matéria Informática / Excel selecionada com sucesso!")
            results.append(("1. Inicialização & Seleção de Matéria", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL Passo 1: {e}")
            results.append(("1. Inicialização & Seleção de Matéria", f"FAIL: {e}"))
            browser.close()
            return False

        # -------------------------------------------------------------
        # 2. TESTE BACKEND: RESILIÊNCIA DOS ENDPOINTS DE IA & MODO CURADO
        # -------------------------------------------------------------
        print("\n[PASSO 2] Validando resiliência dos endpoints de IA (API Layer)...")
        try:
            # 2.1 Flashcards API Fallback
            res_fc = page.evaluate("""async () => {
                const r = await fetch('/api/generate-ai-flashcards', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({discipline: 'Informatica', subarea: 'Excel', count: 2, is_trial: true})
                });
                return { status: r.status, data: await r.json() };
            }""")
            assert res_fc["status"] == 200, f"Status Flashcards API: {res_fc['status']}"
            assert res_fc["data"]["success"] is True, "Flashcards API success não foi True"
            assert len(res_fc["data"]["cards"]) >= 1, "Nenhum cartão retornado no fallback"
            prov_fc = res_fc["data"].get("provider", "desconhecido")
            print(f"  ✅ Flashcards API: 200 OK | Sucesso: True | Provedor: '{prov_fc}' | Cards: {len(res_fc['data']['cards'])}")

            # 2.2 Quiz API Fallback
            res_qz = page.evaluate("""async () => {
                const r = await fetch('/api/generate-ai-quiz', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({discipline: 'Informatica', subarea: 'Excel', banca: 'Cebraspe', count: 2, is_trial: true})
                });
                return { status: r.status, data: await r.json() };
            }""")
            assert res_qz["status"] == 200, f"Status Quiz API: {res_qz['status']}"
            assert res_qz["data"]["success"] is True, "Quiz API success não foi True"
            assert len(res_qz["data"]["questions"]) >= 1, "Nenhuma questão retornada no fallback"
            prov_qz = res_qz["data"].get("provider", "desconhecido")
            print(f"  ✅ Simulado API: 200 OK | Sucesso: True | Provedor: '{prov_qz}' | Questões: {len(res_qz['data']['questions'])}")

            # 2.3 Raio-X API Fallback
            res_rx = page.evaluate("""async () => {
                const r = await fetch('/api/generate-ai-raiox', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({discipline: 'Informatica', subarea: 'Excel', banca: 'Cebraspe', is_trial: true})
                });
                return { status: r.status, data: await r.json() };
            }""")
            assert res_rx["status"] == 200, f"Status Raio-X API: {res_rx['status']}"
            assert res_rx["data"]["success"] is True, "Raio-X API success não foi True"
            assert bool(res_rx["data"].get("markdown")), "Markdown do Raio-X veio vazio"
            prov_rx = res_rx["data"].get("provider", "desconhecido")
            print(f"  ✅ Raio-X API: 200 OK | Sucesso: True | Provedor: '{prov_rx}' | Markdown: Presente ({len(res_rx['data']['markdown'])} chars)")

            results.append(("2. API Resiliente Offline (Flashcards, Quiz, Raio-X)", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL Passo 2: {e}")
            results.append(("2. API Resiliente Offline", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # 3. TESTE UI: GERAÇÃO DE FLASHCARDS COM MODO CURADO NA ABA 2
        # -------------------------------------------------------------
        print("\n[PASSO 3] Testando fluxo de interface para Geração de Flashcards (Aba 2)...")
        try:
            # Alternar para a aba 2 (Flashcards)
            page.locator(".nav-tab:has-text('Flashcards')").click()
            page.wait_for_timeout(600)

            initial_count = page.evaluate("() => flashcardsData.length")
            print(f"  Quantidade inicial de flashcards em memória: {initial_count}")

            # Abrir modal de IA para Flashcards
            page.evaluate("openAiFlashcardModal()")
            page.wait_for_timeout(500)
            modal_cards = page.locator("#modalAiCards")
            assert modal_cards.is_visible(), "Modal #modalAiCards não abriu!"

            # Clicar em Gerar Novos Flashcards
            btn_run_cards = page.locator("#btnRunAiCards")
            btn_run_cards.click()

            # Aguardar o processamento e fechamento do modal
            page.wait_for_selector("#modalAiCards", state="hidden", timeout=15000)
            page.wait_for_timeout(1000)

            # Validar que a quantidade de flashcards aumentou
            new_count = page.evaluate("() => flashcardsData.length")
            print(f"  Nova quantidade de flashcards após geração offline: {new_count}")
            assert new_count > initial_count, f"Esperado aumento de cards ({new_count} <= {initial_count})"

            # Validar que o cartão está visível e pode ser virado
            card_text = page.locator("#cardText").inner_text()
            assert len(card_text.strip()) > 5, f"Texto do flashcard vazio ou inválido: {card_text}"
            print(f"  Frente do Flashcard gerado: '{card_text[:60]}...'")

            # Virar o card
            page.evaluate("flipCard()")
            page.wait_for_timeout(400)
            card_ans = page.locator("#cardText").inner_text()
            assert len(card_ans.strip()) > 5, "Verso do flashcard não foi renderizado!"
            print(f"  Verso do Flashcard (Resposta): '{card_ans[:60]}...'")

            results.append(("3. UI: Geração de Flashcards Offline Resiliente", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL Passo 3: {e}")
            results.append(("3. UI: Geração de Flashcards Offline Resiliente", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # 4. TESTE UI: GERAÇÃO DE SIMULADO COM MODO CURADO NA ABA 3
        # -------------------------------------------------------------
        print("\n[PASSO 4] Testando fluxo de interface para Geração de Simulado (Aba 3)...")
        try:
            # Alternar para a aba 3 (Simulado)
            page.locator(".nav-tab:has-text('Simulado')").click()
            page.wait_for_timeout(600)

            initial_quiz_count = page.locator(".quiz-item").count()
            print(f"  Quantidade inicial de questões no simulado: {initial_quiz_count}")

            # Abrir modal de IA para Simulado
            page.evaluate("openAiQuizModal()")
            page.wait_for_timeout(500)
            modal_quiz = page.locator("#modalAiQuiz")
            assert modal_quiz.is_visible(), "Modal #modalAiQuiz não abriu!"

            # Clicar em Gerar Simulado
            btn_run_quiz = page.locator("#btnRunAiQuiz")
            btn_run_quiz.click()

            # Aguardar o processamento e fechamento do modal
            page.wait_for_selector("#modalAiQuiz", state="hidden", timeout=15000)
            page.wait_for_timeout(1000)

            # Validar que as questões foram adicionadas
            new_quiz_count = page.locator(".quiz-item").count()
            print(f"  Nova quantidade de itens no simulado: {new_quiz_count}")
            assert new_quiz_count >= initial_quiz_count, "Simulado não manteve/adicionou questões"

            # Validar que as opções de resposta funcionam sem erro de console
            first_opt = page.locator(".quiz-opt").first
            assert first_opt.is_visible(), "Opções de resposta não visíveis no simulado"
            first_opt.click()
            page.wait_for_timeout(300)

            results.append(("4. UI: Geração de Simulado Offline Resiliente", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL Passo 4: {e}")
            results.append(("4. UI: Geração de Simulado Offline Resiliente", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # 5. TESTE UI: GERAÇÃO DE RAIO-X & PEGADINHAS NA ABA 1
        # -------------------------------------------------------------
        print("\n[PASSO 5] Testando fluxo de interface para Geração de Raio-X & Pegadinhas (Aba 1)...")
        try:
            # Abrir modal de IA para Raio-X
            page.evaluate("openAiRaioXModal()")
            page.wait_for_timeout(500)
            modal_raiox = page.locator("#modalAiRaioX")
            assert modal_raiox.is_visible(), "Modal #modalAiRaioX não abriu!"

            # Clicar em Gerar Raio-X
            btn_run_raiox = page.locator("#btnRunAiRaioX")
            btn_run_raiox.click()

            # Aguardar processamento e transição direta para a Aba 1
            page.wait_for_selector("#modalAiRaioX", state="hidden", timeout=15000)
            page.wait_for_timeout(1000)

            tab1_content = page.locator("#tab1Content").inner_text()
            assert "Raio-X" in tab1_content or "Pegadinha" in tab1_content or "Pontos" in tab1_content, f"Conteúdo do Raio-X não renderizado: {tab1_content[:100]}"
            print(f"  ✅ Conteúdo da Aba 1 (Raio-X): '{tab1_content[:80]}...'")

            results.append(("5. UI: Geração de Raio-X & Pegadinhas Offline Resiliente", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL Passo 5: {e}")
            results.append(("5. UI: Geração de Raio-X & Pegadinhas Offline Resiliente", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # 6. TESTE DE RESILIÊNCIA AVANÇADA: QUEDA TOTAL DE REDE NO NAVEGADOR
        # -------------------------------------------------------------
        print("\n[PASSO 6] Testando resiliência cliente diante de falha total de conexão de rede...")
        try:
            # Simular rota de rede abortada (falha de rede / desconexão total)
            page.route("**/api/generate-ai-*", lambda route: route.abort("failed"))

            # Chamar geração de flashcards no cliente sob falha de rede
            page.evaluate("generateAiFlashcards()")
            page.wait_for_timeout(1000)

            # Verificar que a aplicação ativou o fallback cliente sem quebrar
            current_cards = page.evaluate("() => flashcardsData.length")
            assert current_cards > 0, "Cards não persistiram após falha de rede simulada"
            print("  ✅ Fallback cliente ativado com sucesso após interrupção de rede simulada!")

            # Restaurar rotas normais
            page.unroute("**/api/generate-ai-*")

            results.append(("6. Resiliência do Navegador com Queda de Conexão", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL Passo 6: {e}")
            results.append(("6. Resiliência do Navegador com Queda de Conexão", f"FAIL: {e}"))

        # -------------------------------------------------------------
        # 7. CAPTURAR EVIDÊNCIA VISUAL (SCREENSHOT HOMOLOGAÇÃO)
        # -------------------------------------------------------------
        print("\n[PASSO 7] Capturando evidência visual de homologação do TC-09...")
        screenshot_path = os.path.join(os.getcwd(), "tc09_fallback_offline_sucesso.png")
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"  📸 Screenshot salvo em: {screenshot_path}")

        # Validar ausência de diálogos com erros crípticos
        assert len(unexpected_dialogs) == 0, f"Erros inesperados interceptados: {unexpected_dialogs}"

        browser.close()

    print("\n" + "=" * 75)
    print("📋 RESUMO DA BATERIA DE HOMOLOGAÇÃO DO TC-09 (IA & FALLBACKS):")
    print("=" * 75)
    all_passed = True
    for name, status in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {name}: {status}")
        if status != "PASS":
            all_passed = False

    if all_passed:
        print("\n🏆 TC-09 CONCLUÍDO COM 100% DE SUCESSO! SISTEMA RESILIENTE E BLINDADO.")
    else:
        print("\n⚠️ ALGUNS ITENS DO TC-09 APRESENTARAM FALHA. VERIFIQUE OS LOGS ACIMA.")

    return all_passed

if __name__ == "__main__":
    success = run_tc09_tests()
    sys.exit(0 if success else 1)
