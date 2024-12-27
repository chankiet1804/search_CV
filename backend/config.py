import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback nếu không có dotenv
    pass

class Config:
    SECRET_KEY = 'your-super-secret-key-123'
    ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
    ELASTICSEARCH_PORT = int(os.getenv('ELASTICSEARCH_PORT', 9200))