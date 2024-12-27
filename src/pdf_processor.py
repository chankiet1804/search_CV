import pdfplumber
import re
from typing import Dict, List
import spacy

class CVProcessor:
    def __init__(self):
        # Load NLP model cho việc extract entities
        self.nlp = spacy.load("en_core_web_sm")
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract toàn bộ text từ file PDF."""
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    
    def clean_text(self, text: str) -> str:
        """Clean và normalize text."""
        # Remove special characters
        text = re.sub(r'[^\w\s@.]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Convert to lowercase
        text = text.lower().strip()
        return text
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract các section chính từ CV."""
        sections = {
            'contact': '',
            'education': '',
            'experience': '',
            'skills': ''
        }
        
        """
        # Tìm email
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
        if emails:
            sections['contact'] = emails[0]
        """
            
        # Tìm education section (pattern matching đơn giản)
        edu_match = re.search(r'education.*?(?=experience|skills|$)', 
                            text, re.IGNORECASE | re.DOTALL)
        if edu_match:
            sections['education'] = self.clean_text(edu_match.group())
            
        # Tìm experience section
        exp_match = re.search(r'experience.*?(?=education|skills|$)',
                            text, re.IGNORECASE | re.DOTALL)
        if exp_match:
            sections['experience'] = self.clean_text(exp_match.group())
            
        # Extract skills using NLP
        doc = self.nlp(text)
        skills = []
        # Identify technical terms, proper nouns as potential skills
        for token in doc:
            if token.pos_ in ['PROPN', 'NOUN'] and len(token.text) > 2:
                skills.append(token.text)
        sections['skills'] = ', '.join(set(skills))
        
        return sections
    
    def process_cv(self, pdf_path: str) -> Dict:
        """Main function để process một CV."""
        # Extract text
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        # Clean text
        cleaned_text = self.clean_text(raw_text)
        
        # Extract sections
        sections = self.extract_sections(cleaned_text)
        
        # Return final structured data
        return {
            'full_text': cleaned_text,
            **sections
        }
    

# Test
# processor = CVProcessor()
# cv_data = processor.process_cv( './data/ACCOUNTANT/10674770.pdf')
# print("\nEducation Section:")
# print(cv_data['education'])

# print("\nExperience Section:")
# print(cv_data['experience'])

# print("\nSkills Section:")
# print(cv_data['skills'])
