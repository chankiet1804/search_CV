from flask import Blueprint, jsonify, request
from .elastic_handler import ElasticHandler

api = Blueprint('api', __name__)
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
        cvs = elastic.search_cv("")
        return jsonify({'cvs': cvs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'})