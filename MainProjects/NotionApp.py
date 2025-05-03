import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import json
import os
import re
import hashlib
import uuid
import subprocess
import tempfile
import pandas as pd
from datetime import timedelta

# File paths for storing data
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PAGES_FILE = os.path.join(DATA_DIR, "pages.json")
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")
CODE_FILES_FILE = os.path.join(DATA_DIR, "code_files.json")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.json")
BALANCES_FILE = os.path.join(DATA_DIR, "balances.json")
BILLS_FILE = os.path.join(DATA_DIR, "bills.json")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize data files if they don't exist
def init_data_files():
    initial_data = {
        USERS_FILE: {},
        PAGES_FILE: {},
        TEAMS_FILE: {},
        CODE_FILES_FILE: {},
        EXPENSES_FILE: {},
        BALANCES_FILE: {},
        BILLS_FILE: {}
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

# Available commands dictionary
COMMANDS = {
    'heading': {
        'description': 'Large heading text',
        'prefix': '/heading',
        'example': '/heading Your Title'
    },
    'subheading': {
        'description': 'Medium heading text',
        'prefix': '/subheading',
        'example': '/subheading Your Subtitle'
    },
    'h3': {
        'description': 'Small heading text',
        'prefix': '/h3',
        'example': '/h3 Section Title'
    },
    'todo': {
        'description': 'Checkbox item',
        'prefix': '/todo',
        'example': '/todo Task to do'
    },
    'list': {
        'description': 'Bullet point',
        'prefix': '/list',
        'example': '/list List item'
    },
    'num': {
        'description': 'Numbered list item',
        'prefix': '/num',
        'example': '/num Numbered item'
    },
    'quote': {
        'description': 'Block quote',
        'prefix': '/quote',
        'example': '/quote Notable text'
    },
    'code': {
        'description': 'Code block',
        'prefix': '/code',
        'example': '/code print("Hello")'
    },
    'table': {
        'description': '2x2 table',
        'prefix': '/table',
        'example': '/table'
    },
    'divider': {
        'description': 'Horizontal line',
        'prefix': '/divider',
        'example': '/divider'
    },
    'date': {
        'description': 'Current date',
        'prefix': '/date',
        'example': '/date'
    },
    'bold': {
        'description': 'Bold text',
        'prefix': '/bold',
        'example': '/bold Important text'
    },
    'italic': {
        'description': 'Italic text',
        'prefix': '/italic',
        'example': '/italic Emphasized text'
    },
    'link': {
        'description': 'Hyperlink',
        'prefix': '/link',
        'example': '/link URL Text'
    },
    'image': {
        'description': 'Image link',
        'prefix': '/image',
        'example': '/image URL Alt-text'
    },
    'callout': {
        'description': 'Info callout box',
        'prefix': '/callout',
        'example': '/callout Important note'
    },
    'code-block': {
        'description': 'Fenced code block',
        'prefix': '/code-block',
        'example': '/code-block python\nprint("Hello")'
    },
    'math': {
        'description': 'Math equation',
        'prefix': '/math',
        'example': '/math E = mc^2'
    }
}

# Programming language options
LANGUAGES = {
    'python': {'name': 'Python', 'ext': '.py', 'ace_mode': 'python'},
    'javascript': {'name': 'JavaScript', 'ext': '.js', 'ace_mode': 'javascript'},
    'java': {'name': 'Java', 'ext': '.java', 'ace_mode': 'java'},
    'cpp': {'name': 'C++', 'ext': '.cpp', 'ace_mode': 'c_cpp'},
    'ruby': {'name': 'Ruby', 'ext': '.rb', 'ace_mode': 'ruby'},
    'go': {'name': 'Go', 'ext': '.go', 'ace_mode': 'golang'}
}

# Configure the page
st.set_page_config(
    page_title="To-DO App",
    page_icon="✅",
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

/* Expander styling */
.streamlit-expanderHeader {
    background-color: #1a1a1a !important;
    border: none !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}

.streamlit-expanderHeader:hover {
    background-color: #222222 !important;
    transform: translateY(-2px);
    box-shadow: 0 0 15px rgba(30, 136, 229, 0.2);
}

/* Checkbox with glow */
.stCheckbox > label > div[role="checkbox"] {
    background-color: #1a1a1a !important;
    border: 2px solid #333 !important;
    transition: all 0.3s ease !important;
}

.stCheckbox > label > div[role="checkbox"]:hover {
    border-color: #1e88e5 !important;
    box-shadow: 0 0 10px rgba(30, 136, 229, 0.3);
}

.stCheckbox > label > div[data-checked="true"] {
    background-color: #1e88e5 !important;
    border-color: #1e88e5 !important;
    animation: checkbox-glow 0.3s ease-in-out;
}

@keyframes checkbox-glow {
    0% {
        transform: scale(0.8);
        opacity: 0.5;
    }
    50% {
        transform: scale(1.1);
        opacity: 0.8;
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

/* Radio buttons with glow */
.stRadio > label > div[role="radiogroup"] > label > div {
    background-color: #1a1a1a !important;
    border: 2px solid #333 !important;
    transition: all 0.3s ease !important;
}

.stRadio > label > div[role="radiogroup"] > label > div:hover {
    border-color: #1e88e5 !important;
    box-shadow: 0 0 10px rgba(30, 136, 229, 0.3);
}

/* Tabs with glow */
.stTabs [data-baseweb="tab-list"] {
    background-color: #1a1a1a !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: white !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #2a2a2a !important;
    transform: translateY(-2px);
}

.stTabs [aria-selected="true"] {
    background-color: #1e88e5 !important;
    box-shadow: 0 0 15px rgba(30, 136, 229, 0.3);
}

/* Cards with hover effect */
.element-container {
    transition: all 0.3s ease !important;
}

.element-container:hover {
    transform: translateY(-2px);
}

/* Table styling */
.stTable {
    background-color: #1a1a1a !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.2) !important;
}

.stTable th {
    background-color: #2a2a2a !important;
    color: white !important;
    padding: 12px !important;
}

.stTable td {
    background-color: #1a1a1a !important;
    color: white !important;
    padding: 12px !important;
    border-bottom: 1px solid #333 !important;
}

/* Code blocks with glow */
pre {
    background-color: #1a1a1a !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    box-shadow: 0 0 15px rgba(30, 136, 229, 0.1) !important;
    transition: all 0.3s ease !important;
}

pre:hover {
    box-shadow: 0 0 20px rgba(30, 136, 229, 0.2) !important;
    transform: translateY(-2px);
}

/* Floating animation for cards */
@keyframes float {
    0% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-5px);
    }
    100% {
        transform: translateY(0px);
    }
}

.element-container {
    animation: float 3s ease-in-out infinite;
}

/* Success message animation */
@keyframes success-glow {
    0% {
        box-shadow: 0 0 5px #4CAF50;
    }
    50% {
        box-shadow: 0 0 20px #4CAF50;
    }
    100% {
        box-shadow: 0 0 5px #4CAF50;
    }
}

.element-container .success {
    animation: success-glow 2s ease-in-out infinite;
}

/* Error message animation */
@keyframes error-glow {
    0% {
        box-shadow: 0 0 5px #f44336;
    }
    50% {
        box-shadow: 0 0 20px #f44336;
    }
    100% {
        box-shadow: 0 0 5px #f44336;
    }
}

.element-container .error {
    animation: error-glow 2s ease-in-out infinite;
}

/* Link hover effect */
a {
    color: #1e88e5 !important;
    text-decoration: none !important;
    transition: all 0.3s ease !important;
    position: relative !important;
}

a:hover {
    color: #90caf9 !important;
    text-shadow: 0 0 10px rgba(30, 136, 229, 0.5);
}

a:hover::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 2px;
    bottom: -2px;
    left: 0;
    background-color: #1e88e5;
    animation: link-glow 1s ease-in-out infinite alternate;
}

@keyframes link-glow {
    from {
        box-shadow: 0 0 5px #1e88e5;
    }
    to {
        box-shadow: 0 0 10px #1e88e5;
    }
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

/* Command dropdown styling */
.streamlit-expanderHeader {
    background: linear-gradient(45deg, #1e88e5, #1976d2) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px !important;
    margin-bottom: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 15px rgba(30, 136, 229, 0.3) !important;
}

.streamlit-expanderHeader:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 30px rgba(30, 136, 229, 0.5) !important;
}

/* Command list styling */
.streamlit-expanderContent {
    background-color: #1a1a1a !important;
    border-radius: 8px !important;
    padding: 16px !important;
    margin-top: 8px !important;
    border: 1px solid #333 !important;
}

/* Ensure all buttons have the same blue style */
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
    width: 100% !important;
    margin: 4px 0 !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 30px rgba(30, 136, 229, 0.5) !important;
    animation: button-glow 1.5s ease-in-out infinite alternate !important;
}

/* Command example styling */
code {
    background-color: #2a2a2a !important;
    color: #1e88e5 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-family: 'Monaco', monospace !important;
}

/* Divider styling in command list */
hr {
    border-color: #333 !important;
    margin: 12px 0 !important;
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
</script>
""", unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = None
if 'current_team' not in st.session_state:
    st.session_state.current_team = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'pages'
if 'expense_filter' not in st.session_state:
    st.session_state.expense_filter = 'all'

# Expense Categories with icons
EXPENSE_CATEGORIES = {
    'Food & Dining': '🍽️',
    'Transportation': '🚗',
    'Shopping': '🛍️',
    'Entertainment': '🎬',
    'Bills & Utilities': '📱',
    'Rent': '🏠',
    'Health': '⚕️',
    'Travel': '✈️',
    'Education': '📚',
    'Business': '💼',
    'Other': '📌'
}

# Add admin credentials
ADMIN_USERNAME = "syon"
ADMIN_PASSWORD = "admin"

def is_admin():
    return (st.session_state.user and 
            st.session_state.user.get('username') == ADMIN_USERNAME)

def show_admin_panel():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👑 Admin Panel")
    
    # Admin Actions
    admin_action = st.sidebar.selectbox(
        "Admin Actions",
        ["User Management", "Account Balances", "Analytics", "System Logs"]
    )
    
    if admin_action == "User Management":
        st.title("👥 User Management")
        users = load_data(USERS_FILE)
        
        # User list with actions
        st.markdown("### User List")
        
        # Create a table of users
        user_data = []
        for uid, u in users.items():
            # Ensure we're getting the username correctly
            username = u.get('username')
            if not username:  # If username is missing, use the user ID
                username = f"User {uid[:8]}"
            
            user_data.append([
                username,
                u.get('email', 'No email'),
                datetime.fromisoformat(u.get('created_at', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M'),
                u.get('status', 'active')
            ])
        
        if user_data:
            st.table({
                'Username': [u[0] for u in user_data],
                'Email': [u[1] for u in user_data],
                'Created': [u[2] for u in user_data],
                'Status': [u[3] for u in user_data]
            })
        
        # User Actions
        col1, col2 = st.columns(2)
        with col1:
            if user_data:  # Only show if there are users
                user_to_act = st.selectbox(
                    "Select User",
                    [u[0] for u in user_data]
                )
                # Find the user ID by matching the displayed username
                user_id = next((uid for uid, u in users.items() 
                             if u.get('username') == user_to_act or 
                             (not u.get('username') and f"User {uid[:8]}" == user_to_act)), None)
                
                if user_id:  # Only show actions if user is found
                    with col2:
                        action = st.selectbox(
                            "Action",
                            ["Ban User", "Delete User", "Reset Password", "Make Admin"]
                        )
                    
                    if st.button("Execute Action"):
                        if action == "Ban User":
                            users[user_id]['status'] = 'banned'
                            st.error(f"Banned user {user_to_act}")
                        elif action == "Delete User":
                            del users[user_id]
                            st.error(f"Deleted user {user_to_act}")
                        elif action == "Reset Password":
                            users[user_id]['password'] = hash_password('password123')
                            st.success(f"Reset password for {user_to_act} to 'password123'")
                        elif action == "Make Admin":
                            users[user_id]['is_admin'] = True
                            st.success(f"Made {user_to_act} an admin")
                        save_data(users, USERS_FILE)
                        st.rerun()
            else:
                st.info("No users found in the system.")
    
    elif admin_action == "Account Balances":
        st.title("💰 Account Balances")
        balances = load_data(BALANCES_FILE)
        users = load_data(USERS_FILE)
        
        # Balance management
        st.markdown("### Modify Balance")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            target_user = st.selectbox(
                "Select User",
                [u.get('username', 'Unknown') for u in users.values()]
            )
            target_id = next(uid for uid, u in users.items() 
                           if u.get('username') == target_user)
        
        with col2:
            amount = st.number_input("Amount", value=0.0, step=10.0)
        
        with col3:
            operation = st.selectbox("Operation", ["Add", "Subtract", "Set"])
        
        if st.button("Update Balance"):
            if target_id not in balances:
                balances[target_id] = {'balance': 0.0, 'owed': 0.0, 'owing': 0.0}
            
            if operation == "Add":
                balances[target_id]['balance'] += amount
            elif operation == "Subtract":
                balances[target_id]['balance'] -= amount
            else:  # Set
                balances[target_id]['balance'] = amount
            
            save_data(balances, BALANCES_FILE)
            st.success(f"Updated balance for {target_user}")
            st.rerun()
        
        # Display all balances
        st.markdown("### All Balances")
        balance_data = []
        for uid, b in balances.items():
            username = users.get(uid, {}).get('username', 'Unknown')
            balance_data.append([
                username,
                b['balance'],
                b['owed'],
                b['owing'],
                b['balance'] + b['owed'] - b['owing']
            ])
        
        if balance_data:
            st.table({
                'Username': [b[0] for b in balance_data],
                'Balance': [f"${b[1]:.2f}" for b in balance_data],
                'Owed': [f"${b[2]:.2f}" for b in balance_data],
                'Owing': [f"${b[3]:.2f}" for b in balance_data],
                'Net': [f"${b[4]:.2f}" for b in balance_data]
            })
        
        # Simple bar chart for balances
        if balance_data:
            st.markdown("### Balance Distribution")
            st.bar_chart({
                'Balance': {b[0]: b[1] for b in balance_data}
            })
    
    elif admin_action == "Analytics":
        st.title("📊 System Analytics")
        
        # User growth
        users = load_data(USERS_FILE)
        user_dates = [datetime.fromisoformat(u.get('created_at', datetime.now().isoformat()))
                     for u in users.values()]
        
        if user_dates:
            # Create simple line chart for user growth
            st.markdown("### User Growth")
            dates = sorted(user_dates)
            cumulative_users = list(range(1, len(dates) + 1))
            st.line_chart({
                'Users': cumulative_users
            })
        
        # Transaction analytics
        expenses = load_data(EXPENSES_FILE)
        all_expenses = []
        for user_expenses in expenses.values():
            if isinstance(user_expenses, list):
                all_expenses.extend(user_expenses)
        
        if all_expenses:
            # Group expenses by category
            categories = {}
            for expense in all_expenses:
                cat = expense['category']
                categories[cat] = categories.get(cat, 0) + expense['amount']
            
            st.markdown("### Expense Categories")
            st.bar_chart(categories)
    
    else:  # System Logs
        st.title("📝 System Logs")
        
        # Show recent activities
        activities = []
        
        # User activities
        for uid, user in load_data(USERS_FILE).items():
            activities.append({
                'Type': 'User Creation',
                'Details': f"User {user.get('username', 'Unknown')} created",
                'Date': datetime.fromisoformat(user.get('created_at', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')
            })
        
        # Transaction activities
        for user_expenses in load_data(EXPENSES_FILE).values():
            if isinstance(user_expenses, list):
                for expense in user_expenses:
                    activities.append({
                        'Type': 'Transaction',
                        'Details': f"{expense['description']} - ${expense['amount']}",
                        'Date': datetime.fromisoformat(expense['date']).strftime('%Y-%m-%d %H:%M')
                    })
        
        # Sort activities by date
        activities.sort(key=lambda x: x['Date'], reverse=True)
        
        # Display activities
        if activities:
            st.markdown("### Recent Activities")
            st.table(activities)

def show_auth_ui():
    st.title("Welcome to To-DO App")
    st.markdown("### Please sign in or create an account")
    
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
                            # Check if user is banned
                            if user_entry[1].get('status') == 'banned':
                                st.error("This account has been banned.")
                                return
                            
                            st.session_state.user = {
                                'username': username,
                                'id': user_entry[0],
                                'is_admin': username == ADMIN_USERNAME and password == ADMIN_PASSWORD or user_entry[1].get('is_admin', False)
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
                            'created_at': datetime.now().isoformat(),
                            'status': 'active',
                            'is_admin': False  # Explicitly set is_admin to False for new users
                        }
                        
                        save_data(users, USERS_FILE)
                        st.success("Account created successfully! Please sign in.")
                        st.rerun()
                    else:
                        st.warning("Please fill in all required fields")

def show_sidebar():
    st.sidebar.title("✅ To-DO App")
    
    # User info
    st.sidebar.markdown(f"Welcome, {st.session_state.user['username']}!")
    
    if st.sidebar.button("Sign Out", key="signout_btn"):
        st.session_state.user = None
        st.rerun()
    
    # Show admin panel for admin user
    if is_admin():
        show_admin_panel()
    
    st.sidebar.markdown("---")
    
    # View selection
    st.sidebar.markdown("### Navigation")
    view = st.sidebar.radio("", ["📄 Pages", "💰 Expenses", "💻 Code", "👥 Teams"])
    st.session_state.current_view = view.split()[1].lower()
    
    if st.session_state.current_view == 'teams':
        show_teams_sidebar()
    elif st.session_state.current_view == 'code':
        show_code_sidebar()
    elif st.session_state.current_view == 'expenses':
        show_expenses_sidebar()
    else:
        show_pages_sidebar()

def show_teams_sidebar():
    teams = load_data(TEAMS_FILE)
    user_id = st.session_state.user['id']
    
    # Create new team
    with st.sidebar.expander("Create New Team"):
        team_name = st.text_input("Team Name")
        if st.button("Create Team"):
            if team_name:
                team_id = str(uuid.uuid4())
                teams[team_id] = {
                    'name': team_name,
                    'owner_id': user_id,
                    'members': [user_id],
                    'created_at': datetime.now().isoformat()
                }
                save_data(teams, TEAMS_FILE)
                st.success(f"Team '{team_name}' created!")
                st.rerun()
    
    # List teams
    st.sidebar.markdown("### Your Teams")
    user_teams = {tid: team for tid, team in teams.items() 
                 if user_id in team['members']}
    
    for team_id, team in user_teams.items():
        icon = "👑" if team['owner_id'] == user_id else "👤"
        if st.sidebar.button(f"{icon} {team['name']}", key=f"team_{team_id}"):
            st.session_state.current_team = team_id
            st.rerun()

def show_code_sidebar():
    code_files = load_data(CODE_FILES_FILE)
    user_id = st.session_state.user['id']
    
    # Create new code file
    with st.sidebar.expander("Create New Code File"):
        filename = st.text_input("Filename")
        language = st.selectbox("Language", list(LANGUAGES.keys()))
        is_private = st.checkbox("Private", value=True)
        team_id = None
        
        if not is_private:
            teams = load_data(TEAMS_FILE)
            user_teams = {tid: team for tid, team in teams.items() 
                        if user_id in team['members']}
            if user_teams:
                team_options = [("None", "")] + [(t['name'], tid) for tid, t in user_teams.items()]
                team_id = st.selectbox("Team", options=team_options, format_func=lambda x: x[0])[1]
        
        if st.button("Create File"):
            if filename:
                file_id = str(uuid.uuid4())
                code_files[file_id] = {
                    'filename': filename,
                    'language': language,
                    'content': '',
                    'owner_id': user_id,
                    'team_id': team_id,
                    'is_private': is_private,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                save_data(code_files, CODE_FILES_FILE)
                st.session_state.current_file = file_id
                st.success(f"File '{filename}' created!")
                st.rerun()
    
    # List code files
    st.sidebar.markdown("### Your Code Files")
    user_files = {fid: f for fid, f in code_files.items() 
                 if f['owner_id'] == user_id or 
                 (not f['is_private'] and f['team_id'] and 
                  user_id in load_data(TEAMS_FILE).get(f['team_id'], {}).get('members', []))}
    
    for file_id, file in user_files.items():
        if st.sidebar.button(f"📄 {file['filename']}", key=f"code_{file_id}"):
            st.session_state.current_file = file_id
            st.rerun()

def show_pages_sidebar():
    pages = load_data(PAGES_FILE)
    user_id = st.session_state.user['id']
    
    # Create new page
    with st.sidebar.expander("Create New Page"):
        page_title = st.text_input("Page Title")
        is_private = st.checkbox("Private", value=True)
        team_id = None
        
        if not is_private:
            teams = load_data(TEAMS_FILE)
            user_teams = {tid: team for tid, team in teams.items() 
                        if user_id in team['members']}
            if user_teams:
                team_options = [("None", "")] + [(t['name'], tid) for tid, t in user_teams.items()]
                team_id = st.selectbox("Team", options=team_options, format_func=lambda x: x[0])[1]
        
        if st.button("Create Page"):
            if page_title:
                page_id = str(uuid.uuid4())
                pages[page_id] = {
                    'title': page_title,
                    'content': '',
                    'owner_id': user_id,
                    'team_id': team_id,
                    'is_private': is_private,
                    'todos': [],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                save_data(pages, PAGES_FILE)
                st.session_state.current_page = page_id
                st.success(f"Page '{page_title}' created!")
                st.rerun()
    
    # List pages
    st.sidebar.markdown("### Your Pages")
    user_pages = {pid: p for pid, p in pages.items() 
                 if p['owner_id'] == user_id or 
                 (not p['is_private'] and p['team_id'] and 
                  user_id in load_data(TEAMS_FILE).get(p['team_id'], {}).get('members', []))}
    
    for page_id, page in user_pages.items():
        if st.sidebar.button(f"📄 {page['title']}", key=f"page_{page_id}"):
            st.session_state.current_page = page_id
            st.rerun()

def show_team_view():
    if st.session_state.current_team:
        teams = load_data(TEAMS_FILE)
        team = teams[st.session_state.current_team]
        users = load_data(USERS_FILE)
        
        st.title(f"Team: {team['name']}")
        
        # Team management
        if team['owner_id'] == st.session_state.user['id']:
            with st.expander("Manage Team"):
                # Add member
                new_member = st.text_input("Add Member (username)")
                if st.button("Add"):
                    user_id = next((uid for uid, u in users.items() 
                                 if u['username'] == new_member), None)
                    if user_id:
                        if user_id not in team['members']:
                            team['members'].append(user_id)
                            save_data(teams, TEAMS_FILE)
                            st.success(f"Added {new_member} to the team!")
                            st.rerun()
                        else:
                            st.warning("User is already a team member")
                    else:
                        st.error("User not found")
                
                # List and remove members
                st.markdown("### Team Members")
                for member_id in team['members']:
                    member = next((u for u in users.values() 
                                if u['id'] == member_id), None)
                    if member:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(member['username'])
                        with col2:
                            if member_id != team['owner_id']:
                                if st.button("Remove", key=f"remove_{member_id}"):
                                    team['members'].remove(member_id)
                                    save_data(teams, TEAMS_FILE)
                                    st.rerun()
        
        # Team content
        tab1, tab2 = st.tabs(["Pages", "Code Files"])
        
        with tab1:
            st.markdown("### Team Pages")
            pages = load_data(PAGES_FILE)
            team_pages = {pid: p for pid, p in pages.items() 
                        if p['team_id'] == st.session_state.current_team}
            
            for page in team_pages.values():
                owner = next((u['username'] for u in users.values() 
                           if u['id'] == page['owner_id']), "Unknown")
                st.write(f"📄 {page['title']} (by {owner})")
        
        with tab2:
            st.markdown("### Team Code Files")
            code_files = load_data(CODE_FILES_FILE)
            team_files = {fid: f for fid, f in code_files.items() 
                        if f['team_id'] == st.session_state.current_team}
            
            for file in team_files.values():
                owner = next((u['username'] for u in users.values() 
                           if u['id'] == file['owner_id']), "Unknown")
                st.write(f"💻 {file['filename']} (by {owner})")

def show_code_view():
    if hasattr(st.session_state, 'current_file'):
        code_files = load_data(CODE_FILES_FILE)
        file = code_files[st.session_state.current_file]
        
        st.title(f"Editing: {file['filename']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Replace st_ace with a regular text area
            st.markdown("### Code Editor")
            content = st.text_area(
                "Code",
                value=file['content'],
                height=400,
                key="code_editor",
                help="Type or paste your code here"
            )
            
            if content != file['content']:
                file['content'] = content
                file['updated_at'] = datetime.now().isoformat()
                save_data(code_files, CODE_FILES_FILE)
        
        with col2:
            st.markdown("### Output")
            if st.button("Run Code"):
                if file['language'] == 'python':
                    try:
                        with tempfile.NamedTemporaryFile(
                            suffix='.py',
                            mode='w',
                            delete=False
                        ) as f:
                            f.write(content)
                            f.flush()
                            
                            result = subprocess.run(
                                ['python', f.name],
                                capture_output=True,
                                text=True
                            )
                            st.code(result.stdout)
                            if result.stderr:
                                st.error(result.stderr)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Running code in this language is not yet supported")

def show_page_view():
    if st.session_state.current_page:
        pages = load_data(PAGES_FILE)
        page = pages[st.session_state.current_page]
        
        st.title(page['title'])
        
        # Quick Command Reference
        with st.expander("💡 Quick Commands", expanded=False):
            cols = st.columns(3)
            for i, (cmd, details) in enumerate(COMMANDS.items()):
                col = cols[i % 3]
                with col:
                    st.markdown(f"""
                    **/{cmd}**  
                    {details['description']}
                    """)
        
        # Content editing
        content = st.text_area(
            "Type / for commands",
            page['content'],
            height=500,
            key="editor",
            help="Use / to access commands (e.g., /todo, /heading)"
        )
        
        if content != page['content']:
            page['content'] = content
            page['updated_at'] = datetime.now().isoformat()
            
            # Extract todos from content
            todos = re.findall(r'/todo\s+(.+)', content)
            existing_todos = {t['content']: t for t in page['todos']}
            
            # Add new todos
            for todo_text in todos:
                if todo_text not in existing_todos:
                    page['todos'].append({
                        'id': str(uuid.uuid4()),
                        'content': todo_text,
                        'is_completed': False,
                        'created_at': datetime.now().isoformat(),
                        'completed_at': None
                    })
            
            save_data(pages, PAGES_FILE)
        
        # Process and display content
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Content")
            st.markdown(process_commands(content), unsafe_allow_html=True)
        
        with col2:
            st.markdown("### To-Dos")
            for todo in page['todos']:
                col1, col2, col3 = st.columns([0.1, 2, 0.2])
                with col1:
                    if st.checkbox("", todo['is_completed'], key=f"todo_{todo['id']}"):
                        todo['is_completed'] = True
                        todo['completed_at'] = datetime.now().isoformat()
                        save_data(pages, PAGES_FILE)
                with col2:
                    st.markdown(f"{'~~' if todo['is_completed'] else ''}{todo['content']}{'~~' if todo['is_completed'] else ''}")
                with col3:
                    if st.button("🗑️", key=f"delete_todo_{todo['id']}"):
                        page['todos'] = [t for t in page['todos'] if t['id'] != todo['id']]
                        save_data(pages, PAGES_FILE)
                        st.rerun()

def show_expenses_sidebar():
    st.sidebar.markdown("### Filters")
    filter_options = {
        'all': '📊 All Transactions',
        'owed': '💰 Money You\'re Owed',
        'owing': '💸 Money You Owe',
        'bills': '📱 Recurring Bills',
        'personal': '👤 Personal Expenses'
    }
    
    selected = st.sidebar.radio(
        "View",
        list(filter_options.keys()),
        format_func=lambda x: filter_options[x]
    )
    st.session_state.expense_filter = selected

def format_amount(amount, include_plus=False):
    if amount >= 0 and include_plus:
        return f"+${amount:,.2f}"
    return f"${abs(amount):,.2f}"

def get_user_balance(user_id):
    balances = load_data(BALANCES_FILE)
    if not isinstance(balances, dict):
        balances = {}
    return balances.get(user_id, {'balance': 0.0, 'owed': 0.0, 'owing': 0.0})

def show_expense_view():
    st.title("💰 Money & Bills")
    
    user_id = st.session_state.user['id']
    balance_data = get_user_balance(user_id)
    
    # Cash App style balance display
    st.markdown("""
    <style>
    .balance-container {
        background: linear-gradient(45deg, #1e88e5, #1976d2);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
    }
    .balance-amount {
        font-size: 48px;
        font-weight: bold;
        margin: 10px 0;
    }
    .balance-label {
        font-size: 18px;
        opacity: 0.9;
    }
    .mini-card {
        background: #1a1a1a;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Balance Overview
    st.markdown(f"""
    <div class="balance-container">
        <div class="balance-label">Your Balance</div>
        <div class="balance-amount">{format_amount(balance_data['balance'])}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add Money / Cash Out buttons
    col1, col2 = st.columns(2)
    with col1:
        with st.form("add_money_form"):
            amount_to_add = st.number_input("Amount to Add ($)", min_value=0.01, step=0.01)
            if st.form_submit_button("Add Money"):
                balances = load_data(BALANCES_FILE)
                if user_id not in balances:
                    balances[user_id] = {'balance': 0.0, 'owed': 0.0, 'owing': 0.0}
                balances[user_id]['balance'] += amount_to_add
                save_data(balances, BALANCES_FILE)
                st.success(f"Added {format_amount(amount_to_add)} to your balance!")
                st.rerun()
    
    with col2:
        with st.form("withdraw_form"):
            amount_to_withdraw = st.number_input("Amount to Withdraw ($)", min_value=0.01, step=0.01)
            if st.form_submit_button("Cash Out"):
                balances = load_data(BALANCES_FILE)
                if user_id not in balances:
                    balances[user_id] = {'balance': 0.0, 'owed': 0.0, 'owing': 0.0}
                if amount_to_withdraw <= balances[user_id]['balance']:
                    balances[user_id]['balance'] -= amount_to_withdraw
                    save_data(balances, BALANCES_FILE)
                    st.success(f"Withdrew {format_amount(amount_to_withdraw)} from your balance!")
                    st.rerun()
                else:
                    st.error("Insufficient balance!")
    
    # Quick Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="mini-card">
            <div style="font-size: 14px; color: #888;">You're Owed</div>
            <div style="font-size: 24px; color: #4CAF50;">+{format_amount(balance_data['owed'])}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="mini-card">
            <div style="font-size: 14px; color: #888;">You Owe</div>
            <div style="font-size: 24px; color: #f44336;">-{format_amount(balance_data['owing'])}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="mini-card">
            <div style="font-size: 14px; color: #888;">Monthly Bills</div>
            <div style="font-size: 24px; color: #ff9800;">{format_amount(sum(bill['amount'] for bill in load_data(BILLS_FILE).get(user_id, [])))}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Actions Tab
    tab1, tab2, tab3 = st.tabs(["💸 Add Expense", "📱 Manage Bills", "🔄 Settle Up"])
    
    with tab1:
        with st.form("add_expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                description = st.text_input("What's it for?")
                amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
                category = st.selectbox(
                    "Category",
                    list(EXPENSE_CATEGORIES.keys()),
                    format_func=lambda x: f"{EXPENSE_CATEGORIES[x]} {x}"
                )
            
            with col2:
                # Get all users except current user
                users = load_data(USERS_FILE)
                other_users = [
                    u.get('username', f"User {uid}") 
                    for uid, u in users.items() 
                    if uid != user_id
                ]
                
                split_with = st.multiselect(
                    "Split with",
                    other_users
                )
                split_type = st.selectbox(
                    "Split type",
                    ["Equal", "Percentage", "Exact amounts"]
                )
                paid_by = st.selectbox(
                    "Paid by",
                    ["You"] + split_with
                )
            
            submit_expense = st.form_submit_button("Add Expense")
            if submit_expense:
                if description and amount > 0:
                    expenses = load_data(EXPENSES_FILE)
                    balances = load_data(BALANCES_FILE)
                    
                    # Initialize user balances if needed
                    if user_id not in balances:
                        balances[user_id] = {'balance': 0.0, 'owed': 0.0, 'owing': 0.0}
                    
                    # Calculate splits
                    num_people = len(split_with) + 1
                    amount_per_person = amount / num_people
                    
                    # Get participant IDs
                    participant_ids = [
                        next(uid for uid, u in users.items() 
                             if u.get('username', f"User {uid}") == participant)
                        for participant in split_with
                    ]
                    
                    # Create expense record
                    new_expense = {
                        'id': str(uuid.uuid4()),
                        'description': description,
                        'amount': amount,
                        'category': category,
                        'paid_by': user_id if paid_by == "You" else next(
                            uid for uid, u in users.items() 
                            if u.get('username', f"User {uid}") == paid_by
                        ),
                        'split_with': [user_id] + participant_ids,
                        'split_type': split_type,
                        'amounts': {user_id: amount_per_person},
                        'date': datetime.now().isoformat(),
                        'settled': False
                    }
                    
                    # Update amounts for split participants
                    for participant_id in participant_ids:
                        new_expense['amounts'][participant_id] = amount_per_person
                        
                        if participant_id not in balances:
                            balances[participant_id] = {'balance': 0.0, 'owed': 0.0, 'owing': 0.0}
                        
                        # Update balances
                        if paid_by == "You":
                            balances[user_id]['owed'] += amount_per_person
                            balances[participant_id]['owing'] += amount_per_person
                        else:
                            balances[user_id]['owing'] += amount_per_person
                            balances[participant_id]['owed'] += amount_per_person
                    
                    # Save everything
                    if user_id not in expenses:
                        expenses[user_id] = []
                    expenses[user_id].append(new_expense)
                    save_data(expenses, EXPENSES_FILE)
                    save_data(balances, BALANCES_FILE)
                    st.success("Expense added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a description and valid amount")

    with tab2:
        st.markdown("### Recurring Bills")
        
        with st.expander("➕ Add New Bill"):
            with st.form("add_bill_form"):
                bill_name = st.text_input("Bill name")
                bill_amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
                bill_category = st.selectbox(
                    "Category",
                    list(EXPENSE_CATEGORIES.keys()),
                    format_func=lambda x: f"{EXPENSE_CATEGORIES[x]} {x}",
                    key="bill_category"
                )
                bill_due_date = st.date_input("Due date")
                bill_recurring = st.selectbox(
                    "Recurring",
                    ["Monthly", "Weekly", "Yearly"]
                )
                
                if st.form_submit_button("Add Bill"):
                    bills = load_data(BILLS_FILE)
                    if user_id not in bills:
                        bills[user_id] = []
                    
                    bills[user_id].append({
                        'id': str(uuid.uuid4()),
                        'name': bill_name,
                        'amount': bill_amount,
                        'category': bill_category,
                        'due_date': bill_due_date.isoformat(),
                        'recurring': bill_recurring,
                        'created_at': datetime.now().isoformat()
                    })
                    
                    save_data(bills, BILLS_FILE)
                    st.success("Bill added successfully!")
                    st.rerun()
        
        # Display bills
        bills = load_data(BILLS_FILE).get(user_id, [])
        if bills:
            for bill in sorted(bills, key=lambda x: x['due_date']):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    with col1:
                        st.write(f"{EXPENSE_CATEGORIES[bill['category']]} {bill['name']}")
                    with col2:
                        st.write(format_amount(bill['amount']))
                    with col3:
                        due_date = datetime.fromisoformat(bill['due_date']).date()
                        days_until = (due_date - datetime.now().date()).days
                        if days_until < 0:
                            st.markdown("🔴 Overdue")
                        elif days_until == 0:
                            st.markdown("🟡 Due today")
                        else:
                            st.write(f"Due in {days_until} days")
                    with col4:
                        if st.button("🗑️", key=f"delete_bill_{bill['id']}"):
                            bills = load_data(BILLS_FILE)
                            bills[user_id] = [b for b in bills[user_id] if b['id'] != bill['id']]
                            save_data(bills, BILLS_FILE)
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("No bills added yet!")
    
    with tab3:
        st.markdown("### Settle Up")
        
        # Get all unsettled expenses
        expenses = load_data(EXPENSES_FILE).get(user_id, [])
        unsettled = [e for e in expenses if not e['settled']]
        
        if unsettled:
            for expense in unsettled:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(expense['description'])
                    with col2:
                        st.write(format_amount(expense['amount']))
                    with col3:
                        if st.button("Settle", key=f"settle_{expense['id']}"):
                            # Update balances
                            balances = load_data(BALANCES_FILE)
                            for participant_id, amount in expense['amounts'].items():
                                if participant_id != expense['paid_by']:
                                    balances[expense['paid_by']]['owed'] -= amount
                                    balances[participant_id]['owing'] -= amount
                            
                            # Mark expense as settled
                            expense['settled'] = True
                            save_data(expenses, EXPENSES_FILE)
                            save_data(balances, BALANCES_FILE)
                            st.success("Expense settled!")
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("No expenses to settle!")

def process_commands(text):
    """Process text commands and convert to formatted HTML"""
    # Process tables first (special case)
    text = re.sub(r'/table\s*\n?', '''
<table>
  <tr>
    <td>Header 1</td>
    <td>Header 2</td>
  </tr>
  <tr>
    <td>Cell 1</td>
    <td>Cell 2</td>
  </tr>
</table>
''', text)
    
    # Process other commands
    text = re.sub(r'/heading\s+(.+)', r'<h1>\1</h1>', text)
    text = re.sub(r'/subheading\s+(.+)', r'<h2>\1</h2>', text)
    text = re.sub(r'/h3\s+(.+)', r'<h3>\1</h3>', text)
    text = re.sub(r'/todo\s+(.+)', r'<input type="checkbox" disabled> \1<br>', text)
    text = re.sub(r'/list\s+(.+)', r'<li>\1</li>', text)
    text = re.sub(r'/num\s+(.+)', r'<ol><li>\1</li></ol>', text)
    text = re.sub(r'/quote\s+(.+)', r'<blockquote>\1</blockquote>', text)
    text = re.sub(r'/code\s+(.+)', r'<code>\1</code>', text)
    text = re.sub(r'/divider', r'<hr>', text)
    text = re.sub(r'/date', datetime.now().strftime("%Y-%m-%d"), text)
    text = re.sub(r'/bold\s+(.+)', r'<strong>\1</strong>', text)
    text = re.sub(r'/italic\s+(.+)', r'<em>\1</em>', text)
    text = re.sub(r'/link\s+(\S+)\s+(.+)', r'<a href="\1">\2</a>', text)
    text = re.sub(r'/image\s+(\S+)\s+(.+)', r'<img src="\1" alt="\2">', text)
    text = re.sub(r'/callout\s+(.+)', r'<div class="callout">\1</div>', text)
    text = re.sub(r'/code-block\s+(\w+)\s*\n(.*?)(?=\n/|\n\n|$)', r'<pre><code class="language-\1">\2</code></pre>', text, flags=re.DOTALL)
    text = re.sub(r'/math\s+(.+)', r'\\[\1\\]', text)
    
    return text

# Main app
def main():
    if not st.session_state.user:
        show_auth_ui()
    else:
        show_sidebar()
        
        if st.session_state.current_view == 'teams':
            show_team_view()
        elif st.session_state.current_view == 'code':
            show_code_view()
        elif st.session_state.current_view == 'expenses':
            show_expense_view()
        else:
            show_page_view()

if __name__ == "__main__":
    main()

