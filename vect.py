from flask import Flask, request, render_template, redirect, url_for
import weaviate
import os
from werkzeug.utils import secure_filename
from PIL import Image
import base64

app = Flask(__name__)
app.config['UPLOAD_TEST_FOLDER'] = 'static/uploads/test'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

client = weaviate.Client("http://localhost:8080")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def initialize_weaviate():
    schema_res = client.schema.get()
    print(schema_res)

    class_exists = any(cls["class"] == "Meme" for cls in schema_res["classes"])

    if not class_exists:
        schema_config = {
            "class": "Meme",
            "vectorizer": "img2vec-neural",
            "vectorIndexType": "hnsw",
            "moduleConfig": {
                "img2vec-neural": {
                    "imageFields": ["image"],
                },
            },
            "properties": [
                {
                    "name": "image",
                    "dataType": ["blob"],
                },
                {
                    "name": "text",
                    "dataType": ["string"],
                },
            ],
        }
        client.schema.create_class(schema_config)
        print("Class 'Meme' created successfully.")
    else:
        print("Class 'Meme' already exists.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_TEST_FOLDER'], filename)
        file.save(file_path)

        with open(file_path, "rb") as img_file:
            img_data = img_file.read()
            b64 = base64.b64encode(img_data).decode('utf-8')
        print("this is image data")
        print(img_data)
        print("this is os path ")
        print(os.path.splitext(filename)[0])
        client.data_object.create({
            "image": b64,
            "text": os.path.splitext(filename)[0]  # Use the file name without extension as the text
        }, "Meme")
        
        
        query_image_base64 = base64.b64encode(img_data).decode('utf-8')
        response = client.query.get("Meme", ["image"]).with_near_image({"image": query_image_base64}).with_limit(1).do()
        print("this is response")
        print(response)
        result_image_base64 = response["data"]["Get"]["Meme"][0]["image"]
        result_image_path = os.path.join(app.config['UPLOAD_TEST_FOLDER'], "result.jpg")
        with open(result_image_path, "wb") as result_image_file:
            result_image_file.write(base64.b64decode(result_image_base64))

        return render_template('result.html', query_image=filename, result_image="result.jpg")

    return redirect(request.url)

if __name__ == '__main__':
    initialize_weaviate()
    app.run(debug=True, port=8000)
