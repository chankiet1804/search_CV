from source.pdf_processor import Processor

processor = Processor()

pdf_path = './Data/Test1/CV7.pdf'
cv_data = processor.extract_text_from_pdf(pdf_path)
data_text = processor.clean_text(cv_data)
sections = processor.parse_resume(data_text)

print(sections["Contact Information"])
print("-"*100)
print(sections["Profile"])
print("-"*100)
print(sections["Experiences"])
print("-"*100)
print(sections["Education"])
print("-"*100)
print(sections["Skills"])
print("-"*100)

# print(sections)