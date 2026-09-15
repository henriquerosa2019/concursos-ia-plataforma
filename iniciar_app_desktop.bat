@echo off
chcp 65001 >nul
title Central de Concursos IA • Modo Aplicativo Desktop

cd /d "C:\PROJETOS IA\Concursos"

:: Mantém atalhos da Área de Trabalho sempre atualizados
cscript //nologo atualizar_atalhos_desktop.vbs >nul 2>&1

echo ======================================================================
echo    CENTRAL DE CONCURSOS PUBLICOS (IA) - MODO APLICATIVO DESKTOP
echo ======================================================================
echo.
echo [1/2] Iniciando Servidor de Estudos Local na porta 8095...
start /B python servidor.py >nul 2>&1

:: Aguarda 2 segundos para o servidor subir
timeout /t 2 /nobreak >nul

echo [2/2] Abrindo Aplicativo em Janela Nativa...

:: Tenta abrir via Microsoft Edge em Modo Aplicativo Nativo (--app)
set EDGE_PATH="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist %EDGE_PATH% set EDGE_PATH="C:\Program Files\Microsoft\Edge\Application\msedge.exe"

if exist %EDGE_PATH% (
    start "" %EDGE_PATH% --app=http://localhost:8095 --window-size=1380,880 --app-id=ConcursosIA
) else (
    :: Fallback para navegador padrao
    start http://localhost:8095
)

echo.
echo Aplicativo em execucao!
echo Voce ja pode utilizar sua Central de Concursos.
echo Para fechar o servidor, basta encerrar esta janela quando terminar os estudos.
echo.
pause
