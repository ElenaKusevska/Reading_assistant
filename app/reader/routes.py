from flask import Blueprint

reader = Blueprint('reader', __name__, template_folder='templates', static_folder='static')

from flask import Flask, render_template, request, url_for, jsonify

import os
import random
from gtts import gTTS

from .pdf_functions import parse_pdf_file
from .txt_functions import parse_txt_file
from .utils import clear_directory


# First view of web app (when it's loaded for the first time):
@reader.route("/", methods=['GET'])
def index():
    rq = random.randint(0,10000)
    return render_template("reader/index.html", rq=rq)


@reader.route("/", methods=['POST'])
def upload():

    # Get file info from HTML form:
    uploaded_file = request.files['file']
    uploaded_file_name = uploaded_file.filename

    # Save and read file:
    if (uploaded_file_name != ''):

        # Clean up file upload directory if it exists,
        # or create it if it doesn't exist:
        file_upload_dir_path = os.path.join(os.getcwd(),"uploaded_file")
        if not os.path.isdir(file_upload_dir_path):
            os.mkdir(file_upload_dir_path)
        else:
            clear_directory(file_upload_dir_path)

        # Save the file:
        uploaded_file_path = os.path.join(file_upload_dir_path,
            uploaded_file_name)
        uploaded_file.save(uploaded_file_path)

        if ".txt" in uploaded_file_name:
            file_text, audio_text = parse_txt_file(uploaded_file_path)

            number_of_audio_files = 1
            audiofilename = '1.mp3'
            myobj = gTTS(text=audio_text, lang='en', slow=False)
            myobj.save(os.getcwd() + url_for('static', filename=audiofilename))
        elif ".pdf" in uploaded_file_name:
            file_text, audio_lines, naudio = parse_pdf_file(uploaded_file_path)

        return jsonify({"success": True, "audio_file": "1.mp3", "number_of_audio_files": naudio, "file_text": file_text})

    else:
        return jsonify({"success": False})



