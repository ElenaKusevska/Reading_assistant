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
            file_text, audio_lines, naudio = parse_pdf_file(uploaded_file_path)

        return jsonify({"success": True, "audio_file": "1.mp3", "number_of_audio_files": naudio, "file_text": file_text})

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

    doc_order = []
    audio_lines = []

    image_files = []
    i_images = 0

    print("pdf file length", len(pdf))
    for page in pdf[4:7]:

        images = page.get_images()
        print("images:", images)
        for image in images:
            print(image)
            xref = image[0]
            base_image = pdf.extract_image(xref)
            with open(os.getcwd() + url_for('static', filename=image[7]), 'wb') as f:
                f.write(base_image['image'])
            image_files.append(image[7])

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:  # iterate through the text blocks\,
            if "ext" in block:
                if block["ext"] == "jpeg":
                    doc_order.append([0,i_images])
                    i_images = i_images + 1
                else:
                    pass
            elif "lines" in block:
                for l in block["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if round(s['size']) > 8:
                            doc_order.append([round(s['size']), s['text']])

    doc_order_merged = [[doc_order[0][0], doc_order[0][1]]]
    j = 0
    for i in range(1, len(doc_order)):
        if doc_order[i][0] > 0 and doc_order[i][0] == doc_order[i-1][0] and doc_order[i-1][1] != "/n":
            doc_order_merged[j][1] = doc_order_merged[j][1] + "/n" + doc_order[i][1]
        else:
            doc_order_merged.append([doc_order[i][0], doc_order[i][1]])
            j = j + 1

    naudio = 0
    doc_order_html = []
    for i in range(0, len(doc_order_merged)):
        if doc_order_merged[i][0] == 0:
            doc_order_html.append(f"<img src=http://127.0.0.1:5000/static/{image_files[doc_order_merged[i][1]]}>")
        else:
            doc_line_html = doc_order_merged[i][1].replace("/n","<br>")
            try:
                myobj = gTTS(text=doc_order_merged[i][1].replace("/n"," "), lang='en', slow=False)
                myobj.save(os.getcwd() + url_for('static', filename=f"{naudio}.mp3"))
                doc_order_html.append(f"<p id=\'{naudio}\'>{doc_order_merged[i][0]} {doc_line_html} </p>")
                print("audio", naudio)
                print(doc_order_merged[i][1])
                naudio = naudio + 1
            except Exception as e:
                doc_order_html.append(f"<p>{doc_order_merged[i][0]} {doc_line_html} </p>")
                print(doc_order_merged[i][1])
                print("Exception", e)


    file_text = " ".join(doc_order_html)

    return file_text, audio_lines, naudio


                    







