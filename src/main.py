from tkinter import Tk
from hand_detection_gui import HandSelectionGUI
import sys
import os
import subprocess

# Adiciona a pasta src no sys.path, para garantir que modules internos sejam encontrados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Pega o diretório do próprio executável, onde quer que ele esteja
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Executando de: {current_dir}")

    # Sobe até a raiz do projeto Unity
    unity_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
    output_dir = os.path.join(unity_root, "output")
    print(f"Procurando executavel do Unity em: {output_dir}")
    exe_path = None

    if os.path.isdir(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith(".exe"):
                exe_path = os.path.join(output_dir, f)
                break

    if exe_path and os.path.isfile(exe_path):
        print(f"Iniciando {exe_path}...")
        subprocess.Popen([exe_path])
    else:
        print(f"WARNING: Nenhum .exe encontrado em '{output_dir}'. Continuando sem abrir o Unity.")

    root = Tk()
    gui = HandSelectionGUI(root)
    root.mainloop()
