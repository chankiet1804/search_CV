from source.pdf_processor import Processor
from source.elastic_handler import ElasticHandler

processor = Processor()
elastic = ElasticHandler()

pdf_path = './Data/Test1/CV1.pdf'
cv_data = processor.process_pdf(pdf_path)
doc_id = elastic.index_cv(cv_data)
