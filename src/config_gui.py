import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

DEFAULT_A = 1.405132e-03
DEFAULT_B = -0.486281
DEFAULT_C = 62.507305


def normalize_user(data):
    """Garante que o dict do usuário tenha A, B e C."""
    return {
        "name": data["name"],
        "A": float(data.get("A", DEFAULT_A)),
        "B": float(data.get("B", DEFAULT_B)),
        "C": float(data.get("C", DEFAULT_C)),
    }


def get_globalconfig_dir():
    """data/globalconfig/ — cria se não existir"""
    path = os.path.join(get_base_dir(), "data", "globalconfig")
    os.makedirs(path, exist_ok=True)
    return path


def get_global_config_path():
    return os.path.join(get_globalconfig_dir(), "config.json")


def load_global_config():
    path = get_global_config_path()
    default = {
        "udp_port": 5052,
        "camera_index": 0,          # ← mesma câmera para GUI e calibração
        "unity_exe": "",
    }
    if not os.path.exists(path):
        save_global_config(default)
        return default.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "udp_port" not in data:
            data["udp_port"] = 5052
        if "camera_index" not in data:
            data["camera_index"] = 0
        if "unity_exe" not in data:
            data["unity_exe"] = ""
        return data
    except Exception:
        return default.copy()


def get_unity_exe():
    return load_global_config().get("unity_exe", "") or ""


def save_global_config(data):
    path = get_global_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_udp_port():
    return int(load_global_config().get("udp_port", 5052))


def get_camera_index():
    return int(load_global_config().get("camera_index", 0))


def open_folder_in_explorer(path):
    """Abre a pasta no explorador de arquivos do sistema."""
    path = os.path.abspath(path)
    os.makedirs(path, exist_ok=True)
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        import subprocess
        subprocess.Popen(["open", path])
    else:
        import subprocess
        subprocess.Popen(["xdg-open", path])


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_profiles_root():
    """data/profiles/ — cria se não existir"""
    path = os.path.join(get_base_dir(), "data", "profiles")
    os.makedirs(path, exist_ok=True)
    return path


def get_json_dir():
    """data/profiles/json/ — onde ficam os .json dos usuários"""
    path = os.path.join(get_profiles_root(), "json")
    os.makedirs(path, exist_ok=True)
    return path


def get_userdata_dir():
    """data/profiles/userdata/ — raiz das pastas de gravação"""
    path = os.path.join(get_profiles_root(), "userdata")
    os.makedirs(path, exist_ok=True)
    return path


def get_user_json_path(name):
    """data/profiles/json/<nome>.json"""
    # Remove caracteres inválidos de nome de arquivo
    safe = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
    return os.path.join(get_json_dir(), f"{safe}.json")


def get_user_data_dir(name):
    """
    data/profiles/userdata/<nome>/
    Cria a pasta do usuário se não existir.
    Use este caminho para exportar CSV/XLSX.
    """
    safe = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
    path = os.path.join(get_userdata_dir(), safe)
    os.makedirs(path, exist_ok=True)
    return path


def get_active_path():
    return os.path.join(get_json_dir(), "_active.json")


def load_all_users():
    """Lê todos os .json de usuários (ignora _active.json)."""
    folder = get_json_dir()
    users = []
    for fname in os.listdir(folder):
        if fname.startswith("_") or not fname.endswith(".json"):
            continue
        fpath = os.path.join(folder, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "name" in data and "C" in data:
                    users.append(normalize_user(data))
        except Exception:
            continue
    return users


def load_active_name():
    path = get_active_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("active_user")
    except Exception:
        return None


def save_active_name(name):
    with open(get_active_path(), "w", encoding="utf-8") as f:
        json.dump({"active_user": name}, f, indent=2, ensure_ascii=False)


def save_user(user_dict):
    """Salva/atualiza data/profiles/<nome>.json"""
    path = get_user_json_path(user_dict["name"])
    # garante as três chaves
    data = {
        "name": user_dict["name"],
        "A": float(user_dict.get("A", DEFAULT_A)),
        "B": float(user_dict.get("B", DEFAULT_B)),
        "C": float(user_dict.get("C", DEFAULT_C)),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    get_user_data_dir(user_dict["name"])  # cria pasta userdata


def delete_user_file(name):
    path = get_user_json_path(name)
    if os.path.exists(path):
        os.remove(path)
    # Opcional: apagar também a pasta userdata do usuário
    import shutil
    user_dir = get_user_data_dir(name)
    if os.path.isdir(user_dir):
        shutil.rmtree(user_dir)


def ensure_default_user():
    """Garante que exista pelo menos o usuário Padrao."""
    users = load_all_users()
    if not users:
        default = {"name": "Padrao", "A": DEFAULT_A, "B": DEFAULT_B, "C": DEFAULT_C}
        save_user(default)
        save_active_name("Padrao")
        return [default]
    # Se não houver ativo válido, define o primeiro
    active = load_active_name()
    names = [u["name"] for u in users]
    if active not in names:
        save_active_name(names[0])
    return users


def get_active_user_coeffs():
    """Retorna o C do usuário ativo (usado pelo HandDetection)."""
    users = ensure_default_user()
    active = load_active_name()
    for u in users:
        if u["name"] == active:
            u = normalize_user(u)
            return u["A"], u["B"], u["C"]
    u = normalize_user(users[0])
    return u["A"], u["B"], u["C"]


def get_active_user_data_dir():
    """Atalho: pasta de gravação do usuário ativo."""
    name = load_active_name()
    if not name:
        ensure_default_user()
        name = load_active_name()
    return get_user_data_dir(name)


class UserConfigGUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuração de Usuários")
        self.geometry("520x580")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.users = ensure_default_user()

        tk.Label(self, text="Usuário ativo:", font=("Arial", 10, "bold")).pack(pady=(15, 5))

        self.user_var = tk.StringVar()
        self.combo = ttk.Combobox(self, textvariable=self.user_var, state="readonly", width=30)
        self.combo.pack(pady=5)
        self.combo.bind("<<ComboboxSelected>>", self.on_user_selected)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Novo usuário", width=14, command=self.create_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Apagar usuário", width=14, command=self.delete_user).pack(side=tk.LEFT, padx=5)

        tk.Label(self, text="Coeficientes de calibração:", font=("Arial", 10, "bold")).pack(pady=(12, 4))

        coeffs_frame = tk.Frame(self)
        coeffs_frame.pack(pady=4)

        # A
        col_a = tk.Frame(coeffs_frame)
        col_a.pack(side=tk.LEFT, padx=8)
        tk.Label(col_a, text="A").pack()
        self.a_var = tk.StringVar()
        tk.Entry(col_a, textvariable=self.a_var, width=14, justify="center").pack()

        # B
        col_b = tk.Frame(coeffs_frame)
        col_b.pack(side=tk.LEFT, padx=8)
        tk.Label(col_b, text="B").pack()
        self.b_var = tk.StringVar()
        tk.Entry(col_b, textvariable=self.b_var, width=14, justify="center").pack()

        # C
        col_c = tk.Frame(coeffs_frame)
        col_c.pack(side=tk.LEFT, padx=8)
        tk.Label(col_c, text="C").pack()
        self.c_var = tk.StringVar()
        tk.Entry(col_c, textvariable=self.c_var, width=14, justify="center").pack()

        tk.Button(
            self,
            text="Salvar coeficientes",
            width=20,
            bg="lightgreen",
            command=self.save_current
        ).pack(pady=(8, 4))

        tk.Button(
            self,
            text="📐  Calibrar (atualizar C)",
            width=28,
            bg="#fff3cd",
            command=self.run_user_calibration
        ).pack(pady=(8, 4))

        tk.Button(
            self,
            text="📂  Abrir pasta do usuário",
            width=28,
            command=self.open_user_folder
        ).pack(pady=(12, 4))

        tk.Label(self, text="Porta UDP (global):", font=("Arial", 10, "bold")).pack(pady=(12, 4))

        port_frame = tk.Frame(self)
        port_frame.pack(pady=2)

        tk.Label(self, text="Ambiente Unity:", font=("Arial", 10, "bold")).pack(pady=(12, 4))

        unity_frame = tk.Frame(self)
        unity_frame.pack(pady=2)

        self.unity_path_var = tk.StringVar(value=get_unity_exe())
        tk.Entry(
            unity_frame,
            textvariable=self.unity_path_var,
            width=42,
            state="readonly"
        ).pack(side=tk.TOP, padx=4, pady=2)

        unity_btn_frame = tk.Frame(self)
        unity_btn_frame.pack(pady=4)

        tk.Button(
            unity_btn_frame,
            text="Selecionar .exe",
            width=16,
            command=self.select_unity_exe
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            unity_btn_frame,
            text="Abrir Unity",
            width=16,
            command=self.open_unity_exe
        ).pack(side=tk.LEFT, padx=4)
        
        bottom = tk.Frame(self)
        bottom.pack(pady=20)

        self.port_var = tk.StringVar(value=str(get_udp_port()))
        tk.Entry(port_frame, textvariable=self.port_var, width=10, justify="center").pack(side=tk.LEFT, padx=4)
        tk.Button(port_frame, text="Salvar porta", width=12, command=self.save_port).pack(side=tk.LEFT, padx=4)

        tk.Button(bottom, text="Fechar", width=12, command=self.destroy).pack(padx=8)

        self.refresh_combo()
        self.select_active()

    def select_unity_exe(self):
        path = filedialog.askopenfilename(
            parent=self,
            title="Selecione o executável do Unity",
            filetypes=[("Executável", "*.exe"), ("Todos os arquivos", "*.*")]
        )
        if not path:
            return

        path = os.path.abspath(path)
        cfg = load_global_config()
        cfg["unity_exe"] = path
        save_global_config(cfg)

        self.unity_path_var.set(path)
        messagebox.showinfo(
            "Salvo",
            f"Caminho do Unity salvo:\n{path}\n\n"
            f"Arquivo: data/globalconfig/config.json",
            parent=self
        )

    def open_unity_exe(self):
        path = get_unity_exe()
        if not path or not os.path.isfile(path):
            messagebox.showwarning(
                "Aviso",
                "Nenhum executável Unity válido configurado.\n"
                "Clique em 'Selecionar .exe' primeiro.",
                parent=self
            )
            return

        try:
            import subprocess
            # Abre sem bloquear a GUI
            subprocess.Popen([path], cwd=os.path.dirname(path))
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir o Unity:\n{e}",
                parent=self
            )

    def run_user_calibration(self):
        name = self.user_var.get()
        if not name:
            messagebox.showwarning("Aviso", "Selecione um usuário primeiro.", parent=self)
            return

        # Avisa o usuário
        ok = messagebox.askokcancel(
            "Calibração",
            "A janela de calibração será aberta.\n\n"
            "Posicione a mão nas distâncias indicadas e pressione 's' para salvar cada ponto.\n"
            "Pressione 'q' para cancelar.\n\n"
            "Ao terminar, o coeficiente C deste usuário será atualizado.",
            parent=self
        )
        if not ok:
            return

        # Esconde a janela de config enquanto calibra (opcional, evita conflito de foco)
        self.withdraw()
        self.update()

        try:
            from calibrar import run_calibration
            result = run_calibration()
        except Exception as e:
            self.deiconify()
            messagebox.showerror("Erro", f"Falha na calibração:\n{e}", parent=self)
            return

        self.deiconify()
        self.lift()
        self.focus_force()

        if result is None:
            messagebox.showwarning(
                "Calibração incompleta",
                "Não foi possível calcular os coeficientes.\n"
                "É necessário pelo menos 3 pontos.",
                parent=self
            )
            return

        A, B, C = result
        # Atualiza o campo na tela
        self.a_var.set(f"{A:.8f}")
        self.b_var.set(f"{B:.6f}")
        self.c_var.set(f"{C:.6f}")

        save_user({
            "name": name,
            "A": float(A),
            "B": float(B),
            "C": float(C),
        })
        save_active_name(name)
        self.refresh_combo()

        messagebox.showinfo(
            "Calibração salva",
            f"Usuário: {name}\n"
            f"A = {A:.6e}\n"
            f"B = {B:.6f}\n"
            f"C = {C:.6f}\n\n"
            f"Salvo em data/profiles/json/{name}.json",
            parent=self
        )

    def open_user_folder(self):
        name = self.user_var.get()
        if not name:
            messagebox.showwarning("Aviso", "Selecione um usuário primeiro.", parent=self)
            return
        folder = get_user_data_dir(name)
        open_folder_in_explorer(folder)

    def save_port(self):
        try:
            port = int(self.port_var.get().strip())
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Porta deve ser um número entre 1 e 65535.", parent=self)
            return

        cfg = load_global_config()
        cfg["udp_port"] = port
        save_global_config(cfg)
        messagebox.showinfo(
            "Salvo",
            f"Porta UDP definida para {port}.\nArquivo: data/globalconfig/config.json",
            parent=self
        )

    def refresh_combo(self):
        self.users = load_all_users()
        names = [u["name"] for u in self.users]
        self.combo["values"] = names

    def select_active(self):
        active = load_active_name()
        if active and active in self.combo["values"]:
            self.user_var.set(active)
        elif self.combo["values"]:
            self.user_var.set(self.combo["values"][0])
        self.on_user_selected()

    def on_user_selected(self, event=None):
        name = self.user_var.get()
        for u in self.users:
            if u["name"] == name:
                u = normalize_user(u)
                self.a_var.set(str(u["A"]))
                self.b_var.set(str(u["B"]))
                self.c_var.set(str(u["C"]))
                save_active_name(name)
                return

        # fallback se não achou
        self.a_var.set(str(DEFAULT_A))
        self.b_var.set(str(DEFAULT_B))
        self.c_var.set(str(DEFAULT_C))

    def create_user(self):
        name = simpledialog.askstring("Novo usuário", "Nome do usuário:", parent=self)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if any(u["name"] == name for u in self.users):
            messagebox.showwarning("Aviso", "Já existe um usuário com esse nome.", parent=self)
            return

        user = {
            "name": name,
            "A": DEFAULT_A,
            "B": DEFAULT_B,
            "C": DEFAULT_C,
        }
        save_user(user)
        save_active_name(name)
        self.refresh_combo()
        self.user_var.set(name)
        self.a_var.set(str(DEFAULT_A))
        self.b_var.set(str(DEFAULT_B))
        self.c_var.set(str(DEFAULT_C))

        messagebox.showinfo(
            "Sucesso",
            f"Usuário '{name}' criado.\nArquivo: data/profiles/json/{name}.json",
            parent=self
        )

    def delete_user(self):
        name = self.user_var.get()
        if not name:
            return
        if len(self.users) <= 1:
            messagebox.showwarning("Aviso", "Não é possível apagar o último usuário.", parent=self)
            return
        if not messagebox.askyesno("Confirmar", f"Apagar o usuário '{name}'?", parent=self):
            return

        delete_user_file(name)
        remaining = load_all_users()
        save_active_name(remaining[0]["name"])
        self.refresh_combo()
        self.select_active()
        messagebox.showinfo("Sucesso", f"Usuário '{name}' removido.", parent=self)

    def save_current(self):
        name = self.user_var.get()
        if not name:
            return
        try:
            a_value = float(self.a_var.get().replace(",", "."))
            b_value = float(self.b_var.get().replace(",", "."))
            c_value = float(self.c_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror(
                "Erro",
                "A, B e C devem ser números válidos.",
                parent=self
            )
            return  # ← obrigatório

        save_user({
            "name": name,
            "A": a_value,
            "B": b_value,
            "C": c_value,
        })
        save_active_name(name)
        self.refresh_combo()

        messagebox.showinfo(
            "Salvo",
            f"Perfil de '{name}' atualizado.\n"
            f"A = {a_value}\nB = {b_value}\nC = {c_value}",
            parent=self
        )
