from flask import Flask, render_template, request, url_for, jsonify

import os
import sys
import shutil
import random
import time
from gtts import gTTS
from PIL import Image
import pymupdf

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

        if ".txt" in uploaded_file_name:
            file_text, audio_text = parse_txt_file(uploaded_file_path)
        elif ".pdf" in uploaded_file_name:
            file_text, audio_text = parse_pdf_file(uploaded_file_path)

        

        myobj = gTTS(text=audio_text, lang='en', slow=False)
        myobj.save(os.getcwd() + url_for('static', filename='audio.mp3'))

        return jsonify({"success": True, "audio_file": "audio.mp3", "file_text": file_text})

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


def parse_txt_file(uploaded_file_path):

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

    return file_text, audio_text

def parse_pdf_file(uploaded_file_path):
    pdf = pymupdf.open(uploaded_file_path)

    print("pdf file length", len(pdf))
    page = pdf[0]

    doc_order = []
    audio_lines = []

    blocks = page.get_text("dict")["blocks"]
    for b in blocks:  # iterate through the text blocks\,
        if "ext" in b:
            if b["ext"] == "jpeg":
                doc_order.append("<p>" + str(s["bbox"]) + "image" + "</p>")
                audio_lines.append("image")
            else:
                pass
        elif "lines" in b:
            for l in b["lines"]:  # iterate through the text lines
                for s in l["spans"]:  # iterate through the text spans
                    doc_order.append("<p>" + str(s["bbox"]) + " " + str(round(s["size"])) + " " + s["text"] + "</p>")
                    audio_lines.append(s["text"])

    file_text = " ".join(doc_order)
    audio_text = " ".join(audio_lines)
    print(file_text)

    return file_text, audio_text











