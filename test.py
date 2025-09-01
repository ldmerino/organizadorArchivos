from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
import sys

class TestDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Dialog")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("Esta es una prueba")
        layout.addWidget(label)
        
        button = QPushButton("Test Button")
        layout.addWidget(button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = TestDialog()
    dialog.show()
    app.exec()