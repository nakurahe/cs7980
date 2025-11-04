"""Tests for the slide extraction module"""

import pytest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.time_utils import ms_to_timestamp, timestamp_to_ms
from src.utils.image_utils import compute_image_hash
from src.text_comparator import TextComparator
from src.ocr_engine import OCREngine


class TestTimeUtils:
    """Test time utility functions"""
    
    def test_ms_to_timestamp(self):
        """Test milliseconds to timestamp conversion"""
        assert ms_to_timestamp(0) == "00:00:00"
        assert ms_to_timestamp(5000) == "00:00:05"
        assert ms_to_timestamp(65000) == "00:01:05"
        assert ms_to_timestamp(3665000) == "01:01:05"
    
    def test_timestamp_to_ms(self):
        """Test timestamp to milliseconds conversion"""
        assert timestamp_to_ms("00:00:00") == 0
        assert timestamp_to_ms("00:00:05") == 5000
        assert timestamp_to_ms("00:01:05") == 65000
        assert timestamp_to_ms("01:01:05") == 3665000
    
    def test_round_trip(self):
        """Test round-trip conversion"""
        original_ms = 125000
        timestamp = ms_to_timestamp(original_ms)
        converted_ms = timestamp_to_ms(timestamp)
        assert original_ms == converted_ms


class TestTextComparator:
    """Test text comparison functionality"""
    
    def setup_method(self):
        """Setup test fixture"""
        self.comparator = TextComparator()
    
    def test_identical_text(self):
        """Test similarity of identical text"""
        text = "Introduction to Machine Learning"
        similarity = self.comparator.calculate_similarity(text, text)
        assert similarity == 1.0
    
    def test_completely_different_text(self):
        """Test similarity of completely different text"""
        text1 = "Introduction to Machine Learning"
        text2 = "Advanced Database Systems"
        similarity = self.comparator.calculate_similarity(text1, text2)
        assert similarity < 0.5
    
    def test_similar_text(self):
        """Test similarity of similar text"""
        text1 = "Introduction to Machine Learning"
        text2 = "Introduction to Machine Learning - Part 1"
        similarity = self.comparator.calculate_similarity(text1, text2)
        assert similarity > 0.7
    
    def test_incremental_slide_detection(self):
        """Test detection of incremental slides"""
        text1 = "Topics:\n• Machine Learning"
        text2 = "Topics:\n• Machine Learning\n• Deep Learning"
        
        is_incremental = self.comparator.is_incremental_slide(text1, text2)
        assert is_incremental is True
    
    def test_empty_strings(self):
        """Test handling of empty strings"""
        assert self.comparator.calculate_similarity("", "") == 1.0
        assert self.comparator.calculate_similarity("test", "") == 0.0
        assert self.comparator.calculate_similarity("", "test") == 0.0


class TestOCREngine:
    """Test OCR engine functionality"""
    
    def test_text_normalization(self):
        """Test text normalization"""
        text = "Hello WORLD!!! This is a TEST."
        normalized = OCREngine.normalize_text(text)
        assert normalized == "hello world this is a test."
    
    def test_clean_text(self):
        """Test text cleaning"""
        engine = OCREngine()
        text = "Line 1\n\n\nLine 2\n  \nLine 3"
        cleaned = engine.clean_text(text)
        assert cleaned == "Line 1\nLine 2\nLine 3"


# Run tests with: pytest tests/test_extractor.py -v
