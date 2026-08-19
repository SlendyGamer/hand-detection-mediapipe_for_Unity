# GUI de selecao de amplitudes

# hand_selection_gui.py

import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from hand_detection import HandDetection
import os
from pygrabber.dshow_graph import FilterGraph
import cv2

class HandSelectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand-ROM")

        # Variáveis para armazenar os dedos selecionados
        self.finger_selection1 = None
        self.finger_selection2 = None

        # Frozenset de 10 pares para poder guardar todas as combinacoes unicas de pares entre dedos
        self.finger_pairs = []
        self.MAX_PAIRS = 10

        #self.finger1 = None
        #self.finger2 = None

        # Dicionário com posições manuais dos dedos e a localização (x,y) de cada em polegadas
        self.finger_positions = {
            "THUMB_TIP": (80, 148),
            "INDEX_FINGER_TIP": (190, 35),
            "MIDDLE_FINGER_TIP": (241, 30),
            "RING_FINGER_TIP": (276, 53),
            "PINKY_TIP": (310, 115)
        }

        # Nomes para exibição
        self.exibit_names = {
            "THUMB_TIP": "Polegar",
            "INDEX_FINGER_TIP": "Indicador",
            "MIDDLE_FINGER_TIP": "Médio",
            "RING_FINGER_TIP": "Anelar",
            "PINKY_TIP": "Mindinho"
        }

        # Montar gui em 2 colunas, uma para a imagem e outra para os pares
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Esquerda - selecao de pares
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, padx=(0, 15))

        # Carregar imagem dentro do canvas
        base_dir = os.path.dirname(__file__)

        img_path = resource_path(os.path.join("images", "png_hand_transp.png"))
        hand_img = Image.open(img_path).resize((400, 400))
        self.hand_photo = ImageTk.PhotoImage(hand_img)

        self.canvas = tk.Canvas(left_frame, width=400, height=400)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.hand_photo)

        # Criar radio buttons dinamicamente no canvas
        self.radio_buttons = {}
        for name, (x, y) in self.finger_positions.items():
            btn = tk.Radiobutton(self.canvas, text="", value=name, indicatoron=False, width=2, height=1, border=0.5, bg="lightblue", command=lambda n=name: self.select_finger(n))
            self.canvas.create_window(x, y, window=btn)
            self.radio_buttons[name] = btn

        # Label de status
        self.status_label = tk.Label(left_frame, text="Selecione o par de dedos", fg="black")
        self.status_label.pack(pady=5)

        # Seleção da câmera
        camera_frame = tk.Frame(self.root)
        camera_frame.pack(pady=(5, 0))

        tk.Label(
            camera_frame,
            text="Câmera:"
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.camera_var = tk.StringVar()

        self.camera_dropdown = ttk.Combobox(
            camera_frame,
            textvariable=self.camera_var,
            state="readonly",
            width=20
        )

        self.camera_dropdown.pack(side=tk.LEFT)

        self.camera_status_label = tk.Label(
            self.root,
            text="",
            fg="red"
        )

        self.camera_status_label.pack(padx=(10, 0))

        self.camera_devices = self.list_cameras()

        if self.camera_devices:
            self.camera_dropdown["values"] = [
                name for index, name in self.camera_devices
            ]
            self.camera_dropdown.current(0)
        else:
            self.camera_dropdown["values"] = ["Nenhuma câmera encontrada"]
            self.camera_dropdown.current(0)

        # Botão de iniciar
        self.start_btn = tk.Button(self.root, text="Calcular Amplitude", command=self.start_detection, bg="lightblue")
        self.start_btn.pack(pady=10)

        # Direita - pares ja selecionados
        right_frame = tk.Frame(main_frame, bd=1, relief=tk.GROOVE)
        right_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(right_frame, text="Pares selecionados", font=("Arial", 11, "bold")).pack(pady=(8, 5))

        # Frame interno que conterá as linhas de pares
        self.pairs_container = tk.Frame(right_frame)
        self.pairs_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        # Mensagem quando a lista está vazia
        self.empty_label = tk.Label(
            self.pairs_container,
            text="Nenhum par ainda",
            fg="gray"
        )
        self.empty_label.pack()
    def select_finger(self, finger_name):
        # Se já atingiu o limite máximo, avisa e sai
        if len(self.finger_pairs) >= self.MAX_PAIRS:
            self.status_label.config(
                text="Limite de 10 pares atingido!",
                fg="red"
            )
            return

        # Primeiro dedo do par
        if self.finger_selection1 is None:
            self.finger_selection1 = finger_name
            self.status_label.config(text=f"Primeiro dedo: {finger_name}\nSelecione o segundo dedo", fg="black")
            self._update_radio_colors()
            return
        # Segundo dedo do par
        if self.finger_selection2 is None:
            if finger_name == self.finger_selection1:
                return

        self.finger_selection2 = finger_name
        pair = frozenset([self.finger_selection1, self.finger_selection2])

        # Verifica se par ja foi selecionado
        if pair in self.finger_pairs:
            self.status_label.config(text="Este par ja foi selecionado!", fg="orange")
        else:
            self.finger_pairs.append(pair)
            self.status_label.config(text=f"Par adicionado: {self.exibit_names[self.finger_selection1]} ↔ {self.exibit_names[self.finger_selection2]}", fg="green")
            self._refresh_pairs_list()

        # Sempre reseta a seleção temporária após tentar adicionar
        self.finger_selection1 = None
        self.finger_selection2 = None
        self._update_radio_colors()

        # Mensagem para limite de pares atingido
        if len(self.finger_pairs) >= self.MAX_PAIRS:
            self.status_label.config(text="Limite de 10 pares atingido!", fg="red")
        else:
            # Pede selecao do proximo par
            self.root.after(1200, lambda: self.status_label.config(text="Selecione o primeiro dedo do próximo par", fg="black"))

    # Atualiza a cor de fundo dos rádios conforme a seleção temporária
    def _update_radio_colors(self):
        for name, btn in self.radio_buttons.items():
            if name == self.finger_selection1 or name == self.finger_selection2:
                btn.config(bg="green")
            else:
                btn.config(bg="lightblue")

    def list_cameras(self):
        graph = FilterGraph()
        cameras = graph.get_input_devices()

        return list(enumerate(cameras))

    # Método de reconstruir lista visual de pares selecionados
    def _refresh_pairs_list(self):
        for widget in self.pairs_container.winfo_children():
            widget.destroy()

        if not self.finger_pairs:
            self.empty_label = tk.Label(self.pairs_container, text="Nenhum par selecionado", fg="gray")
            self.empty_label.pack()
            return

        for pair in self.finger_pairs:
            fingers = list(pair)

            # Ordena alfabeticamente
            fingers.sort()
            name1 = self.exibit_names[fingers[0]]
            name2 = self.exibit_names[fingers[1]]

            row = tk.Frame(self.pairs_container)
            row.pack(fill=tk.X, pady=2)

            lbl = tk.Label(row, text=f"{name1} ↔ {name2}", width=22, anchor="w")
            lbl.pack(side=tk.LEFT)

            # Botão X para remover
            btn_remove = tk.Button(
                row,
                text="✕",
                fg="red",
                width=2,
                command=lambda p=pair: self.remove_pair(p)
            )
            btn_remove.pack(side=tk.RIGHT)

    # Remove um par da lista e atualiza a interface
    def remove_pair(self, pair):
        if pair in self.finger_pairs:
            self.finger_pairs.remove(pair)
            self._refresh_pairs_list()
            self.status_label.config(
                text="Par removido. Pode selecionar novos pares.",
                fg="black"
            )

    # Método que inicia a tela interativa com o usuário
    def start_detection(self):
        if not self.finger_pairs:
            self.status_label.config(text="Selecione ao menos um par antes de iniciar", fg="red")
            return

        # Converte frozensetr para tupla ordenada
        pairs_list = [tuple(sorted(p)) for p in self.finger_pairs]

        if not self.camera_devices:
            self.camera_status_label.config(
                text="Nenhuma câmera disponível",
                fg="red"
            )
            return

        camera_position = self.camera_dropdown.current()
        camera_index = self.camera_devices[camera_position][0]
        camera_name = self.camera_devices[camera_position][1]
        self.camera_status_label.config(text="")
        try:
            hand_detection = HandDetection(
                pairs=pairs_list,
                camera_index=camera_index
            )

            # Verifica se a câmera realmente conseguiu abrir
            if not hand_detection.cap.isOpened():
                hand_detection.cap.release()

                self.camera_status_label.config(
                    text=f"Não foi possível abrir a câmera:\n{camera_name}",
                    fg="red"
                )
                return

            hand_detection.run()

        except Exception as e:
            self.camera_status_label.config(
                text=f"Erro ao abrir a câmera:\n{camera_name}\n{str(e)}",
                fg="red"
            )

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # criado pelo PyInstaller no onefile
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Apenas para debug
if __name__ == "__main__":
    root = tk.Tk()
    app = HandSelectionGUI(root)
    root.mainloop()