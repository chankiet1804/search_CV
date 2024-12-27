import logging
from typing import Dict, List
from elasticsearch import Elasticsearch

class ElasticHandler:
    def __init__(self, host: str = "localhost", port: int = 9200, index_name: str = "cvs", scheme: str = "http"):
        """Initialize Elasticsearch connection and setup index."""
        self.es = Elasticsearch([{'host': host, 'port': port, 'scheme': scheme}])
        self.index_name = index_name
        self.logger = logging.getLogger(__name__)
        
    def create_index(self) -> None:
        """Create index with predefined mapping if it doesn't exist."""
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "cv_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "stop",
                                "snowball"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "cv_id": {
                        "type": "keyword"  # Exact match field
                    },
                    "full_text": {
                        "type": "text",
                        "analyzer": "cv_analyzer",
                        "search_analyzer": "cv_analyzer"
                    },
                    "skills": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            },
                            "text": {
                                "type": "text",
                                "analyzer": "cv_analyzer"
                            }
                        }
                    },
                    "experience": {
                        "type": "nested",
                        "properties": {
                            "title": {"type": "text"},
                            "company": {"type": "text"},
                            "duration": {"type": "text"},
                            "description": {"type": "text"}
                        }
                    },
                    "education": {
                        "type": "nested",
                        "properties": {
                            "degree": {"type": "text"},
                            "institution": {"type": "text"},
                            "year": {"type": "text"}
                        }
                    },
                    "contact": {
                        "properties": {
                            "email": {"type": "keyword"},
                            "phone": {"type": "keyword"},
                            "location": {"type": "text"}
                        }
                    },
                    "metadata": {
                        "properties": {
                            "last_updated": {"type": "text"},
                            "file_name": {"type": "keyword"},
                            "language": {"type": "keyword"}
                        }
                    }
                }
            }
        }

        try:
            if not self.es.indices.exists(index=self.index_name):
                self.es.indices.create(index=self.index_name, body=settings)
                self.logger.info(f"Created index {self.index_name}")
            else:
                self.logger.info(f"Index {self.index_name} already exists")
        except Exception as e:
            self.logger.error(f"Error creating index: {str(e)}")
            raise
    
    def index_cv(self, cv_data: Dict) -> str:
        """Index a single CV document."""
        try:
            # Debug: log the data structure before sending to Elasticsearch
            self.logger.info(f"Indexing CV data: {cv_data}")
            response = self.es.index(index=self.index_name, document=cv_data)
            return response['_id']
        except Exception as e:
            self.logger.error(f"Error indexing document: {str(e)}")
            raise
    
    def search_cv(self, jd_query: str, size: int = 10) -> List[Dict]:
        """Search CVs based on job description."""
        query = {
            "bool": {
                "should": [
                    {
                        "match": {
                            "full_text": {
                                "query": jd_query,
                                "boost": 1.0
                            }
                        }
                    },
                    {
                        "match": {
                            "skills.text": {
                                "query": jd_query,
                                "boost": 2.0
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "experience",
                            "query": {
                                "match": {
                                    "experience.description": {
                                        "query": "python developer",
                                        "boost": 1.5
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        try:
            # Đặt truy vấn bên trong đối tượng 'body'
            response = self.es.search(index=self.index_name, body={"query": query}, size=size)
            return [hit['_source'] for hit in response['hits']['hits']]
        except Exception as e:
            self.logger.error(f"Error searching documents: {str(e)}")
            raise

# # Ví dụ sử dụng
# if __name__ == "__main__":
#     try:
#         elastic = ElasticHandler()
#         elastic.create_index()
#         # Thực hiện các thao tác khác với Elasticsearch
#     except Exception as e:
#         print(f"An error occurred: {e}")