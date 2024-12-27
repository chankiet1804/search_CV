from src.pdf_processor import CVProcessor
from src.elastic_handler import ElasticHandler
from src.transform_data import Transform

# Initialize components
processor = CVProcessor()
elastic = ElasticHandler()
transform = Transform()

#Process CV và index
cv_data = {
    "cv_id": "12345",
    "full_text": "John Doe is a Python developer with experience in Elasticsearch and Machine Learning...",
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
#pdf_path = './data/ACCOUNTANT/10674770.pdf'
#cv_data = processor.process_cv('./data/ACCOUNTANT/10674770.pdf')
#transformed_data = transform.transform_data(cv_data,pdf_path)

# Index processed CV data
doc_id = elastic.index_cv(cv_data)
#doc_id = elastic.index_cv(transformed_data)

# Search CVs
results = elastic.search_cv("machine learning engineer")
print(results)

# print(transformed_data["skills"])
# print("-------------------------------------------------------------------------------")
# print(transformed_data["education"])