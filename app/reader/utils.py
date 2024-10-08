import os


def save_uploaded_file(uploaded_file):
    file_upload_dir = os.path.join(os.getcwd(),"uploaded_file")
    clean_or_create_directory(file_upload_dir)

    # Save the file:
    uploaded_file_path = os.path.join(file_upload_dir,
        uploaded_file.filename)
    uploaded_file.save(uploaded_file_path)

    return uploaded_file_path

def clean_or_create_directory(dir_path):
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    else:
        clean_directory(dir_path)

def clean_directory(dir_path):
    stuff_in_dir = os.listdir(dir_path)
    for athing in stuff_in_dir:
        athings_path = os.path.join(dir_path,athing)
        if os.path.isfile(athings_path):
            os.remove(athings_path)
        elif os.path.isdir(athings_path):
            shutil.rmtree(athings_path)




