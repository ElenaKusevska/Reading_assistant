from flask import Blueprint

reader = Blueprint('reader', __name__, template_folder='templates', static_folder='static')

from flask import Flask, render_template, request, url_for, jsonify

import os
import random
from gtts import gTTS

from .pdf_functions import parse_pdf_file, document_blocks_to_audio
from .txt_functions import parse_txt_file
from .utils import save_uploaded_file


@reader.route("/", methods=['GET'])
def index():
    rq = random.randint(0,10000)
    return render_template("reader/index.html", rq=rq)


@reader.route("/", methods=['POST'])
def upload():

    uploaded_file = request.files['file']

    if (uploaded_file.filename != ''):

        uploaded_file_path = save_uploaded_file(uploaded_file)

        if ".txt" in uploaded_file.filename:
            # logic for txt files not implemented yet
            file_text, audio_text = parse_txt_file(uploaded_file_path)
            return jsonify({"success": False})
            
        elif ".pdf" in uploaded_file.filename:
            doc_order_merged, image_files = parse_pdf_file(uploaded_file_path)
            file_text, naudio = document_blocks_to_audio(doc_order_merged, image_files)

            return jsonify({
                "success": True, 
                "audio_file": "1.mp3", 
                "number_of_audio_files": naudio, 
                "file_text": file_text
            })

    else:
        return jsonify({"success": False})


@reader.route("/pdf_training_data", methods=['GET'])
def pdf_training_data():
    rq = random.randint(0,10000)
    return render_template("reader/generate_training_data.html", rq=rq)


@reader.route("/pdf_training_data", methods=['POST'])
def pdf_training_data_upload():

    uploaded_file = request.files['file']

    if (uploaded_file.filename != ''):

        uploaded_file_path = save_uploaded_file(uploaded_file)

        if ".pdf" in uploaded_file.filename:
            doc_order_merged, image_files = parse_pdf_file(uploaded_file_path)
            csv_data = str(doc_order_merged)

            return jsonify({
                "success": True, 
                "csv_data": csv_data
            })

    else:
        return jsonify({"success": False})


@reader.route("/push_pdf_training_data", methods=['POST'])
def push_pdf_training_data():

    print(request)
    # Add push logic

    return jsonify({"success": True})



