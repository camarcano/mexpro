import os
import json
from flask import render_template, request, jsonify, Response, current_app, stream_with_context
from flask_login import login_required, current_user
from app.ingest import bp
from app.extensions import csrf
from app.models.upload_log import UploadLog


@bp.route('/')
@login_required
def index():
    history = UploadLog.query.order_by(UploadLog.created_at.desc()).limit(20).all()
    return render_template('ingest/upload.html', history=history)


@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Only CSV files are accepted'}), 400

    # Save to upload folder
    upload_dir = current_app.config['CSV_UPLOAD_FOLDER']
    filepath = os.path.join(upload_dir, file.filename)
    file.save(filepath)

    # Start import and stream progress
    from app.ingest.services.csv_importer import import_csv

    def generate():
        for progress in import_csv(filepath, file.filename, current_user.id):
            yield f"data: {json.dumps(progress)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        },
    )


# Exempt the upload route from CSRF since it uses SSE
csrf.exempt(upload)


@bp.route('/history')
@login_required
def history():
    logs = UploadLog.query.order_by(UploadLog.created_at.desc()).all()
    return render_template('ingest/history.html', logs=logs)
