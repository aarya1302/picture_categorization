import os
import requests
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import piexif
from io import BytesIO

subscription_key = "0dbf2f0cb3994017bc9aa3397d80a0c9"
endpoint = "https://imageretrievalwab.cognitiveservices.azure.com/"
analyze_url = endpoint + "vision/v3.1/analyze"

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def filtered_tags(caption, tags): 
    filtered_tags = []
    if caption: 
        if "group" in caption: 
            filtered_tags.append("group")
        
    if tags: 
        if "smile" in tags: 
            filtered_tags.append("smile")
        if "boy" in tags: 
            filtered_tags.append("boy")
        if "girl" in tags:
            filtered_tags.append("girl")
    return filtered_tags
   
#checking exceptions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type': 'application/octet-stream'
        }
        params = {'visualFeatures': 'Categories,Description,Color,Tags'}
        response = requests.post(analyze_url, headers=headers, params=params, data=image_data)
        response.raise_for_status()
        analysis = response.json()
        description = analysis["description"]["captions"][0]["text"].capitalize() if analysis["description"]["captions"] else "No description available"
        print(analysis)
        tags = analysis["tags"]
        tag_texts = [tag['name'] for tag in tags]


        return description, tag_texts
    except Exception as e:
        print(f"Failed to analyze {image_path}: {e}")
        return None, None, None, None, None


#methods to add tags to images 
def add_tags_to_image(image_path, output_path, tags):
    
    img = Image.open(image_path)
    print(img)
    print("image successfully opened")
    try:
        exif_dict = piexif.load(img.info['exif'])
    except KeyError:
        exif_dict = {"Exif": {}}



    
    exif_bytes = piexif.dump(exif_dict)
    
    img.save(output_path, "jpeg", exif=exif_bytes)
    print("image saved")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            print("file is not in dir")

            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            caption,tags= analyze_image(file_path)
            fil_tags = filtered_tags(caption, tags)

            if caption:
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{caption}_{filename}")

                add_tags_to_image(file_path, output_path, tags)

                return render_template('upload.html', filename=f"{caption}_{filename}",caption=caption, tags=fil_tags)
    return render_template('upload.html', filename="", caption="")


if __name__ == '__main__':
    app.run(debug=True)
