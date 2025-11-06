# hand_selection_gui.py

import sys
import tkinter as tk
from PIL import Image, ImageTk
from hand_detection import HandDetection
import os

class HandSelectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand-ROM")

        # Variáveis para armazenar os dedos selecionados
        self.finger1 = None
        self.finger2 = None

        # Dicionário com posições manuais dos dedos e a localização (x,y) de cada em polegadas
        self.finger_positions = {
            "THUMB_TIP": (80, 148),
            "INDEX_FINGER_TIP": (190, 35),
            "MIDDLE_FINGER_TIP": (241, 30),
            "RING_FINGER_TIP": (276, 53),
            "PINKY_TIP": (310, 115)
        }

        # Carregar imagem dentro do canvas
        base_dir = os.path.dirname(__file__)
        
        img_path = resource_path(os.path.join("images", "png_hand_transp.png"))
        hand_img = Image.open(img_path).resize((400, 400))
        self.hand_photo = ImageTk.PhotoImage(hand_img)

        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.hand_photo)

        # Criar radio buttons dinamicamente no canvas
        self.radio_buttons = {}
        for name, (x, y) in self.finger_positions.items():
            btn = tk.Radiobutton(self.canvas, text="", value=name, indicatoron=False,
                                 width=2, height=1, border=0.5, bg="lightblue", command=lambda n=name: self.select_finger(n))
            self.canvas.create_window(x, y, window=btn)
            self.radio_buttons[name] = btn

        # Label de status
        self.status_label = tk.Label(self.root, text="Selecione até dois dedos", fg="black")
        self.status_label.pack(pady=5)

        # Botão de iniciar
        self.start_btn = tk.Button(self.root, text="Calcular Amplitude", command=self.start_detection, bg="lightblue")
        self.start_btn.pack(pady=10)

    def select_finger(self, finger_name):
        if self.finger1 is None:
            self.finger1 = finger_name
            self.status_label.config(text=f"Primeiro dedo: {finger_name}", fg="black")
        elif self.finger2 is None and finger_name != self.finger1:
            self.finger2 = finger_name
            self.status_label.config(text=f"Primeiro dedo: {self.finger1}\n Segundo dedo: {finger_name}", fg="black")
        else:
            # Resetar seleção
            self.finger1 = finger_name
            self.finger2 = None
            self.status_label.config(text=f"Primeiro dedo: {finger_name}")

        # Atualiza visual
        for name, btn in self.radio_buttons.items():
            if name == self.finger1 or name == self.finger2:
                btn.config(bg="green")
            else:
                btn.config(bg="lightblue")

    # Método que inicia a tela interativa com o usuário 
    def start_detection(self):
        if self.finger1 and self.finger2:
            hand_detection = HandDetection(finger1=self.finger1, finger2=self.finger2)
            hand_detection.run()
        else:
            self.status_label.config(text="Selecione dois dedos antes de iniciar", fg="red")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # criado pelo PyInstaller no onefile
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
