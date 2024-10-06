from flask import Flask
from .reader.routes import reader

app = Flask(__name__)
app.register_blueprint(reader, url_prefix='/reader')

if __name__ == "__main__":
    app.run()




