from langchain.chains import LLMChain
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentType, initialize_agent, Tool, ZeroShotAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI
from langchain.memory import ChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
conversation = {}
API_KEY = os.getenv("API_KEY")

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
    system_message = f"""Have a conversation with a human, answering the questions about native gardening best You can. You will get all the user data gathered in conversation.
    Your objective is to help the user choose the best plants for their garden from the list provided here. Answer question and search for the answers. Recommend only the plants from the provided list.
    Take it into account when answering questions. Return as much data about the plants user can choose from as possible 
    Possible plants: {plant_list_str}
    User garden: {user_data_str}
    You have access to the websearch tool use it to retrieve data about the plants."""
    suffix = """Conversation:
    {chat_history}
    Question: {input}
    {agent_scratchpad}"""
    
    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=system_message,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )
    llm = OpenAI(api_key=API_KEY)
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    if conversation:
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

    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory, handle_parsing_errors=True
    )

    return agent_chain

