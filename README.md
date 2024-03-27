 
# Native Garden Assistant

The Native Garden Assistant is a comprehensive web application designed to help users select the best native plants for their gardens based on specific environmental conditions and preferences. This project incorporates web scraping to gather plant data, a Flask-based web server for handling interactions, and a chatbot powered by advanced language models to provide personalized plant recommendations.

## Features

- **User Garden Form**: Collects user preferences and garden conditions through a simple form.
- **Dynamic Plant Recommendations**: Offers plant recommendations tailored to the user's specific garden conditions, such as location, soil type, and sunlight exposure.
- **Chatbot Interaction**: Engages users in a conversational interface, allowing for detailed queries and recommendations.
- **Data-driven Insights**: Utilizes a rich dataset of plants, scraped from reputable sources, ensuring accurate and relevant recommendations.

## Getting Started

### Prerequisites

- Python 3.8+
- Pipenv or virtualenv
- An API key from OpenAI (for the chatbot functionality)

### Installation

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/yourusername/native-garden-assistant.git
   cd native-garden-assistant
   ```
2. Install the required Python packages:
```
pip install -r requirements.txt
```
3. Set up the .env file with your API keys and other configurations:
API_KEY='your_openai_api_key_here'
FLASK_SECRET_KEY='a_random_secret_key'

4. Run the Flask application:
```
python main.py
```

### Usage
Navigate to http://127.0.0.1:5000/ in your web browser to access the application.
Fill out the garden form with your garden's details.
Engage with the chatbot to refine your plant selections based on the chatbot's recommendations.

##Web Scraping
This project employs web scraping to aggregate a comprehensive dataset of native plants. The scraping script navigates through a specified list of states, collecting data on plant names, characteristics, and environmental requirements.

Running the Scraper
```
cd scraping
python sel_ver.py
```
Ensure you have a compatible WebDriver installed for Selenium to function correctly.

##Technology Stack
Frontend: HTML, CSS, JavaScript
Backend: Flask (Python), Selenium (for web scraping)
Data Storage: Pandas DataFrame, JSON files
NLP & Chatbot: OpenAI's GPT models, LangChain

##Acknowledgments
OpenAI for the GPT model used in the chatbot.
Flask for the web framework.
Selenium for the web scraping toolset.