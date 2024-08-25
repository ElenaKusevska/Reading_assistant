from flask import Flask, render_template, request, url_for, jsonify

import os
import sys
import shutil
import random
import time
from gtts import gTTS
from PIL import Image
import pymupdf
import statistics  
from statistics import mode

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

    for page in pdf[4:-2]:
        blocks = page.get_text("dict", flags=20)["blocks"]
        for block in blocks:  # iterate through the text blocks\,
            if "ext" in block:
                if block["ext"] == "jpeg" or block["ext"] == "png":
                    with open(os.getcwd() + url_for('static', filename=f"{i_images}.{block['ext']}"), 'wb') as f:
                        f.write(block['image'])
                    image_files.append(f"{i_images}.{block['ext']}")
                    doc_order.append({
                        "type": "image", 
                        "details": [0,i_images]
                    })
                    i_images = i_images + 1
                else:
                    pass
            elif "lines" in block:
                y = 0
                text = ""
                font_size = 1
                block_lines = []
                for l in block["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        print("-------------------------------")
                        print("flags", s["flags"], s["font"], s["text"])
                        print("-------------------------------")
                        if round(s['size']) > 8:
                            # if we are on a new line
                            if round(s["origin"][1]) > y:
                                if y > 0:
                                    block_lines.append({
                                        "font_size": font_size, 
                                        "x": x, 
                                        "y": y, 
                                        "text": text,
                                        "tab": False
                                    })
                                y = round(s["origin"][1])
                                x = round(s["origin"][0])
                                text = s['text']
                                font_size = round(s['size'])

                                if ".B" in s["font"]:
                                    text = f"<b>{text}</b>"
                            else:
                                text = f"{text} {s['text']}"
                
                # Add the last span
                if text != "":
                    block_lines.append({
                        "font_size": font_size, 
                        "x": x, 
                        "y": y, 
                        "text": text,
                        "tab": False
                    })

                # Mark lines with a tab
                xs = [line["x"] for line in block_lines]
                if len(xs) > 2:
                    mode_x = mode(xs)
                    for line in block_lines:
                        if line["x"] > mode_x:
                            line["tab"] = True
                        

                doc_order.append({"type": "text", "details": block_lines})


    doc_order_merged = []
    for block in doc_order:
        if block["type"] == "text":
            block_text = ""
            for line in block["details"]:
                print(line)
                if not line["tab"]:
                    block_text = block_text + "/n" + line["text"]
                else:
                    doc_order_merged.append([line["font_size"], block_text])
                    block_text = line["text"]
            if block_text != "":
                doc_order_merged.append([line["font_size"], block_text])
        elif block["type"] == "image":
            doc_order_merged.append([0,block["details"][1]])
    

    naudio = 0
    doc_order_html = []
    for i in range(0, len(doc_order_merged)):
        if doc_order_merged[i][0] == 0:
            doc_order_html.append(f'<img src=http://127.0.0.1:5000/static/{image_files[doc_order_merged[i][1]]} class="image">')
        else:
            doc_order_merged[i][1] = doc_order_merged[i][1].replace(" ﬁ ","fi").replace(" fi ","fi")
            doc_line_html = doc_order_merged[i][1].replace("/n","<br>")
            try:
                myobj = gTTS(text=doc_order_merged[i][1].replace("/n"," ").replace("<b>","").replace("</b>",""), 
                    lang='en', slow=False)
                myobj.save(os.getcwd() + url_for('static', filename=f"{naudio}.mp3"))
                doc_order_html.append(f"<p id=\'{naudio}\'>{doc_order_merged[i][0]} {doc_line_html} </p>")
                print("audio", naudio)
                #print(doc_order_merged[i][1])
                naudio = naudio + 1
            except Exception as e:
                doc_order_html.append(f"<p>{doc_order_merged[i][0]} {doc_line_html} </p>")
                print(doc_order_merged[i])
                print("Exception", e)


    file_text = " ".join(doc_order_html)

    return file_text, audio_lines, naudio


                    







