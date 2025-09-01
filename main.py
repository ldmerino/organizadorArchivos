from PySide6.QtWidgets import QApplication
import sys
from organizer.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Organizador de Archivos")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
