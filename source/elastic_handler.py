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

    def search_cv_by_jd(self, jd_data: Dict, size: int = 10, min_score: float = 1.0) -> List[Dict]:
        """Search CVs based on job description data with enhanced matching."""
        
        # Tách required skills thành list và chuẩn hóa
        required_skills = [
            skill.strip().lower() 
            for skill in jd_data.get('Required skills and qualifications', '').split(',')
            if skill.strip()
        ]
        
        query = {
            "bool": {
                "should": [  # Sử dụng should thay vì must để linh hoạt hơn
                    # Match với required skills (trọng số cao nhất)
                    {
                        "terms": {
                            "skills.keyword": required_skills,
                            "boost": 2.0  # Giảm xuống từ 3.0
                        }
                    },
                    # Match với profile
                    {
                        "match": {
                            "profile": {
                                "query": f"{jd_data.get('Objectives of this role', '')} {jd_data.get('Responsibilities', '')}",
                                "operator": "or",  # Thay đổi từ and sang or
                                "minimum_should_match": "30%",  # Giảm xuống từ 70%
                                "boost": 1.0
                            }
                        }
                    },
                    # Match với preferred skills
                    {
                        "match": {
                            "skills.text": {
                                "query": jd_data.get('Preferred skills and qualifications', ''),
                                "boost": 1.5
                            }
                        }
                    },
                    # Match với experience
                    {
                        "nested": {
                            "path": "experience",
                            "query": {
                                "bool": {
                                    "should": [
                                        {
                                            "match": {  # Đổi từ match_phrase sang match
                                                "experience.title": {
                                                    "query": jd_data.get('Objectives of this role', ''),
                                                    "boost": 1.5
                                                }
                                            }
                                        },
                                        {
                                            "match": {
                                                "experience.description": {
                                                    "query": f"{jd_data.get('Responsibilities', '')} {jd_data.get('Required skills and qualifications', '')}",
                                                    "operator": "or",  # Thay đổi từ and sang or
                                                    "minimum_should_match": "30%",  # Giảm xuống từ 60%
                                                    "boost": 1.0
                                                }
                                            }
                                        }
                                    ]
                                }
                            },
                            "score_mode": "max"  # Thay đổi từ avg sang max
                        }
                    }
                ],
                "minimum_should_match": 1  # Giảm xuống từ 2, chỉ cần match 1 điều kiện
            }
        }
        
        try:
            response = self.es.search(
                index=self.index_name,
                body={
                    "query": query,
                    "min_score": min_score,
                    "_source": True,
                    "sort": [
                        {"_score": {"order": "desc"}}
                    ]
                },
                size=size
            )
            
            # Thêm debug info
            self.logger.info(f"Total hits: {response['hits']['total']['value']}")
            self.logger.info(f"Max score: {response['hits']['max_score']}")
            
            results = []
            for hit in response['hits']['hits']:
                result = hit['_source']
                result['search_score'] = hit['_score']
                results.append(result)
                
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {str(e)}")
            raise