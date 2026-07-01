import random
import math


class Visitante:
    """
    Representa a cada persona que entra al Palacio Ferreyra.
    Guardamos en el objeto TODO su historial (sala actual, números
    aleatorios que se usaron para definir sus tiempos, etc.) para que
    el vector de estado pueda mostrar, fila por fila, el detalle
    completo de cada visitante presente en el sistema en ese instante,
    tal como pide la consigna del TP.
    """

    def __init__(self, id_visitante, reloj_llegada, puerta, media_edad=30):
        self.id = id_visitante
        self.reloj_llegada = reloj_llegada
        self.puerta = puerta  # 'A', 'B' o 'C'

        # --- Edad (distribución exponencial, media parametrizable) ---
        self.rnd_edad = random.random()
        edad_calc = -media_edad * math.log(1 - self.rnd_edad)
        self.edad = int(edad_calc)  # truncada, como pide el enunciado

        # --- Estado dinámico del visitante a lo largo de la simulación ---
        self.estado = "Llegando"          # texto legible para la tabla
        self.sala_actual = "Hall"         # Hall / Ventanilla / Pintura / ColaCerveza / Cerveza / Fotografia / Salio
        self.ventanilla = None            # 1 o 2, si corresponde
        self.fue_a_folletos = None        # True / False
        self.tomo_cerveza = None          # True / False / None (no fue elegido a degustar)
        self.fue_a_fotografia = None      # True / False
        self.destino = None               # Destino actual (e.g., 'Ventanilla 1', 'Pintura', 'Salida')

        # --- Duraciones e instantes de finalización de actividades con RND de tiempo ---
        self.duracion_folletos = None
        self.fin_folletos_reloj = None
        self.duracion_pintura = None
        self.fin_pintura_reloj = None
        self.duracion_cerveza = None
        self.fin_cerveza_reloj = None
        self.duracion_fotografia = None
        self.fin_fotografia_reloj = None


        # --- Tiempos / instantes clave (para depurar y para métricas) ---
        self.inicio_cola_informes = None
        self.fin_cola_informes = None
        self.inicio_pintura = None
        self.fin_pintura = None
        self.inicio_cola_cerveza = None
        self.inicio_cerveza = None
        self.fin_cerveza = None
        self.inicio_degustacion = None
        self.fin_degustacion = None
        self.inicio_fotografia = None
        self.fin_fotografia = None
        self.reloj_salida = None

        # --- Números aleatorios usados (para cumplir la consigna de
        #     "mostrar el número aleatorio que se usó para cada variable") ---
        self.rnd_decision_folletos = None
        self.rnd_ventanilla_elegida = None
        self.rnd_tiempo_folletos = None
        self.rnd_tiempo_pintura = None
        self.rnd_decision_fotografia = None
        self.rnd_decision_cerveza = None
        self.rnd_tiempo_cerveza = None
        self.rnd_tiempo_fotografia = None

    def snapshot(self, simulador=None):
        """
        Devuelve un diccionario "plano" con el estado actual del visitante,
        listo para insertarse como columnas del vector de estado.
        """
        # Preparar string para los RNDs del tiempo de pintura (puede ser tupla si es Normal)
        rnd_pintura_str = ""
        if isinstance(self.rnd_tiempo_pintura, tuple):
            rnd_pintura_str = f"{self.rnd_tiempo_pintura[0]:.4f}, {self.rnd_tiempo_pintura[1]:.4f}"
        elif self.rnd_tiempo_pintura is not None:
            rnd_pintura_str = f"{self.rnd_tiempo_pintura:.4f}"

        rnd_foto_str = ""
        if isinstance(self.rnd_tiempo_fotografia, tuple):
            rnd_foto_str = f"{self.rnd_tiempo_fotografia[0]:.4f}, {self.rnd_tiempo_fotografia[1]:.4f}"
        elif self.rnd_tiempo_fotografia is not None:
            rnd_foto_str = f"{self.rnd_tiempo_fotografia:.4f}"
        return {
            "ID": self.id,
            "Puerta": self.puerta,
            "Edad": self.edad,
            "RND_Edad": round(self.rnd_edad, 4),
            "Estado": self.estado,
            "Sala": self.sala_actual,
            "Destino": self.destino if self.destino is not None else "",
            "Llegada": round(self.reloj_llegada, 2),
            "Hora_Llegada": simulador.formatear_hora_reloj(self.reloj_llegada) if simulador is not None else "",
            "RND_Dec_Folletos": round(self.rnd_decision_folletos, 4) if self.rnd_decision_folletos is not None else "",
            "Res_Folletos": "Sí" if self.fue_a_folletos is True else ("No" if self.fue_a_folletos is False else ""),
            "RND_Vent_Elegida": round(self.rnd_ventanilla_elegida, 4) if self.rnd_ventanilla_elegida is not None else "",
            "Res_Vent": self.ventanilla if self.ventanilla is not None else "",
            "RND_Tiempo_Foll": round(self.rnd_tiempo_folletos, 4) if self.rnd_tiempo_folletos is not None else "",
            "Dur_Tiempo_Foll": round(self.duracion_folletos, 2) if self.duracion_folletos is not None else "",
            "Fin_Tiempo_Foll": simulador.formatear_hora_reloj(self.fin_folletos_reloj) if (self.fin_folletos_reloj is not None and simulador is not None) else "",
            "RND_Tiempo_Pintura": rnd_pintura_str,
            "Dur_Tiempo_Pintura": round(self.duracion_pintura, 2) if self.duracion_pintura is not None else "",
            "Fin_Tiempo_Pintura": simulador.formatear_hora_reloj(self.fin_pintura_reloj) if (self.fin_pintura_reloj is not None and simulador is not None) else "",
            "RND_Dec_Foto": round(self.rnd_decision_fotografia, 4) if self.rnd_decision_fotografia is not None else "",
            "Res_Foto": "Sí" if self.fue_a_fotografia is True else ("No" if self.fue_a_fotografia is False else ""),
            "RND_Dec_Cerveza": round(self.rnd_decision_cerveza, 4) if self.rnd_decision_cerveza is not None else "",
            "Res_Cerveza": "Sí" if self.tomo_cerveza is True else ("No" if self.tomo_cerveza is False else ""),
            "RND_Tiempo_Cerveza": round(self.rnd_tiempo_cerveza, 4) if self.rnd_tiempo_cerveza is not None else "",
            "Dur_Tiempo_Cerveza": round(self.duracion_cerveza, 2) if self.duracion_cerveza is not None else "",
            "Fin_Tiempo_Cerveza": simulador.formatear_hora_reloj(self.fin_cerveza_reloj) if (self.fin_cerveza_reloj is not None and simulador is not None) else "",
            "RND_Tiempo_Foto": rnd_foto_str,
            "Dur_Tiempo_Foto": round(self.duracion_fotografia, 2) if self.duracion_fotografia is not None else "",
            "Fin_Tiempo_Foto": simulador.formatear_hora_reloj(self.fin_fotografia_reloj) if (self.fin_fotografia_reloj is not None and simulador is not None) else ""
        }