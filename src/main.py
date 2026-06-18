from tkinter import Tk
from hand_detection_gui import HandSelectionGUI
import sys
import os
import subprocess

# Adiciona a pasta src no sys.path, para garantir que modules internos sejam encontrados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Diretório atual (onde está este arquivo)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Sobe até a raiz do projeto Unity
    unity_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

    # Caminho para o executável
    exe_path = os.path.join(unity_root, "HandTrackingAR.exe")

    if os.path.isfile(exe_path):
        print(f"Iniciando {exe_path}...")
        subprocess.Popen([exe_path])
    else:
        print(f"WARNING: '{exe_path}' não encontrado. Continuando sem abrir o Unity.")

    root = Tk()
    gui = HandSelectionGUI(root)
    root.mainloop()
