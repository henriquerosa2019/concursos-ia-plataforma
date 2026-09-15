"""
Script de Empacotamento Comercial - Central de Concursos IA
Gera o executável standalone (.exe) portátil para Windows para distribuição comercial.
Adequado para venda em plataformas como Hotmart, Kiwify, Eduzz (R$ 67 a R$ 97).
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")
OUTPUT_FOLDER = os.path.join(DIST_DIR, "Central_Concursos_IA")

def check_pyinstaller():
    try:
        import PyInstaller
        return True
    except ImportError:
        print("[!] PyInstaller nao encontrado.")
        print("[*] Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True

def build_app():
    print("==================================================================")
    print("  EMPACOTAMENTO STANDALONE - CENTRAL DE CONCURSOS PUBLICOS IA")
    print("==================================================================")
    
    check_pyinstaller()
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=ConcursosIA",
        "--onedir",
        "--windowed", # sem janela preta de console para o usuario final
        f"--add-data={os.path.join(BASE_DIR, 'index.html')};.",
        f"--add-data={os.path.join(BASE_DIR, 'config.json')};.",
        "--clean",
        "-y",
        os.path.join(BASE_DIR, "servidor.py")
    ]
    
    print("\n[*] Executando PyInstaller...")
    subprocess.check_call(cmd, cwd=BASE_DIR)
    
    built_dir = os.path.join(DIST_DIR, "ConcursosIA")
    if os.path.exists(built_dir):
        print("\n[*] Copiando packs de disciplinas inclusos...")
        packs = ["Informatica", "Direito_Constitucional", "Direito_Administrativo", "Portugues"]
        for pack in packs:
            src = os.path.join(BASE_DIR, pack)
            dst = os.path.join(built_dir, pack)
            if os.path.exists(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"  + Pack copiado: {pack}")
                
        # Copiar iniciar_app_desktop.bat adaptado
        launcher_src = os.path.join(BASE_DIR, "iniciar_app_desktop.bat")
        if os.path.exists(launcher_src):
            shutil.copy2(launcher_src, built_dir)
            
        print("\n==================================================================")
        print("  SUCESSO! PACOTE COMERCIAL GERADO COM SUCESSO:")
        print(f"  Pasta de distribuicao: {built_dir}")
        print("  Basta compactar em .ZIP para enviar aos alunos!")
        print("==================================================================")

if __name__ == "__main__":
    build_app()
