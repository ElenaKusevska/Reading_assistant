from flask import Flask, render_template, request, url_for, jsonify

import os
import sys
import shutil
import random
import time
from gtts import gTTS
import vlc

app = Flask(__name__)

# First view of web app (when it's loaded for the first time):
@app.route("/", methods=['GET'])
def index():
    rq = random.randint(0,10000)
    return render_template("index.html", rq=rq)


@app.route("/", methods=['POST'])
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

        # Read the file:
        uploaded_file=open(uploaded_file_path, "r")

        file_lines = []
        audio_lines = []
        for line in uploaded_file:
            file_lines.append(line + "<br>")
            audio_lines.append(line)
        file_text = " ".join(file_lines)
        audio_text = " ".join(audio_lines)
        print(file_text)

        myobj = gTTS(text=audio_text, lang='en', slow=False)
        myobj.save(os.getcwd() + "/welcome.mp3")

        return jsonify({"success": True, "audio_file": "welcome.mp3", "file_text": file_text})

    else:
        return jsonify({"success": False})

def clear_directory(dir_path):
    stuff_in_dir = os.listdir(dir_path)
    for athing in stuff_in_dir:
        athings_path = os.path.join(dir_path,athing)
        if os.path.isfile(athings_path):
            os.remove(athings_path)
        elif os.path.isdir(athings_path):
            shutil.rmtree(athings_path)











