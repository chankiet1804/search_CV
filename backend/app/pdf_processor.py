import pdfplumber
import re
import json
from typing import Dict, List
import spacy
from datetime import datetime

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
        skills = re.search(r'Skills:(.*)', text, re.DOTALL)

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
    
    def process_skills(self, skills_text: str) -> List[str]:
        """Process skills text into a clean list of skills."""
        if not skills_text:
            return []
            
        # Split by bullet points and clean each skill
        skills = re.split(r'\s*[\uf0b7•]\s*', skills_text)
        # Clean each skill and filter out empty strings
        skills = [self.clean_text(skill) for skill in skills if skill.strip()]
        # Split skills that contain 'Familiarity with' or similar phrases
        cleaned_skills = []
        for skill in skills:
            parts = re.split(r'(?:Familiarity with|Knowledge in|Understanding of)', skill)
            cleaned_skills.extend([part.strip() for part in parts if part.strip()])
        return cleaned_skills

    def process_experience(self, experiences: str) -> List[Dict[str, str]]:
        if not experiences:
            return []

        experience_list = []
        # Split by "Entry Level" or any position title pattern
        entries = re.split(r'(?:\n|^)(?=(?:Entry Level|Senior|Junior|Associate|Lead|Principal|Software|Developer|Engineer))', experiences)
        entries = [entry.strip() for entry in entries if entry.strip()]

        current_exp = {}
        for entry in entries:
            try:
                lines = [line.strip() for line in entry.split('\n') if line.strip()]
                if not lines:
                    continue

                experience_dict = {
                    "title": "",
                    "company": "",
                    "duration": "",
                    "description": ""
                }

                # First line is typically the title
                if lines[0]:
                    experience_dict['title'] = self.clean_text(lines[0])
                
                for line in lines[1:]:  # Start from second line
                    if ': ' in line:
                        key, value = line.split(': ', 1)
                        key = key.lower()
                        if 'company' in key:
                            experience_dict['company'] = self.clean_text(value)
                        elif 'duration' in key or 'period' in key:
                            experience_dict['duration'] = self.clean_text(value)
                    else:
                        # If the line contains "Description" or bullet points, it's part of description
                        if 'Description' in line or '\uf0b7' in line or '•' in line:
                            if experience_dict['description']:
                                experience_dict['description'] += " " + self.clean_text(line)
                            else:
                                experience_dict['description'] = self.clean_text(line)
                        # If we don't have a company yet and it's not a description, it might be the company
                        elif not experience_dict['company'] and not experience_dict['duration']:
                            experience_dict['company'] = self.clean_text(line)
                        # If we don't have duration and it matches date pattern, it's probably duration
                        elif not experience_dict['duration'] and re.search(r'\d{4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', line):
                            experience_dict['duration'] = self.clean_text(line)
                        else:
                            if experience_dict['description']:
                                experience_dict['description'] += " " + self.clean_text(line)
                            else:
                                experience_dict['description'] = self.clean_text(line)

                # Only add if we have at least title and company
                if experience_dict['title'] and experience_dict['company']:
                    experience_list.append(experience_dict)

            except Exception as e:
                print(f"Error processing experience entry: {e}")
                continue

        return experience_list

    def process_education(self, education_text: str) -> List[Dict[str, str]]:
        """Process education information into a structured format."""
        if not education_text:
            return []

        education_list = []
        entries = re.split(r'\n\n|\n(?=(?:Bachelor|Master|Ph\.D|MBA|Associate|Diploma|Certificate))', education_text)
    
        for entry in entries:
            try:
                lines = [line.strip() for line in entry.split('\n') if line.strip()]
                if not lines:
                    continue

                education_dict = {
                    "degree": "",
                    "institution": "",
                    "duration": ""
                }

                # Process each line
                for i, line in enumerate(lines):
                    line = self.clean_text(line)
                    
                    # Extract degree
                    if any(degree in line.lower() for degree in ['bachelor', 'master', 'ph.d', 'mba', 'associate']):
                        education_dict['degree'] = line
                        
                        # Look ahead for institution in next line if current institution is empty
                        if i + 1 < len(lines) and not education_dict['institution']:
                            next_line = self.clean_text(lines[i + 1])
                            if any(edu in next_line.lower() for edu in ['university', 'college', 'school', 'institute']):
                                # Remove "Institution:" prefix if present
                                education_dict['institution'] = re.sub(r'^Institution:\s*', '', next_line, flags=re.IGNORECASE)
                    
                    # Extract institution
                    elif 'institution:' in line.lower() or any(edu in line.lower() for edu in ['university', 'college', 'school', 'institute']):
                        # Remove "Institution:" prefix
                        education_dict['institution'] = re.sub(r'^Institution:\s*', '', line, flags=re.IGNORECASE)
                    
                    # Extract duration
                    elif any(month in line.lower() for month in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']) or \
                        re.search(r'\b\d{4}\b', line):
                        education_dict['duration'] = line.strip()

                # Clean up any remaining prefixes in institution field
                if education_dict['institution']:
                    education_dict['institution'] = re.sub(r'^Institution:\s*', '', education_dict['institution'], flags=re.IGNORECASE)

                # If we have at least a degree, add the entry
                if education_dict['degree']:
                    education_list.append(education_dict)

            except Exception as e:
                print(f"Error processing education entry: {e}")
                continue

        return education_list

    def extract_location(self, contact_text: str) -> str:
        """Extract location information from contact text."""
        location_patterns = [
            r'(?:Address|Location|City|State):\s*([^,\n]+(?:,\s*[^,\n]+)*)',
            r'\b[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\s*\d{5}\b',  # City, State ZIP
            r'\b[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\b',          # City, State
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, contact_text)
            if match:
                # If the pattern has a group, use it, otherwise use the whole match
                location = match.group(1) if len(match.groups()) > 0 else match.group(0)
                return self.clean_text(location)
        
        return ""

    def transform_sections(self, sections: Dict, pdf_path: str) -> Dict:
        """Transform parsed sections into required format."""
        transformed = {
            "cv_id": "0000",
            "profile": self.clean_text(sections.get('Profile', '')),
            "skills": self.process_skills(sections.get('Skills', '')),
            "experience": self.process_experience(sections.get('Experiences', '')),
            "education": self.process_education(sections.get('Education', '')),
            "contact": {
                "email": "",
                "phone": "",
                "location": ""
            },
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "file_name": pdf_path.split('\\')[-1] if '\\' in pdf_path else pdf_path.split('/')[-1],
                "language": "English"
            }
        }

        contact_text = sections.get('Contact Information', '')
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', contact_text)
        phone_match = re.search(r'[\+\d][\d\s-]{8,}', contact_text)
        
        if email_match:
            transformed['contact']['email'] = email_match.group(0).lower().strip()
        if phone_match:
            phone = re.sub(r'\D', '', phone_match.group(0))  # Keep only digits
            transformed['contact']['phone'] = phone
            transformed['cv_id'] = phone[-4:] if len(phone) >= 4 else "0000"
            
        # Extract location
        transformed['contact']['location'] = self.extract_location(contact_text)

        return transformed

    def process_pdf(self, pdf_path: str) -> Dict:
        """Process PDF and return JSON string."""
        raw_text = self.extract_text_from_pdf(pdf_path)
        resume = self.parse_resume(raw_text)
        extract_data = self.transform_sections(resume, pdf_path)
        return extract_data

if __name__ == "__main__":
    processor = Processor()
    pdf_path = '/home/kiet-22520717/Nam3/search_cv/search_CV/backend/app/Example_CV.pdf'
    output = processor.process_pdf(pdf_path)
    print(output)