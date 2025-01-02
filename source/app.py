# app.py
from flask import Flask, render_template, request, send_file, jsonify
import os
import io
import base64
from werkzeug.utils import secure_filename
from elastic_handler import ElasticHandler
from pdf_processor import Processor
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Elasticsearch handler
es_handler = ElasticHandler()
processor = Processor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files[]')
    processed_files = []

    for file in files:
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            cv_data = processor.process_pdf(file_path)
            if cv_data:
                try:
                    doc_id = es_handler.index_cv(cv_data)
                    processed_files.append({
                        'filename': filename,
                        'status': 'success',
                        'doc_id': doc_id
                    })
                except Exception as e:
                    processed_files.append({
                        'filename': filename,
                        'status': 'error',
                        'message': str(e)
                    })
            
            # Clean up uploaded file
            os.remove(file_path)

    return jsonify({'processed_files': processed_files})

@app.route('/search', methods=['POST'])
def search_cvs():
    data = request.get_json()
    print("Received data:", data)
    requirements = data.get('requirements', '')
    responsibilities = data.get('responsibilities', '')
    
    try:
        results = es_handler.search_cv_by_jd(
            job_requirements=str(requirements),
            job_responsibilities=str(responsibilities),
        )
        results_dict = results.body
        return jsonify(results_dict)
    except Exception as e:
        print("Error during search:", str(e))
        return jsonify({'error': str(e)}), 500
    
@app.route('/pdf/<doc_id>', methods=['GET'])
def get_pdf(doc_id):
    try:
        # Lấy tài liệu từ Elasticsearch dựa trên doc_id
        response = es_handler.get_document(index='cvs', doc_id=doc_id)
        # Giả sử bạn lưu trữ PDF ở dạng base64 trong Elasticsearch
        pdf_data = response['_source']['cv_data']

        # Giải mã base64 và chuyển thành byte stream
        pdf_bytes = base64.b64decode(pdf_data)
        pdf_io = io.BytesIO(pdf_bytes)

        # Trả về tệp PDF dưới dạng file
        return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='CV.pdf')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Create Elasticsearch index on startup
    es_handler.create_index()
    app.run(debug=True)