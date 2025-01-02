from source.pdf_processor import Processor
from source.elastic_handler import ElasticHandler
from elasticsearch import Elasticsearch


processor = Processor()
elastic = ElasticHandler()
pdf_path = './Data/Test1/CV10.pdf'
# cv_data = processor.extract_text_from_pdf(pdf_path)
# data_text = processor.clean_text(cv_data)
# sections = processor.parse_resume(data_text)

# print(sections["Contact Information"])
# print("-"*100)
# print(sections["Profile"])
# print("-"*100)
# print(sections["Experiences"])
# print("-"*100)
# print(sections["Education"])
# print("-"*100)
# print(sections["Skills"])
# print("-"*100)

# print(sections)

# cv_data = processor.process_pdf(pdf_path)
# doc_id = elastic.index_cv(cv_data)