@echo off
chcp 65001 >nul
title Painel de Estudos IA - Concursos
cd /d "C:\PROJETOS IA\Concursos"
echo ======================================================================
echo   INICIANDO PAINEL DE ESTUDOS PARA CONCURSOS PUBLICOS (IA)
echo ======================================================================
echo.
echo Abrindo servidor local em http://localhost:8095 ...
echo Para encerrar, feche esta janela ou pressione CTRL+C.
echo.
python servidor.py
pause
