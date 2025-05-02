import streamlit as st
import random
import time

# Page config and title
st.set_page_config(page_title="Dice Roller 🎲", page_icon="🎲")
st.markdown("<h1 style='text-align: center;'>🎲 Dice Roller</h1>", unsafe_allow_html=True)

# CSS for the dice animation and button effects
st.markdown("""
<style>
/* Dice Styles */
.dice {
    width: 100px;
    height: 100px;
    position: relative;
    transform-style: preserve-3d;
    animation: rolling 3s linear;
}

@keyframes rolling {
    0% { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg); }
    30% { transform: rotateX(360deg) rotateY(720deg) rotateZ(360deg); }
    60% { transform: rotateX(720deg) rotateY(1080deg) rotateZ(720deg); }
    100% { transform: rotateX(1080deg) rotateY(1440deg) rotateZ(1080deg); }
}

.dice-face {
    position: absolute;
    width: 100px;
    height: 100px;
    border: 2px solid #e0e0e0;
    background: white;
    display: grid;
    grid-template-areas: 
        "a . c"
        "e g f"
        "d . b";
    border-radius: 10px;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.1);
}

.dot {
    width: 15px;
    height: 15px;
    background: black;
    border-radius: 50%;
    align-self: center;
    justify-self: center;
}

/* Button Styles */
.stButton > button {
    width: 200px;
    position: relative;
    background: linear-gradient(45deg, #2937f0, #9f1ae2) !important;
    color: white !important;
    border: none !important;
    padding: 15px 25px !important;
    border-radius: 25px !important;
    font-size: 18px !important;
    font-weight: bold !important;
    cursor: pointer;
    overflow: hidden;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.stButton > button::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 5px;
    height: 5px;
    background: rgba(255,255,255,.5);
    opacity: 0;
    border-radius: 100%;
    transform: scale(1, 1) translate(-50%);
    transform-origin: 50% 50%;
}

.stButton > button:hover::after {
    animation: ripple 1s ease-out;
}

@keyframes ripple {
    0% {
        transform: scale(0, 0);
        opacity: 0.5;
    }
    100% {
        transform: scale(100, 100);
        opacity: 0;
    }
}

/* Result Styles */
.dice-result {
    text-align: center;
    font-size: 24px;
    margin-top: 20px;
    padding: 10px;
    border-radius: 10px;
    background: rgba(255,255,255,0.1);
    animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Dot positions for each face */
.front { transform: translateZ(50px); }
.back { transform: translateZ(-50px) rotateY(180deg); }
.right { transform: translateX(50px) rotateY(90deg); }
.left { transform: translateX(-50px) rotateY(-90deg); }
.top { transform: translateY(-50px) rotateX(90deg); }
.bottom { transform: translateY(50px) rotateX(-90deg); }

/* Dot layouts */
.dot:nth-child(1) { grid-area: a; }
.dot:nth-child(2) { grid-area: b; }
.dot:nth-child(3) { grid-area: c; }
.dot:nth-child(4) { grid-area: d; }
.dot:nth-child(5) { grid-area: e; }
.dot:nth-child(6) { grid-area: f; }
.dot:nth-child(7) { grid-area: g; }

/* Hide all dots by default */
.dot { display: none; }

/* One dot */
.dice-face[data-value="1"] .dot:nth-child(7) { display: block; }

/* Two dots */
.dice-face[data-value="2"] .dot:nth-child(1),
.dice-face[data-value="2"] .dot:nth-child(2) { display: block; }

/* Three dots */
.dice-face[data-value="3"] .dot:nth-child(1),
.dice-face[data-value="3"] .dot:nth-child(7),
.dice-face[data-value="3"] .dot:nth-child(2) { display: block; }

/* Four dots */
.dice-face[data-value="4"] .dot:nth-child(1),
.dice-face[data-value="4"] .dot:nth-child(2),
.dice-face[data-value="4"] .dot:nth-child(3),
.dice-face[data-value="4"] .dot:nth-child(4) { display: block; }

/* Five dots */
.dice-face[data-value="5"] .dot:nth-child(1),
.dice-face[data-value="5"] .dot:nth-child(2),
.dice-face[data-value="5"] .dot:nth-child(3),
.dice-face[data-value="5"] .dot:nth-child(4),
.dice-face[data-value="5"] .dot:nth-child(7) { display: block; }

/* Six dots */
.dice-face[data-value="6"] .dot:nth-child(1),
.dice-face[data-value="6"] .dot:nth-child(2),
.dice-face[data-value="6"] .dot:nth-child(3),
.dice-face[data-value="6"] .dot:nth-child(4),
.dice-face[data-value="6"] .dot:nth-child(5),
.dice-face[data-value="6"] .dot:nth-child(6) { display: block; }
</style>
""", unsafe_allow_html=True)

if 'rolling' not in st.session_state:
    st.session_state.rolling = False
    st.session_state.dice_result = None

# Center the button with columns
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🎲 Roll the Dice! 🎮"):
        st.session_state.rolling = True
        st.session_state.dice_result = random.randint(1, 6)
    
if st.session_state.rolling:
    # Create the 3D dice with dots
    dice_html = f"""
    <div style="perspective: 1000px; margin: 50px;">
        <div class="dice">
            <div class="dice-face front" data-value="{st.session_state.dice_result}">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="dice-face back" data-value="{7 - st.session_state.dice_result}">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="dice-face right" data-value="{(st.session_state.dice_result % 3) + 2}">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="dice-face left" data-value="{(st.session_state.dice_result % 3) + 4}">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="dice-face top" data-value="{(st.session_state.dice_result % 2) + 3}">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="dice-face bottom" data-value="{(st.session_state.dice_result % 2) + 5}">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    </div>
    """
    st.markdown(dice_html, unsafe_allow_html=True)
    time.sleep(3)  # Wait for animation to complete
    
    # Show result with matching emoji
    dice_emojis = {
        1: "1️⃣",
        2: "2️⃣",
        3: "3️⃣",
        4: "4️⃣",
        5: "5️⃣",
        6: "6️⃣"
    }
    result_html = f"""
    <div class="dice-result">
        You rolled a {st.session_state.dice_result} {dice_emojis[st.session_state.dice_result]}
    </div>
    """
    st.markdown(result_html, unsafe_allow_html=True)
    st.session_state.rolling = False