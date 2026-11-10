
import os
import heapq
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk, messagebox

INF = float("inf")



class PuebloMagico:
    """Vértice del grafo."""

    def __init__(self, id_pueblo, nombre):
        self._id_pueblo = id_pueblo
        self._clave = id_pueblo
        self._nombre = nombre

    @property
    def id_pueblo(self):
        return self._id_pueblo

    @property
    def clave(self):
        return self._clave

    @property
    def nombre(self):
        return self._nombre

    def obtener_nombre_corto(self):
        """Nombre sin la parte posterior a 'de' (p. ej. 'Comitán')."""
        return self._nombre.split(" de ")[0]

    def __str__(self):
        return self._nombre


class Carretera:
    """Arista ponderada (distancia en km)."""

    def __init__(self, origen, destino, distancia_km):
        self._origen = origen
        self._destino = destino
        self._distancia_km = float(distancia_km)

    @property
    def origen(self):
        return self._origen

    @property
    def destino(self):
        return self._destino

    def obtener_distancia(self):
        return self._distancia_km


class Grafo:
    """Grafo ponderado no dirigido con lista de adyacencia."""

    def __init__(self):
        self._pueblos = {}      # id -> PuebloMagico
        self._adyacencia = {}   # id -> [(id_vecino, km)]
        self._carreteras = []   # lista de Carretera (una por arista)

    def agregar_pueblo(self, pueblo):
        self._pueblos[pueblo.id_pueblo] = pueblo
        self._adyacencia.setdefault(pueblo.id_pueblo, [])

    def agregar_carretera(self, a, b, km):
        if a not in self._pueblos or b not in self._pueblos:
            raise ValueError(f"Pueblo desconocido en la carretera {a}-{b}")
        km = float(km)
        if km <= 0:
            raise ValueError(f"Distancia inválida en {a}-{b}: {km}")
        self._adyacencia[a].append((b, km))   # ambos sentidos
        self._adyacencia[b].append((a, km))
        self._carreteras.append(Carretera(a, b, km))

    def obtener_vecinos(self, id_pueblo):
        return self._adyacencia.get(id_pueblo, [])

    def obtener_distancia(self, a, b):
        """Distancia directa entre a y b, o INF si no hay carretera."""
        if a == b:
            return 0.0
        for vecino, km in self._adyacencia.get(a, []):
            if vecino == b:
                return km
        return INF

    def obtener_pueblos(self):
        return list(self._pueblos.values())

    def obtener_carreteras(self):
        return list(self._carreteras)

    def cargar_desde_archivo(self, archivo):
        """R1: lee pueblos (@CLAVE=Nombre) y carreteras (A B km)."""
        with open(archivo, encoding="utf-8") as f:
            for num, linea in enumerate(f, 1):
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                if linea.startswith("@"):
                    clave, _, nombre = linea[1:].partition("=")
                    self.agregar_pueblo(PuebloMagico(clave.strip(), nombre.strip()))
                else:
                    partes = linea.split()
                    if len(partes) != 3:
                        raise ValueError(f"Línea {num} con formato inválido: {linea}")
                    self.agregar_carretera(partes[0], partes[1], partes[2])


class ResultadoRuta:
    """Resultado de una consulta: ruta ordenada y distancia total."""

    def __init__(self, ruta, distancia_total):
        self._ruta = ruta                    # lista de ids de pueblos
        self._distancia_total = distancia_total

    @property
    def ruta(self):
        return self._ruta

    @property
    def distancia_total(self):
        return self._distancia_total

    def existe(self):
        return len(self._ruta) > 0

    def obtener_tramos(self, grafo):
        """Lista de (id_a, id_b, km) tramo por tramo."""
        return [(a, b, grafo.obtener_distancia(a, b))
                for a, b in zip(self._ruta, self._ruta[1:])]



class AlgoritmoRutaMinima(ABC):
    def __init__(self, grafo):
        self._grafo = grafo

    @abstractmethod
    def calcular_ruta(self, origen, destino):
        ...

    @abstractmethod
    def nombre(self):
        ...


class Dijkstra(AlgoritmoRutaMinima):
    """Dijkstra con cola de prioridad (heapq) y vértices previos."""

    def __init__(self, grafo):
        super().__init__(grafo)
        self.pasos = []   # bitácora de los pasos (para mostrarla en pantalla)

    def nombre(self):
        return "Dijkstra"

    def calcular_ruta(self, origen, destino):
        g = self._grafo
        self.pasos = []
        dist = {p.id_pueblo: INF for p in g.obtener_pueblos()}
        previo = {}
        dist[origen.id_pueblo] = 0.0
        cola = [(0.0, origen.id_pueblo)]
        visitados = set()
        self.pasos.append(f"Distancias iniciales: {origen.clave}=0, resto=∞")

        while cola:
            d, u = heapq.heappop(cola)
            if u in visitados:
                continue
            visitados.add(u)
            self.pasos.append(f"Extraer {u} (d={d:g})")
            if u == destino.id_pueblo:          # parada anticipada
                break
            for v, peso in g.obtener_vecinos(u):
                if d + peso < dist[v]:          # relajación
                    dist[v] = d + peso
                    previo[v] = u
                    heapq.heappush(cola, (dist[v], v))
                    self.pasos.append(f"   Relajar {u}→{v}: {dist[v]:g}")

        if dist[destino.id_pueblo] == INF:
            return ResultadoRuta([], INF)

        ruta, actual = [], destino.id_pueblo
        while actual != origen.id_pueblo:
            ruta.append(actual)
            actual = previo[actual]
        ruta.append(origen.id_pueblo)
        ruta.reverse()
        self.pasos.append("Ruta óptima: " + " → ".join(ruta))
        return ResultadoRuta(ruta, dist[destino.id_pueblo])



# INTERFAZ GRÁFICA

POSICIONES = {
    "COP": (80, 70), "OE": (80, 240), "CdC": (190, 155),
    "SCdC": (300, 155), "CdD": (335, 55), "PAL": (335, 260),
}
COL = {"p1": "#EEF0FF", "p2": "#E6F7EE", "p3": "#F1E9FF", "p4": "#FFF0E2",
       "nodo": "#4F46E5", "ruta": "#F97316", "ok": "#16A34A", "mal": "#DC2626"}


class RutaMagica:
    """Interfaz de consola gráfica: controla Grafo, algoritmo y resultados."""

    def __init__(self, raiz, archivo):
        self._raiz = raiz
        self._grafo = Grafo()
        self._grafo.cargar_desde_archivo(archivo)                 # R1
        self._algoritmo = Dijkstra(self._grafo)
        self._lista = self._grafo.obtener_pueblos()               # R2
        self._ruta_actual = []
        self._construir_ui()
        self._dibujar_grafo()
        self._dibujar_matriz()

    def _panel(self, col, titulo, subtitulo, color, ancho):
        f = tk.Frame(self._raiz, bg=color, width=ancho, highlightthickness=1,
                     highlightbackground="#B8B8D0")
        f.grid(row=1, column=col, sticky="nsew", padx=6, pady=6)
        f.grid_propagate(False)
        tk.Label(f, text=titulo, bg=color, font=("Segoe UI", 11, "bold")
                 ).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(f, text=subtitulo, bg=color, fg="#555", font=("Segoe UI", 8)
                 ).pack(anchor="w", padx=10)
        return f

    def _construir_ui(self):
        r = self._raiz
        r.title("Ruta Mágica – Pueblos Mágicos de Chiapas")
        r.configure(bg="#F5F5FA")
        r.geometry("1330x690")
        for c in range(4):
            r.columnconfigure(c, weight=1)
        r.rowconfigure(1, weight=1)

        cab = tk.Frame(r, bg="white", highlightthickness=1, highlightbackground="#DDD")
        cab.grid(row=0, column=0, columnspan=4, sticky="ew", padx=6, pady=6)
        tk.Label(cab, text="🗺  RUTA MÁGICA", bg="white", fg="#4F46E5",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=12, pady=6)
        tk.Label(cab, text="Pueblos Mágicos de Chiapas — Algoritmo de Camino Más Corto",
                 bg="white", fg="#555").pack(side="left")
        tk.Label(cab, text=" ", bg="#4F46E5", fg="white",
                 padx=10, pady=2).pack(side="right", padx=12)

        # 1) Datos de entrada
        p1 = self._panel(0, "① DATOS DE ENTRADA", "Grafo ponderado no dirigido",
                         COL["p1"], 400)
        self._lienzo = tk.Canvas(p1, width=380, height=320, bg=COL["p1"],
                                 highlightthickness=0)
        self._lienzo.pack(pady=6)
        tk.Label(p1, text="● Pueblo Mágico   — Carretera   # = Distancia en km",
                 bg=COL["p1"], fg="#555", font=("Segoe UI", 8)).pack(side="bottom", pady=6)

        # 2) Selección
        p2 = self._panel(1, "② SELECCIÓN", "Parámetros de búsqueda", COL["p2"], 250)
        nombres = [f"{i}. {p.nombre}" for i, p in enumerate(self._lista, 1)]
        tk.Label(p2, text="Origen:", bg=COL["p2"], font=("Segoe UI", 9, "bold")
                 ).pack(anchor="w", padx=12, pady=(18, 2))
        self._cb_origen = ttk.Combobox(p2, values=nombres, state="readonly", width=28)
        self._cb_origen.pack(padx=12)
        tk.Label(p2, text="Destino:", bg=COL["p2"], font=("Segoe UI", 9, "bold")
                 ).pack(anchor="w", padx=12, pady=(18, 2))
        self._cb_destino = ttk.Combobox(p2, values=nombres, state="readonly", width=28)
        self._cb_destino.pack(padx=12)
        tk.Label(p2, text="Algoritmo:", bg=COL["p2"], font=("Segoe UI", 9, "bold")
                 ).pack(anchor="w", padx=12, pady=(18, 2))
        tk.Label(p2, text=self._algoritmo.nombre(), bg="#7C3AED", fg="white",
                 width=26, pady=4).pack(padx=12)
        tk.Button(p2, text="Calcular ruta más corta", bg=COL["ruta"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", pady=6,
                  command=self.iniciar).pack(padx=12, pady=(24, 6), fill="x")
        tk.Button(p2, text="Consultar otra ruta (S)", command=self._nueva_consulta,
                  pady=4).pack(padx=12, fill="x")
        tk.Button(p2, text="Salir (N)", command=self._raiz.destroy,
                  pady=4).pack(padx=12, pady=6, fill="x")
        tk.Label(p2, justify="left", wraplength=210, bg="#D8F3E4", fg="#14532D",
                 font=("Segoe UI", 8), padx=6, pady=6,
                 text="Info: Dijkstra encuentra el camino más corto desde un nodo "
                      "origen a todos los demás (se detiene al llegar al destino)."
                 ).pack(side="bottom", padx=8, pady=8, fill="x")

        # 3) Procesamiento
        p3 = self._panel(2, "③ PROCESAMIENTO", "Matriz de adyacencia (distancias en km)",
                         COL["p3"], 380)
        self._marco_matriz = tk.Frame(p3, bg=COL["p3"])
        self._marco_matriz.pack(pady=8)
        tk.Label(p3, text="Pasos del algoritmo:", bg=COL["p3"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10)
        self._txt_pasos = tk.Text(p3, height=11, width=44, font=("Consolas", 8),
                                  bg="white", state="disabled")
        self._txt_pasos.pack(padx=10, pady=4, fill="both", expand=True)

        # 4) Resultado
        p4 = self._panel(3, "④ RESULTADO", "Camino más corto encontrado", COL["p4"], 330)
        self._lbl_estado = tk.Label(p4, text="Seleccione origen y destino",
                                    bg="#E5E7EB", fg="#374151", pady=5,
                                    font=("Segoe UI", 9, "bold"))
        self._lbl_estado.pack(fill="x", padx=10, pady=(10, 6))
        self._txt_res = tk.Text(p4, height=14, width=40, font=("Consolas", 9),
                                bg="white", state="disabled")
        self._txt_res.pack(padx=10)
        caja = tk.Frame(p4, bg="white", highlightthickness=2,
                        highlightbackground=COL["ruta"])
        caja.pack(fill="x", padx=10, pady=12)
        tk.Label(caja, text="Distancia total", bg="white", fg="#555").pack(pady=(6, 0))
        self._lbl_dist = tk.Label(caja, text="— km", bg="white", fg=COL["ruta"],
                                  font=("Segoe UI", 26, "bold"))
        self._lbl_dist.pack(pady=(0, 6))


    def _dibujar_grafo(self):
        c = self._lienzo
        c.delete("all")
        en_ruta = set(zip(self._ruta_actual, self._ruta_actual[1:]))
        en_ruta |= {(b, a) for a, b in en_ruta}
        for car in self._grafo.obtener_carreteras():
            x1, y1 = POSICIONES[car.origen]
            x2, y2 = POSICIONES[car.destino]
            marcada = (car.origen, car.destino) in en_ruta
            c.create_line(x1, y1, x2, y2, width=5 if marcada else 2,
                          fill=COL["ruta"] if marcada else "#9CA3AF")
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            c.create_rectangle(mx - 20, my - 9, mx + 20, my + 9, fill="white",
                               outline="#D1D5DB")
            c.create_text(mx, my, text=f"{car.obtener_distancia():g}",
                          font=("Segoe UI", 8))
        for p in self._grafo.obtener_pueblos():
            x, y = POSICIONES[p.id_pueblo]
            marcado = p.id_pueblo in self._ruta_actual
            c.create_oval(x - 24, y - 24, x + 24, y + 24,
                          fill=COL["ruta"] if marcado else COL["nodo"], outline="white", width=2)
            c.create_text(x, y, text=p.clave, fill="white", font=("Segoe UI", 9, "bold"))
            c.create_text(x, y + 36, text=p.obtener_nombre_corto(), font=("Segoe UI", 8))

    def _dibujar_matriz(self):
        for w in self._marco_matriz.winfo_children():
            w.destroy()
        ps = self._grafo.obtener_pueblos()
        en_ruta = set(zip(self._ruta_actual, self._ruta_actual[1:]))
        en_ruta |= {(b, a) for a, b in en_ruta}
        kw = dict(width=6, font=("Segoe UI", 8), relief="solid", bd=1)
        tk.Label(self._marco_matriz, text="", **kw).grid(row=0, column=0)
        for i, p in enumerate(ps, 1):
            tk.Label(self._marco_matriz, text=p.clave, bg="#C4B5FD",
                     **kw).grid(row=0, column=i)
            tk.Label(self._marco_matriz, text=p.clave, bg="#C4B5FD",
                     **kw).grid(row=i, column=0)
            for j, q in enumerate(ps, 1):
                d = self._grafo.obtener_distancia(p.id_pueblo, q.id_pueblo)
                txt = "∞" if d == INF else f"{d:g}"
                if (p.id_pueblo, q.id_pueblo) in en_ruta:
                    bg = "#FDBA74"
                elif i == j:
                    bg = "#E5E7EB"
                elif d == INF:
                    bg = "#F3E8FF"
                else:
                    bg = "white"
                tk.Label(self._marco_matriz, text=txt, bg=bg, **kw).grid(row=i, column=j)

    def _escribir(self, widget, texto):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", texto)
        widget.configure(state="disabled")

    def solicitar_pueblo(self, combo):
        """R3: devuelve el PuebloMagico elegido (None si no hay selección)."""
        idx = combo.current()
        return self._lista[idx] if idx >= 0 else None

    def iniciar(self):
        origen = self.solicitar_pueblo(self._cb_origen)
        destino = self.solicitar_pueblo(self._cb_destino)
        if origen is None or destino is None:
            messagebox.showwarning("Datos incompletos",
                                   "Seleccione un pueblo de ORIGEN y uno de DESTINO.")
            return
        if origen.id_pueblo == destino.id_pueblo:                 # R6: mismo pueblo
            res = ResultadoRuta([origen.id_pueblo], 0.0)
            self._algoritmo.pasos = ["Origen y destino son el mismo pueblo."]
        else:
            res = self._algoritmo.calcular_ruta(origen, destino)  # R4
        self._ruta_actual = res.ruta
        self.mostrar_resultado(res, origen, destino)

    def mostrar_resultado(self, res, origen, destino):
        """R5 / R6: muestra resultado en el panel ④ y refresca dibujos."""
        self._dibujar_grafo()
        self._dibujar_matriz()
        self._escribir(self._txt_pasos, "\n".join(self._algoritmo.pasos))
        linea = "=" * 38
        if not res.existe():
            self._lbl_estado.configure(text="[X] SIN RUTA", bg="#FEE2E2", fg=COL["mal"])
            self._escribir(self._txt_res, f"{linea}\n[X] No existe ruta entre esos pueblos.\n{linea}")
            self._lbl_dist.configure(text="— km")
            return
        self._lbl_estado.configure(text="[OK] RUTA ENCONTRADA", bg="#DCFCE7", fg=COL["ok"])
        nombre = lambda i: self._grafo._pueblos[i].obtener_nombre_corto()
        tramos = res.obtener_tramos(self._grafo)
        ancho = max((len(nombre(a)) for a, _, _ in tramos), default=0)
        lineas = [linea, f"Origen : {origen.obtener_nombre_corto()}",
                  f"Destino: {destino.obtener_nombre_corto()}", linea, ""]
        for a, b, km in tramos:
            lineas.append(f"{nombre(a):<{ancho}} --({km:5.1f} km)--> {nombre(b)}")
        if not tramos:
            lineas.append("(origen = destino, no hay tramos)")
        lineas += ["", "Ruta completa:", " -> ".join(nombre(i) for i in res.ruta),
                   "", linea, f"Distancia total: {res.distancia_total:.1f} km", linea]
        self._escribir(self._txt_res, "\n".join(lineas))
        self._lbl_dist.configure(text=f"{res.distancia_total:.1f} km")

    def _nueva_consulta(self):
        """R7: limpia la pantalla para otra consulta sin reiniciar el programa."""
        self._cb_origen.set("")
        self._cb_destino.set("")
        self._ruta_actual = []
        self._dibujar_grafo()
        self._dibujar_matriz()
        self._escribir(self._txt_res, "")
        self._escribir(self._txt_pasos, "")
        self._lbl_estado.configure(text="Seleccione origen y destino",
                                   bg="#E5E7EB", fg="#374151")
        self._lbl_dist.configure(text="— km")


def main():
    carpeta = os.path.dirname(os.path.abspath(__file__))
    raiz = tk.Tk()
    try:
        RutaMagica(raiz, os.path.join(carpeta, "pueblos_chiapas.txt"))
    except (OSError, ValueError) as e:
        messagebox.showerror("Error al cargar el grafo", str(e))
        return
    raiz.mainloop()


if __name__ == "__main__":
    main()
