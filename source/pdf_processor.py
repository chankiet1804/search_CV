import pdfplumber
import re
from typing import Dict, List
import spacy
from datetime import datetime
import random
import base64

class Processor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing special characters and normalizing whitespace."""
        if not text:
            return ""
        # Remove special unicode characters like bullet points
        text = re.sub(r'\uf0b7', '', text)
        # Replace newlines with spaces
        text = re.sub(r'\n', ' ', text)
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def parse_resume(self, text: str) -> Dict:
        sections = {}
        
        # Find different sections in the text
        contact_info = re.search(r'Contact Information(.*?)(?=Profile)', text, re.DOTALL)
        profile = re.search(r'Profile(.*?)(?=Experiences)', text, re.DOTALL)
        experiences = re.search(r'Experiences(.*?)(?=Education)', text, re.DOTALL)
        education = re.search(r'Education(.*?)(?=Skills)', text, re.DOTALL)
        skills = re.search(r'Skills\s*(.*?)(?=$)', text, re.DOTALL)  # Tìm từ Skills đến hết văn bản
    
        if skills:
            sections['Skills'] = skills.group(1).strip()

        if contact_info:
            sections['Contact Information'] = contact_info.group(1).strip()
        if profile:
            sections['Profile'] = profile.group(1).strip()
        if experiences:
            sections['Experiences'] = experiences.group(1).strip()
        if education:
            sections['Education'] = education.group(1).strip()
        if skills:
            sections['Skills'] = skills.group(1).strip()


        return sections
    

    def transform_sections(self, sections: Dict, pdf_path: str) -> Dict:
        # process_pdf path
        with open(pdf_path, "rb") as f:
            # Đọc tệp PDF dưới dạng nhị phân và mã hóa thành base64
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
        transformed = {
            "cv_id": str(random.randint(1000, 100000)),
            "profile": sections["Profile"],
            "skills": sections["Skills"],
            "experience": sections["Experiences"],
            "education": sections["Education"],
            "contact": sections["Contact Information"],
            "cv_data": pdf_data,
            "metadata": {
                "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "file_name": pdf_path.split('/')[-1],
                "language": "English"
            }
        }
        
        return transformed

    def process_pdf(self, pdf_path: str) -> Dict:
        """Process PDF and return JSON string."""
        raw_text = self.extract_text_from_pdf(pdf_path)
        cleaned_data = self.clean_text(raw_text)
        resume = self.parse_resume(cleaned_data)
        extract_data = self.transform_sections(resume, pdf_path)
        return extract_data

# if __name__ == "__main__":
#     processor = Processor()
#     pdf_path = 'C:\\Users\\MINH LOC\\Do an TVanTT\\search_CV\\Data\Test1\\CV2.pdf'  # Update with your actual path
#     json_output = processor.process_pdf(pdf_path)
#     print(json_output)