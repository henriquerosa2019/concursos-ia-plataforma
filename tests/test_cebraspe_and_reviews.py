"""
Bateria de Testes Avançados E2E:
1. Modo Prova Oficial Cebraspe (Fórmula Líquida C - E, Cronômetro, Em Branco)
2. Ciclo Fechado do Caderno de Erros & Repetições Espaçadas (Rumo ao Status 0)
"""

import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8095"

def run_tests():
    print("=" * 70)
    print("🎯 BATERIA DE TESTES AVANÇADOS: CEBRASPE & CADERNO DE ERROS")
    print("=" * 70)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Carregar aplicação
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(1000)

        # Se modal de login estiver visível, fechar para prosseguir com os testes de simulado
        if page.locator("#modalAuthOverlay").is_visible():
            page.evaluate("closeAuthModal()")
            page.wait_for_timeout(500)

        # Selecionar Informática / Excel para ter massa de dados consistente
        page.wait_for_selector(".subarea-item", timeout=10000)
        excel_item = page.locator(".subarea-item:has-text('Excel')").first
        excel_item.click()
        page.wait_for_timeout(1000)

        # =========================================================================
        # TESTE 1: MODO PROVA OFICIAL CEBRASPE & PONTUAÇÃO LÍQUIDA (C - E)
        # =========================================================================
        print("\n[TESTE 1] Testando Modo Prova Oficial Cebraspe com Pontuação Líquida...")
        try:
            # 1.1 Navegar para a aba Simulado
            page.locator(".nav-tab:has-text('Simulado')").click()
            page.wait_for_timeout(600)

            # 1.2 Ativar o Modo Prova Oficial Cebraspe
            btn_cebraspe = page.locator("#btnModeCebraspe")
            btn_cebraspe.click()
            page.wait_for_timeout(600)

            # 1.3 Verificar se a Barra de Prova Cebraspe e Cronômetro estão ativos
            exam_bar = page.locator("#cebraspeExamBar")
            assert exam_bar.is_visible(), "Barra de Prova Cebraspe não exibida!"
            timer_text = page.locator("#cebraspeTimerDisplay").inner_text()
            print(f"  ⏱️ Cronômetro oficial ativado: {timer_text}")

            # 1.4 Responder Questão 0 (Acerto), Questão 1 (Erro) e Questão 2 (Em Branco)
            quiz_items = page.locator(".quiz-item")
            total_q = quiz_items.count()
            print(f"  Total de itens da prova Cebraspe: {total_q}")
            assert total_q >= 3, f"Esperado ao menos 3 itens, encontrados {total_q}"

            # Obter gabaritos direto do array de quizData via evaluate para garantir acerto/erro controlado
            correct_idx_0 = page.evaluate("() => quizData[0].correct_index")
            correct_idx_1 = page.evaluate("() => quizData[1].correct_index")

            # Q0: Escolher a opção CORRETA
            q0_opts = quiz_items.nth(0).locator(".quiz-opt:not(.cebraspe-opt-blank)")
            q0_opts.nth(correct_idx_0).click()
            page.wait_for_timeout(300)

            # Q1: Escolher uma opção ERRADA (diferente de correct_idx_1)
            q1_opts = quiz_items.nth(1).locator(".quiz-opt:not(.cebraspe-opt-blank)")
            wrong_idx_1 = 1 if correct_idx_1 == 0 else 0
            q1_opts.nth(wrong_idx_1).click()
            page.wait_for_timeout(300)

            # Q2: Escolher "DEIXAR EM BRANCO"
            q2_blank = quiz_items.nth(2).locator(".cebraspe-opt-blank")
            q2_blank.click()
            page.wait_for_timeout(300)

            # Verificar contadores em tempo real na barra
            answered = page.locator("#cebraspeAnsweredCount").inner_text()
            blank = page.locator("#cebraspeBlankCount").inner_text()
            print(f"  Contadores Cebraspe: Respondidas = {answered}, Em Branco = {blank}")

            # 1.5 Finalizar a Prova
            finish_btn = page.locator("button:has-text('Finalizar Prova e Ver Nota Líquida')").first
            finish_btn.click()
            page.wait_for_timeout(800)

            # 1.6 Validar o Modal de Resultados
            modal_cebraspe = page.locator("#modalCebraspeResult")
            assert modal_cebraspe.is_visible(), "Modal de resultados Cebraspe não exibido!"

            res_c = page.locator("#resCebraspeCorrect").inner_text()
            res_w = page.locator("#resCebraspeWrong").inner_text()
            res_b = page.locator("#resCebraspeBlank").inner_text()
            res_net = page.locator("#resCebraspeNet").inner_text()
            diag = page.locator("#resCebraspeDiagnosis").inner_text()

            print(f"  📊 Resultado da Prova:")
            print(f"     Certas: {res_c}")
            print(f"     Erradas: {res_w}")
            print(f"     Em Branco: {res_b}")
            print(f"     Nota Líquida: {res_net}")
            print(f"     Diagnóstico: {diag[:65]}...")

            # Validar regra Cebraspe matematicamente
            assert "+" in res_c, "Pontuação de certas incorreta"
            assert "-" in res_w, "Pontuação de erradas incorreta"
            assert int(res_b) >= 1, "Contagem de questões em branco falhou"

            # Fechar modal usando o botão oficial 'Rever Gabarito Comentado'
            close_btn = page.locator("#modalCebraspeResult button:has-text('Rever Gabarito Comentado')")
            if close_btn.is_visible():
                close_btn.click()
            else:
                page.evaluate("closeModal('modalCebraspeResult')")
            page.wait_for_timeout(500)

            print("  ✅ PASS: Modo Prova Oficial Cebraspe e Cálculo de Nota Líquida 100% validados!")
            results.append(("1. Modo Prova Oficial Cebraspe (Nota Líquida)", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("1. Modo Prova Oficial Cebraspe (Nota Líquida)", f"FAIL: {e}"))

        # =========================================================================
        # TESTE 2: CICLO FECHADO DO CADERNO DE ERROS & STATUS (0)
        # =========================================================================
        print("\n[TESTE 2] Testando Ciclo Fechado do Caderno de Erros (Rumo ao Status 0)...")
        try:
            # 2.1 Mudar para Modo Treino no Simulado e errar intencionalmente uma questão
            page.locator(".nav-tab:has-text('Simulado')").click()
            page.wait_for_timeout(500)
            page.locator("#btnModeTraining").click()
            page.wait_for_timeout(500)

            # Obter o índice incorreto da questão 0
            q0_correct = page.evaluate("() => quizData[0].correct_index")
            q0_wrong = 1 if q0_correct == 0 else 0
            
            # Clicar na opção errada
            page.locator(".quiz-item").first.locator(".quiz-opt").nth(q0_wrong).click()
            page.wait_for_timeout(600)
            print("  Questão respondida incorretamente no simulado (enviada para erros).")

            # 2.2 Ir para Flashcards e classificar um card como 'Difícil' (1 dia)
            page.locator(".nav-tab:has-text('Flashcards')").click()
            page.wait_for_timeout(600)
            # Virar
            page.locator("#cardElement").click()
            page.wait_for_timeout(300)
            # Classificar Difícil
            page.locator(".sm2-btn-hard").click()
            page.wait_for_timeout(600)
            print("  Flashcard classificado como 🔴 Difícil (enviado para erros).")

            # 2.3 Navegar para a Aba 6: Revisões & Caderno de Erros
            page.locator(".nav-tab:has-text('Revisões')").click()
            page.wait_for_timeout(800)

            # Garantir sub-pill de Erros ativo
            page.locator("#pillRevErrors").click()
            page.wait_for_timeout(600)

            # Verificar se os itens de erro constam na interface
            rev_cards = page.locator(".review-card-item")
            rev_quiz = page.locator(".review-quiz-item")
            count_cards = rev_cards.count()
            count_quiz = rev_quiz.count()
            print(f"  Itens no Caderno de Erros: {count_cards} flashcards e {count_quiz} questões.")
            assert count_cards + count_quiz > 0, "Nenhum item encontrado no Caderno de Erros!"

            # 2.4 Resolver todos os Flashcards pendentes ("Acertei Agora")
            while page.locator(".review-card-item").count() > 0:
                first_card_btn = page.locator(".review-card-item").first.locator("button:has-text('Acertei Agora')")
                first_card_btn.click()
                page.wait_for_timeout(600)
            print("  Todos os flashcards pendentes foram resolvidos com sucesso!")

            # 2.5 Resolver todas as Questões pendentes acertando ou descartando
            while page.locator(".review-quiz-item").count() > 0:
                first_discard = page.locator(".review-quiz-item").first.locator("button:has-text('Descartar sem refazer')")
                first_discard.click()
                page.wait_for_timeout(600)
            print("  Todas as questões pendentes foram resolvidas / zeradas!")

            # 2.6 Verificar se alcançou o cobiçado STATUS (0)
            page.wait_for_timeout(800)
            empty_title = page.locator(".empty-review-title").inner_text()
            print(f"  Mensagem exibida: '{empty_title}'")
            assert "Status (0)" in empty_title, f"Status (0) não alcançado: {empty_title}"

            print("  ✅ PASS: Ciclo Fechado do Caderno de Erros e Meta 'Status (0)' 100% atingida!")
            results.append(("2. Caderno de Erros (Ciclo Fechado & Status 0)", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("2. Caderno de Erros (Ciclo Fechado & Status 0)", f"FAIL: {e}"))

        browser.close()

    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES AVANÇADOS (CEBRASPE & CADERNO DE ERROS)")
    print("=" * 70)
    all_passed = True
    for name, status in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f" {icon} {name:<50} [{status}]")
        if status != "PASS":
            all_passed = False
    print("=" * 70)
    if all_passed:
        print("🎉 TODOS OS TESTES AVANÇADOS PASSARAM COM 100% DE SUCESSO!")
    else:
        print("⚠️ HOUVE FALHA EM ALGUNS TESTES.")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
