"""
Diálogo principal para procesar PDFs - Versión limpia y modularizada
"""
import os
from typing import List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QProgressBar, 
    QTabWidget, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .styles import UIStyles
from .pdf_tabs import ConfigurationTab, ResultsTab, PreviewTab
from ..processors.pdf_processor import PDFProcessor, ProcessResult
from ..processors.pdf_thread import PDFProcessorThread


class PDFProcessorDialog(QDialog):
    """Diálogo principal para procesar PDFs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesador de PDFs - Certificados y Constancias")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 770)
        
        # Aplicar estilos del programa al diálogo
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {UIStyles.COLORS['bg']};
                color: {UIStyles.COLORS['text']};
            }}
        """)
        
        self.results: List[ProcessResult] = []
        self.worker_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # Título principal
        self._create_title(layout)
        
        # Tabs principales
        self._create_tabs(layout)
        
        # Barra de progreso
        self._create_progress_bar(layout)
        
        # Etiqueta de estado
        self._create_status_label(layout)
        
        # Botones principales
        self._create_buttons(layout)
    
    def _create_title(self, layout):
        """Crear título principal"""
        title_label = QLabel("Procesador Automático de PDFs")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(UIStyles.get_title_style())
        layout.addWidget(title_label)
    
    def _create_tabs(self, layout):
        """Crear pestañas principales"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(UIStyles.get_tab_style())
        
        # Crear pestañas
        self.config_tab = ConfigurationTab()
        self.results_tab = ResultsTab()
        self.preview_tab = PreviewTab()
        
        # Agregar pestañas
        self.tab_widget.addTab(self.config_tab, "Configuración")
        self.tab_widget.addTab(self.results_tab, "Resultados") 
        self.tab_widget.addTab(self.preview_tab, "Vista Previa")
        
        layout.addWidget(self.tab_widget)
    
    def _create_progress_bar(self, layout):
        """Crear barra de progreso"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(UIStyles.get_progress_style())
        layout.addWidget(self.progress_bar)
    
    def _create_status_label(self, layout):
        """Crear etiqueta de estado"""
        self.status_label = QLabel("Listo para procesar archivos")
        self.status_label.setStyleSheet(UIStyles.get_status_style())
        layout.addWidget(self.status_label)
    
    def _create_buttons(self, layout):
        """Crear botones principales"""
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Vista Previa")
        self.preview_btn.clicked.connect(self.preview_processing)
        self.preview_btn.setStyleSheet(UIStyles.get_button_style(UIStyles.COLORS['accent']))
        button_layout.addWidget(self.preview_btn)
        
        self.process_btn = QPushButton("Procesar")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setStyleSheet(UIStyles.get_button_style(UIStyles.COLORS['success']))
        button_layout.addWidget(self.process_btn)
        
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setStyleSheet(UIStyles.get_button_style(UIStyles.COLORS['danger']))
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def preview_processing(self):
        """Mostrar vista previa sin procesar"""
        is_valid, error_msg = self.config_tab.validate_config()
        if not is_valid:
            QMessageBox.warning(self, "Error", error_msg)
            return
        
        try:
            config = self.config_tab.get_config()
            
            # Validación específica para organización por trabajador
            if config['process_type'] == 2:  # Organizar por trabajador
                if not self._validate_organize_input(config['input_path']):
                    return
            
            preview_text = self._generate_preview_text(config)
            self.preview_tab.update_preview(preview_text)
            
            # Cambiar a pestaña de vista previa
            self.tab_widget.setCurrentIndex(2)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error generando vista previa: {str(e)}")
    
    def _validate_organize_input(self, input_path: str) -> bool:
        """Validar entrada específica para organización por trabajador"""
        try:
            # Verificar que existan subcarpetas con PDFs procesados
            subfolders_found = 0
            processor = PDFProcessor()
            
            for item in os.listdir(input_path):
                subfolder_path = os.path.join(input_path, item)
                
                if not os.path.isdir(subfolder_path):
                    continue
                
                # Verificar si es una carpeta de tipo reconocido
                doc_type = processor.detect_document_type(item)
                if not doc_type:
                    continue
                
                # Verificar que tenga PDFs
                pdf_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith('.pdf')]
                if pdf_files:
                    subfolders_found += 1
            
            if subfolders_found == 0:
                QMessageBox.warning(
                    self, "Carpetas no válidas",
                    "No se encontraron subcarpetas con PDFs procesados.\n\n"
                    "Busca una carpeta que contenga subcarpetas como:\n"
                    "• PDFs_Procesados_Certificados/\n"
                    "• PDFs_Procesados_5rentas/\n"
                    "• PDFs_Procesados_Constancias/\n\n"
                    "Estas carpetas deben contener archivos PDF ya renombrados con nombres de trabajadores."
                )
                return False
            
            return True
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error validando carpetas: {str(e)}")
            return False
    
    def _generate_preview_text(self, config: dict) -> str:
        """Generar texto de vista previa"""
        try:
            processor = PDFProcessor()
            preview_lines = []
            
            input_path = config['input_path']
            process_type = config['process_type']
            
            if process_type == 0:  # Separar PDF
                preview_lines.append(f"SEPARANDO PDF: {os.path.basename(input_path)}")
                preview_lines.append("-" * 50)
                
                # Obtener información del PDF
                import PyPDF2
                with open(input_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    
                    # Mostrar primeras 5 páginas como ejemplo
                    max_preview = min(5, total_pages)
                    for i in range(max_preview):
                        text = processor.extract_text_from_pdf(input_path, i)
                        worker_name = processor.extract_worker_name(text)
                        
                        if worker_name:
                            clean_name = processor.clean_filename(worker_name)
                            preview_lines.append(f"Página {i+1}: {worker_name}")
                            preview_lines.append(f"  → Archivo: {clean_name}.pdf")
                        else:
                            preview_lines.append(f"Página {i+1}: [Sin nombre detectado]")
                            preview_lines.append(f"  → Archivo: Pagina_{i+1:03d}.pdf")
                    
                    if total_pages > 5:
                        preview_lines.append(f"... y {total_pages - 5} páginas más")
                        
            elif process_type == 1:  # Renombrar individuales
                preview_lines.append(f"RENOMBRANDO PDFs EN: {input_path}")
                preview_lines.append("-" * 50)
                
                pdf_files = [f for f in os.listdir(input_path) if f.lower().endswith('.pdf')][:10]
                
                for pdf_file in pdf_files:
                    full_path = os.path.join(input_path, pdf_file)
                    text = processor.extract_text_from_pdf(full_path)
                    worker_name = processor.extract_worker_name(text)
                    
                    if worker_name:
                        clean_name = processor.clean_filename(worker_name)
                        preview_lines.append(f"'{pdf_file}' → '{clean_name}.pdf'")
                        preview_lines.append(f"  Trabajador: {worker_name}")
                    else:
                        preview_lines.append(f"'{pdf_file}' → [Sin cambios - no se detectó nombre]")
                
                total_pdfs = len([f for f in os.listdir(input_path) if f.lower().endswith('.pdf')])
                if total_pdfs > 10:
                    preview_lines.append(f"... y {total_pdfs - 10} archivos más")
            
            elif process_type == 2:  # Organizar por trabajador
                preview_lines.append(f"ORGANIZANDO POR TRABAJADOR EN: {input_path}")
                preview_lines.append("-" * 60)
                
                # Escanear subcarpetas disponibles
                subfolders_with_pdfs = []
                worker_docs = {}
                
                for item in os.listdir(input_path):
                    subfolder_path = os.path.join(input_path, item)
                    
                    if not os.path.isdir(subfolder_path):
                        continue
                    
                    # Detectar tipo de documento
                    doc_type = processor.detect_document_type(item)
                    if not doc_type:
                        continue
                    
                    # Contar PDFs en la subcarpeta
                    pdf_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith('.pdf')]
                    if pdf_files:
                        subfolders_with_pdfs.append(f"📁 {item} ({len(pdf_files)} PDFs) → {doc_type}")
                        
                        # Analizar algunos archivos para detectar trabajadores
                        for pdf_file in pdf_files[:3]:  # Solo primeros 3 por carpeta
                            worker_name = processor.extract_worker_name_from_filename(pdf_file)
                            if worker_name:
                                if worker_name not in worker_docs:
                                    worker_docs[worker_name] = {}
                                worker_docs[worker_name][doc_type] = pdf_file
                
                # Mostrar carpetas encontradas
                if subfolders_with_pdfs:
                    preview_lines.append("Carpetas procesadas encontradas:")
                    for folder_info in subfolders_with_pdfs:
                        preview_lines.append(f"  {folder_info}")
                    
                    preview_lines.append("")
                    preview_lines.append(f"Trabajadores únicos detectados: {len(worker_docs)}")
                    preview_lines.append("")
                    
                    # Mostrar estructura resultante (primeros 3 trabajadores)
                    preview_lines.append("Estructura resultante (muestra):")
                    preview_lines.append("PDFs_Procesados_Trabajadores/")
                    
                    for i, (worker_name, docs) in enumerate(list(worker_docs.items())[:3]):
                        preview_lines.append(f"  📂 {worker_name}/")
                        for doc_type in docs.keys():
                            preview_lines.append(f"    📄 {worker_name}_{doc_type}.pdf")
                    
                    if len(worker_docs) > 3:
                        preview_lines.append(f"  ... y {len(worker_docs) - 3} trabajadores más")
                else:
                    preview_lines.append("❌ No se encontraron subcarpetas con PDFs procesados")
                    preview_lines.append("Busca carpetas como: PDFs_Procesados_Certificados, PDFs_Procesados_5rentas, etc.")
            
            return "\n".join(preview_lines)
            
        except Exception as e:
            return f"Error generando vista previa: {str(e)}"
    
    def start_processing(self):
        """Iniciar procesamiento en hilo separado"""
        is_valid, error_msg = self.config_tab.validate_config()
        if not is_valid:
            QMessageBox.warning(self, "Error", error_msg)
            return
        
        config = self.config_tab.get_config()
        
        # Validación específica para organización por trabajador
        if config['process_type'] == 2:  # Organizar por trabajador
            if not self._validate_organize_input(config['input_path']):
                return
        
        # Configurar UI para procesamiento
        self._set_processing_state(True)
        
        # Crear y configurar hilo
        process_types = ["separate", "rename", "organize"]
        process_type = process_types[config['process_type']]
        
        self.worker_thread = PDFProcessorThread(
            config['input_path'],
            config['output_path'],
            process_type
        )
        
        # Conectar señales
        self.worker_thread.progress.connect(self.progress_bar.setValue)
        self.worker_thread.status_update.connect(self.status_label.setText)
        self.worker_thread.result_ready.connect(self.handle_results)
        self.worker_thread.finished_processing.connect(self.processing_finished)
        self.worker_thread.error_occurred.connect(self.handle_error)
        
        # Iniciar procesamiento
        self.worker_thread.start()
    
    def _set_processing_state(self, processing: bool):
        """Configurar estado de la UI durante procesamiento"""
        self.process_btn.setEnabled(not processing)
        self.preview_btn.setEnabled(not processing)
        self.progress_bar.setVisible(processing)
        if processing:
            self.progress_bar.setValue(0)
    
    def handle_results(self, results: List[ProcessResult]):
        """Manejar resultados del procesamiento"""
        self.results = results
        
        # Actualizar pestaña de resultados
        self.results_tab.update_results(results)
        
        # Generar y mostrar resumen
        processor = PDFProcessor()
        summary = processor.get_summary(results)
        self.results_tab.update_summary(summary)
        
        # Cambiar a pestaña de resultados
        self.tab_widget.setCurrentIndex(1)
        
        # Asegurar que la tabla sea visible y se ajuste correctamente
        self.results_tab.results_table.show()
        self.results_tab.results_table.resizeColumnsToContents()
    
    def handle_error(self, error_msg: str):
        """Manejar errores del procesamiento"""
        self._set_processing_state(False)
        self.status_label.setText("Error en el procesamiento")
        QMessageBox.critical(self, "Error", f"Error durante el procesamiento:\n{error_msg}")
    
    def processing_finished(self):
        """Procesamiento terminado"""
        self._set_processing_state(False)
        self.status_label.setText("Procesamiento completado")
        
        if self.results:
            # Mostrar mensaje de finalización
            successful = len([r for r in self.results if r.success])
            total = len(self.results)
            
            if successful == total:
                QMessageBox.information(
                    self, "Completado", 
                    f"Todos los archivos ({total}) se procesaron exitosamente."
                )
            elif successful > 0:
                QMessageBox.information(
                    self, "Completado con errores",
                    f"Se procesaron {successful} de {total} archivos exitosamente.\n"
                    "Revisa la pestaña 'Resultados' para más detalles."
                )
            else:
                QMessageBox.warning(
                    self, "Error", 
                    "No se pudo procesar ningún archivo. Revisa los errores en la pestaña 'Resultados'."
                )
    
    def closeEvent(self, event):
        """Manejar cierre del diálogo"""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self, "Procesamiento en curso",
                "Hay un procesamiento en curso. ¿Desea cancelarlo y cerrar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.worker_thread.cancel()
                self.worker_thread.wait()  # Esperar a que termine
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()