# Importamos todos los widgets necesarios de PySide6
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QSpinBox, QLabel, QHeaderView,
                              QProgressBar, QGroupBox, QTableWidgetItem, 
                              QTableWidget)
from PySide6.QtCore import Qt, QTimer  # Importamos elementos core de Qt
from PySide6.QtGui import QColor       # Importamos QColor para el manejo de colores
from custom_widgets import ValidatedTableWidget  # Nuestro widget personalizado
from models import TokenBucket, Packet, Color    # Nuestros modelos de datos

# Clase para visualizar el estado de los token buckets
class TokenBucketVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Visualización de CBS
        cbs_group = QGroupBox("Committed Bucket (CBS)")
        cbs_layout = QVBoxLayout(cbs_group)
        self.cbs_bar = QProgressBar()
        self.cbs_label = QLabel("0/0")
        self.cir_label = QLabel("CIR: 0")
        cbs_layout.addWidget(self.cbs_bar)
        cbs_layout.addWidget(self.cbs_label)
        cbs_layout.addWidget(self.cir_label)
        
        # Visualización de PBS
        pbs_group = QGroupBox("Peak Bucket (PBS)")
        pbs_layout = QVBoxLayout(pbs_group)
        self.pbs_bar = QProgressBar()
        self.pbs_label = QLabel("0/0")
        self.pir_label = QLabel("PIR: 0")
        pbs_layout.addWidget(self.pbs_bar)
        pbs_layout.addWidget(self.pbs_label)
        pbs_layout.addWidget(self.pir_label)
        
        layout.addWidget(cbs_group)
        layout.addWidget(pbs_group)

    def update_visualization(self, cbs: float, pbs: float, cbs_max: float, 
                           pbs_max: float, cir: float, pir: float):
        self.cbs_bar.setMaximum(int(cbs_max))
        self.cbs_bar.setValue(int(cbs))
        self.cbs_label.setText(f"{cbs:.2f}/{cbs_max:.2f}")
        self.cir_label.setText(f"CIR: {cir:.2f}")
        
        self.pbs_bar.setMaximum(int(pbs_max))
        self.pbs_bar.setValue(int(pbs))
        self.pbs_label.setText(f"{pbs:.2f}/{pbs_max:.2f}")
        self.pir_label.setText(f"PIR: {pir:.2f}")

# Ventana principal de la aplicación
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("trTCM Calculator")
        self.setMinimumSize(1000, 800)
        
        # Creamos el widget central y su layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Creamos los inputs para los parámetros
        params_layout = self._create_param_inputs()
        layout.addLayout(params_layout)
        
        # Añadimos el visualizador de token buckets
        self.visualizer = TokenBucketVisualizer()
        layout.addWidget(self.visualizer)
        
        # Creamos la tabla de entrada de paquetes
        self.input_table = ValidatedTableWidget()
        self.input_table.setColumnCount(2)
        self.input_table.setHorizontalHeaderLabels(["Size", "Spacing"])
        self.input_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.input_table)
        
        # Creamos los botones de control
        buttons_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("Add Row")
        self.remove_row_btn = QPushButton("Remove Row")
        self.step_btn = QPushButton("Step")
        self.auto_btn = QPushButton("Auto")
        self.reset_btn = QPushButton("Reset")
        
        # Añadimos todos los botones al layout
        for btn in (self.add_row_btn, self.remove_row_btn, self.step_btn, 
                   self.auto_btn, self.reset_btn):
            buttons_layout.addWidget(btn)
        layout.addLayout(buttons_layout)
        
        # Creamos la tabla de resultados
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(
            ["Size", "Arrival Time", "Color", "Tc", "Tp"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.results_table)
        
        # Inicializamos el estado de la aplicación
        self.current_row = 0
        self.token_bucket = None
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._step)
        
        # Conectamos las señales de los botones
        self.add_row_btn.clicked.connect(self._add_row)
        self.remove_row_btn.clicked.connect(self._remove_row)
        self.step_btn.clicked.connect(self._step)
        self.auto_btn.clicked.connect(self._toggle_auto)
        self.reset_btn.clicked.connect(self._reset)
        self.input_table.validation_changed.connect(self._update_button_states)
        
        # Añadimos una fila inicial y reseteamos
        self._add_row()
        self._reset()

    # Crea un input para parámetros con etiqueta y spinbox
    def _create_param_input(self, label: str, default: int) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        spinbox = QSpinBox()
        spinbox.setRange(1, 1000000)
        spinbox.setValue(default)
        layout.addWidget(spinbox)
        return layout

    # Añade una nueva fila a la tabla de entrada
    def _add_row(self):
        row = self.input_table.rowCount()
        self.input_table.insertRow(row)
        self.input_table.setItem(row, 0, QTableWidgetItem(""))
        self.input_table.setItem(row, 1, QTableWidgetItem(""))

    # Elimina la última fila de la tabla de entrada
    def _remove_row(self):
        row = self.input_table.rowCount() - 1
        if row >= 0:
            self.input_table.removeRow(row)

    # Resetea el estado de la aplicación
    def _reset(self):
        self.current_row = 0
        cir = self.cir_input.itemAt(1).widget().value()
        pir = self.pir_input.itemAt(1).widget().value()
        cbs = self.cbs_input.itemAt(1).widget().value()
        pbs = self.pbs_input.itemAt(1).widget().value()
        
        self.token_bucket = TokenBucket(cir=cir, pir=pir, cbs=cbs, pbs=pbs)
        self.results_table.setRowCount(0)
        
        self.visualizer.update_visualization(
            self.token_bucket.tc,
            self.token_bucket.tp,
            cbs,
            pbs,
            cir,
            pir
        )
        
        self._update_button_states()

    # Procesa un paso de la simulación
    def _step(self):
        if self.current_row >= self.input_table.rowCount():
            self.animation_timer.stop()
            self.auto_btn.setText("Auto")
            return False

        size_item = self.input_table.item(self.current_row, 0)
        spacing_item = self.input_table.item(self.current_row, 1)

        if not size_item or not spacing_item:
            self.current_row += 1
            return False

        try:
            # Validamos que ambos valores sean números positivos
            size = float(size_item.text())
            spacing = float(spacing_item.text())
            
            if size <= 0 or spacing <= 0:
                raise ValueError
            
            # Calculamos el tiempo de llegada
            if self.current_row == 0:
                arrival_time = spacing
            else:
                prev_arrival = float(self.results_table.item(self.current_row - 1, 1).text())
                arrival_time = prev_arrival + spacing

            # Creamos y procesamos el paquete
            packet = Packet(size=int(size), spacing=spacing, arrival_time=arrival_time)
            color = self.token_bucket.mark_packet(packet)

            # Añadimos los resultados a la tabla
            self.results_table.insertRow(self.current_row)
            self.results_table.setItem(self.current_row, 0, QTableWidgetItem(str(size)))
            self.results_table.setItem(self.current_row, 1, QTableWidgetItem(f"{arrival_time:.2f}"))
            color_item = QTableWidgetItem(color.plain)
            color_item.setForeground(QColor(color.color_code))
            self.results_table.setItem(self.current_row, 2, color_item)
            self.results_table.setItem(self.current_row, 3, QTableWidgetItem(f"{self.token_bucket.tc:.2f}"))
            self.results_table.setItem(self.current_row, 4, QTableWidgetItem(f"{self.token_bucket.tp:.2f}"))

            # Actualizamos la visualización
            self.visualizer.update_visualization(
                self.token_bucket.tc,
                self.token_bucket.tp,
                self.token_bucket.cbs,
                self.token_bucket.pbs,  # Cambiado de ebs a pbs
                self.token_bucket.cir,
                self.token_bucket.pir
            )

            self.current_row += 1
            return True

        except ValueError:
            self.current_row += 1
            return False

    # Alterna entre ejecución automática y manual
    def _toggle_auto(self):
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.auto_btn.setText("Auto")
        else:
            self.animation_timer.start(1000)  # Intervalo de 1 segundo
            self.auto_btn.setText("Stop")

    # Actualiza el estado de los botones según la validación
    def _update_button_states(self, is_valid=False):
        has_rows = self.input_table.rowCount() > 0
        can_continue = self.current_row < self.input_table.rowCount()
        
        # Verificamos si hay filas válidas en la tabla
        valid_rows = len(self.input_table.valid_rows) > 0
        
        self.step_btn.setEnabled(has_rows and (valid_rows or is_valid) and can_continue)
        self.auto_btn.setEnabled(has_rows and (valid_rows or is_valid) and can_continue)
        self.remove_row_btn.setEnabled(has_rows)

    def _create_param_inputs(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        
        # Creamos los inputs para CIR, PIR, CBS y PBS
        self.cir_input = self._create_param_input("CIR:", 1000)
        self.pir_input = self._create_param_input("PIR:", 2000)
        self.cbs_input = self._create_param_input("CBS:", 2000)
        self.pbs_input = self._create_param_input("PBS:", 4000)
        
        for widget in (self.cir_input, self.pir_input, 
                      self.cbs_input, self.pbs_input):
            layout.addLayout(widget)
        
        return layout