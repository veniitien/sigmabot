import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import json
import os
import hashlib
import uuid
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time
import re
import random
from streamlit.components.v1 import html

# Load environment variables
load_dotenv()

# Initialize Gemini API
try:
    # Try to load from environment variable first
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDQM4n9Sm18uRqHciBxPPP6knFz09pLf_I")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error(f"Error initializing Gemini API: {str(e)}")
    st.stop()

# File paths for storing data
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHATS_FILE = os.path.join(DATA_DIR, "chats.json")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize data files if they don't exist
def init_data_files():
    initial_data = {
        USERS_FILE: {},
        CHATS_FILE: {}
    }
    
    for file_path, default_data in initial_data.items():
        try:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
            else:
                # Verify the file is valid JSON and has correct structure
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        # Reset file if data structure is incorrect
                        with open(file_path, 'w') as f:
                            json.dump(default_data, f, indent=2)
        except Exception as e:
            print(f"Error with {file_path}: {str(e)}")
            # Reset file if there's any error
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=2)

init_data_files()

# Data management functions
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Ensure we always return a dictionary
            if not isinstance(data, dict):
                data = {}
            return data
    except:
        return {}

def save_data(data, file_path):
    # Ensure we're saving a dictionary
    if not isinstance(data, dict):
        data = {}
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Configure the page
st.set_page_config(
    page_title="sigmabot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with animations and effects
st.markdown("""
<style>
/* Main theme - pitch black with neon effects */
.stApp {
    background-color: #000000 !important;
    color: #ffffff;
    transition: all 0.3s ease;
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 1rem !important;
}

/* Animated gradient background for headers */
h1, h2, h3 {
    background: linear-gradient(
        45deg,
        #1e88e5,
        #1976d2,
        #2196f3,
        #64b5f6
    );
    background-size: 300% 300%;
    color: white !important;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient 5s ease infinite;
    margin-bottom: 1rem;
    text-shadow: 0 0 10px rgba(33, 150, 243, 0.5);
}

/* Animated gradient background */
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Glowing text inputs */
.stTextInput input, .stTextArea textarea {
    background-color: #1a1a1a !important;
    color: white !important;
    border: 2px solid #333 !important;
    border-radius: 8px !important;
    padding: 12px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 10px rgba(30, 136, 229, 0.1) !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #1e88e5 !important;
    box-shadow: 0 0 20px rgba(30, 136, 229, 0.3) !important;
    transform: translateY(-2px);
}

/* Fancy buttons with glow and ripple */
.stButton > button {
    background: linear-gradient(45deg, #1e88e5, #1976d2) !important;
    color: white !important;
    border: none !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 0 15px rgba(30, 136, 229, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 30px rgba(30, 136, 229, 0.5) !important;
    animation: button-glow 1.5s ease-in-out infinite alternate;
}

@keyframes button-glow {
    from {
        box-shadow: 0 0 15px rgba(30, 136, 229, 0.3);
    }
    to {
        box-shadow: 0 0 30px rgba(30, 136, 229, 0.8);
    }
}

/* Ripple effect */
.ripple {
    position: absolute;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.7);
    animation: ripple 0.8s ease-out;
    pointer-events: none;
}

@keyframes ripple {
    to {
        transform: scale(15);
        opacity: 0;
    }
}

/* Sidebar styling */
.css-1d391kg, .css-1e5imcs {
    background-color: #111111 !important;
    border-right: 1px solid #333 !important;
}

/* Chat message styling */
.chat-message {
    padding: 0.75rem !important;
    margin: 0.25rem 0 !important;
    border-radius: 8px !important;
    animation: message-appear 0.3s ease-out !important;
    max-width: 90% !important;
}

@keyframes message-appear {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.user-message {
    background-color: #1a1a1a;
    border: 1px solid #333;
}

.assistant-message {
    background-color: #1e1e1e;
    border: 1px solid #1e88e5;
    box-shadow: 0 0 15px rgba(30, 136, 229, 0.2);
}

/* Loading animation */
@keyframes loading-glow {
    0% {
        box-shadow: 0 0 5px #1e88e5;
    }
    50% {
        box-shadow: 0 0 20px #1e88e5;
    }
    100% {
        box-shadow: 0 0 5px #1e88e5;
    }
}

.stProgress > div > div {
    background-color: #1e88e5 !important;
    animation: loading-glow 1.5s ease-in-out infinite;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #1a1a1a;
}

::-webkit-scrollbar-thumb {
    background: #333;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #1e88e5;
    box-shadow: 0 0 10px rgba(30, 136, 229, 0.5);
}

/* Robot profile picture */
.robot-avatar {
    width: 32px !important;
    height: 32px !important;
    border-radius: 50% !important;
    margin-right: 8px !important;
    vertical-align: middle !important;
}

/* Loading dots animation */
@keyframes loading-dots {
    0%, 20% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
    80%, 100% { transform: translateY(0); }
}

.loading-dots {
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.loading-dots span {
    width: 8px;
    height: 8px;
    background: #1e88e5;
    border-radius: 50%;
    animation: loading-dots 1.4s infinite;
}

.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

/* Compact input area */
.stTextArea textarea {
    height: 60px !important;
    padding: 8px !important;
    font-size: 14px !important;
}

/* File upload styling */
.stFileUploader {
    margin: 0.5rem 0 !important;
}

.stFileUploader > div {
    background-color: #1a1a1a !important;
    border: 2px solid #333 !important;
    border-radius: 8px !important;
    padding: 8px !important;
}

/* Search bar styling */
.search-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 1rem;
}

.search-bar input {
    flex: 1;
    background-color: #1a1a1a !important;
    color: white !important;
    border: 2px solid #333 !important;
    border-radius: 8px !important;
    padding: 8px !important;
}

.search-bar button {
    background: linear-gradient(45deg, #1e88e5, #1976d2) !important;
    color: white !important;
    border: none !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Flashcard styling */
.quizlet-card {
    background: linear-gradient(45deg, #1e88e5, #1976d2);
    border-radius: 15px;
    padding: 30px;
    margin: 20px auto;
    max-width: 600px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    font-family: 'Helvetica Neue', Arial, sans-serif;
    position: relative;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: white;
    transition: transform 0.6s;
    transform-style: preserve-3d;
}

.quizlet-card-front, .quizlet-card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: 600;
    padding: 20px;
}

.quizlet-card-back {
    transform: rotateY(180deg);
}

.quizlet-card.flipped {
    transform: rotateY(180deg);
}

.quizlet-button {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 2px solid white;
    border-radius: 25px;
    padding: 10px 25px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 10px;
}

.quizlet-button:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.quizlet-progress {
    color: white;
    font-size: 16px;
    margin: 15px 0;
    text-align: center;
}

/* Balloon animation */
@keyframes balloon-rise {
    0% { transform: translateY(100vh) scale(0.5); opacity: 0; }
    10% { transform: translateY(80vh) scale(1); opacity: 1; }
    100% { transform: translateY(-100vh) scale(0.5); opacity: 0; }
}

.balloon {
    position: fixed;
    width: 40px;
    height: 50px;
    background: linear-gradient(45deg, #ff69b4, #ff1493);
    border-radius: 50%;
    animation: balloon-rise 3s ease-out;
    z-index: 1000;
    box-shadow: 0 0 20px rgba(255, 105, 180, 0.5);
}

.balloon::before {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 2px;
    height: 20px;
    background: #ff69b4;
}

/* Timer styles */
.timer-container {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(30, 42, 69, 0.8);
    padding: 10px 20px;
    border-radius: 10px;
    border: 1px solid #2D3B58;
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
    z-index: 1000;
}

.timer-text {
    font-size: 24px;
    color: white;
    text-align: center;
    margin: 0;
}

/* Star animation */
@keyframes star-spin {
    0% { transform: rotate(0deg) scale(0); opacity: 0; }
    50% { transform: rotate(180deg) scale(1); opacity: 1; }
    100% { transform: rotate(360deg) scale(0); opacity: 0; }
}

.star {
    position: fixed;
    width: 30px;
    height: 30px;
    background: gold;
    clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
    animation: star-spin 1.5s ease-out;
    z-index: 1000;
}

/* X animation */
@keyframes x-appear {
    0% { transform: scale(0) rotate(0deg); opacity: 0; }
    50% { transform: scale(1.2) rotate(45deg); opacity: 1; }
    100% { transform: scale(1) rotate(45deg); opacity: 1; }
}

@keyframes x-shatter {
    0% { transform: scale(1) rotate(45deg); opacity: 1; }
    20% { transform: scale(1.2) rotate(45deg); opacity: 1; }
    100% { transform: scale(0) rotate(45deg) translateY(100vh); opacity: 0; }
}

.x-mark {
    position: fixed;
    width: 150px;
    height: 150px;
    color: #ff0000;
    font-size: 150px;
    z-index: 1000;
    text-align: center;
    line-height: 150px;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    text-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
}

.x-mark.appear {
    animation: x-appear 0.5s ease-out forwards;
}

.x-mark.shatter {
    animation: x-shatter 1s ease-in forwards;
}
</style>

<script>
// Ripple effect for buttons
document.addEventListener('DOMContentLoaded', function() {
    function createRipple(event) {
        const button = event.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        
        ripple.className = 'ripple';
        ripple.style.left = event.clientX - rect.left + 'px';
        ripple.style.top = event.clientY - rect.top + 'px';
        
        button.appendChild(ripple);
        
        ripple.addEventListener('animationend', () => {
            ripple.remove();
        });
    }

    document.querySelectorAll('.stButton > button').forEach(button => {
        button.addEventListener('click', createRipple);
    });
});

// Hover glow effect
document.addEventListener('mousemove', function(e) {
    const x = e.clientX;
    const y = e.clientY;
    const buttons = document.querySelectorAll('.stButton > button');
    
    buttons.forEach(button => {
        const rect = button.getBoundingClientRect();
        const buttonX = rect.left + rect.width / 2;
        const buttonY = rect.top + rect.height / 2;
        const distance = Math.sqrt(Math.pow(x - buttonX, 2) + Math.pow(y - buttonY, 2));
        
        if (distance < 100) {
            const intensity = 1 - distance / 100;
            button.style.boxShadow = `0 0 ${30 * intensity}px rgba(30, 136, 229, ${0.5 * intensity})`;
        } else {
            button.style.boxShadow = '';
        }
    });
});

function createBalloon() {
    const colors = ['#ff69b4', '#ff1493', '#ff00ff', '#ff69b4', '#ff1493'];
    for(let i = 0; i < 5; i++) {
        setTimeout(() => {
            const balloon = document.createElement('div');
            balloon.className = 'balloon';
            balloon.style.left = (Math.random() * (window.innerWidth - 40)) + 'px';
            balloon.style.background = colors[i % colors.length];
            document.body.appendChild(balloon);
            setTimeout(() => balloon.remove(), 3000);
        }, i * 200);
    }
}

function createStar() {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.left = Math.random() * window.innerWidth + 'px';
    star.style.top = Math.random() * window.innerHeight + 'px';
    document.body.appendChild(star);
    setTimeout(() => star.remove(), 1500);
}

function showX() {
    const x = document.createElement('div');
    x.className = 'x-mark appear';
    x.innerHTML = '✕';
    document.body.appendChild(x);
    
    setTimeout(() => {
        x.classList.remove('appear');
        x.classList.add('shatter');
        setTimeout(() => x.remove(), 1000);
    }, 500);
}

function flipCard() {
    const card = document.querySelector('.quizlet-card');
    card.classList.toggle('flipped');
}

// Timer update function
function updateTimer() {
    const timerElement = document.getElementById('quiz-timer');
    if (timerElement) {
        const startTime = parseInt(timerElement.getAttribute('data-start-time'));
        const duration = parseInt(timerElement.getAttribute('data-duration'));
        const now = Math.floor(Date.now() / 1000);
        const elapsed = now - startTime;
        const remaining = Math.max(0, duration * 60 - elapsed);
        
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;
        
        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        if (remaining > 0) {
            setTimeout(updateTimer, 1000);
        } else {
            // Time's up - trigger quiz submission
            const submitEvent = new Event('timeUp');
            document.dispatchEvent(submitEvent);
        }
    }
}
</script>
""", unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Web search function
def search_web(query):
    try:
        # Use Serper.dev API
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': '67a891aee4141511db3678cfd3beac28d31de79c',
            'Content-Type': 'application/json'
        }
        payload = {
            'q': query,
            'num': 5  # Number of results to return
        }
        
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        
        results = []
        # Extract organic search results
        if 'organic' in data:
            for result in data['organic'][:5]:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('link', ''),
                    'snippet': result.get('snippet', '')
                })
        
        # Add knowledge graph results if available
        if 'knowledgeGraph' in data:
            kg = data['knowledgeGraph']
            if kg and 'description' in kg:
                results.insert(0, {
                    'title': kg.get('title', 'Knowledge Graph'),
                    'url': kg.get('link', ''),
                    'snippet': kg.get('description', '')
                })
        
        return results
    except Exception as e:
        return [{'error': str(e)}]

# Typing animation function
def type_text(text, container):
    # Clear the container first
    container.empty()
    
    # Create a placeholder for the full text
    full_text = ""
    
    # Convert text to lowercase and add Gen Z style
    text = text.lower()
    text = text.replace("i'm", "im")
    text = text.replace("i am", "im")
    text = text.replace("you are", "ur")
    text = text.replace("you're", "ur")
    text = text.replace("what's up", "wassup")
    text = text.replace("okay", "aight")
    text = text.replace("alright", "aight")
    text = text.replace("brother", "bro")
    text = text.replace("sister", "sis")
    text = text.replace("thank you", "ty")
    text = text.replace("thanks", "ty")
    text = text.replace("no problem", "np")
    text = text.replace("for real", "fr")
    text = text.replace("to be honest", "tbh")
    text = text.replace("in my opinion", "imo")
    text = text.replace("just kidding", "jk")
    text = text.replace("laughing out loud", "lol")
    text = text.replace("right now", "rn")
    text = text.replace("by the way", "btw")
    
    # Type out the text character by character
    for char in text:
        full_text += char
        container.markdown(f"""
        <div class="chat-message assistant-message">
            <span style="font-size: 24px;">🤖</span>
            <strong>sigma:</strong><br>
            {full_text}
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.01)  # Adjust speed as needed

def show_auth_ui():
    st.title("welcome to sigmabot")
    st.markdown("### please sign in or create an account")
    
    # Center the auth forms
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        with tab1:
            with st.form("signin_form", clear_on_submit=True):
                username = st.text_input("Username", key="signin_username")
                password = st.text_input("Password", type="password", key="signin_password")
                submitted = st.form_submit_button("Sign In")
                
                if submitted:
                    if username and password:
                        users = load_data(USERS_FILE)
                        user_entry = next((
                            (uid, user) for uid, user in users.items()
                            if user.get('username') == username
                        ), None)
                        
                        if user_entry and user_entry[1]['password'] == hash_password(password):
                            st.session_state.user = {
                                'username': username,
                                'id': user_entry[0]
                            }
                            st.success("Successfully signed in!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter both username and password")
        
        with tab2:
            with st.form("signup_form", clear_on_submit=True):
                new_username = st.text_input("Choose Username", key="signup_username")
                new_password = st.text_input("Choose Password", type="password", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
                email = st.text_input("Email (optional)", key="signup_email")
                submitted = st.form_submit_button("Create Account")
                
                if submitted:
                    if new_username and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("Passwords do not match!")
                            return
                        
                        users = load_data(USERS_FILE)
                        
                        # Check if username already exists
                        if any(user.get('username') == new_username for user in users.values()):
                            st.error("Username already exists!")
                            return
                        
                        # Create new user
                        user_id = str(uuid.uuid4())
                        users[user_id] = {
                            'username': new_username,
                            'password': hash_password(new_password),
                            'email': email,
                            'created_at': datetime.now().isoformat()
                        }
                        
                        save_data(users, USERS_FILE)
                        st.success("Account created successfully! Please sign in.")
                        st.rerun()
                    else:
                        st.warning("Please fill in all required fields")

def delete_chat(chat_id):
    chats = load_data(CHATS_FILE)
    if chat_id in chats:
        del chats[chat_id]
        save_data(chats, CHATS_FILE)
        if st.session_state.current_chat == chat_id:
            st.session_state.current_chat = None
            st.session_state.chat_history = []
        st.rerun()

def show_sidebar():
    st.sidebar.title("🤖 sigmabot")
    
    # User info
    st.sidebar.markdown(f"welcome, {st.session_state.user['username']}!")
    
    if st.sidebar.button("Sign Out", key="signout_btn"):
        st.session_state.user = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # New chat button
    if st.sidebar.button("New Chat", key="new_chat_btn"):
        st.session_state.current_chat = None
        st.session_state.chat_history = []
        st.rerun()
    
    # Chat history
    st.sidebar.markdown("### Chat History")
    chats = load_data(CHATS_FILE)
    user_chats = {cid: chat for cid, chat in chats.items() 
                 if chat['user_id'] == st.session_state.user['id']}
    
    for chat_id, chat in user_chats.items():
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            if st.button(f"💬 {chat['title']}", key=f"chat_{chat_id}"):
                st.session_state.current_chat = chat_id
                st.session_state.chat_history = chat['messages']
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}"):
                delete_chat(chat_id)

def show_chat_ui():
    st.title("chat with sigmabot")
    
    # Add tabs for different features
    tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Flashcards", "Quiz", "Itinerary"])
    
    with tab1:
        # Chat history display
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <span style="font-size: 24px;">🤖</span>
                        <strong>sigma:</strong><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf', 'docx', 'csv', 'png', 'jpg', 'jpeg', 'gif'])
        if uploaded_file is not None:
            if uploaded_file.type.startswith('image/'):
                # Handle image upload
                st.image(uploaded_file, caption=uploaded_file.name)
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': f"I've uploaded an image: {uploaded_file.name}",
                    'timestamp': datetime.now().isoformat()
                })
                
                # Get AI response for the image
                try:
                    with st.spinner(""):
                        st.markdown("""
                        <div class="loading-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Create a temporary file to save the image
                        temp_file = f"temp_{uploaded_file.name}"
                        with open(temp_file, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        
                        # Generate response for the image
                        response = model.generate_content([
                            "yo, check out this pic and tell me what you see in a chill way, like you're talking to a friend. use gen z slang and keep it casual",
                            temp_file
                        ])
                        
                        # Clean up the temporary file
                        os.remove(temp_file)
                        
                        ai_response = response.text
                        
                        # Create a container for the typing animation
                        response_container = st.empty()
                        
                        # Type out the response
                        type_text(ai_response, response_container)
                        
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': ai_response,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        # Save chat
                        chats = load_data(CHATS_FILE)
                        if not st.session_state.current_chat:
                            st.session_state.current_chat = str(uuid.uuid4())
                            chats[st.session_state.current_chat] = {
                                'user_id': st.session_state.user['id'],
                                'title': f"Image Analysis: {uploaded_file.name}",
                                'messages': st.session_state.chat_history,
                                'created_at': datetime.now().isoformat(),
                                'updated_at': datetime.now().isoformat()
                            }
                        else:
                            chats[st.session_state.current_chat]['messages'] = st.session_state.chat_history
                            chats[st.session_state.current_chat]['updated_at'] = datetime.now().isoformat()
                        
                        save_data(chats, CHATS_FILE)
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
            else:
                # Handle text file upload
                file_content = uploaded_file.getvalue().decode()
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': f"I've uploaded a file: {uploaded_file.name}\n\nContent:\n{file_content}",
                    'timestamp': datetime.now().isoformat()
                })
        
        # Web search
        with st.expander("Search the Web", expanded=False):
            search_query = st.text_input("Enter your search query")
            if st.button("Search"):
                if search_query:
                    # Show loading state
                    with st.spinner("Searching..."):
                        results = search_web(search_query)
                        
                        if results and not any('error' in r for r in results):
                            st.markdown("### Search Results")
                            for result in results:
                                st.markdown(f"""
                                <div class="search-result">
                                    <h4><a href="{result['url']}" target="_blank">{result['title']}</a></h4>
                                    <p>{result['snippet']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error("No results found or an error occurred.")
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area("Type your message...", key="chat_input", height=68)
            col1, col2 = st.columns([1, 5])
            with col1:
                submit = st.form_submit_button("Send")
            
            if submit and user_input:
                # Add user message to history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Get AI response using Gemini
                try:
                    with st.spinner(""):
                        st.markdown("""
                        <div class="loading-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add personality prompt
                        prompt = f"respond to this in a chill, gen z way using slang like 'bro', 'aight', 'cool', etc. keep it casual and lowercase: {user_input}"
                        response = model.generate_content(prompt)
                        ai_response = response.text
                        
                        # Create a container for the typing animation
                        response_container = st.empty()
                        
                        # Type out the response
                        type_text(ai_response, response_container)
                        
                except Exception as e:
                    ai_response = f"yo bro, something went wrong: {str(e)}"
                
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': ai_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Save chat
                chats = load_data(CHATS_FILE)
                if not st.session_state.current_chat:
                    st.session_state.current_chat = str(uuid.uuid4())
                    chats[st.session_state.current_chat] = {
                        'user_id': st.session_state.user['id'],
                        'title': user_input[:30] + "..." if len(user_input) > 30 else user_input,
                        'messages': st.session_state.chat_history,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                else:
                    chats[st.session_state.current_chat]['messages'] = st.session_state.chat_history
                    chats[st.session_state.current_chat]['updated_at'] = datetime.now().isoformat()
                
                save_data(chats, CHATS_FILE)
                st.rerun()

    with tab2:
        show_flashcards_ui()
        
    with tab3:
        show_quiz_ui()

    with tab4:
        show_itinerary_ui()

# Add these functions after the existing functions
def generate_flashcards(content):
    try:
        prompt = f"""create 5 flashcards from this content. format each as a term and definition pair.
        make the definitions clear and concise. content: {content}"""
        response = model.generate_content(prompt)
        cards = []
        for line in response.text.split('\n'):
            line = line.strip()
            if ':' in line:
                term, definition = line.split(':', 1)
                cards.append({
                    'term': term.strip(),
                    'definition': definition.strip(),
                    'mastered': False,
                    'last_reviewed': None
                })
        return cards
    except Exception as e:
        return []

def show_flashcards_ui():
    st.markdown("### 🎴 Flashcards")
    
    # Initialize session state
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = []
    if 'current_card' not in st.session_state:
        st.session_state.current_card = 0
    if 'show_definition' not in st.session_state:
        st.session_state.show_definition = False
    
    # File upload
    uploaded_file = st.file_uploader("Upload content for flashcards", type=['txt', 'pdf', 'docx'])
    if uploaded_file is not None:
        content = uploaded_file.getvalue().decode()
        st.session_state.flashcards = generate_flashcards(content)
        st.session_state.current_card = 0
        st.session_state.show_definition = False
    
    # Manual content input
    content = st.text_area("Or type content for flashcards")
    if st.button("Generate Flashcards") and content:
        st.session_state.flashcards = generate_flashcards(content)
        st.session_state.current_card = 0
        st.session_state.show_definition = False
    
    # Display current flashcard
    if st.session_state.flashcards:
        current = st.session_state.flashcards[st.session_state.current_card]
        
        st.markdown(f"""
        <div class="quizlet-card {'flipped' if st.session_state.show_definition else ''}">
            <div class="quizlet-card-front">
                {current['term']}
            </div>
            <div class="quizlet-card-back">
                {current['definition']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Controls
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.show_definition:
                if st.button("Flip", key="flip_btn"):
                    st.session_state.show_definition = True
                    st.rerun()
            else:
                if st.button("Next", key="next_btn"):
                    st.session_state.current_card = (st.session_state.current_card + 1) % len(st.session_state.flashcards)
                    st.session_state.show_definition = False
                    st.rerun()
        
        st.markdown(f"""
        <div class="quizlet-progress">
            Card {st.session_state.current_card + 1} of {len(st.session_state.flashcards)}
        </div>
        """, unsafe_allow_html=True)

def generate_quiz(category, context=None):
    try:
        prompt = f"""create a quiz with 5 multiple choice questions about {category}"""
        if context:
            prompt += f" specifically focusing on {context}"
        prompt += """. 
        format each question as:
        Q: [question text]
        A) [option A]
        B) [option B]
        C) [option C]
        D) [option D]
        Correct: [letter of correct answer]
        
        make the questions challenging but fair, and ensure each question has exactly 4 options."""
        
        response = model.generate_content(prompt)
        questions = []
        current_question = None
        
        for line in response.text.split('\n'):
            line = line.strip()
            if line.startswith('Q:'):
                if current_question:
                    questions.append(current_question)
                current_question = {
                    'question': line[2:].strip(),
                    'options': [],
                    'correct': None
                }
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                option_letter = line[0]
                option_text = line[2:].strip()
                current_question['options'].append({
                    'letter': option_letter,
                    'text': option_text
                })
            elif line.startswith('Correct:'):
                current_question['correct'] = line[8:].strip()
        
        if current_question:
            questions.append(current_question)
            
        return questions
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return []

def show_quiz_ui():
    st.markdown("### 🎯 Quiz Master")
    
    # Initialize session state for quiz
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'quiz_start_time' not in st.session_state:
        st.session_state.quiz_start_time = None
    if 'quiz_duration' not in st.session_state:
        st.session_state.quiz_duration = None
    if 'show_correct' not in st.session_state:
        st.session_state.show_correct = False

    # Create placeholders for timer and animations
    timer_placeholder = st.empty()
    animation_placeholder = st.empty()

    # Quiz setup (only show if quiz not started)
    if not st.session_state.quiz_questions:
        categories = ["Science", "History", "Sports", "Music", "Movies", "Geography", "Technology", "Art"]
        selected_category = st.selectbox("Choose a category", categories)
        
        context = st.text_area(
            "Optional: Add specific context or topics",
            help="Customize the quiz questions"
        )
        
        minutes = st.number_input("Quiz duration (minutes)", min_value=1, max_value=60, value=5)
        
        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz..."):
                st.session_state.quiz_questions = generate_quiz(selected_category, context if context else None)
                st.session_state.user_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.current_question_index = 0
                st.session_state.quiz_start_time = time.time()
                st.session_state.quiz_duration = minutes
                st.session_state.show_correct = False
                st.rerun() # Rerun to start the quiz and timer

    # Main quiz logic
    elif not st.session_state.quiz_submitted:
        # --- Timer Logic ---
        if st.session_state.quiz_start_time:
            elapsed_time = time.time() - st.session_state.quiz_start_time
            remaining_time = max(0, st.session_state.quiz_duration * 60 - elapsed_time)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)

            # Update timer display using the placeholder
            timer_placeholder.markdown(f"""
            <div class="timer-container">
                <p class="timer-text">⏱️ {minutes:02d}:{seconds:02d}</p>
            </div>
            """, unsafe_allow_html=True)

            # Check if time's up
            if remaining_time <= 0:
                st.session_state.quiz_submitted = True
                st.rerun() # Rerun to show results

            # Force a rerun every second to update the timer
            time.sleep(1)
            st.rerun()
        # --- End Timer Logic ---

        # --- Question Display ---
        current_question = st.session_state.quiz_questions[st.session_state.current_question_index]
        
        st.markdown(f"""
        <div style='text-align: center; font-size: 20px; margin: 20px 0;'>
            Question {st.session_state.current_question_index + 1} of {len(st.session_state.quiz_questions)}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='text-align: center; font-size: 24px; margin: 20px 0;'>
            {current_question['question']}
        </div>
        """, unsafe_allow_html=True)
        
        # --- Answer Buttons ---
        # Disable buttons if answer was shown
        buttons_disabled = st.session_state.show_correct

        col1, col2 = st.columns(2)
        options = current_question['options']
        button_keys = ["option_a", "option_b", "option_c", "option_d"]
        
        # Display buttons A and C in col1
        with col1:
            if st.button(f"A) {options[0]['text']}", key=button_keys[0], use_container_width=True, disabled=buttons_disabled):
                handle_answer('A', animation_placeholder)
            if len(options) > 2 and st.button(f"C) {options[2]['text']}", key=button_keys[2], use_container_width=True, disabled=buttons_disabled):
                 handle_answer('C', animation_placeholder)

        # Display buttons B and D in col2
        with col2:
            if len(options) > 1 and st.button(f"B) {options[1]['text']}", key=button_keys[1], use_container_width=True, disabled=buttons_disabled):
                handle_answer('B', animation_placeholder)
            if len(options) > 3 and st.button(f"D) {options[3]['text']}", key=button_keys[3], use_container_width=True, disabled=buttons_disabled):
                handle_answer('D', animation_placeholder)

        # --- Feedback and Next Button ---
        if st.session_state.show_correct:
            user_answer = st.session_state.user_answers.get(st.session_state.current_question_index)
            correct_answer = current_question['correct']
            
            if user_answer == correct_answer:
                st.success("Correct! 🎉")
            else:
                st.error(f"Incorrect! The correct answer was {correct_answer})")

            # Next button
            if st.button("Next Question"):
                animation_placeholder.empty() # Clear previous animation
                st.session_state.current_question_index += 1
                st.session_state.show_correct = False
                if st.session_state.current_question_index >= len(st.session_state.quiz_questions):
                    st.session_state.quiz_submitted = True
                st.rerun() # Rerun for next question or results

    # Show results if submitted
    elif st.session_state.quiz_submitted:
        timer_placeholder.empty() # Clear timer when quiz is done
        animation_placeholder.empty() # Clear animations

        correct_count = sum(1 for i, q in enumerate(st.session_state.quiz_questions)
                          if st.session_state.user_answers.get(i) == q['correct'])
        
        st.markdown("### Quiz Complete! 🎉")
        st.markdown(f"""
        <div style='text-align: center; font-size: 24px; margin: 20px 0;'>
            Final Score: {correct_count} out of {len(st.session_state.quiz_questions)}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Try Another Quiz"):
            # Reset all quiz state variables
            st.session_state.quiz_questions = []
            st.session_state.user_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.current_question_index = 0
            st.session_state.quiz_start_time = None
            st.session_state.quiz_duration = None
            st.session_state.show_correct = False
            st.rerun()

def handle_answer(answer, animation_placeholder):
    st.session_state.user_answers[st.session_state.current_question_index] = answer
    st.session_state.show_correct = True

    # Trigger animation immediately based on correctness
    current_question = st.session_state.quiz_questions[st.session_state.current_question_index]
    if answer == current_question['correct']:
        # Use placeholder to show balloon animation
        animation_placeholder.markdown("""
        <script>
            (function() {
                const colors = ['#ff69b4', '#ff1493', '#ff00ff', '#ff69b4', '#ff1493'];
                for(let i = 0; i < 5; i++) {
                    setTimeout(() => {
                        const balloon = document.createElement('div');
                        balloon.className = 'balloon';
                        balloon.style.left = (Math.random() * (window.innerWidth - 40)) + 'px';
                        balloon.style.background = colors[i % colors.length];
                        document.body.appendChild(balloon);
                        setTimeout(() => balloon.remove(), 3000);
                    }, i * 200);
                }
            })(); // IIFE to run immediately
        </script>
        """, unsafe_allow_html=True)
    else:
        # Use placeholder to show X animation
        animation_placeholder.markdown("""
        <script>
            (function() {
                const x = document.createElement('div');
                x.className = 'x-mark appear';
                x.innerHTML = '✕';
                document.body.appendChild(x);
                
                setTimeout(() => {
                    x.classList.remove('appear');
                    x.classList.add('shatter');
                    setTimeout(() => x.remove(), 1000);
                }, 500);
            })(); // IIFE to run immediately
        </script>
        """, unsafe_allow_html=True)

    st.rerun() # Rerun to show feedback and Next button

def display_route_map(locations):
    """Display a route map between multiple locations using Google Maps Embed API"""
    if not locations or len(locations) < 2:
        st.warning("Need at least two locations to display a route")
        return
    
    try:
        # First try to use Mapbox
        display_mapbox_map(locations, is_route=True)
    except Exception as e:
        # Fall back to Google Maps if Mapbox fails
        try:
            # Create an iframe to display Google Maps
            api_key = "AIzaSyDQ9z1x7YrqaZG_Cnfvn-vSt6kVDcGyRmQ"  # Google Maps API key
            
            # Format locations for the URL
            origin = locations[0].replace(' ', '+')
            destination = locations[-1].replace(' ', '+')
            waypoints = '|'.join([loc.replace(' ', '+') for loc in locations[1:-1]]) if len(locations) > 2 else ""
            
            # Build the URL for the Google Maps embed API with directions
            if waypoints:
                map_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={destination}&waypoints={waypoints}&mode=driving"
            else:
                map_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={destination}&mode=driving"
            
            # Create the iframe with the map
            iframe_html = f'<iframe width="100%" height="450" frameborder="0" style="border:0" src="{map_url}" allowfullscreen></iframe>'
            st.markdown(iframe_html, unsafe_allow_html=True)
        except Exception as e2:
            st.error(f"Error displaying route map: {str(e2)}")
            # Fallback to simplified map display
            st.info("Route map couldn't be displayed. Here's a text representation:")
            for i, loc in enumerate(locations):
                if i < len(locations) - 1:
                    st.markdown(f"{i+1}. {loc} → {locations[i+1]}")
                else:
                    st.markdown(f"{i+1}. {loc} (Final destination)")

def display_google_map(locations):
    """Display locations on a Google Map with markers"""
    if not locations or len(locations) == 0:
        st.warning("No locations to display on map")
        return
    
    try:
        # First try to use Mapbox
        display_mapbox_map(locations, is_route=False)
    except Exception as e:
        # Fall back to Google Maps if Mapbox fails
        try:
            # Create an iframe to display Google Maps
            api_key = "AIzaSyDQ9z1x7YrqaZG_Cnfvn-vSt6kVDcGyRmQ"  # Google Maps API key
            
            # Format locations for the URL
            markers = '&markers='.join([f"color:red|label:{chr(65+i)}|{loc.replace(' ', '+')}" for i, loc in enumerate(locations)])
            
            # Build the URL for the Google Maps embed API with markers
            map_url = f"https://www.google.com/maps/embed/v1/place?key={api_key}&q={locations[0].replace(' ', '+')}&zoom=8&markers={markers}"
            
            # Create the iframe with the map
            iframe_html = f'<iframe width="100%" height="450" frameborder="0" style="border:0" src="{map_url}" allowfullscreen></iframe>'
            st.markdown(iframe_html, unsafe_allow_html=True)
        except Exception as e2:
            st.error(f"Error displaying location map: {str(e2)}")
            # Fallback to simplified map display
            st.info("Map couldn't be displayed. Here's a text representation of locations:")
            for i, loc in enumerate(locations):
                st.markdown(f"{i+1}. {loc}")

def display_mapbox_map(locations, is_route=False):
    """Display a map using Mapbox with markers or a route"""
    import pydeck as pdk
    
    if not locations or len(locations) == 0:
        st.warning("No locations to display on map")
        return
    
    # Function to convert location names to coordinates (in a real app, use geocoding API)
    def get_coordinates(location_name):
        # This is just a dummy implementation that generates random coordinates
        # In a real app, you would use a geocoding service like Mapbox Geocoding API
        # Simulate geocoding with fixed seeds for consistency
        import hashlib
        
        # Create a hash from the location name to get consistent coordinates
        location_hash = int(hashlib.md5(location_name.encode()).hexdigest(), 16)
        
        # Generate lat/lon within reasonable bounds (roughly within continental US/Europe)
        lat = 30 + (location_hash % 1000) / 1000 * 30  # Between 30 and 60 degrees N
        lon = -120 + (location_hash // 1000 % 1000) / 1000 * 140  # Between -120 and 20 degrees
        
        return {"lat": lat, "lon": lon}
    
    # Convert location names to coordinates
    location_points = [{"name": loc, **get_coordinates(loc)} for loc in locations]
    
    # Create data for the map
    map_data = [{"name": point["name"], "lat": point["lat"], "lon": point["lon"]} for point in location_points]
    
    # Define the view state
    if len(location_points) == 1:
        # For a single location, center on that location
        center_lat = location_points[0]["lat"]
        center_lon = location_points[0]["lon"]
        zoom = 9
    else:
        # For multiple locations, calculate the center
        center_lat = sum(point["lat"] for point in location_points) / len(location_points)
        center_lon = sum(point["lon"] for point in location_points) / len(location_points)
        zoom = 5
    
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=0
    )
    
    # Create layers
    layers = []
    
    # Add ScatterplotLayer for points
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position=["lon", "lat"],
        get_radius=20000,  # in meters
        get_fill_color=[255, 0, 0, 200],
        pickable=True
    )
    layers.append(scatter_layer)
    
    # Add TextLayer for labels
    text_layer = pdk.Layer(
        "TextLayer",
        data=map_data,
        get_position=["lon", "lat"],
        get_text="name",
        get_size=16,
        get_color=[0, 0, 0],
        get_angle=0,
        get_text_anchor="middle",
        get_alignment_baseline="center"
    )
    layers.append(text_layer)
    
    # Add a PathLayer for routes if is_route is True
    if is_route and len(location_points) >= 2:
        path_data = [
            {
                "path": [[point["lon"], point["lat"]] for point in location_points],
                "color": [0, 0, 255]
            }
        ]
        
        path_layer = pdk.Layer(
            "PathLayer",
            data=path_data,
            get_path="path",
            get_color="color",
            width_scale=20,
            width_min_pixels=2,
            get_width=5,
            highlight_color=[255, 255, 0],
            rounded=True,
            pickable=True
        )
        layers.append(path_layer)
    
    # Create the map
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",
        initial_view_state=view_state,
        layers=layers,
        tooltip={
            "html": "<b>{name}</b>",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }
    )
    
    # Display the map
    st.pydeck_chart(deck)

def display_simplified_map(locations, is_route=False):
    """Display a map using Mapbox or fallback to Google Maps or text-based representation"""
    if not locations or len(locations) == 0:
        st.warning("No locations to display on map")
        return
    
    st.markdown("### 🗺️ " + ("Travel Route Map" if is_route and len(locations) >= 2 else "Destinations Map"))
    
    try:
        # Try to use Mapbox first (preferred)
        display_mapbox_map(locations, is_route=is_route)
    except Exception as e:
        # If Mapbox fails, fall back to Google Maps
        if is_route and len(locations) >= 2:
            display_route_map(locations)
        else:
            display_google_map(locations)

def show_hotel_options():
    """Separate function to handle hotel selection"""
    # Hotel options tab
    st.subheader("🏨 Hotel Options")
    
    if 'hotel_options' not in st.session_state or not st.session_state.hotel_options:
        st.info("Generate an itinerary first to see hotel options")
        return
    
    # Initialize selected_hotels if it doesn't exist
    if 'selected_hotels' not in st.session_state:
        st.session_state.selected_hotels = {}
    
    # Create tabs for each destination
    hotel_dest_tabs = st.tabs(list(st.session_state.hotel_options.keys()))
    
    # For each destination tab
    for i, (dest, tab) in enumerate(zip(st.session_state.hotel_options.keys(), hotel_dest_tabs)):
        with tab:
            hotels = st.session_state.hotel_options[dest]
            
            # Show currently selected hotel for this destination if any
            if dest in st.session_state.selected_hotels:
                selected_hotel = st.session_state.selected_hotels[dest]
                st.success(f"✅ Currently selected: **{selected_hotel['name']}** - {selected_hotel['price']} per night")
            
            # Display all hotel options
            for j, hotel in enumerate(hotels):
                with st.expander(f"{hotel['name']} - {hotel['price']} per night", expanded=False):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(hotel['image'], caption=hotel['name'])
                    with col2:
                        st.markdown(f"**Rating:** {hotel['rating']}⭐")
                        st.markdown(f"**Price:** {hotel['price']} per night")
                        st.markdown(f"**Location:** {hotel['location']}")
                        st.markdown(f"**Amenities:** {', '.join(hotel['amenities'])}")
                        st.markdown(f"[View Hotel Website]({hotel['link']})")
                    
                    # Select button with a unique, consistent key
                    key = f"select_hotel_{dest}_{j}"
                    if st.button(f"Select This Hotel", key=key):
                        # Store in session state
                        st.session_state.selected_hotels[dest] = hotel
                        # Force a rerun to refresh the UI
                        st.rerun()

def show_flight_options():
    """Separate function to handle flight selection"""
    # Flight options tab
    st.subheader("✈️ Flight Options")
    
    if 'flight_options' not in st.session_state or not st.session_state.flight_options:
        st.info("Generate an itinerary first to see flight options")
        return
    
    # Initialize selected_flights if it doesn't exist
    if 'selected_flights' not in st.session_state:
        st.session_state.selected_flights = []
    
    # Show currently selected flights
    if st.session_state.selected_flights:
        st.success("✅ Currently selected flights:")
        for i, flight in enumerate(st.session_state.selected_flights):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"{i+1}. {flight['airline']} from {flight['from']} to {flight['to']} on {flight['date']}: {flight['price']}")
            with cols[1]:
                # Remove button with consistent key
                remove_key = f"remove_flight_{i}"
                if st.button("Remove", key=remove_key):
                    st.session_state.selected_flights.remove(flight)
                    st.rerun()
    
    # Group flights by route
    routes = {}
    for flight in st.session_state.flight_options:
        route = f"{flight['from']} → {flight['to']}"
        if route not in routes:
            routes[route] = []
        routes[route].append(flight)
    
    # Create tabs for each route
    flight_route_tabs = st.tabs(list(routes.keys()))
    
    # For each route tab
    for i, (route, tab) in enumerate(zip(routes.keys(), flight_route_tabs)):
        with tab:
            flights = routes[route]
            
            # Display all flight options for this route
            for j, flight in enumerate(flights):
                with st.expander(f"{flight['airline']} - {flight['date']} - {flight['price']}", expanded=False):
                    cols = st.columns([1, 1, 1])
                    with cols[0]:
                        st.markdown(f"**Airline:** {flight['airline']}")
                        st.markdown(f"**Flight:** {flight['flight_number']}")
                    with cols[1]:
                        st.markdown(f"**Departure:** {flight['departure_time']}")
                        st.markdown(f"**Arrival:** {flight['arrival_time']}")
                    with cols[2]:
                        st.markdown(f"**Duration:** {flight['duration']}")
                        st.markdown(f"**Price:** {flight['price']}")
                    
                    st.markdown(f"**Class:** {flight['class']}")
                    if 'layovers' in flight and flight['layovers']:
                        st.markdown(f"**Layovers:** {', '.join(flight['layovers'])}")
                    
                    # Check if this flight is already selected
                    is_selected = any(f['flight_number'] == flight['flight_number'] and 
                                     f['from'] == flight['from'] and 
                                     f['to'] == flight['to'] and
                                     f['date'] == flight['date'] 
                                     for f in st.session_state.selected_flights)
                    
                    # Select button with consistent key
                    key = f"select_flight_{route.replace(' ', '_')}_{j}"
                    
                    if is_selected:
                        st.success("✅ This flight is selected")
                    else:
                        if st.button(f"Select This Flight", key=key):
                            st.session_state.selected_flights.append(flight)
                            st.rerun()

def show_itinerary_ui():
    st.markdown("### 🌎 Travel Itinerary Planner")

    # Initialize session state for itinerary
    if 'itinerary_data' not in st.session_state:
        st.session_state.itinerary_data = None
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    if 'shared_itineraries' not in st.session_state:
        st.session_state.shared_itineraries = {}
    if 'destinations' not in st.session_state:
        st.session_state.destinations = []
    if 'place_reviews' not in st.session_state:
        st.session_state.place_reviews = {}
    if 'current_itinerary_destinations' not in st.session_state:
        st.session_state.current_itinerary_destinations = []
    if 'hotel_options' not in st.session_state:
        st.session_state.hotel_options = {}
    if 'flight_options' not in st.session_state:
        st.session_state.flight_options = {}
    if 'selected_hotels' not in st.session_state:
        st.session_state.selected_hotels = {}
    if 'selected_flights' not in st.session_state:
        st.session_state.selected_flights = []
    if 'plan_confirmed' not in st.session_state:
        st.session_state.plan_confirmed = False
    if 'trip_type' not in st.session_state:
        st.session_state.trip_type = "Multi-City"
    if 'num_destinations' not in st.session_state:
        st.session_state.num_destinations = 2
    if 'adults' not in st.session_state:
        st.session_state.adults = 2
    if 'children' not in st.session_state:
        st.session_state.children = 0
    if 'temperature_unit' not in st.session_state:
        st.session_state.temperature_unit = "Celsius"
    
    # Temperature unit toggle function
    def toggle_temperature_unit():
        if st.session_state.temperature_unit == "Celsius":
            st.session_state.temperature_unit = "Fahrenheit"
        else:
            st.session_state.temperature_unit = "Celsius"
        
        # Convert existing weather data
        if st.session_state.weather_data:
            st.session_state.weather_data = convert_weather_units(
                st.session_state.weather_data, 
                st.session_state.temperature_unit
            )
    
    # Temperature unit selector in sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        temp_col1, temp_col2, temp_col3 = st.columns([1, 1, 1])
        with temp_col1:
            st.write("Temperature:")
        with temp_col2:
            celsius_active = st.session_state.temperature_unit == "Celsius"
            if st.button("°C", type="primary" if celsius_active else "secondary", key="celsius_btn"):
                if not celsius_active:
                    st.session_state.temperature_unit = "Celsius"
                    toggle_temperature_unit()
                    st.rerun()
        with temp_col3:
            fahrenheit_active = st.session_state.temperature_unit == "Fahrenheit"
            if st.button("°F", type="primary" if fahrenheit_active else "secondary", key="fahrenheit_btn"):
                if not fahrenheit_active:
                    st.session_state.temperature_unit = "Fahrenheit"
                    toggle_temperature_unit()
                    st.rerun()

    # Rest of your itinerary UI code would go here

    # Callback functions for auto-refresh - without explicit rerun calls
    def on_trip_type_change():
        st.session_state.trip_type = st.session_state.trip_type_widget
    
    def on_num_destinations_change():
        st.session_state.num_destinations = st.session_state.num_destinations_widget
    
    def on_adults_change():
        st.session_state.adults = st.session_state.adults_widget
    
    def on_children_change():
        st.session_state.children = st.session_state.children_widget
    
    # Tabs for different planning aspects
    plan_tabs = st.tabs(["Destinations & Activities", "Hotels", "Flights", "Complete Itinerary"])
    
    with plan_tabs[0]:
        # Main Destinations and Activities Planning
        st.subheader("🗺️ Plan Your Journey")
        
        # Create two columns: one for inputs, one for the map
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Select trip type
            trip_types = ["One-way", "Round Trip", "Multi-City"]
            trip_type = st.selectbox(
                "Trip Type",
                options=trip_types,
                index=trip_types.index(st.session_state.trip_type),
                key="trip_type_widget",
                on_change=on_trip_type_change
            )
            
            # For multi-city trips, allow selecting number of destinations
            if st.session_state.trip_type == "Multi-City":
                num_destinations = st.number_input(
                    "Number of Destinations",
                    min_value=2,
                    max_value=5,
                    value=st.session_state.num_destinations,
                    key="num_destinations_widget",
                    on_change=on_num_destinations_change
                )
                
                # Initialize children_ages in session state if not present
                if 'children_ages' not in st.session_state:
                    st.session_state.children_ages = []
            
            # Date selection
            departure_date = st.date_input(
                "Departure Date",
                value=datetime.now() + timedelta(days=30),
                min_value=datetime.now()
            )
            
            # Show return date field if it's a round trip
            if st.session_state.trip_type == "Round Trip":
                return_date = st.date_input(
                    "Return Date",
                    value=datetime.now() + timedelta(days=37),
                    min_value=departure_date
                )
            else:
                return_date = departure_date + timedelta(days=7)
            
            # Passenger information
            col_a, col_b = st.columns(2)
            with col_a:
                adults = st.number_input(
                    "Adults",
                    min_value=1,
                    max_value=9,
                    value=st.session_state.adults,
                    key="adults_widget",
                    on_change=on_adults_change
                )
            with col_b:
                children = st.number_input(
                    "Children",
                    min_value=0,
                    max_value=6,
                    value=st.session_state.children,
                    key="children_widget",
                    on_change=on_children_change
                )
                
            # If there are children, ask for their ages
            if st.session_state.children > 0:
                # Ensure we have the right number of age inputs in session state
                if 'children_ages' not in st.session_state:
                    st.session_state.children_ages = [0] * st.session_state.children
                elif len(st.session_state.children_ages) != st.session_state.children:
                    if len(st.session_state.children_ages) < st.session_state.children:
                        st.session_state.children_ages.extend([0] * (st.session_state.children - len(st.session_state.children_ages)))
                    else:
                        st.session_state.children_ages = st.session_state.children_ages[:st.session_state.children]
                
                st.write("Children's Ages:")
                # Create multiple columns for child age inputs
                cols = st.columns(min(3, st.session_state.children))
                for i in range(st.session_state.children):
                    col_index = i % len(cols)
                    with cols[col_index]:
                        age = st.number_input(
                            f"Child {i+1}",
                            min_value=0,
                            max_value=17,
                            value=st.session_state.children_ages[i],
                            key=f"child_age_{i}"
                        )
                        st.session_state.children_ages[i] = age
            
            # Budget selection
            budget_options = ["Budget", "Mid-range", "Luxury"]
            budget_level = st.selectbox("Budget Level", budget_options, index=1)
            
            # Show budget total field based on budget level
            budget_total = None
            if budget_level == "Budget":
                budget_total = st.number_input("Total Budget (USD)", min_value=500, value=1500)
            elif budget_level == "Mid-range":
                budget_total = st.number_input("Total Budget (USD)", min_value=1500, value=3000)
            else:
                budget_total = st.number_input("Total Budget (USD)", min_value=3000, value=6000)
            
            # Destination inputs based on trip type and number of destinations
            destinations = []
            
            if st.session_state.trip_type == "One-way" or st.session_state.trip_type == "Round Trip":
                origin = st.text_input("From (Origin)", "New York", help="Enter your departure city")
                destination = st.text_input("To (Destination)", "Los Angeles", help="Enter your destination city")
                destinations = [origin, destination]
                
                if st.session_state.trip_type == "Round Trip":
                    destinations.append(origin)  # Add origin again for return trip
            else:
                # Multi-city trip
                destinations = []
                for i in range(st.session_state.num_destinations):
                    if i == 0:
                        dest = st.text_input(f"Origin (City 1)", value="New York", help="Enter your first departure city")
                    else:
                        dest = st.text_input(f"Destination {i} {'' if i < st.session_state.num_destinations-1 else '(Final)'}", 
                                           value=f"City {i+1}", 
                                           help=f"{'Enter your destination city' if i < st.session_state.num_destinations-1 else 'Enter your final destination'}")
                    destinations.append(dest)
            
            # Travel interests
            interests = st.multiselect(
                "Travel Interests",
                options=["Beaches", "Museums", "Food & Dining", "Historical Sites", 
                         "Nature & Parks", "Shopping", "Adventure", "Nightlife", 
                         "Family-friendly", "Art & Culture"],
                default=["Food & Dining", "Historical Sites"]
            )
            
            # Additional notes
            notes = st.text_area("Additional Notes or Requirements", 
                                placeholder="Any specific attractions you want to visit or dietary requirements?")
            
            # Generate Itinerary button
            if st.button("Generate Travel Plan", type="primary"):
                # Show loading state
                with st.spinner("Creating your perfect itinerary..."):
                    # Store current destinations for weather lookup and maps
                    st.session_state.destinations = destinations
                    st.session_state.current_itinerary_destinations = destinations.copy()
                    
                    # Store children's ages for booking info
                    if st.session_state.children > 0:
                        st.session_state.current_children_ages = st.session_state.children_ages.copy()
                    
                    # Query Gemini for itinerary
                    prompt = f"""
                    Create a detailed travel itinerary for a {st.session_state.trip_type.lower()} to {', '.join(destinations)}. 
                    Trip details:
                    - Budget level: {budget_level}
                    - Total budget: ${budget_total}
                    - Departure date: {departure_date.strftime('%B %d, %Y')}
                    - {"Return date: " + return_date.strftime('%B %d, %Y') if st.session_state.trip_type == "Round Trip" else ""}
                    - Travel party: {adults} {'adult' if adults == 1 else 'adults'} and {children} {'child' if children == 1 else 'children'}
                    {"- Children's ages: " + ', '.join([str(age) for age in st.session_state.children_ages]) if st.session_state.children > 0 else ""}
                    - Interests: {', '.join(interests)}
                    - Additional notes: {notes}
                    
                    Please include:
                    1. A day-by-day breakdown with activities, attractions, and dining suggestions
                    2. Detailed recommendations for each attraction with at least 1-2 sentences about each place
                    3. Estimated costs for attractions and meals
                    4. Local travel tips and cultural insights
                    5. Typical weather for the time of visit
                    
                    Format the output as a structured itinerary with days and locations clearly marked.
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # Parse Gemini's response - this is a simplified example
                    itinerary_text = response.text
                    
                    # Populate itinerary data
                    st.session_state.itinerary_data = {
                        "trip_type": st.session_state.trip_type,
                        "destinations": destinations,
                        "departure_date": departure_date.strftime('%Y-%m-%d'),
                        "return_date": return_date.strftime('%Y-%m-%d') if st.session_state.trip_type == "Round Trip" else None,
                        "content": itinerary_text,
                        "adults": adults,
                        "children": children,
                        "children_ages": st.session_state.children_ages if st.session_state.children > 0 else [],
                        "budget_level": budget_level,
                        "budget_total": budget_total,
                        "interests": interests,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Generate weather data for each destination
                    weather_data = {}
                    for dest in destinations:
                        weather_data[dest] = fetch_weather_data(dest)
                    
                    st.session_state.weather_data = weather_data
                    
                    # Generate hotel options for each destination
                    hotel_options = {}
                    for dest in destinations:
                        hotel_options[dest] = generate_hotel_options(dest, budget_level, adults + children)
                    
                    st.session_state.hotel_options = hotel_options
                    
                    # Generate flight options based on the itinerary
                    travel_sequence = destinations.copy()
                    
                    st.session_state.flight_options = generate_flight_options(
                        travel_sequence, 
                        departure_date, 
                        return_date, 
                        st.session_state.trip_type, 
                        adults, 
                        children,
                        budget_total
                    )
                    
                    # Generate some reviews for places in the itinerary
                    place_reviews = {}
                    # Extract popular attractions from the itinerary using regex or other methods
                    # For simplicity, here we're just generating reviews for major attractions in destinations
                    for dest in destinations:
                        attractions = [f"{dest} Museum", f"{dest} Gardens", f"{dest} Tower", f"{dest} Market"]
                        for attraction in attractions:
                            place_reviews[attraction] = generate_dummy_reviews(attraction)
                    
                    st.session_state.place_reviews = place_reviews
                    
                    # Redirect to the first day tab
                    st.rerun()
        
        with col2:
            # Map visualization
            if 'destinations' in st.session_state and st.session_state.destinations:
                display_simplified_map(st.session_state.destinations, is_route=True)
    
    with plan_tabs[1]:
        show_hotel_options()
    
    with plan_tabs[2]:
        show_flight_options()
    
    with plan_tabs[3]:
        # Complete Itinerary tab
        st.subheader("📝 Your Complete Travel Plan")
        
        if 'itinerary_data' not in st.session_state or not st.session_state.itinerary_data:
            st.info("Generate an itinerary first to see your complete travel plan")
        else:
            # Show a summary of the trip
            trip_type = st.session_state.itinerary_data.get("trip_type", "")
            destinations = st.session_state.itinerary_data.get("destinations", [])
            
            # Create summary box
            summary_box = st.container(border=True)
            with summary_box:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### {trip_type} to {', '.join(destinations)}")
                    st.markdown(f"**Departure**: {datetime.strptime(st.session_state.itinerary_data.get('departure_date', ''), '%Y-%m-%d').strftime('%B %d, %Y')}")
                    if trip_type == "Round Trip" and st.session_state.itinerary_data.get('return_date'):
                        st.markdown(f"**Return**: {datetime.strptime(st.session_state.itinerary_data.get('return_date', ''), '%Y-%m-%d').strftime('%B %d, %Y')}")
                    
                    # Show passenger info
                    adults = st.session_state.itinerary_data.get("adults", 0)
                    children = st.session_state.itinerary_data.get("children", 0)
                    st.markdown(f"**Travelers**: {adults} {'adult' if adults == 1 else 'adults'} and {children} {'child' if children == 1 else 'children'}")
                    
                    # Show children's ages if any
                    if children > 0 and "children_ages" in st.session_state.itinerary_data:
                        children_ages = st.session_state.itinerary_data.get("children_ages", [])
                        st.markdown(f"**Children's ages**: {', '.join([str(age) for age in children_ages])}")
                
                with col2:
                    # Show summary of selected options
                    if 'selected_hotels' in st.session_state and st.session_state.selected_hotels:
                        st.markdown(f"**Selected Hotels**: {len(st.session_state.selected_hotels)} hotels")
                    
                    if 'selected_flights' in st.session_state and st.session_state.selected_flights:
                        st.markdown(f"**Selected Flights**: {len(st.session_state.selected_flights)} flights")
                    
                    # Show total estimated cost
                    # Calculate cost based on selected hotels and flights or use budget
                    if ('selected_hotels' in st.session_state and st.session_state.selected_hotels) or \
                       ('selected_flights' in st.session_state and st.session_state.selected_flights):
                        
                        # Calculate hotel costs
                        hotel_cost = 0
                        if 'selected_hotels' in st.session_state:
                            for hotel in st.session_state.selected_hotels.values():
                                price_str = hotel.get('price', '').replace('$', '').replace(',', '').split(' ')[0]
                                try:
                                    price = float(price_str)
                                    # Assume 2 nights per destination
                                    hotel_cost += price * 2
                                except:
                                    pass
                        
                        # Calculate flight costs
                        flight_cost = 0
                        if 'selected_flights' in st.session_state:
                            for flight in st.session_state.selected_flights:
                                price_str = flight.get('price', '').replace('$', '').replace(',', '')
                                try:
                                    flight_cost += float(price_str)
                                except:
                                    pass
                        
                        # Show total
                        total_cost = hotel_cost + flight_cost
                        st.markdown(f"**Estimated Cost**: ${total_cost:.2f}")
                    elif "budget_total" in st.session_state.itinerary_data:
                        st.markdown(f"**Budget**: ${st.session_state.itinerary_data.get('budget_total')}")
                    
                    # Show a "Book Now" button that links to a travel site with the itinerary details
                    if st.button("Complete Booking", type="primary"):
                        # Generate a booking link that combines all selected hotels and flights
                        # In a real app, this would connect to a booking API
                        booking_sites = [
                            "https://www.expedia.com",
                            "https://www.booking.com",
                            "https://www.kayak.com",
                            "https://www.tripadvisor.com"
                        ]
                        
                        booking_site = random.choice(booking_sites)
                        
                        # Show a success message with booking information
                        st.success(f"Your booking request has been submitted! You'll receive a confirmation email shortly.")
                        
                        # Display a "View Booking" link that would go to a real booking site
                        st.markdown(f"[View your complete booking on {booking_site.split('//')[1]}]({booking_site})")
            
            # Display weather information
            if st.session_state.weather_data:
                st.markdown("### 🌦️ Weather Information")
                weather_box = st.container(border=True)
                with weather_box:
                    # Create columns for each destination's weather
                    cols = st.columns(min(len(st.session_state.weather_data), 3))
                    for i, (dest, weather) in enumerate(st.session_state.weather_data.items()):
                        col_index = i % len(cols)
                        with cols[col_index]:
                            st.info(f"Weather in {dest}: {weather}")
                            unit_to_show = "°F" if "°C" in weather else "°C"
                            if st.button(f"Show {unit_to_show}", key=f"toggle_temp_main_{dest}"):
                                toggle_temperature_unit()
                                st.rerun()
            
            # Create tabs for each day of the itinerary
            num_days = len(st.session_state.destinations) * 3  # Approximate 3 days per destination
            
            day_tabs = st.tabs([f"Day {i+1}" for i in range(num_days)])
            
            # Split the content by days
            content = st.session_state.itinerary_data.get('content', '')
            days = re.split(r'Day \d+:|DAY \d+:', content)
            if days and not days[0].strip():  # Remove empty first element if it exists
                days = days[1:]
            
            # Ensure we have content for each tab
            while len(days) < num_days:
                days.append("Itinerary details not available for this day.")
            
            # For each day tab
            for i, (day_content, tab) in enumerate(zip(days, day_tabs)):
                with tab:
                    # Display the day's itinerary
                    st.markdown(f"### Day {i+1}: {datetime.strptime(st.session_state.itinerary_data.get('departure_date'), '%Y-%m-%d') + timedelta(days=i):%B %d, %Y}")
                    
                    # Display weather info if available
                    if st.session_state.weather_data and st.session_state.current_itinerary_destinations:
                        dest_index = min(i // 3, len(st.session_state.current_itinerary_destinations) - 1) if st.session_state.current_itinerary_destinations else 0
                        if st.session_state.current_itinerary_destinations and dest_index < len(st.session_state.current_itinerary_destinations):
                            dest = st.session_state.current_itinerary_destinations[dest_index]
                            if dest in st.session_state.weather_data:
                                weather = st.session_state.weather_data[dest]
                                w_col1, w_col2 = st.columns([4, 1])
                                with w_col1:
                                    st.info(f"🌦️ Weather in {dest}: {weather}")
                                with w_col2:
                                    unit_to_show = "°F" if "°C" in weather else "°C"
                                    if st.button(f"Show {unit_to_show}", key=f"toggle_temp_{i}"):
                                        toggle_temperature_unit()
                                        st.rerun()
                    
                    # Display the day's content in a box
                    content_box = st.container(border=True)
                    with content_box:
                        st.markdown(day_content)
                    
                    # Extract locations from day content using regex
                    locations = extract_locations(day_content)
                    
                    # If we have locations, show a map
                    if locations:
                        st.markdown("### 📍 Day's Locations")
                        display_simplified_map(locations)
                        
                        # Add direct booking links for attractions
                        st.markdown("### 🎫 Book Attractions")
                        booking_cols = st.columns(min(len(locations), 3))
                        for j, loc in enumerate(locations):
                            with booking_cols[j % len(booking_cols)]:
                                # Generate dummy booking link
                                booking_sites = [
                                    {"name": "Viator", "url": f"https://www.viator.com/search/{loc.replace(' ', '%20')}"},
                                    {"name": "GetYourGuide", "url": f"https://www.getyourguide.com/s/?q={loc.replace(' ', '%20')}"},
                                    {"name": "TripAdvisor", "url": f"https://www.tripadvisor.com/Search?q={loc.replace(' ', '%20')}"}
                                ]
                                site = random.choice(booking_sites)
                                st.markdown(f"[Book {loc} tickets on {site['name']}]({site['url']})")
                    
                    # Show reviews for places mentioned in the day's content
                    reviews_to_show = []
                    for place, reviews in st.session_state.place_reviews.items():
                        if place.lower() in day_content.lower():
                            reviews_to_show.append((place, reviews))
                    
                    if reviews_to_show:
                        st.markdown("### 💬 Traveler Reviews")
                        for place, reviews in reviews_to_show:
                            with st.expander(f"{place} - {sum(r['rating'] for r in reviews) / len(reviews):.1f}⭐ ({len(reviews)} reviews)", expanded=False):
                                for review in reviews:
                                    st.markdown(f"""
                                    **{review['rating']}⭐ by {review['name']}** - {review['date']}  
                                    "{review['comment']}"
                                    """)
                                    st.markdown("---")
            
            # Actions for the completed itinerary
            st.markdown("### 🔄 Actions")
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("Download Itinerary as PDF"):
                    st.info("Generating PDF... (This feature would generate a PDF in a real implementation)")
                    # Show a download link (simulated)
                    st.markdown(f"[Download Itinerary_{'_'.join(st.session_state.destinations)}.pdf](#)")
            
            with action_col2:
                if st.button("Share with Friends"):
                    # Create a unique sharing ID
                    share_id = str(uuid.uuid4())
                    
                    # Store itinerary in shared_itineraries
                    if 'shared_itineraries' not in st.session_state:
                        st.session_state.shared_itineraries = {}
                        
                    st.session_state.shared_itineraries[share_id] = {
                        "itinerary": st.session_state.itinerary_data,
                        "weather": st.session_state.weather_data,
                        "hotels": st.session_state.selected_hotels if 'selected_hotels' in st.session_state else {},
                        "flights": st.session_state.selected_flights if 'selected_flights' in st.session_state else [],
                        "shared_by": st.session_state.user["username"],
                        "shared_at": datetime.now().isoformat()
                    }
                    
                    st.success(f"share this link with your friends: https://sigmabot.streamlit.app/shared/{share_id}")
                    
                    # Display sharing options
                    share_cols = st.columns(4)
                    with share_cols[0]:
                        st.markdown("[![WhatsApp](https://img.icons8.com/color/48/000000/whatsapp.png)](https://wa.me/?text=check%20out%20my%20travel%20plan%20on%20sigmabot:%20https://sigmabot.streamlit.app/shared/{share_id})")
                    with share_cols[1]:
                        st.markdown("[![Email](https://img.icons8.com/color/48/000000/gmail-new.png)](mailto:?subject=my%20travel%20plan%20on%20sigmabot&body=check%20out%20my%20travel%20plan:%20https://sigmabot.streamlit.app/shared/{share_id})")
                    with share_cols[2]:
                        st.markdown("[![Facebook](https://img.icons8.com/color/48/000000/facebook-new.png)](https://www.facebook.com/sharer/sharer.php?u=https://sigmabot.streamlit.app/shared/{share_id})")
                    with share_cols[3]:
                        st.markdown("[![Twitter](https://img.icons8.com/color/48/000000/twitter.png)](https://twitter.com/intent/tweet?text=check%20out%20my%20travel%20plan%20on%20sigmabot!&url=https://sigmabot.streamlit.app/shared/{share_id})")
            
            with action_col3:
                if st.button("Regenerate Itinerary"):
                    st.session_state.itinerary_data = None
                    st.session_state.weather_data = None
                    st.session_state.hotel_options = {}
                    st.session_state.flight_options = []
                    st.session_state.selected_hotels = {}
                    st.session_state.selected_flights = []
                    st.rerun()

def extract_locations(day_content):
    """Extract location names from itinerary text"""
    # Extract text between quotes as potential locations
    locations = re.findall(r'"([^"]*)"', day_content)
    
    # If no locations found, look for text in italics
    if not locations:
        locations = re.findall(r'\*([^*]*)\*', day_content)
    
    # If still no locations, try some heuristics
    if not locations:
        # Look for capitalized phrases (potentially locations)
        locations = re.findall(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', day_content)
    
    # Remove duplicates and return
    return list(set(locations))

def convert_weather_units(weather_data, unit):
    """Convert weather data between Celsius and Fahrenheit"""
    converted_weather = {}
    
    for location, weather in weather_data.items():
        if '°C' in weather and unit == "Fahrenheit":
            # Extract the temperature value
            temp_parts = weather.split(', ')
            conditions = temp_parts[0]
            temp_str = temp_parts[-1]
            temp_value = float(temp_str.replace('°C', ''))
            # Convert Celsius to Fahrenheit: (C × 9/5) + 32
            fahrenheit_temp = (temp_value * 9/5) + 32
            # Format with 1 decimal place
            converted_weather[location] = f"{conditions}, {fahrenheit_temp:.1f}°F"
        elif '°F' in weather and unit == "Celsius":
            # Extract the temperature value
            temp_parts = weather.split(', ')
            conditions = temp_parts[0]
            temp_str = temp_parts[-1]
            temp_value = float(temp_str.replace('°F', ''))
            # Convert Fahrenheit to Celsius: (F - 32) × 5/9
            celsius_temp = (temp_value - 32) * 5/9
            # Format with 1 decimal place
            converted_weather[location] = f"{conditions}, {celsius_temp:.1f}°C"
        else:
            # Keep as is if no conversion needed or if format is not recognized
            converted_weather[location] = weather
    
    return converted_weather

def fetch_weather_data(location):
    """Fetch weather data for a location using OpenWeatherMap API (with fallback to dummy data)"""
    try:
        # Attempt to use a real weather API
        api_key = os.getenv("OPENWEATHER_API_KEY", "")
        
        if not api_key:
            # Fallback to dummy data if API key not available
            return generate_dummy_weather()
            
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric"  # for temperature in Celsius
        }
        
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            condition = data["weather"][0]["main"]
            description = data["weather"][0]["description"]
            
            # Format based on user's preferred temperature unit
            if 'temperature_unit' in st.session_state and st.session_state.temperature_unit == "Fahrenheit":
                # Convert Celsius to Fahrenheit
                temp_f = (temp * 9/5) + 32
                return f"{condition} ({description}), {temp_f:.1f}°F"
            else:
                return f"{condition} ({description}), {temp:.1f}°C"
        else:
            # Fallback to dummy data if API call fails
            return generate_dummy_weather()
    except Exception as e:
        # Fallback to dummy data if any error occurs
        return generate_dummy_weather()

def generate_dummy_weather():
    """Generate dummy weather data for fallback"""
    conditions = ["Sunny", "Partly Cloudy", "Rainy", "Clear", "Overcast", "Thunderstorms", "Snowy", "Foggy"]
    condition = random.choice(conditions)
    
    # Generate temperature based on user's preferred unit
    if 'temperature_unit' in st.session_state and st.session_state.temperature_unit == "Fahrenheit":
        temp = random.randint(59, 86)  # 15-30°C in Fahrenheit
        return f"{condition}, {temp}°F"
    else:
        temp = random.randint(15, 30)
        return f"{condition}, {temp}°C"

def generate_dummy_reviews(place):
    """Generate dummy reviews for a place"""
    # List of fictional reviewers
    reviewers = ["Alex J.", "Maya S.", "Carlos R.", "Sophie T.", "Raj P.", "Emma L.", "Takashi M."]
    
    # List of positive comments
    positive_comments = [
        "Absolutely loved this place! Highlight of my trip.",
        "The atmosphere was incredible, definitely recommend.",
        "Such a beautiful spot, worth every penny.",
        "Amazing experience, the photos don't do it justice.",
        "Friendly staff and wonderful experience overall."
    ]
    
    # List of mixed comments
    mixed_comments = [
        "Nice place but a bit crowded. Go early to avoid lines.",
        "Beautiful views but expensive. Budget accordingly.",
        "Interesting experience, though slightly overrated.",
        "Worth visiting, but be prepared for tourist prices.",
        "Good experience overall, but the facilities could be better."
    ]
    
    # Generate 3-5 random reviews
    num_reviews = random.randint(3, 5)
    reviews = []
    
    for _ in range(num_reviews):
        # Generate random rating (3-5 stars)
        rating = random.randint(3, 5)
        
        # Pick appropriate comment based on rating
        if rating >= 4:
            comment = random.choice(positive_comments)
        else:
            comment = random.choice(mixed_comments)
        
        # Generate random date within last 3 months
        days_ago = random.randint(1, 90)
        review_date = (datetime.now() - timedelta(days=days_ago)).strftime("%b %d, %Y")
        
        reviews.append({
            "name": random.choice(reviewers),
            "rating": rating,
            "comment": comment,
            "date": review_date
        })
    
    return reviews

def generate_hotel_options(destination, budget_level, guests):
    """Generate hotel options for a destination with valid booking links"""
    # Number of hotels to generate
    num_hotels = random.randint(3, 6)
    
    # Hotel name prefixes and suffixes
    prefixes = ["Grand", "Royal", "Luxury", "City", "Park", "Central", "Bay", "Ocean", "Mountain", "Palace"]
    suffixes = ["Hotel", "Resort", "Suites", "Inn", "Lodge", "Residence", "Plaza", "Towers", "Retreat"]
    
    # Budget-based price ranges
    if budget_level == "Budget":
        price_range = ["$70", "$85", "$100", "$120", "$150"]
    elif budget_level == "Mid-range":
        price_range = ["$150", "$180", "$210", "$250", "$300"]
    else:  # Luxury
        price_range = ["$300", "$400", "$500", "$600", "$800"]
    
    # Rating ranges
    if budget_level == "Budget":
        rating_range = [3, 3.5, 4]
    elif budget_level == "Mid-range":
        rating_range = [3.5, 4, 4.5]
    else:  # Luxury
        rating_range = [4, 4.5, 5]
    
    # Common amenities
    basic_amenities = ["Wi-Fi", "Air conditioning", "TV", "Private bathroom"]
    mid_amenities = ["Swimming pool", "Gym", "Restaurant", "Bar", "Room service"]
    luxury_amenities = ["Spa", "Concierge", "Valet parking", "Business center", "Rooftop terrace"]
    
    # Generate hotels
    hotels = []
    for _ in range(num_hotels):
        # Generate a random hotel name
        hotel_name = f"{random.choice(prefixes)} {destination} {random.choice(suffixes)}"
        
        # Select a random price
        price = random.choice(price_range)
        
        # Select a rating
        rating = random.choice(rating_range)
        
        # Select amenities based on budget
        amenities = basic_amenities.copy()
        if budget_level in ["Mid-range", "Luxury"]:
            amenities.extend(random.sample(mid_amenities, k=random.randint(2, len(mid_amenities))))
        if budget_level == "Luxury":
            amenities.extend(random.sample(luxury_amenities, k=random.randint(2, len(luxury_amenities))))
        
        # Generate a random location in the destination
        locations = [
            f"Downtown {destination}",
            f"{destination} City Center",
            f"Historic District, {destination}",
            f"{random.choice(['North', 'South', 'East', 'West'])} {destination}",
            f"{destination} {random.choice(['Waterfront', 'Beach', 'Harbor', 'Hills', 'Gardens'])}"
        ]
        location = random.choice(locations)
        
        # Generate a dummy image URL (a real implementation would use actual hotel images)
        image = f"https://source.unsplash.com/random/300x200/?hotel,{destination.lower().replace(' ', '')}"
        
        # Generate valid booking links with proper URL structure for actual hotels
        booking_site = random.choice([
            {
                "name": "Booking.com",
                "url": "https://www.booking.com/searchresults.html",
                "params": f"?ss={destination.replace(' ', '+')}&checkin_year={datetime.now().year}&checkin_month={datetime.now().month}&checkout_year={datetime.now().year}&checkout_month={datetime.now().month + 1 if datetime.now().month < 12 else 1}&group_adults={guests}&no_rooms=1"
            },
            {
                "name": "Hotels.com",
                "url": "https://www.hotels.com/search.do",
                "params": f"?destination-id={destination.replace(' ', '%20')}&q-check-in={datetime.now().strftime('%Y-%m-%d')}&q-check-out={(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}&q-rooms=1&q-room-0-adults={guests}&q-room-0-children=0"
            },
            {
                "name": "Expedia",
                "url": "https://www.expedia.com/Hotel-Search",
                "params": f"?destination={destination.replace(' ', '%20')}&startDate={(datetime.now()).strftime('%Y-%m-%d')}&endDate={(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}&adults={guests}"
            }
        ])
        
        link = f"{booking_site['url']}{booking_site['params']}"
        
        hotels.append({
            "name": hotel_name,
            "price": price,
            "rating": rating,
            "location": location,
            "amenities": amenities,
            "image": image,
            "link": link
        })
    
    return hotels

def generate_flight_options(travel_sequence, departure_date, return_date, trip_type, adults, children, budget_total=None):
    """Generate flight options based on the travel sequence with valid booking links"""
    if not travel_sequence or len(travel_sequence) < 2:
        return []
    
    # Airlines
    airlines = ["Delta Air Lines", "United Airlines", "American Airlines", "British Airways", 
                "Lufthansa", "Emirates", "Qatar Airways", "Singapore Airlines", "Air France"]
    
    # Budget airlines to prioritize if budget_total is specified
    budget_airlines = ["Frontier", "Spirit", "Ryanair", "EasyJet", "Southwest", 
                      "JetBlue", "WOW air", "AirAsia", "Wizz Air", "Volaris"]
    
    # Airline codes for URL construction
    airline_codes = {
        "Delta Air Lines": "DL",
        "United Airlines": "UA",
        "American Airlines": "AA",
        "British Airways": "BA",
        "Lufthansa": "LH",
        "Emirates": "EK",
        "Qatar Airways": "QR",
        "Singapore Airlines": "SQ",
        "Air France": "AF",
        "Frontier": "F9",
        "Spirit": "NK",
        "Ryanair": "FR",
        "EasyJet": "U2",
        "Southwest": "WN",
        "JetBlue": "B6",
        "WOW air": "WW",
        "AirAsia": "AK",
        "Wizz Air": "W6",
        "Volaris": "Y4"
    }
    
    # Flight classes
    if budget_total:
        # Prioritize economy and budget airlines for budget travelers
        classes = ["Economy", "Premium Economy"]
        class_weights = [0.9, 0.1]
        # Add budget airlines to the main list
        airlines = budget_airlines + airlines
    else:
        classes = ["Economy", "Premium Economy", "Business", "First"]
        class_weights = [0.7, 0.2, 0.08, 0.02]  # Probability weights
    
    flights = []
    
    # Generate flights based on travel sequence
    for i in range(len(travel_sequence) - 1):
        from_city = travel_sequence[i]
        to_city = travel_sequence[i+1]
        
        # Determine date for this flight leg
        if i == 0:
            # First leg uses departure date
            flight_date = departure_date
        elif i == len(travel_sequence) - 2 and trip_type == "Round Trip":
            # Last leg of round trip uses return date
            flight_date = return_date
        else:
            # Middle legs use estimated dates based on typical stay
            days_offset = i * 3  # Assume 3 days per destination
            flight_date = departure_date + timedelta(days=days_offset)
        
        # Number of flight options for this leg
        num_options = random.randint(2, 4)
        
        for _ in range(num_options):
            # Select random airline - prioritize budget airlines for budget travelers
            if budget_total:
                # 80% chance to select a budget airline if budget is specified
                if random.random() < 0.8:
                    airline = random.choice(budget_airlines)
                else:
                    airline = random.choice(airlines)
            else:
                airline = random.choice(airlines)
            
            # Get airline code
            airline_code = airline_codes.get(airline, airline[:2].upper())
            
            # Generate flight number
            flight_number = f"{airline_code}{random.randint(100, 9999)}"
            
            # Generate departure and arrival times
            base_hour = random.randint(6, 22)
            departure_time = f"{base_hour:02d}:{random.choice(['00', '15', '30', '45'])}"
            
            # Flight duration depends on the cities (dummy logic)
            duration_hours = random.randint(1, 12)
            duration_minutes = random.choice([0, 15, 30, 45])
            duration = f"{duration_hours}h {duration_minutes}m"
            
            # Calculate arrival time
            arrival_hour = (base_hour + duration_hours) % 24
            arrival_minute = (int(departure_time.split(':')[1]) + duration_minutes) % 60
            arrival_time = f"{arrival_hour:02d}:{arrival_minute:02d}"
            
            # Determine if there are layovers
            # Budget flights more likely to have layovers
            has_layover_chance = 0.5 if budget_total else 0.3
            has_layover = random.random() < has_layover_chance
            layovers = []
            
            if has_layover:
                num_layovers = random.randint(1, 2)
                possible_layovers = ["Chicago", "Atlanta", "Dallas", "Frankfurt", "Dubai", 
                                    "London", "Paris", "Tokyo", "Singapore", "Amsterdam"]
                layovers = random.sample(possible_layovers, k=num_layovers)
            
            # Select flight class using weighted probability
            flight_class = random.choices(classes, weights=class_weights)[0]
            
            # Generate price based on class and passenger count
            base_price = 0
            if flight_class == "Economy":
                # Budget airlines offer cheaper economy prices
                if airline in budget_airlines:
                    base_price = random.randint(50, 300)
                else:
                    base_price = random.randint(150, 500)
            elif flight_class == "Premium Economy":
                base_price = random.randint(450, 800)
            elif flight_class == "Business":
                base_price = random.randint(1000, 3000)
            else:  # First class
                base_price = random.randint(3000, 8000)
            
            # Adjust price based on duration
            price_multiplier = 1 + (duration_hours / 10)
            base_price = int(base_price * price_multiplier)
            
            # Budget airlines often have extra fees
            if airline in budget_airlines:
                extra_fees = random.randint(20, 100)
                base_price += extra_fees
            
            # Calculate total price for all passengers
            total_price = base_price * adults + (base_price * 0.75 * children)
            price = f"${total_price:.2f}"
            
            # Generate valid booking links for real flight search pages
            booking_site = random.choice([
                {
                    "name": "Expedia",
                    "url": "https://www.expedia.com/Flights-Search",
                    "params": f"?trip=oneway&leg1={from_city.replace(' ', '%20')}({from_city[:3].upper()})-{to_city.replace(' ', '%20')}({to_city[:3].upper()})&departure-date={flight_date.strftime('%Y-%m-%d')}&adult={adults}&child={children}&class={flight_class.lower().replace(' ', '')}"
                },
                {
                    "name": "Kayak",
                    "url": "https://www.kayak.com/flights",
                    "params": f"/{from_city[:3].upper()}-{to_city[:3].upper()}/{flight_date.strftime('%Y-%m-%d')}/{flight_class.lower().replace(' ', '')}/{adults}adults/{children}children"
                },
                {
                    "name": "Skyscanner",
                    "url": "https://www.skyscanner.com/transport/flights",
                    "params": f"/{from_city.lower().replace(' ', '-')}/{to_city.lower().replace(' ', '-')}/{flight_date.strftime('%Y%m%d')}/?adults={adults}&adultsv2={adults}&cabinclass={flight_class.lower().replace(' ', '')}&children={children}&childrenv2=&inboundaltsenabled=false&outboundaltsenabled=false"
                }
            ])
            
            booking_link = f"{booking_site['url']}{booking_site['params']}"
            
            flights.append({
                "from": from_city,
                "to": to_city,
                "date": flight_date.strftime("%Y-%m-%d"),
                "airline": airline,
                "flight_number": flight_number,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": duration,
                "layovers": layovers if layovers else [],
                "class": flight_class,
                "price": price,
                "booking_link": booking_link
            })
    
    # Sort flights by price for budget travelers
    if budget_total:
        flights.sort(key=lambda x: float(x['price'].replace('$', '').replace(',', '')))
    
    return flights

# Main app
def main():
    if not st.session_state.user:
        show_auth_ui()
    else:
        show_sidebar()
        show_chat_ui()

if __name__ == "__main__":
    main()


