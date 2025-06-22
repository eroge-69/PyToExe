import streamlit as st
from agno.agent import Agent
from agno.models.perplexity import Perplexity
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
from agno.document.reader.pdf_reader import PDFReader
from agno.storage.agent.sqlite import SqliteAgentStorage
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

# Storage functions (merged from load_storage.py)
def load_session_storage():
    """Load appropriate storage based on environment"""
    storage_path = os.getenv("AGENT_STORAGE_PATH", "business_agent.db")
    return SqliteAgentStorage(
        table_name="client_sessions",
        db_file=storage_path
    )

def load_personality_storage():
    """Separate storage for personality analysis"""
    storage_path = os.getenv("PERSONALITY_STORAGE_PATH", "personality_data.db")
    return SqliteAgentStorage(
        table_name="personality_sessions",
        db_file=storage_path
    )

def load_task_storage():
    """Separate storage for task extraction"""
    storage_path = os.getenv("TASK_STORAGE_PATH", "task_data.db")
    return SqliteAgentStorage(
        table_name="task_sessions",
        db_file=storage_path
    )

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# LaTeX processing functions
def process_latex_content(content):
    """Convert LaTeX expressions to Streamlit-compatible format"""
    if not content:
        return content
    
    # Protect code blocks from LaTeX processing
    code_blocks = []
    def replace_code(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    # Protect inline code and code blocks
    content = re.sub(r'``````', replace_code, content)
    content = re.sub(r'`[^`]+`', replace_code, content)
    
    # Convert LaTeX delimiters to Streamlit format
    # Display math: \[ ... \] -> $$ ... $$
    content = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', content, flags=re.DOTALL)
    
    # Inline math: \( ... \) -> $ ... $
    content = re.sub(r'\\\((.*?)\\\)', r'$\1$', content, flags=re.DOTALL)
    
    # Restore code blocks
    for i, code_block in enumerate(code_blocks):
        content = content.replace(f"__CODE_BLOCK_{i}__", code_block)
    
    return content

def display_content_with_latex(content, font_family="Arial"):
    """Display content with proper LaTeX rendering and font styling"""
    if not content:
        return
    
    # Process LaTeX expressions
    processed_content = process_latex_content(content)
    
    # Check if content contains LaTeX expressions
    has_latex = ('$$' in processed_content or 
                '$' in processed_content and not processed_content.count('$') % 2)
    
    if has_latex:
        # Use regular markdown for LaTeX content (Streamlit handles LaTeX in markdown)
        st.markdown(processed_content)
    else:
        # Use styled HTML for regular text
        st.markdown(
            f"<span style='font-family:{font_family},sans-serif'>{processed_content}</span>", 
            unsafe_allow_html=True
        )

# Enhanced Sidebar API Configuration
st.sidebar.header("🔑 API Configuration")

# Load environment variables as defaults
pplx_api_key_env = os.getenv("PERPLEXITY_API_KEY")
groq_api_key_env = os.getenv("GROQ_API_KEY")
openai_api_key_env = os.getenv("OPENAI_API_KEY")
openrouter_api_key_env = os.getenv("OPENROUTER_API_KEY")

# Provider selection (always available)
provider_choice = st.sidebar.selectbox("Choose API Provider:", ["Perplexity", "Groq", "OpenAI", "OpenRouter"])

# API Key input for each provider (always available)
st.sidebar.subheader(f"{provider_choice} Configuration")

if provider_choice == "Perplexity":
    # Show current status if env key exists
    if pplx_api_key_env:
        st.sidebar.info("✅ API key found in environment")
    
    # Always allow manual input
    pplx_api_key = st.sidebar.text_input(
        "Enter Perplexity API Key:", 
        value="",
        type="password",
        help="Leave empty to use environment variable if available"
    )
    
    # Use manual input if provided, otherwise use environment variable
    current_api_key = pplx_api_key if pplx_api_key else pplx_api_key_env
    
    if current_api_key:
        model_options = ["sonar", "sonar-pro"]
        selected_model = st.sidebar.selectbox("Select Model:", model_options)
    else:
        st.sidebar.error("Please provide a Perplexity API key")
        selected_model = None

elif provider_choice == "Groq":
    if groq_api_key_env:
        st.sidebar.info("✅ API key found in environment")
    
    groq_api_key = st.sidebar.text_input(
        "Enter Groq API Key:", 
        value="",
        type="password",
        help="Leave empty to use environment variable if available"
    )
    
    current_api_key = groq_api_key if groq_api_key else groq_api_key_env
    
    if current_api_key:
        model_options = ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"]
        selected_model = st.sidebar.selectbox("Select Model:", model_options)
    else:
        st.sidebar.error("Please provide a Groq API key")
        selected_model = None

elif provider_choice == "OpenAI":
    if openai_api_key_env:
        st.sidebar.info("✅ API key found in environment")
    
    openai_api_key = st.sidebar.text_input(
        "Enter OpenAI API Key:", 
        value="",
        type="password",
        help="Leave empty to use environment variable if available"
    )
    
    current_api_key = openai_api_key if openai_api_key else openai_api_key_env
    
    if current_api_key:
        model_options = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
        selected_model = st.sidebar.selectbox("Select Model:", model_options)
    else:
        st.sidebar.error("Please provide an OpenAI API key")
        selected_model = None

elif provider_choice == "OpenRouter":
    if openrouter_api_key_env:
        st.sidebar.info("✅ API key found in environment")
    
    openrouter_api_key = st.sidebar.text_input(
        "Enter OpenRouter API Key:", 
        value="",
        type="password",
        help="Leave empty to use environment variable if available"
    )
    
    current_api_key = openrouter_api_key if openrouter_api_key else openrouter_api_key_env
    
    if current_api_key:
        model_options = [
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-haiku",
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "meta-llama/llama-3.1-70b-instruct",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemini-pro-1.5",
            "mistralai/mixtral-8x7b-instruct",
            "cohere/command-r-plus"
        ]
        selected_model = st.sidebar.selectbox("Select Model:", model_options)
    else:
        st.sidebar.error("Please provide an OpenRouter API key")
        selected_model = None

# Display current configuration status
if current_api_key and selected_model:
    key_source = "Manual Input" if (
        (provider_choice == "Perplexity" and pplx_api_key) or
        (provider_choice == "Groq" and groq_api_key) or
        (provider_choice == "OpenAI" and openai_api_key) or
        (provider_choice == "OpenRouter" and openrouter_api_key)
    ) else "Environment Variable"
    
    st.sidebar.success(f"✅ Ready: {provider_choice} - {selected_model}")
    st.sidebar.caption(f"API Key Source: {key_source}")

def create_model_instance(provider, model_name, api_key):
    if provider == "Perplexity":
        return Perplexity(id=model_name, api_key=api_key)
    elif provider == "Groq":
        return Groq(id=model_name, api_key=api_key)
    elif provider == "OpenAI":
        return OpenAIChat(id=model_name, api_key=api_key)
    elif provider == "OpenRouter":
        return OpenRouter(id=model_name, api_key=api_key)

# File upload
pdf_text = ""
uploaded_pdf = st.file_uploader("Upload a PDF for context", type="pdf")
if uploaded_pdf:
    reader = PDFReader()
    with open("temp_uploaded.pdf", "wb") as f:
        f.write(uploaded_pdf.read())
    documents = reader.read("temp_uploaded.pdf")
    pdf_text = "\n".join([doc.content for doc in documents if doc.content])
    st.success("PDF loaded and text extracted!")

# Sidebar task manager
with st.sidebar:
    st.header("📋 Task Manager")
    if st.session_state.tasks:
        st.subheader("Current Tasks:")
        for i, task in enumerate(st.session_state.tasks):
            col1, col2 = st.columns([4, 1])
            with col1:
                completed = st.checkbox(task["text"], key=f"task_{i}", value=task.get("completed", False))
                if completed != task.get("completed", False):
                    st.session_state.tasks[i]["completed"] = completed
            with col2:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.tasks.pop(i)
                    st.rerun()
    else:
        st.info("No tasks yet. Start chatting to extract tasks!")

    st.subheader("Add Manual Task:")
    manual_task = st.text_input("Enter a task:", key="manual_task_input")
    if st.button("Add Task") and manual_task:
        st.session_state.tasks.append({
            "text": manual_task,
            "completed": False,
            "source": "manual"
        })
        st.rerun()

    if st.session_state.tasks and st.button("Clear All Tasks"):
        st.session_state.tasks = []
        st.rerun()

    st.markdown("---")
    font_options = ["Arial", "Calibri", "Comic Sans MS", "Courier New", "Georgia", "Helvetica", "Times New Roman", "Trebuchet MS", "Verdana"]
    selected_font = st.selectbox("Choose chat font", font_options, index=0, key="font_select")
    st.session_state.selected_font = selected_font
    st.markdown(f"""
        <style>
        html, body, [class^='st-'] {{
            font-family: '{selected_font}', sans-serif !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# Agent creation with LaTeX-aware instructions
@st.cache_resource
def create_personality_agent(provider, model_name, api_key):
    return Agent(
        name="Personality Agent",
        role="Summarize the conversation and identify the user's personality traits.",
        model=create_model_instance(provider, model_name, api_key),
        add_history_to_messages=True,
        storage=load_personality_storage(),
        instructions="""
            Summarize the conversation and give a brief personality analysis.
            When including mathematical expressions, use proper LaTeX formatting:
            - Use \\( and \\) for inline math
            - Use \\[ and \\] for display math
        """,
        markdown=True,
        stream=False,
    )

@st.cache_resource
def create_task_agent(provider, model_name, api_key):
    return Agent(
        name="Task Agent",
        role="Extract tasks from the conversation.",
        model=create_model_instance(provider, model_name, api_key),
        add_history_to_messages=True,
        storage=load_task_storage(),
        instructions="""
            Extract actionable tasks. Return as list, one per line starting with '- '.
            When including mathematical expressions, use proper LaTeX formatting:
            - Use \\( and \\) for inline math
            - Use \\[ and \\] for display math
        """,
        markdown=True,
        stream=False,
    )

@st.cache_resource
def create_main_agent(provider, model_name, api_key, _personality_agent, _task_agent):
    return Agent(
        name="Main Agent",
        role="Talk to the user and delegate to other agents.",
        model=create_model_instance(provider, model_name, api_key),
        add_history_to_messages=True,
        storage=load_session_storage(),
        team=[_personality_agent, _task_agent],
        instructions="""
            Talk to the user naturally and helpfully.
            Provide complete, well-formatted responses.
            When including mathematical expressions, use proper LaTeX formatting:
            - Use \\( expression \\) for inline math
            - Use \\[ expression \\] for display math (block equations)
            Do not mention delegation or other agents in your response.
        """,
        markdown=True,
        stream=False,
    )

def parse_tasks_from_response(response_text):
    tasks = []
    for line in response_text.split('\n'):
        line = line.strip()
        if line.startswith('- ') or line.startswith('* '):
            task = line[2:].strip()
            if len(task) > 3:
                tasks.append({"text": task, "completed": False, "source": "extracted"})
    return tasks

# Main application logic
if current_api_key and selected_model:
    personality_agent = create_personality_agent(provider_choice, selected_model, current_api_key)
    task_agent = create_task_agent(provider_choice, selected_model, current_api_key)
    main_agent = create_main_agent(provider_choice, selected_model, current_api_key, personality_agent, task_agent)

    st.title(f"🤖 AI Learning Assistant ({provider_choice} - {selected_model})")

    # Display chat history with LaTeX support
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            display_content_with_latex(
                message['content'], 
                st.session_state.get('selected_font', 'Arial')
            )

    if prompt := st.chat_input("You:"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            display_content_with_latex(
                prompt, 
                st.session_state.get('selected_font', 'Arial')
            )

        with st.chat_message("assistant"):
            try:
                message_placeholder = st.empty()
                full_prompt = f"Context from PDF:\n{pdf_text}\n\nUser: {prompt}" if pdf_text else prompt
                response = main_agent.run(full_prompt)
                content = response.content if hasattr(response, "content") else str(response)
                
                with message_placeholder.container():
                    display_content_with_latex(
                        content, 
                        st.session_state.get('selected_font', 'Arial')
                    )
                    
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")
                content = "Sorry, I encountered an error processing your request."
                with message_placeholder.container():
                    display_content_with_latex(
                        content, 
                        st.session_state.get('selected_font', 'Arial')
                    )

            st.session_state.messages.append({"role": "assistant", "content": content})

        # Task extraction with LaTeX support
        try:
            task_response = task_agent.run(f"Extract tasks from this conversation: User said: '{prompt}'")
            task_content = task_response.content if hasattr(task_response, "content") else str(task_response)
            new_tasks = parse_tasks_from_response(task_content)
            for task in new_tasks:
                if task["text"].lower() not in [t["text"].lower() for t in st.session_state.tasks]:
                    st.session_state.tasks.append(task)
            if new_tasks:
                st.rerun()
        except Exception as e:
            st.error(f"Error in task extraction: {str(e)}")

        # Analysis sections with LaTeX support
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("🧠 Personality Analysis", expanded=False):
                try:
                    res = personality_agent.run(f"Analyze this conversation: User said: '{prompt}'")
                    analysis_content = res.content if hasattr(res, 'content') else str(res)
                    display_content_with_latex(
                        analysis_content,
                        st.session_state.get('selected_font', 'Arial')
                    )
                except Exception as e:
                    st.error(f"Error in personality analysis: {str(e)}")

        with col2:
            with st.expander("📋 Latest Task Analysis", expanded=False):
                try:
                    res = task_agent.run(f"Extract tasks from this conversation: User said: '{prompt}'")
                    task_analysis_content = res.content if hasattr(res, 'content') else str(res)
                    display_content_with_latex(
                        task_analysis_content,
                        st.session_state.get('selected_font', 'Arial')
                    )
                except Exception as e:
                    st.error(f"Error in task extraction: {str(e)}")

else:
    st.warning("Please configure your API settings in the sidebar to start using the assistant.")
    st.info("Choose a provider and enter your API key to begin.")
