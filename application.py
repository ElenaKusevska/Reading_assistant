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

            number_of_audio_files = 1
            audiofilename = '1.mp3'
            myobj = gTTS(text=audio_text, lang='en', slow=False)
            myobj.save(os.getcwd() + url_for('static', filename=audiofilename))
        elif ".pdf" in uploaded_file_name:
            file_text, audio_lines = parse_pdf_file(uploaded_file_path)

            number_of_audio_files = len(audio_lines)
            for i in range(0, number_of_audio_files):
                audiofilename = f'{i}.mp3'
                print(audio_lines[i])
                try:
                    myobj = gTTS(text=audio_lines[i], lang='en', slow=False)
                    myobj.save(os.getcwd() + url_for('static', filename=audiofilename))
                except Exception as e:
                    print("Exception", e)
                print("audio", i)

        

        

        return jsonify({"success": True, "audio_file": "1.mp3", "number_of_audio_files": number_of_audio_files, "file_text": file_text})

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

    image_files = []
    images = page.get_images()
    for image in images:
        print(image)
        xref = image[0]
        base_image = pdf.extract_image(xref)
        with open(os.getcwd() + url_for('static', filename=image[7]), 'wb') as f:
            f.write(base_image['image'])
        image_files.append(image[7])

    doc_order = []
    audio_lines = []

    i_text = 0
    i_images = 0
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:  # iterate through the text blocks\,
        if "ext" in block:
            if block["ext"] == "jpeg":
                doc_order.append(f"<img src=http://127.0.0.1:5000/static/{image_files[i_images]}>")
                i_images = i_images + 1
            else:
                pass
        elif "lines" in block:
            for l in block["lines"]:  # iterate through the text lines
                for s in l["spans"]:  # iterate through the text spans
                    # {str(s['bbox'])}
                    doc_order.append(f"<p id=\'{i_text}\'> {str(round(s['size']))} {s['text']} </p>")
                    audio_lines.append(s["text"])
                    i_text = i_text + 1

    file_text = " ".join(doc_order)
    print(file_text)

    return file_text, audio_lines











