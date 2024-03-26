
from flask import Flask, jsonify, render_template, request
from flask_session import Session  # This is for server-side session management
from flask import redirect
from datetime import datetime
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv
import os
import flask
from langchain.chains import LLMChain
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentType, initialize_agent, Tool, ZeroShotAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI

GPT_MODEL = "gpt-3.5-turbo-0613"
# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'  # Use server-side session management
Session(app) 


@app.route("/chatbot")
def home():
    flask.session.pop('agent_chain', None)

    return render_template("chatbot.html")

def get_llm_response(user_text, chain):
    text = chain.run(input=user_text)
    return text

def get_llm(user_data, plant_list):
    search = DuckDuckGoSearchRun()
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="Use when You want to search information for the plants for the user.",
        )
    ]    
    # Convert the dictionary to a JSON string and format it for readability
    user_data_str = '\n'.join(f"{key}: {value}" for key, value in user_data.items())


    # Join the list elements into a single string
    plant_list_str = ", ".join(plant_list)
    prefix = f"""Have a conversation with a human, answering the questions about native gardening best You can. You will get all the user data gathered in conversation.
    Your objective is to help the user choose the best plants for their garden from the list provided here. Answer question and search for the answers. Recommend only the plants from the provided list.
    Take it into account when answering questions. Return as much data about the plants user can choose from as possible 
    Possible plants: {plant_list_str}
    User garden: {user_data_str}
    You have access to the following tools:"""
    suffix = """Conversation:
    {chat_history}
    Question: {input}
    {agent_scratchpad}"""

    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )
    memory = ConversationBufferMemory(memory_key="chat_history")
    llm = OpenAI(api_key=API_KEY)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory, handle_parsing_errors=True
    )
    flask.session['agent_chain'] = agent_chain
    return agent_chain

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    # Get a response from your LLM or simulation
    if 'agent_chain' not in flask.session:
        # Initialize the LLM chain if it doesn't exist in the session
        # Assuming 'user_data' and 'plant_list' are available or you fetch them accordingly
        user_data = {}  # Fetch or define user_data
        plant_list = []  # Fetch or define plant_list
        flask.session['agent_chain'] = get_llm(user_data, plant_list)
    agent_chain = flask.session['agent_chain']
    llm_response = get_llm_response(user_text, agent_chain)
    return jsonify({"text":llm_response})

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

    return redirect('/chatbot')

app.run(debug = True)