"""OCR engine wrapper for text extraction"""

import pytesseract
from PIL import Image
import numpy as np
import cv2
from typing import Dict, Any


class OCREngine:
    """Wrapper for Tesseract OCR operations"""
    
    def __init__(self, language: str = "eng", config: str = ""):
        """
        Initialize OCR engine
        
        Args:
            language: Tesseract language code (default: "eng")
            config: Additional Tesseract configuration
        """
        self.language = language
        self.config = config or "--psm 6"  # Assume uniform block of text
        
        # Test if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            raise RuntimeError(
                "Tesseract OCR not found. Please install it:\n"
                "  macOS: brew install tesseract\n"
                "  Linux: apt-get install tesseract-ocr\n"
                "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
            ) from e
    
    def extract_text(self, frame: np.ndarray) -> str:
        """
        Extract text from frame
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            Extracted text
        """
        # Convert BGR to RGB for PIL
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            rgb_frame = frame
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Extract text
        text = pytesseract.image_to_string(
            pil_image,
            lang=self.language,
            config=self.config
        )
        
        return text.strip()
    
    def extract_text_with_confidence(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Extract text with confidence scores
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            Dictionary with text and confidence information
        """
        # Convert BGR to RGB for PIL
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            rgb_frame = frame
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Get detailed OCR data
        data = pytesseract.image_to_data(
            pil_image,
            lang=self.language,
            config=self.config,
            output_type=pytesseract.Output.DICT
        )
        
        # Calculate average confidence
        confidences = [int(conf) for conf in data["conf"] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Extract text
        text = pytesseract.image_to_string(
            pil_image,
            lang=self.language,
            config=self.config
        ).strip()
        
        return {
            "text": text,
            "confidence": avg_confidence / 100.0,  # Normalize to 0-1
            "word_count": len([w for w in data["text"] if w.strip()])
        }
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        lines = [line.strip() for line in text.split("\n")]
        lines = [line for line in lines if line]  # Remove empty lines
        
        return "\n".join(lines)
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison (lowercase, remove special chars)
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        import re
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters except spaces and basic punctuation
        text = re.sub(r"[^a-z0-9\s.,!?-]", "", text)
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        return text
