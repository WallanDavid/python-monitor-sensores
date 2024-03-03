import tkinter as tk
from tkinter import ttk, messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class SensorMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Sensores")

        self.users = [{"username": "admin", "password": "admin"}]
        self.current_user = None  # Armazena o usuário autenticado

        # Adiciona uma barra de menu
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Menu "Arquivo"
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Arquivo", menu=self.file_menu)
        self.file_menu.add_command(label="Exportar Dados", command=self.export_data)

        # Menu "Usuário"
        self.user_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Usuário", menu=self.user_menu)
        self.user_menu.add_command(label="Login", command=self.show_login_window)
        self.user_menu.add_command(label="Logout", command=self.logout_user)
        self.user_menu.entryconfig("Logout", state=tk.DISABLED)  # Inicia desativado

        self.temperatura_label = ttk.Label(root, text="Temperatura:")
        self.temperatura_label.grid(row=0, column=0, padx=10, pady=5)

        self.temperatura_value = ttk.Label(root, text="")
        self.temperatura_value.grid(row=0, column=1, padx=10, pady=5)

        self.umidade_label = ttk.Label(root, text="Umidade:")
        self.umidade_label.grid(row=1, column=0, padx=10, pady=5)

        self.umidade_value = ttk.Label(root, text="")
        self.umidade_value.grid(row=1, column=1, padx=10, pady=5)

        self.pressao_label = ttk.Label(root, text="Pressão Atmosférica:")
        self.pressao_label.grid(row=2, column=0, padx=10, pady=5)

        self.pressao_value = ttk.Label(root, text="")
        self.pressao_value.grid(row=2, column=1, padx=10, pady=5)

        self.luminosidade_label = ttk.Label(root, text="Luminosidade:")
        self.luminosidade_label.grid(row=3, column=0, padx=10, pady=5)

        self.luminosidade_value = ttk.Label(root, text="")
        self.luminosidade_value.grid(row=3, column=1, padx=10, pady=5)

        self.start_button = ttk.Button(root, text="Iniciar Monitoramento", command=self.start_monitoring)
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.export_button = ttk.Button(root, text="Exportar Dados", command=self.export_data)
        self.export_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.update_frequency_var = tk.StringVar()
        self.update_frequency_var.set("1000")
        self.update_frequency_entry = ttk.Entry(root, textvariable=self.update_frequency_var)
        self.update_frequency_label = ttk.Label(root, text="Frequência de Atualização (ms):")
        self.update_frequency_label.grid(row=6, column=0, padx=10, pady=5)
        self.update_frequency_entry.grid(row=6, column=1, padx=10, pady=5)

        self.login_button = ttk.Button(root, text="Login", command=self.show_login_window)
        self.login_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.register_button = ttk.Button(root, text="Cadastrar", command=self.register_user)
        self.register_button.grid(row=8, column=0, columnspan=2, pady=10)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=2, rowspan=8, padx=10, pady=10)

        self.data = {"temperatura": [], "umidade": [], "pressao": [], "luminosidade": []}
        self.data_storage = {"temperatura": [], "umidade": [], "pressao": [], "luminosidade": []}
        self.is_monitoring = False
        self.notification_threshold = 28.0

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.login_window = None

    def show_login_window(self):
        # Evita a abertura de várias janelas de login simultaneamente
        if self.login_window and self.login_window.winfo_exists():
            return

        # Janela de login
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")

        ttk.Label(self.login_window, text="Usuário:").grid(row=0, column=0, padx=10, pady=5)
        username_entry = ttk.Entry(self.login_window, textvariable=self.username_var)
        username_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.login_window, text="Senha:").grid(row=1, column=0, padx=10, pady=5)
        password_entry = ttk.Entry(self.login_window, textvariable=self.password_var, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        login_button = ttk.Button(self.login_window, text="Login", command=self.authenticate_user)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def authenticate_user(self):
        username = self.username_var.get()
        password = self.password_var.get()

        # Verifica se o usuário e a senha correspondem a um usuário existente
        user_exists = any(user["username"] == username and user["password"] == password for user in self.users)

        if user_exists:
            self.current_user = username
            messagebox.showinfo("Login bem-sucedido", f"Bem-vindo, {username}!")
            self.user_menu.entryconfig("Login", state=tk.DISABLED)  # Desativa o item de menu "Login"
            self.user_menu.entryconfig("Logout", state=tk.NORMAL)  # Ativa o item de menu "Logout"
        else:
            messagebox.showerror("Erro de Login", "Usuário ou senha incorretos!")

        self.login_window.destroy()

    def logout_user(self):
        self.current_user = None
        messagebox.showinfo("Logout", "Usuário desconectado com sucesso!")
        self.user_menu.entryconfig("Login", state=tk.NORMAL)  # Ativa o item de menu "Login"
        self.user_menu.entryconfig("Logout", state=tk.DISABLED)  # Desativa o item de menu "Logout"

    def update_values(self):
        if self.is_monitoring:
            temperatura = random.uniform(20, 30)
            umidade = random.uniform(40, 70)
            pressao = random.uniform(980, 1020)
            luminosidade = random.uniform(0, 100)

            self.temperatura_value.config(text=f"{temperatura:.2f} °C")
            self.umidade_value.config(text=f"{umidade:.2f} %")
            self.pressao_value.config(text=f"{pressao:.2f} hPa")
            self.luminosidade_value.config(text=f"{luminosidade:.2f} lux")

            self.data["temperatura"].append(temperatura)
            self.data["umidade"].append(umidade)
            self.data["pressao"].append(pressao)
            self.data["luminosidade"].append(luminosidade)

            self.data_storage["temperatura"].append(temperatura)
            self.data_storage["umidade"].append(umidade)
            self.data_storage["pressao"].append(pressao)
            self.data_storage["luminosidade"].append(luminosidade)

            self.check_threshold()
            self.plot_data()

            self.root.after(int(self.update_frequency_var.get()), self.update_values)

    def start_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.start_button.config(text="Parar Monitoramento")
            self.update_values()
        else:
            self.is_monitoring = False
            self.start_button.config(text="Iniciar Monitoramento")

    def plot_data(self):
        self.ax.clear()
        self.ax.plot(np.arange(len(self.data["temperatura"])), self.data["temperatura"], label="Temperatura")
        self.ax.plot(np.arange(len(self.data["umidade"])), self.data["umidade"], label="Umidade")
        self.ax.plot(np.arange(len(self.data["pressao"])), self.data["pressao"], label="Pressão Atmosférica")
        self.ax.plot(np.arange(len(self.data["luminosidade"])), self.data["luminosidade"], label="Luminosidade")

        self.ax.set_xlabel("Tempo")
        self.ax.set_ylabel("Valores")
        self.ax.legend()

        self.canvas.draw()

    def check_threshold(self):
        if self.data["temperatura"] and self.data["temperatura"][-1] > self.notification_threshold:
            messagebox.showwarning("Aviso de Temperatura", f"A temperatura ultrapassou {self.notification_threshold} °C!")

    def export_data(self):
        with open("dados_exportados.csv", "w") as file:
            file.write("Temperatura,Umidade,Pressao,Luminosidade\n")
            for i in range(len(self.data_storage["temperatura"])):
                file.write(f"{self.data_storage['temperatura'][i]},{self.data_storage['umidade'][i]},"
                           f"{self.data_storage['pressao'][i]},{self.data_storage['luminosidade'][i]}\n")

    def register_user(self):
        # Janela de cadastro
        register_window = tk.Toplevel(self.root)
        register_window.title("Cadastro de Usuário")

        # Campos de entrada para o cadastro
        ttk.Label(register_window, text="Novo Usuário:").grid(row=0, column=0, padx=10, pady=5)
        new_username_entry = ttk.Entry(register_window, textvariable=tk.StringVar())
        new_username_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(register_window, text="Nova Senha:").grid(row=1, column=0, padx=10, pady=5)
        new_password_entry = ttk.Entry(register_window, textvariable=tk.StringVar(), show="*")
        new_password_entry.grid(row=1, column=1, padx=10, pady=5)

        # Botão para confirmar o cadastro
        register_button = ttk.Button(register_window, text="Cadastrar", command=lambda: self.add_user(
            new_username_entry.get(), new_password_entry.get(), register_window))
        register_button.grid(row=2, column=0, columnspan=2, pady=10)

    def add_user(self, username, password, register_window):
        # Adiciona o novo usuário à lista temporária
        self.users.append({"username": username, "password": password})
        messagebox.showinfo("Cadastro bem-sucedido", "Usuário cadastrado com sucesso!")
        register_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorMonitor(root)
    root.mainloop()
