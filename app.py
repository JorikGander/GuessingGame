import streamlit as st

# Title of the app
st.title("Simple Interactive Streamlit App")

# Input for the user's name
name = st.text_input("What's your name?", "")

# Input for a number
number = st.slider("Choose a number", 1, 100, 1)

# Display a dynamic message
if name:
    st.write(f"Hello, {name}! You chose the number {number}.")
else:
    st.write("Please enter your name above to see a personalized message!")

# Add a fun fact about the chosen number
st.write(f"Fun Fact: {number} squared is {number**2}.")

