
from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route("/chatbot")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(userText)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/garden-form")
def form():
    return render_template("form.html")

@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Extract form data
    form_data = {
        'location': request.form.get('location'),
        'gardenSize': request.form.get('gardenSize'),
        'existingPlants': request.form.get('existingPlants').split(';'),
        'shade': request.form.get('shade'),
        'soilType': request.form.get('soilType'),
        'water': request.form.get('water')
    }

    # Filter out empty strings in existingPlants
    form_data['existingPlants'] = list(filter(None, form_data['existingPlants']))

    # Save to a JSON file
    file_path = 'answers.json'
    with open(file_path, 'w') as json_file:
        json.dump(form_data, json_file, indent=4)

    # Redirect or inform the user after submission
    return 'Form submitted successfully!'

app.run(debug = True)