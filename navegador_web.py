import tkinter as tk
from tkinter import messagebox

class NavegadorWeb:
    def __init__(self, root):
        self.root = root
        self.root.title("Navegador Web")
        self.root.geometry("450x420")
        self.root.config(bg="#f0f2f5")

        self.pila_atras = []
        self.pila_adelante = []
        self.pagina_actual = "about:blank"
        self.CAPACIDAD_MAXIMA = 4

        self.armar_interfaz()
        self.actualizar_info()

    def armar_interfaz(self):
        titulo = tk.Label(self.root, text="Navegador Web - Pilas", font=("Arial", 14, "bold"), bg="#f0f2f5", fg="#222")
        titulo.pack(pady=10)

        f_url = tk.Frame(self.root, bg="#f0f2f5")
        f_url.pack(pady=5, fill=tk.X, padx=20)

        lbl = tk.Label(f_url, text="URL:", font=("Arial", 10, "bold"), bg="#f0f2f5")
        lbl.pack(side=tk.LEFT, padx=5)

        self.txt_url = tk.Entry(f_url, font=("Arial", 11), width=25)
        self.txt_url.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.txt_url.insert(0, "https://")

        btn_vis = tk.Button(f_url, text="Visitar", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", command=self.visitar)
        btn_vis.pack(side=tk.LEFT, padx=5)

        f_botones = tk.Frame(self.root, bg="#f0f2f5")
        f_botones.pack(pady=10)

        self.btn_b = tk.Button(f_botones, text="Atrás", font=("Arial", 10), width=12, command=self.back)
        self.btn_b.grid(row=0, column=0, padx=10)

        self.btn_f = tk.Button(f_botones, text="Adelante", font=("Arial", 10), width=12, command=self.forward)
        self.btn_f.grid(row=0, column=1, padx=10)

        f_estado = tk.LabelFrame(self.root, text=" Estado ", font=("Arial", 10, "bold"), bg="#f0f2f5", fg="#444")
        f_estado.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.l_act = tk.Label(f_estado, text="estas en: about:blank", font=("Arial", 11, "bold"), bg="#f0f2f5", fg="#1a73e8", anchor="w")
        self.l_act.pack(fill=tk.X, padx=10, pady=5)

        self.l_atr = tk.Label(f_estado, text="pila atras: []", font=("Arial", 9), bg="#f0f2f5", anchor="w")
        self.l_atr.pack(fill=tk.X, padx=10, pady=2)

        self.l_ade = tk.Label(f_estado, text="pila adelante: []", font=("Arial", 9), bg="#f0f2f5", anchor="w")
        self.l_ade.pack(fill=tk.X, padx=10, pady=2)

    def actualizar_info(self):
        self.l_act.config(text="estas en: " + self.pagina_actual)
        self.l_atr.config(text="pila atras: " + str(self.pila_atras))
        self.l_ade.config(text="pila adelante: " + str(self.pila_adelante))

    def visitar(self):
        url = self.txt_url.get().strip()
        if not url or url == "https://":
            messagebox.showwarning("error", "URL vacia o invalida")
            return

        if len(self.pila_atras) >= self.CAPACIDAD_MAXIMA:
            messagebox.showerror("error", f"PILA LLENADA [{self.CAPACIDAD_MAXIMA}]")
            return

        self.pila_atras.append(self.pagina_actual)
        self.pagina_actual = url
        self.pila_adelante.clear()
        
        self.txt_url.delete(0, tk.END)
        self.txt_url.insert(0, "https://")
        self.actualizar_info()

    def back(self):
        if len(self.pila_atras) == 0:
            messagebox.showinfo("info", "X PILA VACIA")
            return

        if len(self.pila_adelante) < self.CAPACIDAD_MAXIMA:
            self.pila_adelante.append(self.pagina_actual)

        self.pagina_actual = self.pila_atras.pop()
        self.actualizar_info()

    def forward(self):
        if len(self.pila_adelante) == 0:
            messagebox.showinfo("info", "X PILA VACIA")
            return

        if len(self.pila_atras) < self.CAPACIDAD_MAXIMA:
            self.pila_atras.append(self.pagina_actual)

        self.pagina_actual = self.pila_adelante.pop()
        self.actualizar_info()

def main():
    root = tk.Tk()
    NavegadorWeb(root)
    root.mainloop()

if __name__ == "__main__":
    main()