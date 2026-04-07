import re
from typing import Dict, Any, List, Optional

try:
    import pytesseract
    from PIL import ImageGrab, Image
except ImportError:
    pass

class VisionAwareness:
    """
    Agrega capacidades analíticas a la máquina local para no siempre depender 
    de Gemini Vision (ahorro token) si la tarea es encontrar un texto específico en pantalla.
    """
    
    @staticmethod
    async def get_screen_text() -> Dict[str, Any]:
        """Toma captura global y extrae todo su texto en crudo."""
        try:
            img = ImageGrab.grab()
            text = pytesseract.image_to_string(img)
            return {"status": "success", "text": text}
        except Exception as e:
            return {"status": "error", "message": f"OCR failed: {e}. Check if Tesseract is installed."}

    @staticmethod
    async def find_element_by_text(target_text: str) -> Dict[str, Any]:
        """
        Devuelve las coordenadas delimitadoras (bounding box) de un texto visualizado en pantalla.
        Retorna {"x": int, "y": int} correspondiente al centro del texto si lo encuentra.
        """
        try:
            img = ImageGrab.grab()
            # Usar modo diccionarios para obtener bounding boxes
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            for i in range(len(data['text'])):
                word = data['text'][i].strip()
                # Unmatch case insensitive básico
                if target_text.lower() in word.lower() and len(word) > 2:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    center_x = x + w // 2
                    center_y = y + h // 2
                    return {"status": "success", "coords": {"x": center_x, "y": center_y}, "word": word}
                    
            return {"status": "error", "message": f"Text '{target_text}' not found visually."}
        except Exception as e:
            return {"status": "error", "message": f"OCR detection failed: {str(e)}"}
