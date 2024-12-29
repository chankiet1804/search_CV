from backend.app.pdf_processor import Processor
from backend.app.elastic_handler import ElasticHandler

# Initialize components
processor = Processor()
elastic = ElasticHandler()

#Process CV và index
cv_data1 = {
    "cv_id": "12345",
    "profile": "John Doe is a Python developer with experience in Elasticsearch and Machine Learning...",
    "skills": ["Python", "Elasticsearch", "Machine Learning"],
    "experience": [
        {
            "title": "Senior Python Developer",
            "company": "Tech Solutions Inc.",
            "duration": "2018-2023",
            "description": "Developed and maintained web applications, led a team of developers..."
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Innovations",
            "duration": "2015-2018",
            "description": "Designed and implemented machine learning models, collaborated with data scientists..."
        }
    ],
    "education": [
        {
            "degree": "Master's in Computer Science",
            "institution": "University of Technology",
            "year": "2015-06-15"
        },
        {
            "degree": "Bachelor's in Information Technology",
            "institution": "State University",
            "year": "2013-06-15"
        }
    ],
    "contact": {
        "email": "johndoe@example.com",
        "phone": "123-456-7890",
        "location": "New York, USA"
    },
    "metadata": {
        "last_updated": "2023-12-01",
        "file_name": "john_doe_cv.pdf",
        "language": "English"
    }
}
cv_data2 = {
    "cv_id": "123",
    "profile": "Acknowledge Python and SQL",
    "skills": ["Elasticsearch", "Machine Learning"],
    "experience": [
        {
            "title": "SPython Developer",
            "company": "FPT",
            "duration": "2018-2023",
            "description": "Developed and maintained web applications, led a team of developers..."
        },
        
    ],
    "education": [
        {
            "degree": "Master's in Computer Science",
            "institution": "UIT",
            "year": "2015-06-15"
        },
    ],
    "contact": {
        "email": "hkaido@example.com",
        "phone": "04934923242",
        "location": "Nagasaki, Japan"
    },
    "metadata": {
        "last_updated": "2023-12-01",
        "file_name": "jhkaido_cv.pdf",
        "language": "English"
    }
}
pdf_path = '/home/kiet-22520717/Nam3/search_cv/search_CV/backend/app/Example_CV.pdf'
cv_data = processor.process_pdf(pdf_path)
#transformed_data = transform.transform_data(cv_data,pdf_path)

# Index processed CV data
doc_id = elastic.index_cv(cv_data1)
doc_id = elastic.index_cv(cv_data2)
doc_id = elastic.index_cv(cv_data)

jd_data = {
    "About company": "Công ty ABC...",
    "Objectives of this role": "Junio Software Developer",
    "Responsibilities": "Participate in the full software development lifecycle, including analysis, design, test, and delivery",
    "Required skills and qualifications": "Python, SQL, Cloud, UI/UX, System design, Linux",
    "Preferred skills and qualifications": "Docker, Git"
}

# Search CVs
#results = elastic.search_cv("Software Development Life Cycle")
results = elastic.search_cv_by_jd(jd_data,min_score=2.0)
print(results)

# print(transformed_data["skills"])
# print("-------------------------------------------------------------------------------")
# print(transformed_data["education"])