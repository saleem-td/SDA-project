import openai
import streamlit as st
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Load environment variables
load_dotenv()

# Set up Streamlit page title
st.title("Chatbot with Azure OpenAI")

# Azure OpenAI Configuration
api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # Example: "https://your-resource-name.openai.azure.com/"
api_key = os.getenv("AZURE_OPENAI_KEY")  # Your Azure OpenAI API key
api_version = "2024-02-01"  # Replace with the latest API version
deployment_id = "gpt-4-turbo"  # Replace with your actual deployment name

# Ensure API key and endpoint are available
if not api_key or not api_base:
    st.error("Missing API key or endpoint. Please check your environment variables.")
    st.stop()

# Create a project client using environment variables loaded from the .env file
project = AIProjectClient.from_connection_string(
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"], credential=DefaultAzureCredential()
)

# Create a chat completions client
chat_client = project.inference.get_chat_completions_client()

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What is up?"):
    # Save and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from Azure OpenAI
    with st.chat_message("assistant"):
        try:
            response = chat_client.create_chat_completion(
                engine=deployment_id,  # Azure uses "engine" instead of "model"
                messages=st.session_state.messages,
                api_key=api_key,  # Provide API key explicitly
                base_url=f"{api_base}/openai/deployments",
                api_version=api_version
            )
            assistant_reply = response["choices"][0]["message"]["content"]

            # Display assistant response
            st.markdown(assistant_reply)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        except Exception as e:
            st.error(f"Error: {str(e)}")
