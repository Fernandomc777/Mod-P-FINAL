import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


# ======================= MODELO =======================

class Producto:
    def __init__(self, id, nombre, categoria, precio):
        self._id = id
        self._nombre = nombre
        self._categoria = categoria
        self._precio = precio

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def categoria(self):
        return self._categoria

    @property
    def precio(self):
        return self._precio


class ItemCarrito:
    def __init__(self, producto, cantidad):
        self._producto = producto
        self._cantidad = cantidad

    @property
    def producto(self):
        return self._producto

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor):
        self._cantidad = valor

    @property
    def subtotal(self):
        return self._producto.precio * self._cantidad


class Catalogo:
    def __init__(self):
        self._productos = [
            Producto(1, "Teclado", "Accesorios", 450),
            Producto(2, "Mouse", "Accesorios", 250),
            Producto(3, "Monitor", "Electronica", 3200),
            Producto(4, "Audifonos", "Audio", 800),
            Producto(5, "Memoria USB", "Almacenamiento", 180),
        ]

    @property
    def productos(self):
        return self._productos

    def buscar_por_id(self, id):
        for p in self._productos:
            if p.id == id:
                return p
        return None

    def buscar_por_nombre(self, nombre):
        for p in self._productos:
            if nombre.lower() in p.nombre.lower():
                return p
        return None


class Carrito:
    def __init__(self):
        self._items = []

    def _buscar_item_por_id(self, id):
        for item in self._items:
            if item.producto.id == id:
                return item
        return None

    def _buscar_item_por_nombre(self, nombre):
        for item in self._items:
            if nombre.lower() in item.producto.nombre.lower():
                return item
        return None

    def esta_vacio(self):
        return len(self._items) == 0

    def agregar_producto(self, producto, cantidad):
        existente = self._buscar_item_por_id(producto.id)
        if existente is not None:
            existente.cantidad += cantidad
        else:
            self._items.append(ItemCarrito(producto, cantidad))

    def modificar_cantidad_por_id(self, id, nueva_cantidad):
        item = self._buscar_item_por_id(id)
        if item is None:
            return False
        item.cantidad = nueva_cantidad
        return True

    def eliminar_por_id(self, id):
        item = self._buscar_item_por_id(id)
        if item is None:
            return False
        self._items.remove(item)
        return True

    def eliminar_por_nombre(self, nombre):
        item = self._buscar_item_por_nombre(nombre)
        if item is None:
            return False
        self._items.remove(item)
        return True

    def vaciar(self):
        self._items.clear()

    @property
    def total(self):
        return sum(i.subtotal for i in self._items)

    @property
    def total_articulos(self):
        return sum(i.cantidad for i in self._items)

    @property
    def items(self):
        return self._items


# ======================= INTERFAZ =======================

class AplicacionCarrito(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Carrito de Compras")
        self.geometry("980x560")
        self.minsize(900, 500)

        self.catalogo = Catalogo()
        self.carrito = Carrito()

        self._crear_widgets()
        self._cargar_catalogo()
        self._refrescar_carrito()

    # ---------- construcción de la interfaz ----------
    def _crear_widgets(self):
        principal = ttk.Frame(self, padding=10)
        principal.pack(fill="both", expand=True)
        principal.columnconfigure(0, weight=1)
        principal.columnconfigure(1, weight=1)
        principal.rowconfigure(0, weight=1)

        self._crear_panel_catalogo(principal)
        self._crear_panel_carrito(principal)

        self.barra_estado = tk.StringVar(value="Bienvenido.")
        ttk.Label(principal, textvariable=self.barra_estado, relief="sunken",
                  anchor="w", padding=4).grid(row=1, column=0, columnspan=2,
                                              sticky="ew", pady=(8, 0))

    def _crear_panel_catalogo(self, padre):
        marco = ttk.LabelFrame(padre, text="Catálogo de productos", padding=8)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        marco.rowconfigure(1, weight=1)
        marco.columnconfigure(0, weight=1)

        # --- búsqueda ---
        busq = ttk.Frame(marco)
        busq.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.modo_busqueda = tk.StringVar(value="nombre")
        ttk.Radiobutton(busq, text="ID", variable=self.modo_busqueda,
                        value="id").pack(side="left")
        ttk.Radiobutton(busq, text="Nombre", variable=self.modo_busqueda,
                        value="nombre").pack(side="left", padx=(0, 6))
        self.entrada_busqueda = ttk.Entry(busq)
        self.entrada_busqueda.pack(side="left", fill="x", expand=True)
        self.entrada_busqueda.bind("<Return>", lambda e: self.buscar_producto())
        ttk.Button(busq, text="Buscar", command=self.buscar_producto).pack(
            side="left", padx=(6, 0))

        # --- tabla de catálogo ---
        cols = ("id", "nombre", "categoria", "precio")
        self.tabla_catalogo = ttk.Treeview(marco, columns=cols, show="headings",
                                           selectmode="browse")
        for col, texto, ancho in (("id", "ID", 40), ("nombre", "Producto", 120),
                                  ("categoria", "Categoría", 110),
                                  ("precio", "Precio", 80)):
            self.tabla_catalogo.heading(col, text=texto)
            self.tabla_catalogo.column(col, width=ancho,
                                       anchor="e" if col in ("id", "precio") else "w")
        self.tabla_catalogo.grid(row=1, column=0, sticky="nsew")
        self.tabla_catalogo.bind("<Double-1>", lambda e: self.agregar_al_carrito())

        # --- agregar ---
        agregar = ttk.Frame(marco)
        agregar.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Label(agregar, text="Cantidad:").pack(side="left")
        self.spin_cantidad = ttk.Spinbox(agregar, from_=1, to=999, width=6)
        self.spin_cantidad.set(1)
        self.spin_cantidad.pack(side="left", padx=6)
        ttk.Button(agregar, text="Agregar al carrito",
                   command=self.agregar_al_carrito).pack(side="left")

    def _crear_panel_carrito(self, padre):
        marco = ttk.LabelFrame(padre, text="Carrito", padding=8)
        marco.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        cols = ("id", "nombre", "precio", "cantidad", "subtotal")
        self.tabla_carrito = ttk.Treeview(marco, columns=cols, show="headings",
                                          selectmode="browse")
        for col, texto, ancho in (("id", "ID", 40), ("nombre", "Producto", 120),
                                  ("precio", "Precio", 80), ("cantidad", "Cant.", 50),
                                  ("subtotal", "Subtotal", 90)):
            self.tabla_carrito.heading(col, text=texto)
            self.tabla_carrito.column(col, width=ancho,
                                      anchor="w" if col == "nombre" else "e")
        self.tabla_carrito.grid(row=0, column=0, sticky="nsew")

        self.var_total = tk.StringVar()
        ttk.Label(marco, textvariable=self.var_total,
                  font=("TkDefaultFont", 12, "bold")).grid(
            row=1, column=0, sticky="e", pady=6)

        botones = ttk.Frame(marco)
        botones.grid(row=2, column=0, sticky="ew")
        for i in range(3):
            botones.columnconfigure(i, weight=1)
        ttk.Button(botones, text="Modificar cantidad",
                   command=self.modificar_cantidad).grid(
            row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(botones, text="Eliminar seleccionado",
                   command=self.eliminar_seleccionado).grid(
            row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(botones, text="Eliminar por nombre",
                   command=self.eliminar_por_nombre).grid(
            row=0, column=2, sticky="ew", padx=2, pady=2)
        ttk.Button(botones, text="Vaciar carrito",
                   command=self.vaciar_carrito).grid(
            row=1, column=0, columnspan=1, sticky="ew", padx=2, pady=2)
        ttk.Button(botones, text="Finalizar compra",
                   command=self.finalizar_compra).grid(
            row=1, column=1, columnspan=2, sticky="ew", padx=2, pady=2)

    # ---------- refrescar vistas ----------
    def _cargar_catalogo(self):
        for p in self.catalogo.productos:
            self.tabla_catalogo.insert(
                "", "end", iid=str(p.id),
                values=(p.id, p.nombre, p.categoria, f"${p.precio:.2f}"))

    def _refrescar_carrito(self):
        self.tabla_carrito.delete(*self.tabla_carrito.get_children())
        for item in self.carrito.items:
            p = item.producto
            self.tabla_carrito.insert(
                "", "end", iid=str(p.id),
                values=(p.id, p.nombre, f"${p.precio:.2f}", item.cantidad,
                        f"${item.subtotal:.2f}"))
        self.var_total.set(f"TOTAL: ${self.carrito.total:.2f}")

    def _estado(self, texto):
        self.barra_estado.set(texto)

    # ---------- utilidades ----------
    def _leer_cantidad(self):
        try:
            cantidad = int(self.spin_cantidad.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un número válido.")
            return None
        if cantidad <= 0:
            messagebox.showwarning("Cantidad inválida",
                                   "La cantidad debe ser mayor a 0.")
            return None
        return cantidad

    def _id_seleccionado(self, tabla):
        sel = tabla.selection()
        return int(sel[0]) if sel else None

    # ---------- acciones ----------
    def buscar_producto(self):
        texto = self.entrada_busqueda.get().strip()
        if not texto:
            messagebox.showinfo("Buscar", "Escribe un ID o un nombre para buscar.")
            return

        if self.modo_busqueda.get() == "id":
            try:
                encontrado = self.catalogo.buscar_por_id(int(texto))
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa un número válido.")
                return
        else:
            encontrado = self.catalogo.buscar_por_nombre(texto)

        if encontrado is None:
            messagebox.showinfo("Buscar", "Producto no encontrado.")
            self._estado("Producto no encontrado.")
        else:
            self.tabla_catalogo.selection_set(str(encontrado.id))
            self.tabla_catalogo.see(str(encontrado.id))
            self._estado(f"Producto encontrado: {encontrado.nombre} "
                         f"(${encontrado.precio:.2f})")

    def agregar_al_carrito(self):
        id = self._id_seleccionado(self.tabla_catalogo)
        if id is None:
            messagebox.showinfo("Agregar", "Selecciona un producto del catálogo.")
            return
        cantidad = self._leer_cantidad()
        if cantidad is None:
            return

        producto = self.catalogo.buscar_por_id(id)
        self.carrito.agregar_producto(producto, cantidad)
        self._refrescar_carrito()
        self._estado(f"¡{cantidad} x {producto.nombre} agregado al carrito!")

    def modificar_cantidad(self):
        if self.carrito.esta_vacio():
            messagebox.showinfo("Modificar",
                                "El carrito está vacío, no hay nada que modificar.")
            return
        id = self._id_seleccionado(self.tabla_carrito)
        if id is None:
            messagebox.showinfo("Modificar", "Selecciona un producto del carrito.")
            return

        nueva = simpledialog.askinteger("Modificar cantidad", "Nueva cantidad:",
                                        parent=self, minvalue=0)
        if nueva is None:
            return
        if nueva <= 0:
            messagebox.showwarning(
                "Cantidad inválida",
                "La cantidad debe ser mayor a 0.\n"
                "(Usa Eliminar si quieres quitarlo)")
            return

        if self.carrito.modificar_cantidad_por_id(id, nueva):
            self._refrescar_carrito()
            self._estado("¡Cantidad actualizada!")
        else:
            messagebox.showinfo("Modificar", "Ese producto no está en el carrito.")

    def eliminar_seleccionado(self):
        if self.carrito.esta_vacio():
            messagebox.showinfo("Eliminar",
                                "El carrito está vacío, no hay nada que eliminar.")
            return
        id = self._id_seleccionado(self.tabla_carrito)
        if id is None:
            messagebox.showinfo("Eliminar", "Selecciona un producto del carrito.")
            return
        if self.carrito.eliminar_por_id(id):
            self._refrescar_carrito()
            self._estado("¡Producto eliminado del carrito!")

    def eliminar_por_nombre(self):
        if self.carrito.esta_vacio():
            messagebox.showinfo("Eliminar",
                                "El carrito está vacío, no hay nada que eliminar.")
            return
        nombre = simpledialog.askstring("Eliminar por nombre",
                                        "Nombre del producto a eliminar:",
                                        parent=self)
        if not nombre or not nombre.strip():
            return
        if self.carrito.eliminar_por_nombre(nombre.strip()):
            self._refrescar_carrito()
            self._estado("¡Producto eliminado del carrito!")
        else:
            messagebox.showinfo("Eliminar", "Ese producto no está en el carrito.")

    def vaciar_carrito(self):
        if self.carrito.esta_vacio():
            messagebox.showinfo("Vaciar", "El carrito ya está vacío.")
            return
        if messagebox.askyesno("Vaciar carrito",
                               "¿Está seguro que desea vaciar el carrito?"):
            self.carrito.vaciar()
            self._refrescar_carrito()
            self._estado("¡Carrito vaciado!")
        else:
            self._estado("Operación cancelada.")

    def finalizar_compra(self):
        if self.carrito.esta_vacio():
            messagebox.showinfo(
                "Finalizar compra",
                "El carrito está vacío, no hay compra que finalizar.")
            return

        lineas = ["=== RESUMEN DE COMPRA ===", ""]
        for item in self.carrito.items:
            lineas.append(f"{item.producto.nombre:<14} x{item.cantidad:<3} "
                          f"${item.subtotal:>9.2f}")
        lineas += [
            "",
            f"Productos distintos: {len(self.carrito.items)}",
            f"Artículos totales: {self.carrito.total_articulos}",
            f"Total a pagar: ${self.carrito.total:.2f}",
            "",
            "¡Gracias por su compra!",
        ]
        messagebox.showinfo("Finalizar compra", "\n".join(lineas))

        self.carrito.vaciar()
        self._refrescar_carrito()
        self._estado("Compra finalizada. ¡Gracias!")


if __name__ == "__main__":
    AplicacionCarrito().mainloop()
