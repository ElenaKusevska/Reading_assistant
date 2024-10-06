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