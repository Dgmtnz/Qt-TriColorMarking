# Importamos las bibliotecas necesarias para el manejo de datos y tipos
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Definimos una enumeración para los tres colores posibles en srTCM
class Color(Enum):
    # Cada color tiene dos valores: el texto plano y el código de color para la UI
    GREEN = ("green", "green")      # Verde: el paquete cabe en el bucket comprometido
    YELLOW = ("yellow", "#DAA520")  # Amarillo: el paquete cabe en el bucket de exceso
    RED = ("red", "red")           # Rojo: el paquete no cabe en ningún bucket

    def __init__(self, plain, color_code):
        self.plain = plain            # Texto que se mostrará en la interfaz
        self.color_code = color_code  # Código de color para la visualización

# Clase que representa un paquete de datos usando dataclass para simplificar
@dataclass
class Packet:
    size: int                     # Tamaño del paquete
    spacing: float                # Tiempo entre este paquete y el anterior
    arrival_time: float           # Tiempo de llegada absoluto
    color: Optional[Color] = None # Color asignado (inicialmente None)

# Clase principal que implementa el algoritmo Token Bucket
class TokenBucket:
    def __init__(self, cir: float, pir: float, cbs: float, pbs: float):
        # Parámetros de configuración
        self.cir = cir  # Committed Information Rate
        self.pir = pir  # Peak Information Rate
        self.cbs = cbs  # Committed Burst Size
        self.pbs = pbs  # Peak Burst Size
        
        # Estado actual de los buckets
        self.tc = cbs   # Tokens en bucket comprometido
        self.tp = pbs   # Tokens en bucket pico
        
        self.last_update = 0.0

    def update(self, current_time: float):
        delta = current_time - self.last_update
        
        # Actualizar tokens según CIR y PIR
        self.tc = min(self.cbs, self.tc + delta * self.cir)
        self.tp = min(self.pbs, self.tp + delta * self.pir)
        
        self.last_update = current_time

    def mark_packet(self, packet: Packet) -> Color:
        self.update(packet.arrival_time)
        
        if self.tc >= packet.size:
            # Si hay suficientes tokens en tc, marcamos como verde
            self.tc -= packet.size
            return Color.GREEN
        elif self.tp >= packet.size:
            # Si hay suficientes tokens en tp, marcamos como amarillo
            self.tp -= packet.size
            return Color.YELLOW
        else:
            # Si no hay suficientes tokens en ningún bucket, marcamos como rojo
            return Color.RED