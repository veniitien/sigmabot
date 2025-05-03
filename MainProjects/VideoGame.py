import streamlit as st
import hashlib
import json
import os
from datetime import datetime
import time
import math
import random

# Page configuration
st.set_page_config(
    page_title="GameVerse 🎮",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_game' not in st.session_state:
    st.session_state.current_game = None
if 'coins' not in st.session_state:
    st.session_state.coins = 0
if 'game_progress' not in st.session_state:
    st.session_state.game_progress = {}
if 'friend_requests' not in st.session_state:
    st.session_state.friend_requests = []
if 'friends' not in st.session_state:
    st.session_state.friends = []
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# CSS styles
st.markdown("""
<style>
    /* Main styles */
    .stApp {
        background-color: #000000 !important;
        color: white;
    }
    
    /* Navigation bar */
    .nav-bar {
        background: rgba(30, 42, 69, 0.8);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #2D3B58;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Game cards */
    .game-card {
        background: rgba(30, 42, 69, 0.8);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #2D3B58;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .game-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at center, rgba(59, 130, 246, 0.1), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .game-card::after {
        content: '';
        position: absolute;
        width: 5px;
        height: 5px;
        background: rgba(59, 130, 246, 0.5);
        border-radius: 50%;
        transform: scale(1);
        opacity: 0;
    }
    
    .game-card:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 
            0 8px 25px rgba(59, 130, 246, 0.3),
            0 0 0 1px rgba(59, 130, 246, 0.3);
        border-color: #3B82F6;
    }
    
    .game-card:hover::before {
        opacity: 1;
    }
    
    .game-card:active::after {
        animation: ripple 0.6s ease-out;
    }
    
    @keyframes ripple {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        100% {
            transform: scale(100);
            opacity: 0;
        }
    }
    
    .game-card h3 {
        position: relative;
        display: inline-block;
    }
    
    .game-card h3::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 2px;
        bottom: -4px;
        left: 0;
        background: linear-gradient(90deg, #3B82F6, #60A5FA);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
    }
    
    .game-card:hover h3::after {
        transform: scaleX(1);
    }
    
    /* Friend system */
    .friend-item {
        background: rgba(30, 42, 69, 0.8);
        border: 1px solid #2D3B58;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .friend-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
        border-color: #3B82F6;
    }
    
    .friend-item:active::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        background: radial-gradient(circle at center, rgba(59, 130, 246, 0.2), transparent);
        animation: ripple 0.6s ease-out;
    }
    
    .friend-avatar {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #3B82F6, #60A5FA);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    
    .friend-item:hover .friend-avatar {
        transform: scale(1.1);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    
    /* Notifications */
    .notification {
        background: rgba(30, 42, 69, 0.8);
        border: 1px solid #2D3B58;
        padding: 12px 15px;
        border-radius: 10px;
        margin: 8px 0;
        animation: slideIn 0.3s ease;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .notification:hover {
        transform: translateX(5px);
        border-color: #3B82F6;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    
    .notification:active::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        background: radial-gradient(circle at center, rgba(59, 130, 246, 0.2), transparent);
        animation: ripple 0.6s ease-out;
    }
    
    /* Button styles */
    .stButton > button {
        background: linear-gradient(45deg, #3B82F6, #60A5FA) !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    }
    
    .stButton > button:active::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        background: radial-gradient(circle at center, rgba(255, 255, 255, 0.2), transparent);
        animation: ripple 0.6s ease-out;
    }
    
    /* Input styles */
    .stTextInput > div > div > input {
        background-color: rgba(30, 42, 69, 0.8) !important;
        color: white !important;
        border: 1px solid #2D3B58 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Stats display */
    .stats {
        display: flex;
        align-items: center;
        gap: 15px;
        color: #94A3B8;
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 5px;
        transition: all 0.3s ease;
    }
    
    .stat-item:hover {
        color: white;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# User data handling
def load_users():
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            json.dump({}, f)
    with open('users.json', 'r') as f:
        return json.load(f)

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication functions
def login(username, password):
    users = load_users()
    if username in users and users[username]['password'] == hash_password(password):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.coins = users[username].get('coins', 0)
        st.session_state.game_progress = users[username].get('progress', {})
        return True
    return False

def signup(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        'password': hash_password(password),
        'created_at': str(datetime.now()),
        'coins': 100,  # Starting coins
        'progress': {},
        'friends': [],
        'friend_requests': [],
        'notifications': []
    }
    save_users(users)
    return True

def save_progress():
    if st.session_state.logged_in:
        users = load_users()
        users[st.session_state.username].update({
            'coins': st.session_state.coins,
            'progress': st.session_state.game_progress,
            'friends': st.session_state.friends,
            'friend_requests': st.session_state.friend_requests,
            'notifications': st.session_state.notifications
        })
        save_users(users)

def send_friend_request(from_user, to_user):
    users = load_users()
    if to_user in users and to_user != from_user:
        if 'friend_requests' not in users[to_user]:
            users[to_user]['friend_requests'] = []
        if from_user not in users[to_user]['friend_requests']:
            users[to_user]['friend_requests'].append(from_user)
            users[to_user]['notifications'] = users[to_user].get('notifications', [])
            users[to_user]['notifications'].append(f"{from_user} sent you a friend request!")
            save_users(users)
            return True
    return False

def accept_friend_request(user, friend):
    users = load_users()
    if friend in users[user]['friend_requests']:
        # Add to friends list
        if 'friends' not in users[user]:
            users[user]['friends'] = []
        if 'friends' not in users[friend]:
            users[friend]['friends'] = []
        
        users[user]['friends'].append(friend)
        users[friend]['friends'].append(user)
        
        # Remove request
        users[user]['friend_requests'].remove(friend)
        
        # Add notification
        users[friend]['notifications'] = users[friend].get('notifications', [])
        users[friend]['notifications'].append(f"{user} accepted your friend request!")
        
        save_users(users)
        return True
    return False

def reject_friend_request(user, friend):
    users = load_users()
    if friend in users[user]['friend_requests']:
        users[user]['friend_requests'].remove(friend)
        save_users(users)
        return True
    return False

# Game definitions
games = {
    "Space Runner": {
        "icon": "🚀",
        "description": "Navigate through space avoiding obstacles",
        "difficulty": "Medium",
        "players_online": 45
    },
    "Cookie Clicker": {
        "icon": "🍪",
        "description": "Click cookies to earn points and upgrades",
        "difficulty": "Easy",
        "players_online": 128
    },
    "Pixel Adventure": {
        "icon": "👾",
        "description": "Classic platformer with modern twists",
        "difficulty": "Hard",
        "players_online": 67,
        "new": True
    },
    "Pet Simulator": {
        "icon": "🐾",
        "description": "Adopt and care for virtual pets",
        "difficulty": "Easy",
        "players_online": 89,
        "premium": True
    }
}

# Main interface
def main():
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 30px;'>🎮 GameVerse</h1>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.container():
                st.markdown("<div style='background: #1E2A45; padding: 25px; border-radius: 15px; border: 1px solid #2D3B58;'>", unsafe_allow_html=True)
                st.subheader("Login")
                login_username = st.text_input("Username", key="login_username")
                login_password = st.text_input("Password", type="password", key="login_password")
                if st.button("Login"):
                    if login(login_username, login_password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            with st.container():
                st.markdown("<div style='background: #1E2A45; padding: 25px; border-radius: 15px; border: 1px solid #2D3B58;'>", unsafe_allow_html=True)
                st.subheader("Sign Up")
                signup_username = st.text_input("Choose Username", key="signup_username")
                signup_password = st.text_input("Choose Password", type="password", key="signup_password")
                if st.button("Sign Up"):
                    if signup(signup_username, signup_password):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists")
                st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # Navigation and user info
        st.markdown(
            f"""
            <div class='nav-bar'>
                <span>Welcome, {st.session_state.username}! 👋</span>
                <div class='stats'>
                    <div class='stat-item'>🎮 Games: {len(st.session_state.game_progress)}</div>
                    <div class='stat-item'>🪙 Coins: {st.session_state.coins}</div>
                    <div class='stat-item'>👥 Friends: {len(st.session_state.friends)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Sidebar with friends and notifications
        with st.sidebar:
            st.subheader("👥 Friends")
            new_friend = st.text_input("Add Friend")
            if st.button("Send Request"):
                if send_friend_request(st.session_state.username, new_friend):
                    st.success("Friend request sent!")
                else:
                    st.error("User not found or already friends")
            
            if st.session_state.friend_requests:
                st.subheader("Friend Requests")
                for request in st.session_state.friend_requests:
                    col1, col2, col3 = st.columns([2,1,1])
                    with col1:
                        st.markdown(f"<div class='friend-item'><div class='friend-avatar'>{request[0].upper()}</div>{request}</div>", unsafe_allow_html=True)
                    with col2:
                        if st.button("Accept", key=f"accept_{request}"):
                            accept_friend_request(st.session_state.username, request)
                            st.rerun()
                    with col3:
                        if st.button("Reject", key=f"reject_{request}"):
                            reject_friend_request(st.session_state.username, request)
                            st.rerun()
            
            if st.session_state.friends:
                st.subheader("Your Friends")
                for friend in st.session_state.friends:
                    st.markdown(f"<div class='friend-item'><div class='friend-avatar'>{friend[0].upper()}</div>{friend}</div>", unsafe_allow_html=True)
            
            if st.session_state.notifications:
                st.subheader("Notifications")
                for notification in st.session_state.notifications:
                    st.markdown(f"<div class='notification'>{notification}</div>", unsafe_allow_html=True)
            
            if st.button("Logout"):
                save_progress()
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()
        
        # Main content area
        if not st.session_state.current_game:
            st.subheader("🎮 Available Games")
            
            cols = st.columns(2)
            for idx, (game_name, game_info) in enumerate(games.items()):
                with cols[idx % 2]:
                    # Game card with proper HTML escaping
                    st.markdown(
                        f"""
                        <div class='game-card'>
                            <h3>{game_info['icon']} {game_name}</h3>
                            <p>{game_info['description']}</p>
                            <div class='stats'>
                                <span>👥 {game_info['players_online']}</span>
                                <span>🎯 {game_info['difficulty']}</span>
                                {'<span style="color: #FFD700">⭐ Premium</span>' if game_info.get('premium', False) else ''}
                                {'<span style="color: #FF4444">NEW!</span>' if game_info.get('new', False) else ''}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"Play {game_name}", key=game_name):
                        st.session_state.current_game = game_name
                        st.rerun()
        
        else:
            # Back button
            if st.button("← Back to Games"):
                st.session_state.current_game = None
                st.rerun()
            
            # Game interfaces
            if st.session_state.current_game == "Space Runner":
                st.title(f"🚀 Space Runner")
                
                # Initialize game state
                if 'player_pos' not in st.session_state:
                    st.session_state.player_pos = 50
                if 'score' not in st.session_state:
                    st.session_state.score = 0
                if 'game_speed' not in st.session_state:
                    st.session_state.game_speed = 1
                if 'stars_collected' not in st.session_state:
                    st.session_state.stars_collected = 0
                if 'star_pos' not in st.session_state:
                    st.session_state.star_pos = {'x': random.randint(20, 80), 'y': random.randint(20, 80)}
                
                # Game UI
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    star_pos_x1 = random.randint(0, 100)
                    star_pos_y1 = random.randint(0, 100)
                    star_pos_x2 = random.randint(0, 100)
                    star_pos_y2 = random.randint(0, 100)
                    star_pos_x3 = random.randint(0, 100)
                    star_pos_y3 = random.randint(0, 100)
                    
                    game_canvas = f"""
                        <div style='
                            background: linear-gradient(180deg, #000033 0%, #000066 100%);
                            height: 500px;
                            border-radius: 15px;
                            position: relative;
                            overflow: hidden;
                            box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
                            border: 1px solid rgba(59, 130, 246, 0.5);'>
                            
                            <div style='position: absolute; width: 100%; height: 100%; 
                                background: radial-gradient(circle at {star_pos_x1}% {star_pos_y1}%, rgba(255,255,255,0.3) 1px, transparent 1px),
                                radial-gradient(circle at {star_pos_x2}% {star_pos_y2}%, rgba(255,255,255,0.2) 1px, transparent 1px),
                                radial-gradient(circle at {star_pos_x3}% {star_pos_y3}%, rgba(255,255,255,0.1) 1px, transparent 1px);
                                background-size: 100px 100px, 150px 150px, 200px 200px;'>
                            </div>
                            
                            <div style='
                                position: absolute;
                                top: {st.session_state.star_pos["y"]}%;
                                left: {st.session_state.star_pos["x"]}%;
                                font-size: 24px;
                                animation: pulse 1s infinite;'>⭐</div>
                            
                            <div style='
                                position: absolute;
                                bottom: {st.session_state.player_pos}%;
                                left: 10%;
                                width: 60px;
                                height: 60px;
                                transition: all 0.3s ease;'>
                                <div style='
                                    width: 100%;
                                    height: 100%;
                                    background: linear-gradient(45deg, #3B82F6, #60A5FA);
                                    clip-path: polygon(50% 0%, 20% 100%, 80% 100%);
                                    position: relative;
                                    filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.5));'>
                                    <div style='
                                        position: absolute;
                                        bottom: -10px;
                                        left: 50%;
                                        transform: translateX(-50%);
                                        width: 20px;
                                        height: 20px;
                                        background: #FF6B6B;
                                        border-radius: 50%;
                                        filter: blur(5px);
                                        animation: glow 0.5s alternate infinite;'>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <style>
                            @keyframes pulse {{
                                0% {{ transform: scale(1); }}
                                50% {{ transform: scale(1.2); }}
                                100% {{ transform: scale(1); }}
                            }}
                            @keyframes glow {{
                                from {{ opacity: 0.5; }}
                                to {{ opacity: 1; }}
                            }}
                        </style>
                    """
                    st.markdown(game_canvas, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div style='background: rgba(30, 42, 69, 0.8); padding: 20px; border-radius: 10px; border: 1px solid rgba(59, 130, 246, 0.3);'>
                            <h3 style='color: #60A5FA; margin-bottom: 15px;'>Stats</h3>
                            <p style='font-size: 18px;'>🎯 Score: {st.session_state.score}</p>
                            <p style='font-size: 18px;'>⚡ Speed: {st.session_state.game_speed:.1f}x</p>
                            <p style='font-size: 18px;'>⭐ Stars: {st.session_state.stars_collected}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Controls
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("← Move Left"):
                        st.session_state.player_pos = max(0, st.session_state.player_pos - 10)
                        # Check star collection
                        if abs(st.session_state.player_pos - st.session_state.star_pos['y']) < 15 and abs(10 - st.session_state.star_pos['x']) < 15:
                            st.session_state.stars_collected += 1
                            st.session_state.coins += 2
                            st.session_state.star_pos = {'x': random.randint(20, 80), 'y': random.randint(20, 80)}
                            st.success("Star collected! +2 coins! ⭐")
                
                with col2:
                    if st.button("Boost 🚀"):
                        st.session_state.score += int(10 * st.session_state.game_speed)
                        st.session_state.game_speed = min(3, st.session_state.game_speed + 0.1)
                        if st.session_state.score % 50 == 0:
                            st.session_state.coins += 5
                            st.success("Score bonus! +5 coins! 🪙")
                
                with col3:
                    if st.button("Move Right →"):
                        st.session_state.player_pos = min(100, st.session_state.player_pos + 10)
                        # Check star collection
                        if abs(st.session_state.player_pos - st.session_state.star_pos['y']) < 15 and abs(10 - st.session_state.star_pos['x']) < 15:
                            st.session_state.stars_collected += 1
                            st.session_state.coins += 2
                            st.session_state.star_pos = {'x': random.randint(20, 80), 'y': random.randint(20, 80)}
                            st.success("Star collected! +2 coins! ⭐")
            
            elif st.session_state.current_game == "Cookie Clicker":
                st.title(f"🍪 Cookie Clicker")
                
                # Initialize game state
                if 'cookies' not in st.session_state:
                    st.session_state.cookies = 0
                if 'multiplier' not in st.session_state:
                    st.session_state.multiplier = 1
                if 'auto_clickers' not in st.session_state:
                    st.session_state.auto_clickers = 0
                
                # Game UI
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(
                        """
                        <div style='text-align: center; padding: 20px;'>
                            <div style='font-size: 150px; cursor: pointer;'>
                                🍪
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if st.button("Click Cookie!", key="cookie"):
                        gained = int(1 * st.session_state.multiplier)
                        st.session_state.cookies += gained
                        if st.session_state.cookies % 100 == 0:
                            st.session_state.coins += 1
                            st.success(f"Milestone reached! +1 coin 🪙")
                
                with col2:
                    st.markdown(
                        f"""
                        <div style='background: rgba(30, 42, 69, 0.8); padding: 20px; border-radius: 10px;'>
                            <h3>Stats</h3>
                            <p>Cookies: {st.session_state.cookies}</p>
                            <p>Multiplier: x{st.session_state.multiplier}</p>
                            <p>Auto Clickers: {st.session_state.auto_clickers}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("### 🛠️ Upgrades")
                    if st.button("Upgrade Multiplier (25 coins)") and st.session_state.coins >= 25:
                        st.session_state.multiplier += 0.5
                        st.session_state.coins -= 25
                        st.success("Multiplier upgraded!")
                    
                    if st.button("Buy Auto Clicker (50 coins)") and st.session_state.coins >= 50:
                        st.session_state.auto_clickers += 1
                        st.session_state.coins -= 50
                        st.success("Auto Clicker purchased!")
                
                # Add auto-clicker functionality
                if st.session_state.auto_clickers > 0:
                    st.session_state.cookies += st.session_state.auto_clickers
                    if st.session_state.cookies % 50 == 0:
                        st.session_state.coins += 1
                        st.success("Auto-clicker bonus! +1 coin! 🪙")
            
            elif st.session_state.current_game == "Pixel Adventure":
                st.title("👾 Pixel Adventure")
                
                # Initialize game state
                if 'player_x' not in st.session_state:
                    st.session_state.player_x = 20
                if 'player_y' not in st.session_state:
                    st.session_state.player_y = 60
                if 'pixel_score' not in st.session_state:
                    st.session_state.pixel_score = 0
                
                # Game UI
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    css_style = """
                    <style>
                    .player {
                        box-shadow: 0 0 10px rgba(91, 156, 246, 0.5);
                        animation: float 2s ease-in-out infinite;
                    }
                    @keyframes float {
                        0% { transform: translateY(0px); }
                        50% { transform: translateY(-10px); }
                        100% { transform: translateY(0px); }
                    }
                    </style>
                    """
                    
                    container_div = "<div style='background: #1a1a1a; height: 400px; border-radius: 15px; position: relative; overflow: hidden; border: 2px solid #4a4a4a;'>"
                    player_div = "<div class='player' style='position: absolute; left: " + str(st.session_state.player_x) + "%; top: " + str(st.session_state.player_y) + "%; width: 32px; height: 32px; background: #5b9cf6; border-radius: 4px; transition: all 0.2s ease;'></div>"
                    closing_div = "</div>"
                    
                    game_canvas = container_div + player_div + closing_div + css_style
                    st.markdown(game_canvas, unsafe_allow_html=True)
                
                with col2:
                    stats_html = "<div style='background: rgba(30, 42, 69, 0.8); padding: 20px; border-radius: 10px;'>"
                    stats_html += "<h3>Stats</h3>"
                    stats_html += "<p>Score: " + str(st.session_state.pixel_score) + "</p>"
                    stats_html += "<p>Position: (" + str(st.session_state.player_x) + ", " + str(st.session_state.player_y) + ")</p>"
                    stats_html += "</div>"
                    st.markdown(stats_html, unsafe_allow_html=True)
                
                # Controls
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("⬅️ Left"):
                        st.session_state.player_x = max(0, st.session_state.player_x - 10)
                        st.session_state.pixel_score += 1
                
                with col2:
                    if st.button("⬆️ Up"):
                        st.session_state.player_y = max(0, st.session_state.player_y - 10)
                        st.session_state.pixel_score += 1
                
                with col3:
                    if st.button("⬇️ Down"):
                        st.session_state.player_y = min(90, st.session_state.player_y + 10)
                        st.session_state.pixel_score += 1
                
                with col4:
                    if st.button("➡️ Right"):
                        st.session_state.player_x = min(90, st.session_state.player_x + 10)
                        st.session_state.pixel_score += 1
                
                # Score rewards
                if st.session_state.pixel_score > 0 and st.session_state.pixel_score % 50 == 0:
                    st.session_state.coins += 5
                    st.success("Movement milestone reached! +5 coins! 🪙")
            
            elif st.session_state.current_game == "Pet Simulator":
                st.title(f"🐾 Pet Simulator")
                
                # Initialize pet state
                if 'pets' not in st.session_state:
                    st.session_state.pets = []
                if 'pet_names' not in st.session_state:
                    st.session_state.pet_names = {}
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if st.session_state.pets:
                        st.markdown("### Your Pets")
                        for pet in st.session_state.pets:
                            pet_name = st.session_state.pet_names.get(pet, pet)
                            st.markdown(
                                f"""
                                <div style='background: rgba(30, 42, 69, 0.8); padding: 20px; border-radius: 10px; margin: 10px 0;'>
                                    <h3>{pet_name}</h3>
                                    <div style='display: flex; gap: 20px;'>
                                        <div>Happiness: 70%</div>
                                        <div>Energy: 80%</div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"Play with {pet_name}", key=f"play_{pet}"):
                                    st.success(f"{pet_name} is happy! 🎉")
                            with col2:
                                if st.button(f"Feed {pet_name}", key=f"feed_{pet}"):
                                    if st.session_state.coins >= 5:
                                        st.session_state.coins -= 5
                                        st.success(f"{pet_name} is full! 🍖")
                                    else:
                                        st.error("Not enough coins!")
                    else:
                        st.info("You don't have any pets yet! Adopt one from the store.")
                
                with col2:
                    st.markdown("### 🏪 Pet Store")
                    pets = ["🐶 Puppy", "🐱 Kitten", "🐰 Bunny", "🐹 Hamster"]
                    for pet in pets:
                        if st.button(f"Adopt {pet} (50 coins)"):
                            if st.session_state.coins >= 50:
                                st.session_state.pets.append(pet)
                                st.session_state.coins -= 50
                                st.success(f"You adopted a {pet}!")
                                st.balloons()
                            else:
                                st.error("Not enough coins!")
                
                # Add earning mechanics
                if st.session_state.pets:
                    for pet in st.session_state.pets:
                        if random.random() < 0.1:  # 10% chance per pet
                            st.session_state.coins += 1
                            st.success(f"{pet} found a coin! 🪙")

if __name__ == "__main__":
    main()
