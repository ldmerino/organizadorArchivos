"""
Patrones regex para extracción de nombres de trabajadores de documentos PDF
"""
import re
from typing import List, Optional

class WorkerNamePatterns:
    """Patrones regex para extraer nombres de trabajadores de documentos laborales"""
    
    # Palabras que deben excluirse de los nombres detectados
    EXCLUDED_WORDS = [
        'fecha', 'baja', 'alta', 'certificado', 'constancia', 
        'trabajador', 'empleado', 'dni', 'documento', 'prestadores',
        'empleador', 'ejercicio', 'gravable', 'retenciones', 'rentas',
        'quinta', 'categoría', 'certifica'
    ]
    
    # Patrones ordenados por especificidad (más específicos primero)
    PATTERNS = [
        # Certificados de trabajo - Patrón más confiable
        r'(?:Que el Sr\.|Que la Sra\.)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,4})\s+(?:identificado|identificada)\s+con\s+(?:DNI|C\.?I\.?)',
        
        # Constancias de baja - Formato específico PERÚ\nNOMBRE\nFECHA
        r'PERÚ\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+)\s+\d{2}/\d{2}/\d{4}',
        
        # Constancias con "Apellidos y nombres:"
        r'(?:Apellidos y nombres|Nombres y apellidos):\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,4})',
        
        # Rentas 5ta categoría
        r'(?:Trabajador|Empleado):\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,4})',
        
        # Patrón general para nombres seguidos de DNI
        r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,4})\s+(?:DNI|C\.?I\.?)\s*[:\-]?\s*\d',
    ]
    
    @classmethod
    def extract_worker_name(cls, text: str) -> Optional[str]:
        """
        Extrae el nombre del trabajador del texto del PDF
        
        Args:
            text: Texto extraído del PDF
            
        Returns:
            Nombre del trabajador en formato Title Case o None si no se encuentra
        """
        if not text or not text.strip():
            return None
            
        for pattern in cls.PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if matches:
                for match in matches:
                    name = match.strip() if isinstance(match, str) else match[0].strip()
                    
                    # Limpiar el nombre
                    name = re.sub(r'\s+', ' ', name)
                    name = name.replace(',', '').strip()
                    
                    # Validar que sea un nombre válido
                    if cls._is_valid_name(name):
                        return name.title()
        
        return None
    
    @classmethod
    def _is_valid_name(cls, name: str) -> bool:
        """
        Valida si un nombre extraído es válido
        
        Args:
            name: Nombre a validar
            
        Returns:
            True si el nombre es válido, False en caso contrario
        """
        if not name or len(name) > 50:
            return False
            
        words = name.lower().split()
        
        # Debe tener al menos 2 palabras
        if len(words) < 2:
            return False
            
        # Cada palabra debe tener al menos 2 caracteres
        if not all(len(word) >= 2 for word in words):
            return False
            
        # No debe contener palabras excluidas
        if any(word in cls.EXCLUDED_WORDS for word in words):
            return False
            
        return True