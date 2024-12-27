from typing import Dict, List
import uuid  
import os
from datetime import datetime
import re

class Transform:

    def transform_data(self, raw_cv_data: dict, pdf_path: str) -> dict:
        return {
            "cv_id": str(uuid.uuid4()),
            "full_text": raw_cv_data["full_text"],
            "skills": raw_cv_data["skills"],
            "experience": raw_cv_data["experience"], 
            "education": raw_cv_data["education"],
            "contact": raw_cv_data["contact"],
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "file_name": os.path.basename(pdf_path)
            }
        }