import logging
from typing import Dict
from elasticsearch import Elasticsearch
import base64

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
                        "analyzer": "cv_analyzer",
                        "search_analyzer": "cv_analyzer"
                    },
                    "experience": {
                        "type": "text",
                        "analyzer": "cv_analyzer",
                        "search_analyzer": "cv_analyzer"
                    },
                    "education": {
                        "type": "text",
                        "analyzer": "cv_analyzer",
                        "search_analyzer": "cv_analyzer"
                    },
                    "cv_data":{
                        "type" : "text"
                    },
                    "contact": {
                        "type": "text",
                    },
                    "metadata": {
                        "properties": {
                            "last_updated": {"type": "date"},
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
    

    def search_cv_by_jd(self, job_requirements: str,job_responsibilities : str, size: int = 5) :
        """
        Tìm kiếm CV dựa trên yêu cầu công việc và trách nhiệm công việc, có hỗ trợ fuzzy matching
        
        Args:
            es_client: Elasticsearch client
            index_name: Tên index chứa CV
            job_requirements: Các kỹ năng yêu cầu từ JD
            job_responsibilities: Các trách nhiệm công việc từ JD
            size: Số lượng kết quả trả về
        """
        query = {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": job_requirements,
                            "fields": [
                                "skills^3",
                                "experience^2",
                                "profile"
                            ],
                            "type": "best_fields",
                            "operator": "or",
                            "minimum_should_match": "70%",
                            "fuzziness": "AUTO",
                            "prefix_length": 2,  # Số ký tự đầu tiên phải khớp chính xác
                            "max_expansions": 50,  # Số lượng từ biến thể tối đa cho mỗi term
                            "fuzzy_transpositions": True  # Cho phép hoán đổi 2 ký tự liền kề
                        }
                    },
                    {
                        "multi_match": {
                            "query": job_responsibilities,
                            "fields": [
                                "experience^3",
                                "profile^2",
                                "skills"
                            ],
                            "type": "best_fields",
                            "operator": "or",
                            "minimum_should_match": "60%",
                            "fuzziness": "AUTO",
                            "prefix_length": 2,
                            "max_expansions": 50,
                            "fuzzy_transpositions": True
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }

        # Thêm synonyms query để bắt các từ đồng nghĩa và viết tắt phổ biến
        synonyms_query = {
            "bool": {
                "should": [
                    {
                        "match": {
                            "skills": {
                                "query": job_requirements,
                                "fuzziness": "AUTO",
                                "prefix_length": 2,
                                "operator": "or"
                            }
                        }
                    },
                    {
                        "match": {
                            "experience": {
                                "query": job_responsibilities,
                                "fuzziness": "AUTO",
                                "prefix_length": 2,
                                "operator": "or"
                            }
                        }
                    }
                ]
            }
        }

        # Kết hợp queries
        final_query = {
            "bool": {
                "should": [
                    query,
                    synonyms_query
                ],
                "minimum_should_match": 1
            }
        }

        # Highlight configuration
        highlight = {
            "fields": {
                "skills": {
                    "number_of_fragments": 3,
                    "fragment_size": 150,
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"]
                },
                "experience": {
                    "number_of_fragments": 3,
                    "fragment_size": 150,
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"]
                },
                "profile": {
                    "number_of_fragments": 3,
                    "fragment_size": 150,
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"]
                }
            }
        }

        response = self.es.search(
            index=self.index_name,
            query=final_query,
            highlight=highlight,
            size=size,
            _source=["cv_id", "skills", "experience", "profile","cv_data", "metadata"]
        )

        return response
    
    def get_document(self, index, doc_id):
        try:
            response = self.es.get(index=index, id=doc_id)
            return response
        except Exception as e:
            print("Error getting document:", e)
            return None