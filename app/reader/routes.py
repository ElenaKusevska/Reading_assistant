from flask import Blueprint

reader = Blueprint('reader', __name__, template_folder='templates', static_folder='static')

from flask import Flask, render_template, request, url_for, jsonify

import os
import random
from gtts import gTTS

from .pdf_functions import parse_pdf_file
from .txt_functions import parse_txt_file
from .utils import save_uploaded_file


# First view of web app (when it's loaded for the first time):
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
            file_text, audio_lines, naudio = parse_pdf_file(uploaded_file_path)

            return jsonify({
                "success": True, 
                "audio_file": "1.mp3", 
                "number_of_audio_files": naudio, 
                "file_text": file_text
            })

    else:
        return jsonify({"success": False})



