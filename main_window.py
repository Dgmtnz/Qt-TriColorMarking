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
        # Creamos el layout principal
        layout = QVBoxLayout(self)
        
        # Visualización de tokens comprometidos (tc)
        tc_group = QGroupBox("Committed Tokens")
        tc_layout = QVBoxLayout(tc_group)
        self.tc_bar = QProgressBar()  # Barra de progreso para tc
        self.tc_label = QLabel("0/0")  # Etiqueta para mostrar valores tc
        tc_layout.addWidget(self.tc_bar)
        tc_layout.addWidget(self.tc_label)
        
        # Visualización de tokens de exceso (te)
        te_group = QGroupBox("Excess Tokens")
        te_layout = QVBoxLayout(te_group)
        self.te_bar = QProgressBar()  # Barra de progreso para te
        self.te_label = QLabel("0/0")  # Etiqueta para mostrar valores te
        te_layout.addWidget(self.te_bar)
        te_layout.addWidget(self.te_label)
        
        # Añadimos ambos grupos al layout principal
        layout.addWidget(tc_group)
        layout.addWidget(te_group)

    # Método para actualizar la visualización de los buckets
    def update_visualization(self, tc: float, te: float, cbs: float, ebs: float):
        # Actualizamos la barra y etiqueta de tc
        self.tc_bar.setMaximum(int(cbs))
        self.tc_bar.setValue(int(tc))
        self.tc_label.setText(f"{tc:.2f}/{cbs:.2f}")
        
        # Actualizamos la barra y etiqueta de te
        self.te_bar.setMaximum(int(ebs))
        self.te_bar.setValue(int(te))
        self.te_label.setText(f"{te:.2f}/{ebs:.2f}")

# Ventana principal de la aplicación
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("srTCM Calculator")
        self.setMinimumSize(1000, 800)
        
        # Creamos el widget central y su layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Creamos los inputs para los parámetros CBS y EBS
        params_layout = QHBoxLayout()
        self.cbs_input = self._create_param_input("CBS:", 2000)
        self.ebs_input = self._create_param_input("EBS:", 2000)
        for widget in (self.cbs_input, self.ebs_input):
            params_layout.addLayout(widget)
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
            ["Size", "Arrival Time", "Color", "Tc", "Te"])
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
        cbs = self.cbs_input.itemAt(1).widget().value()
        ebs = self.ebs_input.itemAt(1).widget().value()
        self.token_bucket = TokenBucket(cir=1.0, cbs=cbs, ebs=ebs)
        
        self.results_table.setRowCount(0)
        
        self.visualizer.update_visualization(
            self.token_bucket.tc,
            self.token_bucket.te,
            cbs,
            ebs
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

        if size_item and spacing_item:
            try:
                # Obtenemos los datos del paquete
                size = int(size_item.text())
                spacing = float(spacing_item.text())
                arrival_time = spacing if self.current_row == 0 else \
                    float(self.results_table.item(self.current_row - 1, 1).text()) + spacing

                # Creamos y procesamos el paquete
                packet = Packet(size=size, spacing=spacing, arrival_time=arrival_time)
                color = self.token_bucket.mark_packet(packet)

                # Añadimos los resultados a la tabla
                self.results_table.insertRow(self.current_row)
                self.results_table.setItem(self.current_row, 0, QTableWidgetItem(str(size)))
                self.results_table.setItem(self.current_row, 1, QTableWidgetItem(f"{arrival_time:.2f}"))
                color_item = QTableWidgetItem(color.plain)
                color_item.setForeground(QColor(color.color_code))
                self.results_table.setItem(self.current_row, 2, color_item)
                self.results_table.setItem(self.current_row, 3, QTableWidgetItem(f"{self.token_bucket.tc:.2f}"))
                self.results_table.setItem(self.current_row, 4, QTableWidgetItem(f"{self.token_bucket.te:.2f}"))

                # Actualizamos la visualización
                self.visualizer.update_visualization(
                    self.token_bucket.tc,
                    self.token_bucket.te,
                    self.token_bucket.cbs,
                    self.token_bucket.ebs
                )

                self.current_row += 1
                return True

            except ValueError:
                self.current_row += 1
                return False
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
        self.step_btn.setEnabled(has_rows and is_valid and 
                                self.current_row < self.input_table.rowCount())
        self.auto_btn.setEnabled(has_rows and is_valid and 
                                self.current_row < self.input_table.rowCount())