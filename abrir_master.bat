@echo off
chcp 65001 >nul
title Painel Master • Centro de Comando do Projeto Aprovacao
cd /d "C:\PROJETOS IA\Concursos"
echo ======================================================================
echo   PROJETO APROVACAO - ACESSO PRIVILEGIADO DA CONTA MASTER
echo ======================================================================
echo.
echo Abrindo Centro de Comando Master em http://localhost:8095/index.html?admin=master ...
echo.

start "" "http://localhost:8095/index.html?admin=master"
python servidor.py
pause
