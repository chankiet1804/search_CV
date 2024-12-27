from flask import Blueprint, jsonify, request
from flask_cors import CORS
from .elastic_handler import ElasticHandler

api = Blueprint('api', __name__)
CORS(api)  # Cho phép cross-origin requests
elastic = ElasticHandler()

@api.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        jd = data.get('jd')
        if not jd:
            return jsonify({'error': 'Vui lòng nhập mô tả công việc'}), 400

        results = elastic.search_cv(jd)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/cvs', methods=['GET'])
def list_cvs():
    try:
        cvs = elastic.get_all_cvs()
        return jsonify({'cvs': cvs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500