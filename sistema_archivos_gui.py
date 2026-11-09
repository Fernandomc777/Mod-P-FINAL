import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DIRECTORIO = "Directorio"
ARCHIVO = "Archivo"

SOLO_DIRECTORIO_VACIO = True


# ======================= MODELO =======================

class Nodo:
    def __init__(self, nombre, extension, tamano, tipo):
        self.nombre = nombre
        self.extension = extension      # "-" para directorios
        self.tamano = tamano            # 0 para directorios
        self.tipo = tipo
        self.izq = None
        self.der = None

    def es_directorio(self):
        return self.tipo == DIRECTORIO

    def es_archivo(self):
        return self.tipo == ARCHIVO

    def info(self):
        return (f"Nombre: {self.nombre}\n"
                f"Extensión: {self.extension}\n"
                f"Tipo: {self.tipo}\n"
                f"Tamaño: {self.tamano} bytes")

    def linea(self):
        return (f"{self.nombre} | ext: {self.extension} | "
                f"{self.tamano} bytes | {self.tipo}")


def comparar(a, b):
    """Compara nombres alfabéticamente (sin distinguir mayúsculas)."""
    a, b = a.lower(), b.lower()
    return (a > b) - (a < b)


def validar_elemento(nombre, extension, tamano, tipo):
    """Devuelve None si es válido, o un mensaje de error."""
    if not nombre or not nombre.strip():
        return "El nombre del elemento no puede estar vacío."
    if tipo == ARCHIVO:
        if not extension or extension.strip() in ("", "-"):
            return "Un archivo debe tener extensión."
        if tamano < 0:
            return "El tamaño de un archivo debe ser mayor o igual a cero."
    elif tipo == DIRECTORIO:
        if extension not in ("", "-", None):
            return "Un directorio no debe tener extensión."
    else:
        return "Tipo inválido."
    return None


class ArbolArchivos:
    def __init__(self, nombre_raiz):
        err = validar_elemento(nombre_raiz, "-", 0, DIRECTORIO)
        if err:
            raise ValueError(err)
        self.raiz = Nodo(nombre_raiz, "-", 0, DIRECTORIO)

    # ---- Insertar
    def insertar(self, nuevo):
        """Inserta usando el nombre como clave. Devuelve (ok, mensaje)."""
        err = validar_elemento(nuevo.nombre, nuevo.extension,
                               nuevo.tamano, nuevo.tipo)
        if err:
            return False, err
        if self.buscar(nuevo.nombre):
            return False, "El elemento ya existe."

        actual = self.raiz
        while True:
            if actual.es_archivo():
                return False, ("ERROR: No se puede insertar el elemento.\n"
                               "Un archivo no puede contener otros elementos.")
            if comparar(nuevo.nombre, actual.nombre) < 0:
                if actual.izq is None:
                    actual.izq = nuevo
                    return True, "Elemento insertado correctamente."
                actual = actual.izq
            else:
                if actual.der is None:
                    actual.der = nuevo
                    return True, "Elemento insertado correctamente."
                actual = actual.der

    # ---- Buscar
    def buscar(self, nombre):
        actual = self.raiz
        while actual:
            c = comparar(nombre, actual.nombre)
            if c == 0:
                return actual
            actual = actual.izq if c < 0 else actual.der
        return None

    # ---- Eliminar
    def eliminar(self, nombre):
        """Devuelve (ok, mensaje)."""
        if comparar(nombre, self.raiz.nombre) == 0:
            return False, "No se puede eliminar el directorio raíz."
        nodo = self.buscar(nombre)
        if nodo is None:
            return False, "El elemento no existe en el sistema de archivos."
        if (nodo.es_directorio() and SOLO_DIRECTORIO_VACIO
                and (nodo.izq or nodo.der)):
            return False, ("El directorio no está vacío. "
                           "Un directorio solo puede eliminarse si está vacío.")
        self.raiz = self._eliminar(self.raiz, nombre)
        return True, "Elemento eliminado correctamente."

    def _eliminar(self, nodo, nombre):
        if nodo is None:
            return None
        c = comparar(nombre, nodo.nombre)
        if c < 0:
            nodo.izq = self._eliminar(nodo.izq, nombre)
        elif c > 0:
            nodo.der = self._eliminar(nodo.der, nombre)
        else:
            # Situación 1: hoja
            if nodo.izq is None and nodo.der is None:
                return None
            # Situación 2: un hijo
            if nodo.izq is None:
                return nodo.der
            if nodo.der is None:
                return nodo.izq
            # Situación 3: dos hijos -> sucesor inorden
            suc = nodo.der
            while suc.izq:
                suc = suc.izq
            nodo.nombre, nodo.extension = suc.nombre, suc.extension
            nodo.tamano, nodo.tipo = suc.tamano, suc.tipo
            nodo.der = self._eliminar(nodo.der, suc.nombre)
        return nodo

    # ---- Recorridos
    def inorden(self):
        res = []
        def rec(n):
            if n:
                rec(n.izq); res.append(n); rec(n.der)
        rec(self.raiz)
        return res

    def preorden(self):
        res = []
        def rec(n):
            if n:
                res.append(n); rec(n.izq); rec(n.der)
        rec(self.raiz)
        return res

    def postorden(self):
        res = []
        def rec(n):
            if n:
                rec(n.izq); rec(n.der); res.append(n)
        rec(self.raiz)
        return res

    # ---- Validación de reglas
    def validar_reglas(self):
        problemas = []
        if not self.raiz.es_directorio():
            problemas.append("La raíz no es un directorio.")
        vistos = set()

        def rec(n, minimo, maximo):
            if n is None:
                return
            clave = n.nombre.lower()
            if clave in vistos:
                problemas.append(f"Nombre duplicado: {n.nombre}")
            vistos.add(clave)
            if n.es_archivo() and (n.izq or n.der):
                problemas.append(f"El archivo '{n.nombre}' tiene hijos.")
            err = validar_elemento(n.nombre, n.extension, n.tamano, n.tipo)
            if err:
                problemas.append(f"'{n.nombre}': {err}")
            if minimo is not None and comparar(n.nombre, minimo) < 0:
                problemas.append(f"'{n.nombre}' viola el orden del ABB.")
            if maximo is not None and comparar(n.nombre, maximo) > 0:
                problemas.append(f"'{n.nombre}' viola el orden del ABB.")
            rec(n.izq, minimo, n.nombre)
            rec(n.der, n.nombre, maximo)

        rec(self.raiz, None, None)
        return problemas


def calcular_posiciones(raiz):
    """x = posición inorden, y = profundidad. Devuelve {id(nodo): (col, nivel)}."""
    pos, contador = {}, [0]
    def rec(n, nivel):
        if n is None:
            return
        rec(n.izq, nivel + 1)
        pos[id(n)] = (contador[0], nivel)
        contador[0] += 1
        rec(n.der, nivel + 1)
    rec(raiz, 0)
    return pos


# ======================= INTERFAZ =======================

COLOR_DIR = "#9FD3F5"
COLOR_ARCH = "#F8C9A8"
COLOR_RESALTE = "#FFE066"


class AplicacionArchivos(tk.Tk):
    ANCHO_NODO, ALTO_NODO = 110, 44
    SEP_X, SEP_Y, MARGEN = 125, 100, 50

    def __init__(self):
        super().__init__()
        self.title("Sistema de Archivos - Árbol Binario de Búsqueda")
        self.geometry("1150x680")
        self.minsize(950, 560)
        self.withdraw()

        nombre = self._pedir_raiz()
        if nombre is None:
            self.destroy()
            return
        self.arbol = ArbolArchivos(nombre)
        self.resaltado = None      # nombre del nodo resaltado en el canvas
        self.nodos_canvas = {}     # id de item del canvas -> nodo

        self._crear_widgets()
        self.deiconify()
        self._log(f"Directorio raíz '{nombre}' creado.")
        self._redibujar()

    def _pedir_raiz(self):
        while True:
            nombre = simpledialog.askstring(
                "Directorio raíz", "Nombre del directorio raíz:", parent=self)
            if nombre is None:
                return None
            if nombre.strip():
                return nombre.strip()
            messagebox.showerror("Error", "El nombre no puede estar vacío.")

    # ---------- construcción de la interfaz ----------
    def _crear_widgets(self):
        principal = ttk.Frame(self, padding=8)
        principal.pack(fill="both", expand=True)
        principal.columnconfigure(1, weight=1)
        principal.rowconfigure(0, weight=3)
        principal.rowconfigure(1, weight=1)

        self._crear_panel_control(principal)
        self._crear_panel_arbol(principal)
        self._crear_panel_salida(principal)

    def _crear_panel_control(self, padre):
        marco = ttk.Frame(padre)
        marco.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 8))

        # --- formulario ---
        form = ttk.LabelFrame(marco, text="Elemento", padding=8)
        form.pack(fill="x")
        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.var_nombre = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_nombre, width=22).grid(
            row=0, column=1, pady=2)
        ttk.Label(form, text="Extensión:").grid(row=1, column=0, sticky="w")
        self.var_ext = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_ext, width=22).grid(
            row=1, column=1, pady=2)
        ttk.Label(form, text="Tamaño (bytes):").grid(row=2, column=0, sticky="w")
        self.var_tam = tk.StringVar(value="0")
        ttk.Entry(form, textvariable=self.var_tam, width=22).grid(
            row=2, column=1, pady=2)
        ttk.Label(form, text="(extensión y tamaño solo aplican a archivos)",
                  font=("TkDefaultFont", 8)).grid(row=3, column=0, columnspan=2,
                                                  sticky="w", pady=(2, 0))

        # --- operaciones ---
        ops = ttk.LabelFrame(marco, text="Operaciones", padding=8)
        ops.pack(fill="x", pady=8)
        botones = [
            ("Crear directorio", self.crear_directorio),
            ("Insertar archivo", self.insertar_archivo),
            ("Buscar por nombre", self.buscar_elemento),
            ("Mostrar información", self.mostrar_informacion),
            ("Eliminar elemento", self.eliminar_elemento),
            ("Validar reglas", self.validar_reglas),
        ]
        for texto, comando in botones:
            ttk.Button(ops, text=texto, command=comando).pack(fill="x", pady=2)

        # --- recorridos ---
        rec = ttk.LabelFrame(marco, text="Recorridos", padding=8)
        rec.pack(fill="x")
        ttk.Button(rec, text="Inorden", command=lambda: self.recorrido(
            "inorden")).pack(fill="x", pady=2)
        ttk.Button(rec, text="Preorden", command=lambda: self.recorrido(
            "preorden")).pack(fill="x", pady=2)
        ttk.Button(rec, text="Postorden", command=lambda: self.recorrido(
            "postorden")).pack(fill="x", pady=2)

        # --- leyenda ---
        ley = ttk.LabelFrame(marco, text="Leyenda", padding=8)
        ley.pack(fill="x", pady=8)
        for color, texto in ((COLOR_DIR, "Directorio"), (COLOR_ARCH, "Archivo"),
                             (COLOR_RESALTE, "Resaltado")):
            fila = ttk.Frame(ley)
            fila.pack(anchor="w")
            tk.Label(fila, bg=color, width=2, relief="solid", bd=1).pack(
                side="left", padx=(0, 6), pady=1)
            ttk.Label(fila, text=texto).pack(side="left")

    def _crear_panel_arbol(self, padre):
        marco = ttk.LabelFrame(padre, text="Estructura del árbol "
                                           "(clic en un nodo para seleccionarlo)",
                               padding=4)
        marco.grid(row=0, column=1, sticky="nsew")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(marco, bg="white", highlightthickness=0)
        sb_x = ttk.Scrollbar(marco, orient="horizontal", command=self.canvas.xview)
        sb_y = ttk.Scrollbar(marco, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=sb_x.set, yscrollcommand=sb_y.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x.grid(row=1, column=0, sticky="ew")
        self.canvas.bind("<Button-1>", self._clic_canvas)

    def _crear_panel_salida(self, padre):
        marco = ttk.LabelFrame(padre, text="Salida", padding=4)
        marco.grid(row=1, column=1, sticky="nsew", pady=(8, 0))
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        self.texto = tk.Text(marco, height=8, wrap="word", state="disabled",
                             font=("Consolas", 10))
        sb = ttk.Scrollbar(marco, command=self.texto.yview)
        self.texto.configure(yscrollcommand=sb.set)
        self.texto.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        ttk.Button(marco, text="Limpiar salida", command=self._limpiar_log).grid(
            row=1, column=0, sticky="e", pady=(4, 0))

    # ---------- salida de texto ----------
    def _log(self, mensaje):
        self.texto.configure(state="normal")
        self.texto.insert("end", mensaje + "\n")
        self.texto.see("end")
        self.texto.configure(state="disabled")

    def _limpiar_log(self):
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.configure(state="disabled")

    # ---------- dibujo del árbol ----------
    def _redibujar(self):
        c = self.canvas
        c.delete("all")
        self.nodos_canvas = {}

        pos = calcular_posiciones(self.arbol.raiz)
        columnas = max(col for col, _ in pos.values()) + 1
        niveles = max(niv for _, niv in pos.values()) + 1
        w = self.MARGEN * 2 + columnas * self.SEP_X
        h = self.MARGEN * 2 + niveles * self.SEP_Y
        c.configure(scrollregion=(0, 0, w, h))

        def centro(n):
            col, niv = pos[id(n)]
            return (self.MARGEN + col * self.SEP_X + self.SEP_X // 2,
                    self.MARGEN + niv * self.SEP_Y)

        def rec(n):
            if n is None:
                return
            x, y = centro(n)
            for hijo, lado in ((n.izq, "izq"), (n.der, "der")):
                if hijo:
                    hx, hy = centro(hijo)
                    c.create_line(x, y + self.ALTO_NODO // 2,
                                  hx, hy - self.ALTO_NODO // 2,
                                  arrow="last", fill="#555")
            rec(n.izq)
            rec(n.der)

            if self.resaltado and comparar(n.nombre, self.resaltado) == 0:
                color, grosor = COLOR_RESALTE, 3
            else:
                color = COLOR_DIR if n.es_directorio() else COLOR_ARCH
                grosor = 1
            rect = c.create_rectangle(
                x - self.ANCHO_NODO // 2, y - self.ALTO_NODO // 2,
                x + self.ANCHO_NODO // 2, y + self.ALTO_NODO // 2,
                fill=color, outline="#333", width=grosor)
            etiqueta = n.nombre if n.es_directorio() else f"{n.nombre}.{n.extension}"
            t1 = c.create_text(x, y - 8, text=etiqueta, font=("Arial", 10, "bold"))
            t2 = c.create_text(x, y + 10, text=n.tipo, font=("Arial", 8))
            for item in (rect, t1, t2):
                self.nodos_canvas[item] = n

        rec(self.arbol.raiz)

    def _clic_canvas(self, evento):
        x = self.canvas.canvasx(evento.x)
        y = self.canvas.canvasy(evento.y)
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in items:
            nodo = self.nodos_canvas.get(item)
            if nodo:
                self.var_nombre.set(nodo.nombre)
                self.resaltado = nodo.nombre
                self._redibujar()
                self._log(f"Seleccionado: {nodo.linea()}")
                return

    # ---------- utilidades ----------
    def _nombre(self):
        return self.var_nombre.get().strip()

    def _resultado(self, ok, msg):
        self._log(msg)
        if ok:
            self._redibujar()
        else:
            messagebox.showerror("Error", msg, parent=self)

    # ---------- acciones ----------
    def crear_directorio(self):
        ok, msg = self.arbol.insertar(Nodo(self._nombre(), "-", 0, DIRECTORIO))
        if ok:
            self.resaltado = self._nombre()
        self._resultado(ok, msg)

    def insertar_archivo(self):
        ext = self.var_ext.get().strip().lstrip(".")
        try:
            tam = int(self.var_tam.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Ingresa un tamaño entero válido.",
                                 parent=self)
            return
        ok, msg = self.arbol.insertar(Nodo(self._nombre(), ext, tam, ARCHIVO))
        if ok:
            self.resaltado = self._nombre()
        self._resultado(ok, msg)

    def buscar_elemento(self):
        nombre = self._nombre()
        if not nombre:
            messagebox.showinfo("Buscar", "Escribe el nombre del elemento.",
                                parent=self)
            return
        nodo = self.arbol.buscar(nombre)
        if nodo:
            self.resaltado = nodo.nombre
            self._redibujar()
            self._log("\nElemento encontrado\n" + nodo.info())
        else:
            self.resaltado = None
            self._redibujar()
            self._log("El elemento no existe en el sistema de archivos.")
            messagebox.showinfo("Buscar",
                                "El elemento no existe en el sistema de archivos.",
                                parent=self)

    def mostrar_informacion(self):
        nodo = self.arbol.buscar(self._nombre())
        if nodo is None:
            messagebox.showinfo("Información",
                                "El elemento no existe en el sistema de archivos.",
                                parent=self)
            return
        self.resaltado = nodo.nombre
        self._redibujar()
        self._log("\nInformación del elemento\n" + nodo.info())
        messagebox.showinfo("Información del elemento", nodo.info(), parent=self)

    def eliminar_elemento(self):
        nombre = self._nombre()
        if not nombre:
            messagebox.showinfo("Eliminar", "Escribe o selecciona el elemento a "
                                            "eliminar.", parent=self)
            return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar '{nombre}'?",
                                   parent=self):
            return
        ok, msg = self.arbol.eliminar(nombre)
        if ok:
            self.resaltado = None
            self.var_nombre.set("")
        self._resultado(ok, msg)

    def recorrido(self, tipo):
        nodos = getattr(self.arbol, tipo)()
        self._log(f"\n--- Recorrido {tipo} ---")
        for n in nodos:
            self._log(n.linea())

    def validar_reglas(self):
        problemas = self.arbol.validar_reglas()
        if problemas:
            self._log("Se encontraron problemas:")
            for p in problemas:
                self._log(" - " + p)
            messagebox.showwarning("Validación", "\n".join(problemas), parent=self)
        else:
            msg = "El sistema de archivos cumple todas las reglas."
            self._log(msg)
            messagebox.showinfo("Validación", msg, parent=self)


if __name__ == "__main__":
    app = AplicacionArchivos()
    if app.winfo_exists():
        app.mainloop()
