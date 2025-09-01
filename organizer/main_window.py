from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFileDialog, QMessageBox,
    QTreeView, QToolBar, QInputDialog, QFileSystemModel,
    QStatusBar
)
from PySide6.QtCore import QDir, QModelIndex, Qt
from PySide6.QtGui import QAction
import os
import shutil
from send2trash import send2trash
from .ui.pdf_dialog import PDFProcessorDialog  # Import actualizado
from PySide6.QtCore import QSize

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Organizador de Archivos")
        self.resize(1100, 700)
        
        # Estilo para la ventana principal
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a202c;
                color: #e2e8f0;
            }
            QWidget {
                background-color: #1a202c;
                color: #e2e8f0;
            }
        """)

        # Inicializar historial de navegación ANTES de usar set_root_path
        self._history: list[str] = []
        self._future: list[str] = []

        # Modelo de sistema de archivos
        self.model = QFileSystemModel(self)
        self.model.setReadOnly(False)
        self.model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)

        # Vista de árbol con estilos mejorados
        self.view = QTreeView(self)
        self.view.setModel(self.model)
        self.view.setSortingEnabled(True)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.view.setUniformRowHeights(True)
        self.view.setWordWrap(False)
        self.view.doubleClicked.connect(self.on_double_clicked)
        
        # Estilos para la vista de archivos
        self.view.setStyleSheet("""
            QTreeView {
                background-color: #1a202c;
                color: #e2e8f0;
                border: 1px solid #4a5568;
                border-radius: 8px;
                font-size: 13px;
                gridline-color: #2d3748;
                selection-background-color: rgba(66, 153, 225, 0.3);
                selection-color: #ffffff;
                alternate-background-color: #2d3748;
            }
            QTreeView::item {
                padding: 6px;
                border: none;
            }
            QTreeView::item:hover {
                background-color: rgba(74, 85, 104, 0.5);
            }
            QTreeView::item:selected {
                background-color: rgba(66, 153, 225, 0.4);
                color: #ffffff;
            }
            QTreeView::item:selected:active {
                background-color: rgba(66, 153, 225, 0.5);
            }
            QHeaderView::section {
                background-color: #2d3748;
                color: #e2e8f0;
                padding: 8px;
                border: 1px solid #4a5568;
                font-weight: 600;
            }
            QHeaderView::section:hover {
                background-color: #4a5568;
            }
            QScrollBar:vertical {
                background: #2d3748;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #4a5568;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #718096;
            }
        """)

        # Layout principal
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.addWidget(self.view)
        self.setCentralWidget(central)
        
        # Agregar status bar con estilos
        status_bar = QStatusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2d3748;
                color: #e2e8f0;
                border-top: 1px solid #4a5568;
                padding: 4px;
                font-size: 12px;
            }
        """)
        self.setStatusBar(status_bar)

        tb = QToolBar("Acciones", self)
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        tb.setIconSize(QSize(20, 20))
        tb.setStyleSheet("""
            QToolBar {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 8px;
                padding: 6px;
                spacing: 3px;
            }
            QToolButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 8px 12px;
                margin: 2px;
                font-size: 13px;
                font-weight: 500;
                color: #e2e8f0;
                min-width: 80px;
            }
            QToolButton:hover {
                background: rgba(66, 153, 225, 0.3);
                border-color: #4299e1;
                color: #ffffff;
            }
            QToolButton:pressed {
                background: rgba(66, 153, 225, 0.5);
                border-color: #3182ce;
            }
            QToolButton:disabled {
                color: #718096;
                background: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.1);
            }
            QToolBar::separator {
                background: #4a5568;
                width: 2px;
                margin: 6px 8px;
                border-radius: 1px;
            }
        """)
        self.addToolBar(tb)

        # Crear acciones con símbolos Unicode para mejor identificación
        act_open = QAction("📁 Abrir carpeta", self)
        act_open.setToolTip("Seleccionar una carpeta para navegar")
        act_open.triggered.connect(self.open_folder)
        tb.addAction(act_open)

        act_rename = QAction("✏️ Renombrar", self)
        act_rename.setShortcut("F2")
        act_rename.setToolTip("Renombrar archivo o carpeta (F2)")
        act_rename.triggered.connect(self.rename_selected)
        tb.addAction(act_rename)

        act_move = QAction("📤 Mover", self)
        act_move.setToolTip("Mover archivo a otra ubicación")
        act_move.triggered.connect(self.move_selected)
        tb.addAction(act_move)

        act_delete = QAction("🗑️ Eliminar", self)
        act_delete.setToolTip("Enviar archivo a la papelera")
        act_delete.triggered.connect(self.delete_selected)
        tb.addAction(act_delete)

        act_refresh = QAction("🔄 Actualizar", self)
        act_refresh.setToolTip("Actualizar vista de archivos")
        act_refresh.triggered.connect(self.refresh)
        tb.addAction(act_refresh)

        tb.addSeparator()

        # Botones de navegación con símbolos Unicode
        self.back_btn = QAction("◀ Atrás", self)
        self.back_btn.setShortcut("Alt+Left")
        self.back_btn.setToolTip("Ir a carpeta anterior (Alt+Left)")
        self.back_btn.triggered.connect(self.go_back)
        self.back_btn.setEnabled(False)
        tb.addAction(self.back_btn)

        self.forward_btn = QAction("▶ Adelante", self)
        self.forward_btn.setShortcut("Alt+Right") 
        self.forward_btn.setToolTip("Ir a carpeta siguiente (Alt+Right)")
        self.forward_btn.triggered.connect(self.go_forward)
        self.forward_btn.setEnabled(False)
        tb.addAction(self.forward_btn)

        self.up_btn = QAction("⬆ Subir", self)
        self.up_btn.setShortcut("Alt+Up")
        self.up_btn.setToolTip("Subir un nivel en la jerarquía (Alt+Up)")
        self.up_btn.triggered.connect(self.go_up)
        tb.addAction(self.up_btn)

        tb.addSeparator()

        act_pdf_processor = QAction("📄 Procesar PDFs", self)
        act_pdf_processor.setToolTip("Procesar certificados y constancias laborales automáticamente")
        act_pdf_processor.triggered.connect(self.open_pdf_processor)
        tb.addAction(act_pdf_processor)

        # Establece carpeta inicial a Home
        home = QDir.homePath()
        self.set_root_path(home)

    # ----- Métodos de navegación -----
    def set_root_path(self, path: str):
        current_root = self.view.rootIndex()
        if current_root.isValid():
            current_path = self.model.filePath(current_root)
            if current_path != path and (not self._history or current_path != self._history[-1]):
                self._history.append(current_path)
                self._future.clear()
        
        root_index = self.model.setRootPath(path)
        self.view.setRootIndex(root_index)
        self.view.resizeColumnToContents(0)
        self.update_navigation_buttons()

    def go_back(self):
        if len(self._history) > 0:
            current_root = self.view.rootIndex()
            if current_root.isValid():
                current_path = self.model.filePath(current_root)
                self._future.insert(0, current_path)
            
            previous_path = self._history.pop()
            root_index = self.model.setRootPath(previous_path)
            self.view.setRootIndex(root_index)
            self.view.resizeColumnToContents(0)
            self.update_navigation_buttons()

    def go_forward(self):
        if len(self._future) > 0:
            current_root = self.view.rootIndex()
            if current_root.isValid():
                current_path = self.model.filePath(current_root)
                self._history.append(current_path)
            
            next_path = self._future.pop(0)
            root_index = self.model.setRootPath(next_path)
            self.view.setRootIndex(root_index)
            self.view.resizeColumnToContents(0)
            self.update_navigation_buttons()

    def go_up(self):
        current_root = self.view.rootIndex()
        if current_root.isValid():
            current_path = self.model.filePath(current_root)
            parent_path = os.path.dirname(current_path)
            if parent_path != current_path:
                self.set_root_path(parent_path)

    def update_navigation_buttons(self):
        self.back_btn.setEnabled(len(self._history) > 0)
        self.forward_btn.setEnabled(len(self._future) > 0)
        
        current_root = self.view.rootIndex()
        if current_root.isValid():
            current_path = self.model.filePath(current_root)
            parent_path = os.path.dirname(current_path)
            self.up_btn.setEnabled(parent_path != current_path)
        else:
            self.up_btn.setEnabled(False)

    # ----- Helpers de UI -----
    def current_index(self) -> QModelIndex:
        idx = self.view.currentIndex()
        if not idx.isValid():
            return QModelIndex()
        return idx

    def open_pdf_processor(self):
        dialog = PDFProcessorDialog(self)
        current_root = self.view.rootIndex()
        if current_root.isValid():
            current_path = self.model.filePath(current_root)
            try:
                pdf_files = [f for f in os.listdir(current_path) if f.lower().endswith('.pdf')]
                if pdf_files:
                    dialog.config_tab.input_path.setText(current_path)
            except (PermissionError, FileNotFoundError):
                pass
        dialog.exec()

    # ----- Slots/Acciones -----
    def open_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Selecciona una carpeta")
        if path:
            self.set_root_path(path)

    def on_double_clicked(self, index: QModelIndex):
        if self.model.isDir(index):
            folder_path = self.model.filePath(index)
            self.set_root_path(folder_path)

    def rename_selected(self):
        idx = self.current_index()
        if not idx.isValid():
            QMessageBox.information(self, "Renombrar", "Selecciona un elemento en la lista.")
            return

        path = self.model.filePath(idx)
        base_dir = os.path.dirname(path)
        old_name = os.path.basename(path)

        new_name, ok = QInputDialog.getText(self, "Renombrar", f"Nuevo nombre para:\n{old_name}")
        if not ok or not new_name.strip():
            return

        new_path = os.path.join(base_dir, new_name)
        if os.path.exists(new_path):
            QMessageBox.warning(self, "Renombrar", "Ya existe un archivo con ese nombre.")
            return

        try:
            os.rename(path, new_path)
            self.statusBar().showMessage(f"Renombrado: {old_name} -> {new_name}", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo renombrar: {e}")

    def move_selected(self):
        idx = self.current_index()
        if not idx.isValid():
            QMessageBox.information(self, "Mover", "Selecciona un elemento en la lista.")
            return

        src_path = self.model.filePath(idx)
        target_dir = QFileDialog.getExistingDirectory(self, "Mover a carpeta...")
        if not target_dir:
            return

        dst_path = os.path.join(target_dir, os.path.basename(src_path))
        if os.path.abspath(src_path) == os.path.abspath(dst_path):
            return

        if os.path.exists(dst_path):
            QMessageBox.warning(self, "Mover", "El destino ya contiene un archivo con el mismo nombre.")
            return

        try:
            shutil.move(src_path, dst_path)
            self.statusBar().showMessage(f"Movido a: {dst_path}", 4000)
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo mover: {e}")

    def delete_selected(self):
        idx = self.current_index()
        if not idx.isValid():
            QMessageBox.information(self, "Eliminar", "Selecciona un elemento en la lista.")
            return

        path = self.model.filePath(idx)
        file_name = os.path.basename(path)
        
        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", f"El archivo ya no existe:\n{path}")
            return
            
        reply = QMessageBox.question(
            self, "Eliminar a Papelera",
            f"¿Enviar a la papelera?\n\n{file_name}\n\nRuta: {path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            normalized_path = os.path.normpath(path)
            send2trash(normalized_path)
            self.statusBar().showMessage(f"'{file_name}' enviado a papelera.", 4000)
            self.refresh()
        except Exception as e:
            error_msg = str(e)
            reply = QMessageBox.question(
                self, "Error al enviar a papelera", 
                f"No se pudo enviar a la papelera:\n{error_msg}\n\n"
                f"¿Desea eliminar permanentemente el archivo?\n"
                f"ADVERTENCIA: Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    if os.path.isfile(normalized_path):
                        os.remove(normalized_path)
                    elif os.path.isdir(normalized_path):
                        shutil.rmtree(normalized_path)
                    
                    self.statusBar().showMessage(f"'{file_name}' eliminado permanentemente.", 4000)
                    self.refresh()
                except Exception as e2:
                    QMessageBox.critical(self, "Error", f"No se pudo eliminar el archivo:\n{e2}")

    def refresh(self):
        current_root = self.view.rootIndex()
        if current_root.isValid():
            self.view.resizeColumnToContents(0)