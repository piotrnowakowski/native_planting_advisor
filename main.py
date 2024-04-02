
from flask import Flask, jsonify, render_template, request
from flask_session import Session  # This is for server-side session management
from flask import redirect
import flask
from pathlib import Path
from datetime import datetime
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv
import os
import pandas as pd

from langchain import hub
from langchain.chains import LLMChain
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentType, initialize_agent, Tool, ZeroShotAgent, AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


GPT_MODEL = "gpt-3.5-turbo-0613"
# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'  # Use server-side session management
Session(app) 
AGENT_CHAIN = None

@app.route("/chatbot")
def home():
    flask.session.pop('agent_chain', None)

    return render_template("chatbot.html")

def get_llm_response(user_text, chain):
    text = chain.run(input=user_text)
    return text

def get_llm(user_data, plant_list):
    global AGENT_CHAIN
    search = DuckDuckGoSearchRun()
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="Use when You want to search information for the plants for the user.",
        )
    ]    
    #Convert the dictionary to a JSON string and format it for readability
    #tools = [TavilySearchResults(max_results=3)]
    
    user_data_str = '\n'.join(f"{key}: {value}" for key, value in user_data.items())
    # Join the list elements into a single string
    plant_list_str = ", ".join(plant_list)
    prefix = f"""Have a conversation with a human, answering the questions about native gardening best You can. You will get all the user data gathered in conversation.
    Your objective is to help the user choose the best plants for their garden from the list provided here. Answer question and search for the answers. Recommend only the plants from the provided list.
    Take it into account when answering questions. Return as much data about the plants user can choose from as possible. 
    The outcome of the conversation should be a list of plants that are best suited for the user's and he choosed them from the list provided.
    Possible plants: {plant_list_str}
    User garden: {user_data_str}
    You have access to the following tools:"""
    suffix = """Conversation:
    {chat_history}
    Question: {input}
    {agent_scratchpad}"""
    prefix = prefix + "\n{agent_scratchpad}"

    # prompt = ZeroShotAgent.create_prompt(
    #     tools,
    #     prefix=prefix,
    #     suffix=suffix,
    #     input_variables=["input", "chat_history", "agent_scratchpad"],
    # )

    prompt = hub.pull("hwchase17/openai-tools-agent")
    #prompt.set_input_variables(input=prefix, chat_history="", agent_scratchpad="")
    prompt = prompt.partial(instructions=prefix)
    
    # prompt = ChatPromptTemplate.from_messages([
    #     ("system", prefix),
    #     ("user", "{input}"),
    #     MessagesPlaceholder(variable_name="agent_scratchpad")
    # ])

    if 'conversation.history' in flask.session:
        conversation_history = flask.session['conversation.history']
        memory = ConversationBufferMemory(memory_key="chat_history")
        memory.chat_memory.add_ai_message(str(message))
        for message in conversation_history:
            if message['role'] == 'user':
                memory.chat_memory.add_ai_message(str(message))
            elif message['role'] == 'assistant':
                memory.chat_memory.add_human_message(str(message))
    else:
        memory = ConversationBufferMemory(memory_key="chat_history")
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, api_key=API_KEY)
    #llm = OpenAI(api_key=API_KEY)
    
    #llm_chain = LLMChain(llm=llm, prompt=prompt)
    #agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    AGENT_CHAIN = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory, handle_parsing_errors=True
    )

    flask.session['agent_chain'] = AGENT_CHAIN.to_json()
    return AGENT_CHAIN

def get_relevant_plants(user_data):
    # Assuming 'user_data' may include a 'state' key for filtering by state code
    state_code = user_data.get('location') if user_data else None
    df = pd.read_csv('whole_data.csv')

    filtered_df = df.copy()

    if state_code:
        filtered_df = filtered_df[filtered_df['State Code'] == state_code]
    filters = {
        'State Code': user_data.get('location'),
        'Shade': user_data.get('shade'),
        'Water': user_data.get('water')
    }
    # Proceed with other filters if the dataframe is not empty
    if not filtered_df.empty:
        for column, value in filters.items():
            if column in filtered_df.columns and value:
                # Special handling for "Sun" column to match any part of the value
                if column == 'Sun':
                    pattern = '|'.join(value)  # Create a regex pattern to match any of the values
                    filtered_df = filtered_df[filtered_df[column].str.contains(pattern, na=False)]
                else:  # Direct matching for other columns
                    filtered_df = filtered_df[filtered_df[column] == value]

    # Check if the filtered dataframe is not empty
    if not filtered_df.empty:
        plant_names = filtered_df['Scientific Name'].tolist()
        return plant_names
    else:
        # If filtering by state code already resulted in an empty df, return empty list
        return []
    

def conversation_summary():
    global AGENT_CHAIN

    memory = AGENT_CHAIN.memory.chat_memort.get()
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, api_key=API_KEY)
    prompt = ChatPromptTemplate( """Based on the conversation history please make a list of plants with their distinctive features that user choose in this conversation""" + str(''.join(memory)))
    answer = llm.invoke(prompt)
    return answer.content
    

@app.route("/get")
def get_bot_response():
    global AGENT_CHAIN
    user_text = request.args.get('msg')
    # Get a response from your LLM or simulation
    if not AGENT_CHAIN:
        try:
            with open('answers.json') as f:
                user_data = json.load(f)
        except FileNotFoundError:
            user_data = {}
        
        plant_list = get_relevant_plants(user_data)  
        AGENT_CHAIN = get_llm(user_data, plant_list)
    llm_response = get_llm_response(user_text, AGENT_CHAIN)
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
    # Save form data to answers.json
    if os.path.exists('answers.json'):
        os.remove('answers.json')

    with open('answers.json', 'w') as f:
        json.dump(form_data, f)
    return redirect('/chatbot')

app.run(debug = True)