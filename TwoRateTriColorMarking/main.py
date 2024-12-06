# Importamos las bibliotecas necesarias
import sys
from PySide6.QtWidgets import QApplication, QTableWidget
from main_window import MainWindow

# Función para aplicar estilos a la aplicación
def apply_styles(app):
    # Establecemos el estilo Fusion como base
    app.setStyle('Fusion')
    
    # Definimos los estilos CSS para cada componente
    app.setStyleSheet("""
        /* Estilo para la ventana principal */
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        /* Estilo para las barras de progreso */
        QProgressBar {
            border: 1px solid #bbb;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #3498db;
        }
        
        /* Estilo para los botones */
        QPushButton {
            padding: 5px 15px;
            border: 1px solid #bbb;
            border-radius: 4px;
            background-color: #fff;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton:disabled {
            background-color: #f0f0f0;
            color: #999;
        }
        
        /* Estilo para las tablas */
        QTableWidget {
            gridline-color: #ddd;
        }
    """)

# Punto de entrada de la aplicación
if __name__ == "__main__":
    # Creamos la aplicación
    app = QApplication(sys.argv)
    # Aplicamos los estilos
    apply_styles(app)
    # Creamos y mostramos la ventana principal
    window = MainWindow()
    window.show()
    # Iniciamos el bucle de eventos
    sys.exit(app.exec()) 