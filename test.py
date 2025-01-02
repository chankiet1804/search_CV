from source.pdf_processor import Processor
from source.elastic_handler import ElasticHandler
import os 

# Initialize components
processor = Processor()
elastic = ElasticHandler()

# pdf_directory = './Data/Test1/'

# for filename in os.listdir(pdf_directory):
#     if filename.endswith('.pdf'):
#         # Construct the full path to the PDF file
#         pdf_path = os.path.join(pdf_directory, filename)
        
#         # Index data
#         cv_data = processor.process_pdf(pdf_path)
#         doc_id = elastic.index_cv(cv_data)
        

#Thông tin từ JD với một số lỗi chính tả cố ý
requirements = """
- Recent graduate with a degree in Accounting, Finance, or a related field
- Basic knowledge of accounting principles and practices
- Familiarity with accounting software and tools (e.g., QuickBooks, Tally)
- Strong analytical and problem-solving skills
- Attention to detail and ability to manage financial data accurately
- Proficiency in Microsoft Excel and other office tools
"""

responsibilities = """
- Assist in preparing and maintaining financial records
- Support in the preparation of financial reports and statements
- Process invoices and manage accounts payable and receivable
- Help in reconciling bank statements and maintaining general ledger
- Assist with audits and ensure compliance with financial regulations
- Collaborate with the finance team to improve accounting processes
"""

results = elastic.search_cv_by_jd(
    job_requirements=requirements,
    job_responsibilities=responsibilities
)

def display_results(results):
    print(f"Tìm thấy {results['hits']['total']['value']} kết quả\n")
    
    for hit in results['hits']['hits']:
        print(f"CV ID: {hit['_source']['cv_id']}")
        print(f"Score: {hit['_score']}")
        
        if 'highlight' in hit:
            print("\nĐoạn văn phù hợp:")
            for field, highlights in hit['highlight'].items():
                print(f"\n{field.upper()}:")
                for highlight in highlights:
                    print(f"  • {highlight}")
        
        if 'metadata' in hit['_source']:
            print("\nThông tin thêm:")
            metadata = hit['_source']['metadata']
            if 'language' in metadata:
                print(f"Ngôn ngữ: {metadata['language']}")
            if 'last_updated' in metadata:
                print(f"Cập nhật lần cuối: {metadata['last_updated']}")
        
        print("\n" + "="*80 + "\n")

display_results(results)