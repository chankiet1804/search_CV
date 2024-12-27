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
                    "profile": {
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
            # Kiểm tra nếu index chưa tồn tại
            if not self.es.indices.exists(index=self.index_name):
                self.es.indices.create(index=self.index_name, body=settings)
                self.logger.info(f"Created index {self.index_name}")
            else:
                # Kiểm tra index đã tồn tại
                self.logger.info(f"Index {self.index_name} already exists. Proceeding to check settings and mappings.")
                
                # Kiểm tra sự khác biệt giữa mapping và settings đã tạo (nếu cần thiết)
                current_mapping = self.es.indices.get_mapping(index=self.index_name)
                # Có thể thêm code kiểm tra sự thay đổi giữa current_mapping và settings ở đây.

        except Exception as e:
            self.logger.error(f"Error creating index {self.index_name}: {str(e)}")
            raise  # Để lỗi được phát hiện và xử lý bởi các phần khác
    
    def index_cv(self, cv_data: Dict) -> str:
        """Index a single CV document using cv_id as the document id."""
        try:
            document_id = cv_data.get('cv_id')
        
            if not document_id:
                self.logger.error("cv_id is missing in the provided CV data")
                raise ValueError("cv_id is required for indexing")
            
            # Kiểm tra xem tài liệu đã tồn tại chưa
            if self.es.exists(index=self.index_name, id=document_id):
                self.logger.info(f"Document with cv_id {document_id} already exists. Skipping indexing.")
                return document_id  # Hoặc bạn có thể xóa tài liệu cũ và index lại nếu cần
            
            # Debug: log the data structure before sending to Elasticsearch
            self.logger.info(f"Indexing CV data with cv_id {document_id}: {cv_data}")
            
            response = self.es.index(index=self.index_name, id=document_id, document=cv_data)
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
                            "profile": {
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
                                        "query": jd_query,
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
