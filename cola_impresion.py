import random
import tkinter as tk
from tkinter import messagebox


# ----------------------------------------------------------------------
# LÓGICA (sin interfaz)
# ----------------------------------------------------------------------
class ColaImpresion:
    """Cola circular FIFO con capacidad fija de seis trabajos."""

    CAPACIDAD = 6   # Límite de trabajos pendientes

    def __init__(self):
        self._trabajos = [0] * self.CAPACIDAD   # Número de PC de cada solicitud
        self._frente = 0                         # Índice del siguiente trabajo a imprimir
        self._cantidad = 0                       # Posiciones ocupadas

    # --- consultas ---
    @property
    def trabajos(self):
        return list(self._trabajos)

    @property
    def frente(self):
        return self._frente

    @property
    def cantidad(self):
        return self._cantidad

    @property
    def final(self):
        """Posición donde se insertará el siguiente trabajo."""
        return (self._frente + self._cantidad) % self.CAPACIDAD

    def esta_vacia(self):
        return self._cantidad == 0

    def esta_llena(self):
        return self._cantidad == self.CAPACIDAD

    def ocupada(self, posicion):
        """True si la posición del arreglo contiene un trabajo pendiente."""
        return (posicion - self._frente) % self.CAPACIDAD < self._cantidad

    def obtener_orden(self):
        """Lista de PCs en orden de atención (FIFO), sin modificar la cola."""
        return [self._trabajos[(self._frente + i) % self.CAPACIDAD]
                for i in range(self._cantidad)]

    # --- operaciones ---
    def agregar_trabajo(self):
        """Agrega una PC aleatoria (1-5) al final lógico. Devuelve la PC o None si está llena."""
        if self.esta_llena():
            return None
        computadora = random.randint(1, 5)
        self._trabajos[self.final] = computadora   # el módulo reutiliza espacios
        self._cantidad += 1
        return computadora

    def imprimir_documento(self):
        """Retira e imprime el primer trabajo. Devuelve la PC o None si está vacía."""
        if self.esta_vacia():
            return None
        computadora = self._trabajos[self._frente]
        self._frente = (self._frente + 1) % self.CAPACIDAD
        self._cantidad -= 1
        return computadora


# ----------------------------------------------------------------------
# INTERFAZ GRÁFICA
# ----------------------------------------------------------------------
COLORES_PC = {1: "#60A5FA", 2: "#34D399", 3: "#FBBF24", 4: "#F87171", 5: "#A78BFA"}


class AplicacionCola:
    """Ventana principal: dibuja la cola circular y conecta los botones."""

    ANCHO_CASILLA = 100

    def __init__(self, raiz):
        self._raiz = raiz
        self._cola = ColaImpresion()
        self._construir_ui()
        self._actualizar()

    def _construir_ui(self):
        r = self._raiz
        r.title("Cola de impresión – FIFO")
        r.configure(bg="#F3F4F6")
        r.resizable(False, False)

        tk.Label(r, text="🖨  COLA DE IMPRESIÓN - FIFO", bg="#1F2937", fg="white",
                 font=("Segoe UI", 16, "bold"), pady=10).pack(fill="x")

        self._lbl_contador = tk.Label(r, bg="#F3F4F6", font=("Segoe UI", 12, "bold"))
        self._lbl_contador.pack(pady=(10, 0))

        ancho = self.ANCHO_CASILLA * ColaImpresion.CAPACIDAD + 20
        self._lienzo = tk.Canvas(r, width=ancho, height=170, bg="white",
                                 highlightthickness=1, highlightbackground="#D1D5DB")
        self._lienzo.pack(padx=14, pady=10)

        botones = tk.Frame(r, bg="#F3F4F6")
        botones.pack(pady=4)
        estilo = dict(width=22, pady=6, relief="flat", font=("Segoe UI", 10, "bold"),
                      fg="white")
        tk.Button(botones, text="1. Agregar trabajo", bg="#2563EB",
                  command=self.agregar, **estilo).grid(row=0, column=0, padx=5, pady=3)
        tk.Button(botones, text="2. Imprimir documento", bg="#16A34A",
                  command=self.imprimir, **estilo).grid(row=0, column=1, padx=5, pady=3)
        tk.Button(botones, text="3. Mostrar cola", bg="#7C3AED",
                  command=self.mostrar, **estilo).grid(row=0, column=2, padx=5, pady=3)
        tk.Button(botones, text="0. Salir", bg="#6B7280",
                  command=self.salir, **estilo).grid(row=0, column=3, padx=5, pady=3)

        tk.Label(r, text="Orden de atención (el primero se imprime primero):",
                 bg="#F3F4F6", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(8, 0))
        self._lbl_orden = tk.Label(r, bg="#F3F4F6", fg="#1F2937", font=("Consolas", 11),
                                   anchor="w")
        self._lbl_orden.pack(fill="x", padx=16)

        tk.Label(r, text="Registro:", bg="#F3F4F6", font=("Segoe UI", 9, "bold")
                 ).pack(anchor="w", padx=16, pady=(8, 0))
        self._log = tk.Text(r, height=8, width=82, font=("Consolas", 9),
                            state="disabled", bg="#111827", fg="#E5E7EB")
        self._log.pack(padx=14, pady=(0, 14))

    # ---------- dibujo ----------
    def _actualizar(self):
        c, cola = self._lienzo, self._cola
        c.delete("all")
        w = self.ANCHO_CASILLA
        for i in range(ColaImpresion.CAPACIDAD):
            x0, y0, x1, y1 = 10 + i * w + 4, 45, 10 + (i + 1) * w - 4, 125
            if cola.ocupada(i):
                pc = cola.trabajos[i]
                relleno, texto = COLORES_PC[pc], f"PC{pc}"
            else:
                relleno, texto = "#F9FAFB", "libre"
            c.create_rectangle(x0, y0, x1, y1, fill=relleno, outline="#374151", width=2)
            c.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=texto,
                          font=("Segoe UI", 14, "bold"),
                          fill="#111827" if cola.ocupada(i) else "#9CA3AF")
            c.create_text((x0 + x1) / 2, 135, text=f"índice {i}", fill="#6B7280",
                          font=("Segoe UI", 8))
            if i == cola.frente and not cola.esta_vacia():
                c.create_text((x0 + x1) / 2, 28, text="▼ FRENTE", fill="#16A34A",
                              font=("Segoe UI", 9, "bold"))
            if i == cola.final and not cola.esta_llena():
                c.create_text((x0 + x1) / 2, 155, text="▲ FINAL (siguiente)", fill="#2563EB",
                              font=("Segoe UI", 9, "bold"))

        estado = ("VACÍA" if cola.esta_vacia() else "LLENA" if cola.esta_llena() else "")
        self._lbl_contador.configure(
            text=f"Cola de impresión: {cola.cantidad}/{ColaImpresion.CAPACIDAD} trabajos"
                 + (f"  —  {estado}" if estado else ""),
            fg="#DC2626" if estado else "#111827")
        orden = cola.obtener_orden()
        self._lbl_orden.configure(
            text="  →  ".join(f"{i}. PC{pc}" for i, pc in enumerate(orden, 1))
            if orden else "La cola de impresión está VACÍA")

    def _registrar(self, texto):
        self._log.configure(state="normal")
        self._log.insert("end", texto + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    # ---------- acciones ----------
    def agregar(self):
        pc = self._cola.agregar_trabajo()
        if pc is None:
            self._registrar("La cola de impresión está LLENA")
            messagebox.showwarning("Cola llena", "La cola de impresión está LLENA.")
        else:
            self._registrar(f"Trabajo agregado desde PC{pc}.")
        self._actualizar()

    def imprimir(self):
        pc = self._cola.imprimir_documento()
        if pc is None:
            self._registrar("La cola de impresión está VACÍA")
            messagebox.showinfo("Cola vacía", "La cola de impresión está VACÍA.")
        else:
            self._registrar(f"Imprimiendo documento de PC{pc}.")
        self._actualizar()

    def mostrar(self):
        cola = self._cola
        self._registrar(f"Cola de impresión: {cola.cantidad}/{ColaImpresion.CAPACIDAD} trabajos")
        if cola.esta_vacia():
            self._registrar("La cola de impresión está VACÍA")
        else:
            for i, pc in enumerate(cola.obtener_orden(), 1):
                self._registrar(f"  {i}. PC{pc}")

    def salir(self):
        self._registrar("Programa finalizado.")
        self._raiz.destroy()


def main():
    raiz = tk.Tk()
    AplicacionCola(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
