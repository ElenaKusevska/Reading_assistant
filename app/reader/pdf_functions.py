import os
from gtts import gTTS
from PIL import Image
import pymupdf
from statistics import mode

from flask import url_for

def parse_pdf_file(uploaded_file_path):
    pdf = pymupdf.open(uploaded_file_path)

    doc_order = []

    image_files = []
    i_images = 0

    for page in pdf[0:2]:
        blocks = page.get_text("dict", flags=20)["blocks"]
        for block in blocks:  # iterate through the text blocks\,
            if "ext" in block:
                if block["ext"] == "jpeg" or block["ext"] == "png":
                    with open(os.getcwd() + url_for('reader.static', filename=f"{i_images}.{block['ext']}"), 'wb') as f:
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
                        if round(s['size']) > 7:
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
                if not line["tab"]:
                    block_text = block_text + "/n" + line["text"]
                else:
                    doc_order_merged.append([line["font_size"], block_text])
                    block_text = line["text"]
            if block_text != "":
                doc_order_merged.append([line["font_size"], block_text])
        elif block["type"] == "image":
            doc_order_merged.append([0,block["details"][1]])

    print(doc_order_merged)

    return doc_order_merged, image_files


def document_blocks_to_audio(doc_order_merged, image_files):

    naudio = 0
    doc_order_html = []
    for i in range(0, len(doc_order_merged)):
        if doc_order_merged[i][0] == 0:
            doc_order_html.append(f'<img src=http://127.0.0.1:5000/reader/static/{image_files[doc_order_merged[i][1]]} class="image">')
        else:
            doc_order_merged[i][1] = doc_order_merged[i][1].replace(" fi ","fi").replace(" fl ","fl")
            doc_order_merged[i][1] = doc_order_merged[i][1].replace(" . ",". ").replace(" , ",", ")
            doc_line_html = doc_order_merged[i][1].replace("/n","<br>")
            try:
                myobj = gTTS(text=doc_order_merged[i][1].replace("/n"," ").replace("<b>","").replace("</b>",""), 
                    lang='en', slow=False)
                myobj.save(os.getcwd() + url_for('reader.static', filename=f"{naudio}.mp3"))
                doc_order_html.append(f"<p id=\'{naudio}\'>{doc_order_merged[i][0]} {doc_line_html} </p>")
                print("audio", naudio)
                #print(doc_order_merged[i][1])
                naudio = naudio + 1
            except Exception as e:
                doc_order_html.append(f"<p>{doc_order_merged[i][0]} {doc_line_html} </p>")
                print(doc_order_merged[i])
                print("Exception", e)


    file_text = " ".join(doc_order_html)

    return file_text, naudio