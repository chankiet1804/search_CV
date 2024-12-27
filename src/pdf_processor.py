import pdfplumber
import re
from typing import Dict, List
import spacy

class Processor:
    def __init__(self):
        # Load NLP model cho việc extract entities
        self.nlp = spacy.load("en_core_web_sm")
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Add code here"""
    
    def clean_text(self, text: str) -> str:
        """Clean và normalize text."""
        
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract các section chính từ CV."""
        
    
    def process_cv(self, pdf_path: str) -> Dict:
        """Main function để process một CV."""
        
    
