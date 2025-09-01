"""
Threading para procesamiento de PDFs sin bloquear la interfaz de usuario
"""
import os
from typing import List
from PySide6.QtCore import QThread, Signal

from .pdf_processor import PDFProcessor, ProcessResult


class PDFProcessorThread(QThread):
    """
    Hilo para procesar PDFs sin bloquear la UI
    
    Signals:
        progress: Progreso del procesamiento (0-100)
        status_update: Actualización del estado actual
        result_ready: Resultados listos (List[ProcessResult])
        finished_processing: Procesamiento completado
        error_occurred: Error durante el procesamiento
    """
    
    progress = Signal(int)
    status_update = Signal(str)
    result_ready = Signal(list)  # List[ProcessResult]
    finished_processing = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, source_path: str, output_folder: str, process_type: str):
        """
        Inicializar el hilo de procesamiento
        
        Args:
            source_path: Ruta del archivo o carpeta fuente
            output_folder: Carpeta de salida
            process_type: Tipo de procesamiento ('separate', 'rename' o 'organize')
        """
        super().__init__()
        self.source_path = source_path
        self.output_folder = output_folder
        self.process_type = process_type
        self.processor = PDFProcessor()
        self._is_cancelled = False
    
    def cancel(self):
        """Cancelar el procesamiento"""
        self._is_cancelled = True
    
    def run(self):
        """Ejecutar el procesamiento en el hilo separado"""
        try:
            if self._is_cancelled:
                return
                
            results = []
            
            if self.process_type == "separate":
                results = self._process_separate()
            elif self.process_type == "rename":
                results = self._process_rename()
            elif self.process_type == "organize":
                results = self._process_organize()
            else:
                self.error_occurred.emit(f"Tipo de procesamiento no válido: {self.process_type}")
                return
            
            if not self._is_cancelled:
                self.result_ready.emit(results)
                self.finished_processing.emit()
                
        except Exception as e:
            self.error_occurred.emit(f"Error durante el procesamiento: {str(e)}")
    
    def _process_separate(self) -> List[ProcessResult]:
        """Procesar separación de PDF multi-página"""
        self.status_update.emit("Separando PDF multi-página...")
        self.progress.emit(10)
        
        if self._is_cancelled:
            return []
        
        results = self.processor.separate_multi_page_pdf(
            self.source_path, 
            self.output_folder
        )
        
        self.progress.emit(100)
        return results
    
    def _process_rename(self) -> List[ProcessResult]:
        """Procesar renombrado de PDFs individuales"""
        try:
            pdf_files = [
                f for f in os.listdir(self.source_path) 
                if f.lower().endswith('.pdf')
            ]
            
            if not pdf_files:
                self.status_update.emit("No se encontraron archivos PDF")
                return []
            
            results = []
            total_files = len(pdf_files)
            
            for i, pdf_file in enumerate(pdf_files):
                if self._is_cancelled:
                    break
                
                input_path = os.path.join(self.source_path, pdf_file)
                self.status_update.emit(f"Procesando: {pdf_file}")
                
                result = self.processor.rename_single_pdf(input_path, self.output_folder)
                results.append(result)
                
                # Actualizar progreso
                progress = int((i + 1) / total_files * 100)
                self.progress.emit(progress)
            
            return results
            
        except Exception as e:
            raise Exception(f"Error procesando archivos: {str(e)}")
    
    def _process_organize(self) -> List[ProcessResult]:
        """Procesar organización por trabajador"""
        try:
            self.status_update.emit("Escaneando carpetas procesadas...")
            self.progress.emit(10)
            
            if self._is_cancelled:
                return []
            
            # Verificar que existan subcarpetas con PDFs
            subfolders = []
            for item in os.listdir(self.source_path):
                subfolder_path = os.path.join(self.source_path, item)
                if os.path.isdir(subfolder_path):
                    # Verificar si tiene PDFs
                    pdf_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith('.pdf')]
                    if pdf_files:
                        subfolders.append(item)
            
            if not subfolders:
                self.status_update.emit("No se encontraron subcarpetas con PDFs")
                return [ProcessResult(
                    original_file=self.source_path,
                    success=False,
                    error="No se encontraron subcarpetas con archivos PDF procesados"
                )]
            
            self.status_update.emit(f"Organizando documentos de {len(subfolders)} carpetas...")
            self.progress.emit(30)
            
            if self._is_cancelled:
                return []
            
            # Ejecutar organización
            results = self.processor.organize_by_worker(
                self.source_path,
                self.output_folder
            )
            
            self.progress.emit(100)
            return results
            
        except Exception as e:
            raise Exception(f"Error organizando por trabajador: {str(e)}")
    
    def get_preview_data(self) -> dict:
        """
        Obtener datos de vista previa sin procesar archivos
        
        Returns:
            Diccionario con información de vista previa
        """
        try:
            preview_data = {
                'files': [],
                'total_files': 0,
                'estimated_results': []
            }
            
            if self.process_type == "separate":
                preview_data.update(self._get_separate_preview())
            elif self.process_type == "rename":
                preview_data.update(self._get_rename_preview())
            elif self.process_type == "organize":
                preview_data.update(self._get_organize_preview())
            
            return preview_data
            
        except Exception as e:
            return {
                'error': f"Error generando vista previa: {str(e)}",
                'files': [],
                'total_files': 0
            }
    
    def _get_separate_preview(self) -> dict:
        """Vista previa para separación de PDF"""
        try:
            import PyPDF2
            
            with open(self.source_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                preview_pages = []
                max_preview = min(5, total_pages)  # Mostrar máximo 5 páginas
                
                for i in range(max_preview):
                    text = self.processor.extract_text_from_pdf(self.source_path, i)
                    worker_name = self.processor.extract_worker_name(text)
                    
                    preview_pages.append({
                        'page': i + 1,
                        'worker_name': worker_name,
                        'has_name': worker_name is not None
                    })
                
                return {
                    'total_pages': total_pages,
                    'preview_pages': preview_pages,
                    'showing_preview': max_preview < total_pages
                }
                
        except Exception as e:
            return {
                'error': f"Error leyendo PDF: {str(e)}",
                'total_pages': 0,
                'preview_pages': []
            }
    
    def _get_rename_preview(self) -> dict:
        """Vista previa para renombrado de PDFs"""
        try:
            pdf_files = [
                f for f in os.listdir(self.source_path) 
                if f.lower().endswith('.pdf')
            ]
            
            if not pdf_files:
                return {
                    'total_files': 0,
                    'preview_files': [],
                    'message': 'No se encontraron archivos PDF en la carpeta'
                }
            
            preview_files = []
            max_preview = min(10, len(pdf_files))  # Mostrar máximo 10 archivos
            
            for pdf_file in pdf_files[:max_preview]:
                full_path = os.path.join(self.source_path, pdf_file)
                text = self.processor.extract_text_from_pdf(full_path)
                worker_name = self.processor.extract_worker_name(text)
                
                preview_files.append({
                    'original_name': pdf_file,
                    'worker_name': worker_name,
                    'new_name': f"{self.processor.clean_filename(worker_name)}.pdf" if worker_name else None,
                    'has_name': worker_name is not None
                })
            
            return {
                'total_files': len(pdf_files),
                'preview_files': preview_files,
                'showing_preview': max_preview < len(pdf_files)
            }
            
        except Exception as e:
            return {
                'error': f"Error leyendo archivos: {str(e)}",
                'total_files': 0,
                'preview_files': []
            }
    
    def _get_organize_preview(self) -> dict:
        """Vista previa para organización por trabajador"""
        try:
            # Escanear subcarpetas
            subfolders_found = []
            worker_docs = {}
            
            for item in os.listdir(self.source_path):
                subfolder_path = os.path.join(self.source_path, item)
                
                if not os.path.isdir(subfolder_path):
                    continue
                
                # Detectar tipo de documento
                doc_type = self.processor.detect_document_type(item)
                if not doc_type:
                    continue
                
                subfolders_found.append({
                    'folder_name': item,
                    'doc_type': doc_type
                })
                
                # Buscar PDFs
                pdf_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith('.pdf')]
                
                for pdf_file in pdf_files[:5]:  # Mostrar solo primeros 5 por carpeta
                    worker_name = self.processor.extract_worker_name_from_filename(pdf_file)
                    
                    if worker_name:
                        if worker_name not in worker_docs:
                            worker_docs[worker_name] = {}
                        worker_docs[worker_name][doc_type] = pdf_file
            
            # Contar totales
            total_workers = len(worker_docs)
            total_docs = sum(len(docs) for docs in worker_docs.values())
            
            return {
                'subfolders_found': subfolders_found,
                'worker_docs': worker_docs,
                'total_workers': total_workers,
                'total_docs': total_docs,
                'showing_preview': True
            }
            
        except Exception as e:
            return {
                'error': f"Error escaneando carpetas: {str(e)}",
                'subfolders_found': [],
                'worker_docs': {},
                'total_workers': 0
            }