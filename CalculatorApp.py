import streamlit as st

# Initialize session state for calculator display
if 'display' not in st.session_state:
    st.session_state.display = "0"

st.title("🖩 Calculator App")

# Display box
st.text_input("", value=st.session_state.display, key="calc_display", disabled=True)

# Update function for buttons
def update_display(value):
    if value == 'C':
        st.session_state.display = "0"
    else:
        if st.session_state.display == "0":
            st.session_state.display = str(value)
        else:
            st.session_state.display += str(value)
    st.rerun()

# Create a 4x4 grid layout for the calculator
col1, col2, col3, col4 = st.columns([1,1,1,15])

# Row 1
with col1:
    if st.button("7"):
        update_display(7)
with col2:
    if st.button("8"):
        update_display(8)
with col3:
    if st.button("9"):
        update_display(9)
with col4:
    if st.button(":material/close:"):  # Times symbol
        update_display("*")

# Row 2
col5, col6, col7, col8 = st.columns([1,1,1,15])
with col5:
    if st.button("4"):
        update_display(4)
with col6:
    if st.button("5"):
        update_display(5)
with col7:
    if st.button("6"):
        update_display(6)
with col8:
    if st.button("\u00F7"):  # Division symbol
        update_display("/")

# Row 3
col9, col10, col11, col12 = st.columns([1,1,1,15])
with col9:
    if st.button("1"):
        update_display(1)
with col10:
    if st.button("2"):
        update_display(2)
with col11:
    if st.button("3"):
        update_display(3)
with col12:
    if st.button(":material/remove:"):  # Minus symbol
        update_display("-")

# Row 4
col13, col14, col15, col16 = st.columns([1,1,1,15])
with col13:
    if st.button("0"):
        update_display(0)
with col14:
    if st.button("C", type='primary'):
        update_display('C')
with col15:
    if st.button("=", type='primary'):
        try:
            st.session_state.display = str(eval(st.session_state.display))
        except:
            st.session_state.display = "Error"
        st.rerun()
with col16:
    if st.button(":material/add:"):  # Plus symbol
        update_display("+")

