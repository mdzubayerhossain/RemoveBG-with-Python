import os
import io
from flask import Flask, request, send_file , jsonify
from PIL import Image
from rembg import remove
from flask_cors import CORS  # Import the CORS class
import base64

app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/process_image": {"origins": "http://127.0.0.1:5500"}})  # Specify the allowed origin
# app = Flask(__name__)

# Define a directory to store uploaded images temporarily
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def remove_background(input_image):
#     img = remove(input_image)
#     return img

def remove_bg(input_path):
    with open(input_path, "rb") as inp_file:
        img = remove(inp_file.read())
        print('remove bg okay')
        return img


def overlay_img(overlay_image, background_image_path, position, size):
    background_image = Image.open(background_image_path)
    overlay_image = Image.open(io.BytesIO(overlay_image))
    overlay_image = overlay_image.resize(size)
    background_image.paste(overlay_image, position, overlay_image)
    return background_image



@app.route('/', methods=['GET'])
def index():
    return jsonify({'status':'okay'})

@app.route('/process_image', methods=['POST'])
def process_image():
    print(request)
    if 'image' not in request.files:
        
        return "No file part", 400

    file = request.files['image']
    
    if file.filename == '':
        return "No selected file", 400

    if file:
        inputFileName = 'input_img.jpg'
        # Save the uploaded image to the temporary directory
        # filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        filename = os.path.join(app.config['UPLOAD_FOLDER'], inputFileName)
        file.save(filename)

        # Define custom positioning and sizing
        position = (100, 370)  # The position where you want to place the overlay image (x, y)
        size = (800, 1000)  # The size to which you want to resize the overlay image (width, height)

        # Remove the background from the uploaded image
        img_without_bg = remove_bg(filename)

        # Overlay the processed image on a background
        result_image = overlay_img(img_without_bg, 'banner3.jpg', position, size)

        # Save the result
        result_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'result.png')
        result_image.save(result_filename)

        # Convert the result image to base64
        with open(result_filename, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Return the base64 encoded image data in the response
        return jsonify({'image': base64_image})

        # # Return the processed image
        # return send_file(result_filename, mimetype='image/png')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
    # app.run(host='127.0.0.1', port=5000)
