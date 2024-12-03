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
    def __init__(self, cir: float, cbs: float, ebs: float):
        # Inicializamos los parámetros del token bucket
        self.cir = cir          # Tasa de tokens (no usado en este caso)
        self.cbs = cbs          # Tamaño máximo del bucket comprometido
        self.ebs = ebs          # Tamaño máximo del bucket de exceso
        self.tc = cbs           # Tokens actuales en bucket comprometido
        self.te = ebs           # Tokens actuales en bucket de exceso
        self.last_update = 0.0  # Último tiempo de actualización

    def update(self, current_time: float):
        # Calculamos el tiempo transcurrido desde la última actualización
        delta = current_time - self.last_update
        # Calculamos los nuevos tokens generados
        new_tokens = delta * self.cir
        
        # Primero llenamos el bucket tc
        tokens_for_tc = min(self.cbs - self.tc, new_tokens)
        self.tc += tokens_for_tc
        
        # Si sobran tokens, los usamos para llenar te
        remaining_tokens = new_tokens - tokens_for_tc
        if remaining_tokens > 0:
            self.te = min(self.ebs, self.te + remaining_tokens)
        
        self.last_update = current_time

    def mark_packet(self, packet: Packet) -> Color:
        # Actualizamos los tokens antes de procesar el paquete
        self.update(packet.arrival_time)
        
        # Aplicamos el algoritmo srTCM
        if self.tc >= packet.size:
            # Si hay suficientes tokens en tc, marcamos como verde
            self.tc -= packet.size
            return Color.GREEN
        elif self.te >= packet.size:
            # Si hay suficientes tokens en te, marcamos como amarillo
            self.te -= packet.size
            return Color.YELLOW
        else:
            # Si no hay suficientes tokens en ningún bucket, marcamos como rojo
            return Color.RED