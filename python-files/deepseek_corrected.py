from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import TextLoader

import pickle
from dotenv import load_dotenv
import os
import streamlit as st
from streamlit_chat import message
import io
import asyncio
import requests
import html2text
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
import json
import logging

# Custom classes for OpenRouter integration
from langchain.embeddings.base import Embeddings
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from typing import List, Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Enhanced PDFChat with OpenRouter",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()
# Use OpenRouter API key instead of OpenAI
api_key = "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"

# OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"
#deepseek/deepseek-chat-v3-0324:free


# Use a local embedding model since OpenRouter doesn't provide embeddings
from sentence_transformers import SentenceTransformer
import numpy as np

class LocalEmbeddings(Embeddings):
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        try:
            logger.info(f"Embedding {len(texts)} documents")
            embeddings = self.model.encode(texts).tolist()
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        try:
            logger.info(f"Embedding query: {text[:50]}...")
            embedding = self.model.encode([text])[0].tolist()
            return embedding
        except Exception as e:
            logger.error(f"Error embedding query: {str(e)}")
            raise

# Custom Chat model for OpenRouter
class OpenRouterChat:
    def __init__(self, openrouter_api_key: str, model: str = OPENROUTER_MODEL, temperature: float = 0.7):
        self.openrouter_api_key = openrouter_api_key
        self.model = model
        self.temperature = temperature
        self.base_url = OPENROUTER_BASE_URL

    def __call__(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",  # Required by OpenRouter
            "X-Title": "PDFChat App"  # Required by OpenRouter
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"OpenRouter API status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")

async def main():
    async def storeDocEmbeds(file, filename):
        print("Inside the storedoc func")
        reader = PdfReader(file)
        print("reading content done")
        corpus = ''.join([p.extract_text() for p in reader.pages if p.extract_text()])

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(corpus)

        # Use local embeddings instead of OpenRouter
        embeddings = LocalEmbeddings()
        vectors = FAISS.from_texts(chunks, embeddings)

        with open(filename + ".pkl", "wb") as f:
            pickle.dump(vectors, f)

    async def getDocEmbeds(file, filename):
        if not os.path.isfile(filename + ".pkl"):
            await storeDocEmbeds(file, filename)

        with open(filename + ".pkl", "rb") as f:
            vectors = pickle.load(f)

        return vectors
    
    async def storeStringEmbeds(input_string, filename):
        corpus = input_string

        with open(filename, 'w') as f:
            f.write(input_string)

        loader = TextLoader(filename)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)

        # Use local embeddings
        embeddings = LocalEmbeddings()
        vectors = FAISS.from_documents(chunks, embeddings)

        with open(filename + ".pkl", "wb") as f:
            pickle.dump(vectors, f)

    async def getStringEmbeds(input_string, filename):
        if not os.path.isfile(filename + ".pkl"):
            await storeStringEmbeds(input_string, filename)

        with open(filename + ".pkl", "rb") as f:
            vectors = pickle.load(f)

        return vectors

    def extract_text_from_url(url):
        try:
            response = requests.get(url, timeout=10)
            converter = html2text.HTML2Text()
            converter.ignore_links = True
            text = converter.handle(response.text)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from URL: {str(e)}")
            return f"Error: Could not extract text from URL. {str(e)}"

    async def conversational_chat(query):
        try:
            if option == "database":
                # For database queries, use OpenRouter directly
                openrouter_chat = OpenRouterChat(openrouter_api_key=api_key)
                
                # Format the chat history for OpenRouter
                messages = []
                for human, assistant in st.session_state['history']:
                    messages.append({"role": "user", "content": human})
                    messages.append({"role": "assistant", "content": assistant})
                
                messages.append({"role": "user", "content": query})
                
                response = openrouter_chat(messages)
                result = response['choices'][0]['message']['content']
                st.session_state['history'].append((query, result))
                return result
            
            # For PDF and Blog queries
            openrouter_chat = OpenRouterChat(openrouter_api_key=api_key)
            
            # Format the chat history for OpenRouter
            messages = []
            for human, assistant in st.session_state['history']:
                messages.append({"role": "user", "content": human})
                messages.append({"role": "assistant", "content": assistant})
            
            messages.append({"role": "user", "content": query})
            
            response = openrouter_chat(messages)
            result = response['choices'][0]['message']['content']
            st.session_state['history'].append((query, result))
            return result
            
        except Exception as e:
            logger.error(f"Error in conversational_chat: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"

    if 'history' not in st.session_state:
        st.session_state['history'] = []

    # Creating the chatbot interface
    st.title("PDFChat with OpenRouter")

    option = st.selectbox("Select Option", ("PDF", "Blog", "database"))

    if option == "PDF":
        uploaded_file = st.file_uploader("Choose a file", type="pdf")

        if uploaded_file is not None:
            with st.spinner("Processing..."):
                uploaded_file.seek(0)
                file = uploaded_file.read()
                vectors = await getDocEmbeds(io.BytesIO(file), uploaded_file.name)
                # Store vectors in session state for later use
                st.session_state['vectors'] = vectors
            st.session_state['ready'] = True

    elif option == "Blog":
        url = st.text_input("Enter the URL of the blog")

        if url:
            with st.spinner("Processing..."):
                content = extract_text_from_url(url)
                if content.startswith("Error:"):
                    st.error(content)
                else:
                    vectors = await getStringEmbeds(content, "blog.txt")
                    # Store vectors in session state for later use
                    st.session_state['vectors'] = vectors
                    st.session_state['ready'] = True

    elif option == "database":
        uploaded_file = st.file_uploader("Choose a Database file", type="db")
        if uploaded_file is not None:
            with st.spinner("Processing..."):
                # Save the uploaded file temporarily
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Create database connection
                db = SQLDatabase.from_uri(f'sqlite:///./{uploaded_file.name}')
                # Store db in session state for later use
                st.session_state['db'] = db
            st.session_state['ready'] = True

    if st.session_state.get('ready', False):
        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["Welcome! You can now ask any questions"]

        if 'past' not in st.session_state:
            st.session_state['past'] = ["Hey!"]

        response_container = st.container()
        container = st.container()

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input("Query:", placeholder="e.g: Summarize the document", key='input')
                submit_button = st.form_submit_button(label='Send')

            if submit_button and user_input:
                with st.spinner("Thinking..."):
                    output = await conversational_chat(user_input)
                    st.session_state['past'].append(user_input)
                    st.session_state['generated'].append(output)

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    if i < len(st.session_state['past']):
                        st.markdown(
                            "<div style='background-color: #90caf9; color: black; padding: 10px; border-radius: 5px; width: 70%; float: right; margin: 5px;'>"+ st.session_state["past"][i] +"</div>",
                            unsafe_allow_html=True
                        )
                    message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")

if __name__ == "__main__":
    asyncio.run(main())
