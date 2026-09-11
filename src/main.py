# Arquivo que inicia todas as classes e aplicativos

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

    root = Tk()
    gui = HandSelectionGUI(root)
    root.mainloop()
