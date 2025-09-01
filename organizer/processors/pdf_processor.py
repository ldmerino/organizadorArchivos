import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import fitz  # PyMuPDF - mejor para extracción de texto
import PyPDF2
from dataclasses import dataclass

from ..utils.patterns import WorkerNamePatterns

@dataclass
class ProcessResult:
    """Resultado del procesamiento de un archivo"""
    original_file: str
    success: bool
    new_name: Optional[str] = None
    worker_name: Optional[str] = None
    error: Optional[str] = None
    pages_processed: int = 0

class PDFProcessor:
    """Procesador de PDFs para extraer nombres y organizar archivos"""
    
    def __init__(self):
        self.results: List[ProcessResult] = []
        
    def extract_worker_name(self, text: str) -> Optional[str]:
        """
        Extrae el nombre del trabajador del texto del PDF usando patrones centralizados
        
        Args:
            text: Texto extraído del PDF
            
        Returns:
            Nombre del trabajador en formato Title Case o None si no se encuentra
        """
        return WorkerNamePatterns.extract_worker_name(text)
    
    def clean_filename(self, filename: str) -> str:
        """
        Limpia el nombre para que sea válido como nombre de archivo
        
        Args:
            filename: Nombre original del archivo
            
        Returns:
            Nombre de archivo válido y limpio
        """
        if not filename:
            return "archivo_sin_nombre"
            
        # Caracteres inválidos para nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Normalizar espacios
        filename = re.sub(r'\s+', ' ', filename)
        filename = filename.strip()
        
        # Limitar longitud
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename
    
    def extract_text_from_pdf(self, pdf_path: str, page_num: int = 0) -> str:
        """
        Extrae texto de una página específica del PDF
        
        Args:
            pdf_path: Ruta del archivo PDF
            page_num: Número de página a extraer (0-indexed)
            
        Returns:
            Texto extraído de la página
        """
        # Intentar con PyMuPDF (mejor calidad)
        try:
            doc = fitz.open(pdf_path)
            if page_num < len(doc):
                text = doc[page_num].get_text()
                doc.close()
                if text.strip():
                    return text
            doc.close()
        except Exception:
            pass
        
        # Fallback a PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if page_num < len(pdf_reader.pages):
                    text = pdf_reader.pages[page_num].extract_text()
                    return text
        except Exception:
            pass
        
        return ""
    
    def separate_multi_page_pdf(self, input_path: str, output_folder: str) -> List[ProcessResult]:
        """
        Separa un PDF multi-página en archivos individuales por trabajador
        
        Args:
            input_path: Ruta del PDF multi-página
            output_folder: Carpeta donde guardar los archivos separados
            
        Returns:
            Lista de resultados del procesamiento
        """
        results = []
        
        try:
            # Validar que el archivo existe y es PDF
            if not os.path.exists(input_path) or not input_path.lower().endswith('.pdf'):
                return [ProcessResult(
                    original_file=os.path.basename(input_path),
                    success=False,
                    error="Archivo no válido o no es PDF"
                )]
            
            # Crear carpeta de salida
            os.makedirs(output_folder, exist_ok=True)
            
            with open(input_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                if total_pages == 0:
                    return [ProcessResult(
                        original_file=os.path.basename(input_path),
                        success=False,
                        error="El PDF no contiene páginas"
                    )]
                
                for page_num in range(total_pages):
                    try:
                        # Extraer texto de la página
                        text = self.extract_text_from_pdf(input_path, page_num)
                        worker_name = self.extract_worker_name(text)
                        
                        if worker_name:
                            # Crear nombre de archivo
                            clean_name = self.clean_filename(worker_name)
                            filename = f"{clean_name}.pdf"
                            output_path = os.path.join(output_folder, filename)
                            
                            # Evitar duplicados
                            counter = 1
                            while os.path.exists(output_path):
                                filename = f"{clean_name}_{counter:03d}.pdf"
                                output_path = os.path.join(output_folder, filename)
                                counter += 1
                            
                            # Crear PDF con solo esta página
                            pdf_writer = PyPDF2.PdfWriter()
                            pdf_writer.add_page(pdf_reader.pages[page_num])
                            
                            with open(output_path, 'wb') as output_file:
                                pdf_writer.write(output_file)
                            
                            results.append(ProcessResult(
                                original_file=f"{os.path.basename(input_path)} - Página {page_num + 1}",
                                success=True,
                                new_name=filename,
                                worker_name=worker_name,
                                pages_processed=1
                            ))
                        else:
                            # No se pudo extraer nombre
                            filename = f"Pagina_{page_num + 1:03d}.pdf"
                            output_path = os.path.join(output_folder, filename)
                            
                            pdf_writer = PyPDF2.PdfWriter()
                            pdf_writer.add_page(pdf_reader.pages[page_num])
                            
                            with open(output_path, 'wb') as output_file:
                                pdf_writer.write(output_file)
                            
                            results.append(ProcessResult(
                                original_file=f"{os.path.basename(input_path)} - Página {page_num + 1}",
                                success=False,
                                new_name=filename,
                                error="No se pudo extraer nombre del trabajador",
                                pages_processed=1
                            ))
                            
                    except Exception as e:
                        results.append(ProcessResult(
                            original_file=f"{os.path.basename(input_path)} - Página {page_num + 1}",
                            success=False,
                            error=f"Error procesando página: {str(e)}",
                            pages_processed=1
                        ))
        
        except Exception as e:
            results.append(ProcessResult(
                original_file=os.path.basename(input_path),
                success=False,
                error=f"Error abriendo archivo: {str(e)}"
            ))
        
        return results
    
    def rename_single_pdf(self, input_path: str, output_folder: str = None) -> ProcessResult:
        """
        Renombra un PDF individual basado en el contenido
        
        Args:
            input_path: Ruta del PDF a renombrar
            output_folder: Carpeta de destino (opcional, usa la misma carpeta si es None)
            
        Returns:
            Resultado del procesamiento
        """
        try:
            # Validar archivo
            if not os.path.exists(input_path) or not input_path.lower().endswith('.pdf'):
                return ProcessResult(
                    original_file=os.path.basename(input_path),
                    success=False,
                    error="Archivo no válido o no es PDF"
                )
            
            # Extraer texto y nombre
            text = self.extract_text_from_pdf(input_path)
            if not text.strip():
                return ProcessResult(
                    original_file=os.path.basename(input_path),
                    success=False,
                    error="No se pudo extraer texto del PDF"
                )
            
            worker_name = self.extract_worker_name(text)
            if not worker_name:
                return ProcessResult(
                    original_file=os.path.basename(input_path),
                    success=False,
                    error="No se pudo extraer nombre del trabajador"
                )
            
            # Determinar carpeta de salida
            if output_folder is None:
                output_folder = os.path.dirname(input_path)
            else:
                os.makedirs(output_folder, exist_ok=True)
            
            # Crear nuevo nombre
            clean_name = self.clean_filename(worker_name)
            extension = Path(input_path).suffix
            
            new_filename = f"{clean_name}{extension}"
            output_path = os.path.join(output_folder, new_filename)
            
            # Evitar sobreescribir
            counter = 1
            while os.path.exists(output_path):
                new_filename = f"{clean_name}_{counter:03d}{extension}"
                output_path = os.path.join(output_folder, new_filename)
                counter += 1
            
            # Copiar archivo con nuevo nombre
            shutil.copy2(input_path, output_path)
            
            return ProcessResult(
                original_file=os.path.basename(input_path),
                success=True,
                new_name=new_filename,
                worker_name=worker_name,
                pages_processed=1
            )
            
        except Exception as e:
            return ProcessResult(
                original_file=os.path.basename(input_path),
                success=False,
                error=f"Error procesando archivo: {str(e)}"
            )
    
    def get_summary(self, results: List[ProcessResult]) -> Dict:
        """
        Genera resumen de resultados del procesamiento
        
        Args:
            results: Lista de resultados de procesamiento
            
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        if not results:
            return {
                'total_processed': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0.0,
                'workers_found': 0,
                'total_pages': 0
            }
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        # Obtener trabajadores únicos
        unique_workers = set()
        for result in successful:
            if result.worker_name:
                unique_workers.add(result.worker_name)
        
        return {
            'total_processed': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': (len(successful) / len(results) * 100) if results else 0,
            'workers_found': len(unique_workers),
            'total_pages': sum(r.pages_processed for r in results if r.pages_processed)
        }
    
    def organize_by_worker(self, source_folder: str, output_folder: str) -> List[ProcessResult]:
        """
        Organiza documentos ya procesados agrupándolos por trabajador
        
        Args:
            source_folder: Carpeta padre que contiene subcarpetas procesadas
            output_folder: Carpeta donde crear las carpetas por trabajador
            
        Returns:
            Lista de resultados del procesamiento
        """
        results = []
        
        try:
            # Validar que la carpeta fuente existe
            if not os.path.exists(source_folder):
                return [ProcessResult(
                    original_file=source_folder,
                    success=False,
                    error="La carpeta fuente no existe"
                )]
            
            # Crear carpeta de salida
            os.makedirs(output_folder, exist_ok=True)
            
            # Buscar subcarpetas con PDFs procesados
            worker_docs = {}  # {worker_name: {doc_type: file_path}}
            
            # Escanear subcarpetas
            for item in os.listdir(source_folder):
                subfolder_path = os.path.join(source_folder, item)
                
                if not os.path.isdir(subfolder_path):
                    continue
                
                # Detectar tipo de documento por nombre de carpeta
                doc_type = self.detect_document_type(item)
                if not doc_type:
                    continue
                
                # Buscar PDFs en la subcarpeta
                pdf_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith('.pdf')]
                
                for pdf_file in pdf_files:
                    worker_name = self.extract_worker_name_from_filename(pdf_file)
                    
                    if worker_name:
                        if worker_name not in worker_docs:
                            worker_docs[worker_name] = {}
                        
                        worker_docs[worker_name][doc_type] = os.path.join(subfolder_path, pdf_file)
            
            # Crear carpetas por trabajador y organizar documentos
            for worker_name, documents in worker_docs.items():
                try:
                    # Crear carpeta del trabajador
                    worker_folder = os.path.join(output_folder, worker_name)
                    os.makedirs(worker_folder, exist_ok=True)
                    
                    # Copiar documentos con nuevo nombre
                    for doc_type, source_path in documents.items():
                        new_filename = f"{worker_name}_{doc_type}.pdf"
                        destination_path = os.path.join(worker_folder, new_filename)
                        
                        shutil.copy2(source_path, destination_path)
                        
                        results.append(ProcessResult(
                            original_file=os.path.basename(source_path),
                            success=True,
                            new_name=new_filename,
                            worker_name=worker_name,
                            pages_processed=1
                        ))
                        
                except Exception as e:
                    results.append(ProcessResult(
                        original_file=f"Documentos de {worker_name}",
                        success=False,
                        error=f"Error organizando trabajador: {str(e)}"
                    ))
            
            return results
            
        except Exception as e:
            return [ProcessResult(
                original_file=source_folder,
                success=False,
                error=f"Error organizando por trabajador: {str(e)}"
            )]
    
    def detect_document_type(self, folder_name: str) -> Optional[str]:
        """
        Detecta el tipo de documento basado en el nombre de la carpeta fuente
        
        Args:
            folder_name: Nombre de la carpeta (ej: "PDFs_Procesados_Certificados")
            
        Returns:
            Tipo de documento normalizado o None si no se reconoce
        """
        folder_lower = folder_name.lower()
        
        # Mapeo de patrones de carpeta a tipos de documento
        type_mapping = {
            'certificad': 'Certificados',
            '5renta': '5Rentas', 
            'renta': '5Rentas',
            'constancia': 'Constancias',
            'trabajo': 'Certificados'  # "PDFs_Procesados_Trabajo" → Certificados
        }
        
        for pattern, doc_type in type_mapping.items():
            if pattern in folder_lower:
                return doc_type
        
        return None
    
    def extract_worker_name_from_filename(self, filename: str) -> Optional[str]:
        """
        Extrae el nombre del trabajador de un nombre de archivo ya procesado
        
        Args:
            filename: Nombre del archivo (ej: "Juan Pérez García.pdf")
            
        Returns:
            Nombre del trabajador o None si no se puede extraer
        """
        # Remover extensión .pdf
        name_without_ext = os.path.splitext(filename)[0]
        
        # Remover numeración al final si existe (ej: "Juan Pérez_001")

        name_cleaned = re.sub(r'_\d{3}$', '', name_without_ext)
        
        # Validar que sea un nombre válido (al menos 2 palabras, formato título)
        words = name_cleaned.split()
        if len(words) >= 2 and all(len(word) >= 2 for word in words):
            return name_cleaned
        
        return None