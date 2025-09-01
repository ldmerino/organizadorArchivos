"""
Pestañas para el procesador de PDFs
"""
import os
from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox,
    QCheckBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from .styles import UIStyles
from ..processors.pdf_processor import ProcessResult
from ..processors.pdf_thread import PDFProcessorThread


class ConfigurationTab(QWidget):
    """Pestaña de configuración del procesador"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Crear scroll area para contenido largo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Grupo: Archivos de entrada
        input_group = QGroupBox("Archivos de Entrada")
        input_group.setStyleSheet(UIStyles.get_group_style())
        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(10)
        
        input_layout.addWidget(QLabel("Carpeta/Archivo:"), 0, 0)
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Selecciona la carpeta o archivo PDF a procesar...")
        self.input_path.setStyleSheet(UIStyles.get_input_style())
        self.input_path.setMinimumHeight(40)
        input_layout.addWidget(self.input_path, 0, 1)
        
        self.browse_input_btn = QPushButton("Examinar...")
        self.browse_input_btn.setStyleSheet(UIStyles.get_small_button_style())
        self.browse_input_btn.setFixedSize(120, 40)
        input_layout.addWidget(self.browse_input_btn, 0, 2)
        
        # Tipo de procesamiento
        input_layout.addWidget(QLabel("Tipo de proceso:"), 1, 0)
        self.process_type = QComboBox()
        self.process_type.addItems([
            "Separar PDF multi-página → archivos individuales",
            "Renombrar PDFs → nombres de trabajadores",
            "Organizar por trabajador → carpetas individuales"
        ])
        self.process_type.setStyleSheet(UIStyles.get_combobox_style())
        input_layout.addWidget(self.process_type, 1, 1, 1, 2)
        
        # Inicializar placeholders
        self.update_placeholders()
        
        input_layout.setColumnStretch(1, 1)
        layout.addWidget(input_group)
        
        # Grupo: Salida
        output_group = QGroupBox("Carpeta de Salida")
        output_group.setStyleSheet(UIStyles.get_group_style())
        output_layout = QGridLayout(output_group)
        output_layout.setSpacing(10)
        
        output_layout.addWidget(QLabel("Carpeta destino:"), 0, 0)
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Carpeta donde se guardarán los archivos procesados...")
        self.output_path.setStyleSheet(UIStyles.get_input_style())
        self.output_path.setMinimumHeight(40)
        output_layout.addWidget(self.output_path, 0, 1)
        
        self.browse_output_btn = QPushButton("Examinar...")
        self.browse_output_btn.setStyleSheet(UIStyles.get_small_button_style())
        self.browse_output_btn.setFixedSize(120, 40)
        output_layout.addWidget(self.browse_output_btn, 0, 2)
        
        output_layout.setColumnStretch(1, 1)
        layout.addWidget(output_group)
        
        # Layout horizontal para guía de uso
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(15)
        
        # Información de uso (ocupa todo el ancho)
        info_group = QGroupBox("Guía de Uso")
        info_group.setStyleSheet(UIStyles.get_group_style())
        info_layout = QVBoxLayout(info_group)

        info_text = (
            "Explicación detallada:\n\n"
            "1) Separar PDF multi-página\n"
            "   Entrada: Un PDF con 50 páginas de certificados\n"
            "   Resultado: 50 archivos individuales: \"Juan Pérez.pdf\", \"María García.pdf\", ...\n\n"
            "2) Renombrar PDFs individuales\n"
            "   Entrada: Carpeta con 'doc1.pdf', 'archivo_123.pdf', 'temp.pdf'\n"
            "   Resultado: 'Carlos López.pdf', 'Ana Martínez.pdf', 'Pedro Silva.pdf'\n\n"
            "3) Organizar por trabajador\n"
            "   Entrada: Carpeta con PDFs_Procesados_Certificados/, PDFs_Procesados_5rentas/, etc.\n"
            "   Resultado: PDFs_Procesados_Trabajadores/Juan Pérez/Juan Pérez_Certificados.pdf, etc.\n\n"
            "Documentos compatibles: Certificados laborales, Constancias de trabajo,\n"
            "Rentas 5ta categoría, Documentos con DNI.\n\n"
            "Tip: usa 'Vista Previa' para verificar que los nombres se extraigan correctamente."
        )
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet(UIStyles.get_status_style())
        info_layout.addWidget(info_label)
        
        horizontal_layout.addWidget(info_group)
        layout.addLayout(horizontal_layout)
        
        # Configurar scroll area
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Conectar señales
        self.browse_input_btn.clicked.connect(self.browse_input)
        self.browse_output_btn.clicked.connect(self.browse_output)
        
        # Conectar cambio de tipo de proceso para actualizar placeholders
        self.process_type.currentIndexChanged.connect(self.update_placeholders)
    
    def update_placeholders(self):
        """Actualizar placeholders según el tipo de procesamiento seleccionado"""
        process_index = self.process_type.currentIndex()
        
        if process_index == 0:  # Separar PDF multi-página
            self.input_path.setPlaceholderText("Selecciona un archivo PDF multi-página a separar...")
        elif process_index == 1:  # Renombrar PDFs individuales  
            self.input_path.setPlaceholderText("Selecciona carpeta con archivos PDF individuales...")
        elif process_index == 2:  # Organizar por trabajador
            self.input_path.setPlaceholderText("Selecciona carpeta padre con subcarpetas procesadas (PDFs_Procesados_*)...")
    
    def browse_input(self):
        """Buscar carpeta o archivo de entrada según el tipo de procesamiento"""
        process_index = self.process_type.currentIndex()
        
        if process_index == 0:  # Separar PDF multi-página
            path, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar PDF multi-página", "", "PDF Files (*.pdf)"
            )
        elif process_index == 1:  # Renombrar PDFs individuales
            path = QFileDialog.getExistingDirectory(
                self, "Seleccionar carpeta con PDFs individuales"
            )
        elif process_index == 2:  # Organizar por trabajador
            path = QFileDialog.getExistingDirectory(
                self, "Seleccionar carpeta padre con subcarpetas procesadas"
            )
        else:
            return
        
        if path:
            self.input_path.setText(path)
            
            # Sugerir carpeta de salida automáticamente
            if not self.output_path.text():
                if process_index == 0:  # Separar PDF
                    suggested_output = os.path.join(os.path.dirname(path), "PDFs_Procesados")
                elif process_index == 1:  # Renombrar
                    suggested_output = os.path.join(path, "PDFs_Procesados")
                elif process_index == 2:  # Organizar por trabajador
                    suggested_output = os.path.join(path, "PDFs_Procesados_Trabajadores")
                
                self.output_path.setText(suggested_output)
    
    def browse_output(self):
        """Buscar carpeta de salida"""
        path = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de destino"
        )
        if path:
            self.output_path.setText(path)
    
    def get_config(self) -> dict:
        """Obtener configuración actual"""
        return {
            'input_path': self.input_path.text(),
            'output_path': self.output_path.text(),
            'process_type': self.process_type.currentIndex()
        }
    
    def validate_config(self) -> tuple[bool, str]:
        """Validar configuración actual"""
        if not self.input_path.text():
            return False, "Selecciona una carpeta o archivo de entrada"
            
        if not os.path.exists(self.input_path.text()):
            return False, "La ruta de entrada no existe"
            
        if not self.output_path.text():
            return False, "Selecciona una carpeta de salida"
            
        return True, ""


class ResultsTab(QWidget):
    """Pestaña de resultados del procesamiento"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # Resumen estadístico
        self.summary_label = QLabel("Sin resultados aún")
        self.summary_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f4fd;")
        layout.addWidget(self.summary_label)
        
        # Tabla de resultados
        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels([
            "Archivo Original", "Nuevo Nombre", "Trabajador", "Estado", "Error"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)
        
    def update_results(self, results: List[ProcessResult]):
        """Actualizar tabla con nuevos resultados"""
        self.results_table.setRowCount(len(results))
        
        for i, result in enumerate(results):
            self.results_table.setItem(i, 0, QTableWidgetItem(result.original_file))
            self.results_table.setItem(i, 1, QTableWidgetItem(result.new_name or ""))
            self.results_table.setItem(i, 2, QTableWidgetItem(result.worker_name or ""))
            self.results_table.setItem(i, 3, QTableWidgetItem("Exitoso" if result.success else "Error"))
            self.results_table.setItem(i, 4, QTableWidgetItem(result.error or ""))
            
            # Colorear filas según resultado
            if result.success:
                color = QColor("#d4edda")  # Verde claro
            else:
                color = QColor("#f8d7da")  # Rojo claro
                
            for j in range(5):
                self.results_table.item(i, j).setBackground(color)
    
    def update_summary(self, summary: dict):
        """Actualizar resumen estadístico"""
        summary_text = (
            f"Resumen del procesamiento:\n"
            f"• Total procesados: {summary['total_processed']}\n"
            f"• Exitosos: {summary['successful']}\n"
            f"• Con errores: {summary['failed']}\n"
            f"• Tasa de éxito: {summary['success_rate']:.1f}%\n"
            f"• Trabajadores únicos encontrados: {summary['workers_found']}"
        )
        self.summary_label.setText(summary_text)


class PreviewTab(QWidget):
    """Pestaña de vista previa del procesamiento"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # Encabezado informativo
        info_layout = QHBoxLayout()
        
        preview_label = QLabel("Vista previa del procesamiento:")
        preview_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        info_layout.addWidget(preview_label)
        
        info_layout.addStretch()
        
        help_label = QLabel("Tip: Revisa los nombres detectados antes de procesar")
        help_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        info_layout.addWidget(help_label)
        
        layout.addLayout(info_layout)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet(UIStyles.get_textedit_style())
        
        # Texto inicial informativo
        initial_text = """
┌─ VISTA PREVIA DEL PROCESAMIENTO ─┐

Para ver qué archivos se procesarán y cómo quedarán nombrados:

1. Selecciona una carpeta o archivo PDF en la pestaña "Configuración"
2. Elige el tipo de procesamiento que deseas
3. Haz clic en el botón "Vista Previa" (abajo)

Aquí verás:
• Los nombres originales de los archivos
• Los nuevos nombres que se asignarán
• Los trabajadores detectados en cada documento
• Cualquier problema o archivo que no se pueda procesar

Esto te permitirá verificar que todo esté correcto antes de ejecutar 
el procesamiento real.
        """
        
        self.preview_text.setPlainText(initial_text)
        layout.addWidget(self.preview_text)
        
    def update_preview(self, preview_text: str):
        """Actualizar contenido de la vista previa"""
        self.preview_text.setPlainText(preview_text)
        
    def clear_preview(self):
        """Limpiar vista previa"""
        initial_text = """
┌─ VISTA PREVIA DEL PROCESAMIENTO ─┐

Esperando configuración válida para mostrar vista previa...
        """
        self.preview_text.setPlainText(initial_text)