"""
Teste Automatizado Playwright:
Autenticação e Criação de Contas do Projeto Aprovação (com Supabase)
"""

import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8095"

def run_auth_tests():
    print("=" * 70)
    print("🚀 TESTE E2E: AUTENTICAÇÃO E CRIAÇÃO DE CONTAS - PROJETO APROVAÇÃO")
    print("=" * 70)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # 1. Carregar a aplicação
        print("\n[PASSO 1] Acessando aplicação e verificando marca 'Projeto Aprovação'...")
        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(1000)
            brand_text = page.locator(".brand-title").inner_text()
            assert "Projeto Aprovação" in brand_text, f"Marca inesperada: {brand_text}"
            print(f"  ✅ Marca verificada no topo: '{brand_text.replace(chr(10), ' ')}'")
            results.append(("1. Identidade Visual Projeto Aprovação", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("1. Identidade Visual Projeto Aprovação", f"FAIL: {e}"))

        # 2. Abrir Modal de Autenticação pelo Topbar
        print("\n[PASSO 2] Abrindo tela de Login / Criação de Contas...")
        try:
            auth_modal = page.locator("#modalAuthOverlay")
            if not auth_modal.is_visible():
                auth_badge = page.locator("#userAuthBadge")
                auth_badge.click()
                page.wait_for_timeout(500)

            page.wait_for_selector("#modalAuthOverlay", state="visible", timeout=5000)
            assert auth_modal.is_visible(), "Modal de autenticação não abriu!"
            modal_title = auth_modal.locator("h2").inner_text()
            assert "Projeto Aprovação" in modal_title, f"Título do modal incorreto: {modal_title}"
            print(f"  ✅ Modal aberto com sucesso! Título: '{modal_title}'")
            results.append(("2. Abertura do Modal de Autenticação", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("2. Abertura do Modal de Autenticação", f"FAIL: {e}"))

        # 3. Testar Alternância para 'Criar Nova Conta' e cadastrar novo aluno
        print("\n[PASSO 3] Criando nova conta de estudante no Supabase...")
        try:
            page.locator("#authTabRegister").click()
            page.wait_for_timeout(400)

            # Preencher campos de cadastro
            test_ts = int(time.time())
            test_name = f"Aluno Teste {test_ts % 1000}"
            test_email = f"aluno_{test_ts}@aprovacao.com.br"
            test_pass = "Aprovado2026!"

            page.fill("#authRegName", test_name)
            page.fill("#authRegEmail", test_email)
            page.fill("#authRegPassword", test_pass)
            page.fill("#authRegConfirm", test_pass)

            # Submeter cadastro
            page.locator("#btnSubmitRegister").click()
            page.wait_for_timeout(1500)

            # Verificar se logou e atualizou a barra superior
            user_text = page.locator("#userAuthText").inner_text()
            print(f"  Badge de usuário após cadastro: '{user_text}'")
            assert "Sair" in user_text, f"Usuário não foi autenticado após cadastro: {user_text}"
            print(f"  ✅ Nova conta '{test_email}' cadastrada e autenticada com sucesso!")
            results.append(("3. Criação de Nova Conta & Sync Supabase", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("3. Criação de Nova Conta & Sync Supabase", f"FAIL: {e}"))

        # 4. Testar Logout
        print("\n[PASSO 4] Testando encerramento de sessão (Logout)...")
        try:
            page.wait_for_timeout(500)
            page.evaluate("logoutUser()")
            page.wait_for_timeout(600)
            auth_modal = page.locator("#modalAuthOverlay")
            page.wait_for_selector("#modalAuthOverlay", state="visible", timeout=5000)
            user_text = page.locator("#userAuthText").inner_text()
            assert user_text == "Entrar", f"Texto do botão inesperado após logout: {user_text}"
            assert auth_modal.is_visible(), "Modal não reabriu após logout!"
            print("  ✅ Logout efetuado e tela de login reexibida!")
            results.append(("4. Logout e Reabertura do Modal", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("4. Logout e Reabertura do Modal", f"FAIL: {e}"))

        # 5. Testar Login com a conta henriquerosa2019
        print("\n[PASSO 5] Testando login com a conta 'henriquerosa2019'...")
        try:
            page.wait_for_selector("#authLoginUser", state="visible", timeout=5000)
            page.fill("#authLoginUser", "henriquerosa2019")
            page.fill("#authLoginPassword", "123456")
            page.locator("#btnSubmitLogin").click()
            page.wait_for_timeout(1200)

            user_text = page.locator("#userAuthText").inner_text()
            print(f"  Badge após login henriquerosa2019: '{user_text}'")
            assert "Henrique" in user_text, f"Nome do usuário não exibido: {user_text}"
            print("  ✅ Login de 'henriquerosa2019' realizado com 100% de sucesso!")
            results.append(("5. Login de Usuário (henriquerosa2019)", "PASS"))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append(("5. Login de Usuário (henriquerosa2019)", f"FAIL: {e}"))

        browser.close()

    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES DE AUTENTICAÇÃO - PROJETO APROVAÇÃO")
    print("=" * 70)
    all_passed = True
    for name, status in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f" {icon} {name:<50} [{status}]")
        if status != "PASS":
            all_passed = False
    print("=" * 70)
    if all_passed:
        print("🎉 TODOS OS TESTES DE AUTENTICAÇÃO FORAM CONCLUÍDOS COM SUCESSO!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM.")
    print("=" * 70)

if __name__ == "__main__":
    run_auth_tests()
