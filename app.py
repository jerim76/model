import os
import openai
import tensorflow as tf
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, send_from_directory
import uuid  # For generating unique filenames

# Initialize Flask app
app = Flask(__name__)

# Setup upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Replace with your actual OpenAI API key (get it from https://platform.openai.com/api-keys)
# OPENAI_API_KEY = 'your-api-key-here'
openai.api_key = os.getenv('OPENAI_API_KEY', 'sk-test-key')  # Use environment variable in production

# Class names for prediction
class_names = ['healthy', 'leaf blight', 'leafcurl', 'septorio leaf spot']

# Load model - note: in this environment we'll mock it
try:
    # In a real environment, you would use:
    # model = tf.keras.models.load_model('tomato_keras.keras')
    model = None
    print("Model loading would normally happen here")
except Exception as e:
    print(f"Model loading error: {e}")
    model = None

def classify_image(image_path):
    """Classify an image - mocked version for demonstration"""
    # In a real implementation:
    # img = Image.open(image_path).resize((224, 224)).convert('RGB')
    # img_array = np.array(img) / 255.0
    # img_array = np.expand_dims(img_array, axis=0)
    # predictions = model.predict(img_array)
    # class_index = np.argmax(predictions[0])
    
    # Mock prediction for demonstration
    print(f"Classifying image: {image_path}")
    return np.random.choice(class_names)  # Random class for demo

def generate_description(class_name):
    """Generate disease description - mocked version for demonstration"""
    print(f"Generating description for: {class_name}")
    
    # In a real implementation, you would use:
    # response = openai.ChatCompletion.create(
    #     model="gpt-4-turbo",
    #     messages=[
    #         {"role": "system", "content": "You're a plant expert..."},
    #         {"role": "user", "content": f"Describe {class_name}..."}
    #     ],
    #     max_tokens=100
    # )
    # return response.choices[0].message['content']
    
    # Mock response
    descriptions = {
        'healthy': "Healthy tomato plants have vibrant green leaves with no spots or discoloration. Maintain proper watering and nutrient balance to keep plants healthy.",
        'leaf blight': "Leaf blight appears as brown spots with yellow halos on leaves. Remove affected leaves and apply copper-based fungicides weekly to control spread.",
        'leafcurl': "Leaf curl causes upward curling and distortion of leaves. Control whiteflies with insecticidal soap and remove severely infected plants to prevent spread.",
        'septorio leaf spot': "Septorio leaf spot shows as small, circular spots with gray centers. Apply fungicides containing chlorothalonil and improve air circulation around plants."
    }
    return descriptions.get(class_name, "No description available.")

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        file = request.files.get('image')
        if file and file.filename != '':
            # Generate unique filename
            unique_id = uuid.uuid4().hex
            ext = os.path.splitext(file.filename)[1]
            filename = f"{unique_id}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            file.save(filepath)
            class_name = classify_image(filepath)
            description = generate_description(class_name)
            
            result = {
                'filename': filename,
                'class_name': class_name,
                'description': description
            }
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tomato Disease Classifier</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background-color: #f9f9f9; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .upload-form { margin: 20px 0; text-align: center; }
            .result { margin-top: 30px; padding: 20px; background-color: #e8f4f8; border-radius: 5px; }
            img { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; padding: 5px; }
            .disease { color: #c0392b; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍅 Tomato Disease Classifier</h1>
            
            <form class="upload-form" method="post" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required>
                <br><br>
                <input type="submit" value="Analyze Image">
            </form>
            
            {% if result %}
            <div class="result">
                <h2>Analysis Result</h2>
                <img src="{{ url_for('static', filename='uploads/' + result.filename) }}" alt="Uploaded leaf image">
                <p><strong>Condition:</strong> <span class="disease">{{ result.class_name }}</span></p>
                <p><strong>Description:</strong> {{ result.description }}</p>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """, result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
