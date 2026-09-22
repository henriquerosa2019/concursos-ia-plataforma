@echo off
chcp 65001 >nul
title Estudio de Teste - Video e Momentos da Aula
cd /d "C:\PROJETOS IA\Concursos"
echo ======================================================================
echo   ESTUDIO DE TESTE: VIDEO E MOMENTOS DA AULA (OPCAO B)
echo ======================================================================
echo.
echo Abrindo o Estudio Interativo no navegador...
start http://localhost:8095/estudio_momentos_video.html
echo.
echo Verificando servidor local em http://localhost:8095 ...
netstat -ano | findstr :8095 >nul
if %errorlevel% neq 0 (
    echo Servidor local nao estava ativo. Iniciando servidor...
    python servidor.py
) else (
    echo Servidor ja esta em execucao! Estudio pronto para testes.
)
