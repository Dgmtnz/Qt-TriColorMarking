# Importamos los widgets y elementos necesarios de PySide6
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal

# Widget personalizado para tabla con validación
class ValidatedTableWidget(QTableWidget):
    # Señal que se emite cuando cambia el estado de validación
    validation_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        # Conectamos el cambio de items con la validación
        self.itemChanged.connect(self._validate_item)
        # Conjunto para mantener las filas válidas
        self.valid_rows = set()

    def _validate_item(self, item):
        row = item.row()
        try:
            # Intentamos convertir el texto a número
            value = float(item.text()) if item.text() else 0
            if value <= 0:
                raise ValueError
            # Si es válido, ponemos fondo blanco
            item.setBackground(QColor("white"))
            
            # Verificamos que ambas columnas de la fila sean válidas
            other_col = 1 if item.column() == 0 else 0
            other_item = self.item(row, other_col)
            if other_item and float(other_item.text()) > 0:
                self.valid_rows.add(row)
            else:
                self.valid_rows.discard(row)
        except ValueError:
            # Si no es válido, ponemos fondo rosa
            item.setBackground(QColor("pink"))
            self.valid_rows.discard(row)

        # Emitimos señal basada en si hay al menos una fila válida
        all_valid = len(self.valid_rows) > 0
        self.validation_changed.emit(all_valid)