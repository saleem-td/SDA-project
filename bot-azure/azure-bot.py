import openai
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page title
st.title("Chatbot with Azure OpenAI")

# Set up Azure OpenAI client
openai.api_type = "azure"
openai.api_base = "https://salim-m7kouj33-eastus2.cognitiveservices.azure.com/"  # Fixed base URL
openai.api_version = "2024-02-01-preview"  # Fixed API version
openai.api_key = os.getenv("AZURE_API_KEY")  # Secure API key handling

# Define deployment ID (this is the model name in Azure)
deployment_id = "gpt-4o"  # Ensure this matches your Azure deployment name

# Set up session state
if "messages" not in st.session_state:
    st.session_state.messages = []  

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What is up?"):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from Azure OpenAI
    with st.chat_message("assistant"):
        try:
            response = openai.ChatCompletion.create(
                deployment_id=deployment_id,  # Fixed parameter
                messages=st.session_state.messages
            )
            assistant_reply = response["choices"][0]["message"]["content"]

            # Display assistant's message
            st.markdown(assistant_reply)

            # Save assistant's response
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            st.error(f"Error: {str(e)}")
