@echo off
chcp 65001 >nul
title Matriz Visual de Homologacao - Projeto Aprovacao (Miro Board)
cd /d "C:\PROJETOS IA\Concursos"

echo ======================================================================
echo   ABRINDO QUADRO MIRO DE HOMOLOGACAO & TESTES E2E
echo   Projeto Aprovacao - Metodo 4 Pilares de Alta Retencao
echo ======================================================================
echo.
echo Abrindo em http://localhost:8095/matriz-testes ...
echo.

start "" "http://localhost:8095/matriz-testes"
timeout /t 2 >nul
exit
