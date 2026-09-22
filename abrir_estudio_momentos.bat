@echo off
chcp 65001 >nul
title Estudio de Teste - Video e Momentos da Aula
cd /d "C:\PROJETOS IA\Concursos"

echo ======================================================================
echo   ESTUDIO DE TESTE: VIDEO E MOMENTOS DA AULA
echo ======================================================================
echo.

:: Verificar se o servidor na porta 8095 ja esta respondendo
netstat -ano | findstr :8095 | findstr LISTENING >nul
if %errorlevel% neq 0 (
    echo [1/2] Iniciando servidor local em segundo plano...
    start /min "Servidor Concursos IA" python servidor.py
    echo [2/2] Aguardando inicializacao do servidor...
    timeout /t 2 /nobreak >nul
) else (
    echo Servidor local ja esta ativo na porta 8095!
)

echo.
echo Abrindo o Estudio no navegador (URL oficial HTTP)...
start http://localhost:8095/estudio_momentos_video.html
echo.
echo Pronto! Você pode manter esta janela aberta ou minimizada.
timeout /t 3 /nobreak >nul
exit
