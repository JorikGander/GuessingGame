import streamlit as st
import random
from openai import OpenAI
import pandas as pd
import plotly.express as px
import string
import os

# OpenAI API setup 
MODEL = "gpt-4o-mini"

# Function to get a random animal using OpenAI
def get_random_animal():
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    """
    Uses OpenAI to generate a random animal name.
    """
    prompt = "Generate a single random animal name, and output it as plain text. Choose an animal that is not completly unknown!"
    
    try:
        chat_completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        # Extract the animal name from the response
        random_animal = chat_completion.choices[0].message.content.strip().lower()
    except Exception as e:
        # Default to a predefined animal in case of API failure
        random_animal = "cat"
        st.error(f"Error generating random animal: {e}")

    return random_animal

# Initialize session state variables
if "target_animal" not in st.session_state:
    st.session_state.target_animal = get_random_animal()
if "games_played" not in st.session_state:
    st.session_state.games_played = 0
if "guesses_per_game" not in st.session_state:
    st.session_state.guesses_per_game = []
if "current_game_guesses" not in st.session_state:
    st.session_state.current_game_guesses = 0
if "guess_feedback" not in st.session_state:
    st.session_state.guess_feedback = {
        "Very Bad Guess": 0,
        "Bad Guess": 0,
        "Okay Guess": 0,
        "Good Guess": 0,
        "Very Good Guess": 0,
    }

# Function to interact with OpenAI
def evaluate_guess(target_animal, guess):
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    """
    Evaluates the user's guess against the target animal using GPT-4o-mini.
    Provides hints based on the number of guesses made so far.
    """
    num_guesses = st.session_state.current_game_guesses

    # Adjust hint difficulty based on the number of guesses
    if num_guesses < 5:
        hint_level = "only slightly helpful"
    elif 5 <= num_guesses <= 12:
        hint_level = "slightly helpful"
    else:
        hint_level = "helpful"

    question = (
        f"The user is playing a guessing game. The target animal is '{target_animal}', "
        f"and they guessed '{guess}'. The user has made {num_guesses} guesses so far. "
        f"Provide a {hint_level} hint based on the guess and the target animal. Do not be so revealing and only give one information, especially for only slightly helpful and slightly helpful hints. Do not make it too easy."
    )
    
    try:
        # Make the API call using the provided client style
        chat_completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": question},
            ],
        )
        # Extract the content from the response
        assistant_response = chat_completion.choices[0].message.content
    except Exception as e:
        # Handle exceptions gracefully
        assistant_response = f"Error: {e}"
    
    return assistant_response


# Function to reset the game
def reset_game():
    st.session_state.games_played += 1
    st.session_state.guesses_per_game.append(st.session_state.current_game_guesses)
    st.session_state.current_game_guesses = 0
    st.session_state.target_animal = get_random_animal()
    st.session_state.guess_log = []

# Sidebar navigation
page = st.sidebar.selectbox("Select a page:", ["Play", "Stats"])

def normalize_feedback(feedback):
    # Remove trailing punctuation and whitespace
    feedback = feedback.strip().rstrip(string.punctuation).strip()
    # Standardize casing to match dictionary keys
    feedback = feedback.title()
    return feedback


# Function to log guesses and evaluate the last guess
def evaluate_last_guess(target_animal, guess, guess_log):
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    """
    Sends the entire game log of guesses and hints to the LLM
    and evaluates the last guess with qualitative feedback.
    """
    if len(guess_log) <= 1:
        return "Not enough hints yet to evaluate this guess."
    
    # Prepare the log as text
    log_text = "\n".join(
        [f"Guess {i+1}: {entry['guess']} | Hint: {entry['hint']}" for i, entry in enumerate(guess_log)]
    )

    # Construct the prompt
    prompt = (
        f"The user is playing an animal guessing game."
        f"Below is the log of the guesses and hints provided during the game:\n\n{log_text}\n\n"
        f"The user's last guess is '{guess}'. Provide feedback on the last guess as one of the following: "
        f"'Very bad guess', 'Bad guess', 'Okay guess', 'Good guess', 'Very good guess'. Base your evaluation on wether it was plausible to guess this animal based on the hints before. Provide only the feedback."
    )
    
    try:
        # Make the API call
        chat_completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        # Extract the LLM's feedback
        feedback = chat_completion.choices[0].message.content.strip()

        # Normalize the feedback
        feedback = normalize_feedback(feedback)

        # Validate and update feedback stats
        if feedback in st.session_state.guess_feedback:
            st.session_state.guess_feedback[feedback] += 1
  
    except Exception as e:
        # Handle exceptions gracefully
        feedback = f"Error: {e}"
    
    return feedback


# Initialize a log for guesses and hints
if "guess_log" not in st.session_state:
    st.session_state.guess_log = []

# "Play" Page
if page == "Play":
    st.title("Animal Guessing Game with AI")
    st.write("Guess the animal I'm thinking of!")

    # Chat component for guessing
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("Enter your guess here:")
    if user_input:
        user_guess = user_input.lower().strip()
        st.session_state.current_game_guesses += 1

        if user_guess == st.session_state.target_animal:
            response = f"🎉 Yes! You've guessed it right: {st.session_state.target_animal.capitalize()}!"
            reset_game()
            # Reset the guess log after the game ends
            st.session_state.guess_log = []
        else:
            ai_response = evaluate_guess(st.session_state.target_animal, user_guess)
            response = f"No. {ai_response}"

            # Log the guess and hint
            st.session_state.guess_log.append({"guess": user_guess, "hint": ai_response})

            # Evaluate the last guess
            feedback = evaluate_last_guess(st.session_state.target_animal, user_guess, st.session_state.guess_log)
            response += f"\n\nFeedback on your last guess: {feedback}"

        # Append the conversation to the chat history
        st.session_state.chat_history.append({"user": user_input, "response": response})

    # Display chat history
    for entry in st.session_state.chat_history:
        st.chat_message("user").write(entry["user"])
        st.chat_message("assistant").write(entry["response"])

#Stats page
elif page == "Stats":
    st.title("Game Statistics")

    # Display total games played and average guesses per game
    session_avg_guesses = (
        sum(st.session_state.guesses_per_game) / st.session_state.games_played
        if st.session_state.games_played > 0
        else 0
    )

    st.metric("Games Played (This Session)", st.session_state.games_played)
    st.metric("Average Guesses (This Session)", round(session_avg_guesses, 2))

    # Plot session stats with Plotly
    st.subheader("Session Stats")
    if st.session_state.games_played > 0:
        session_counts = pd.Series(st.session_state.guesses_per_game).value_counts().sort_index()
        session_data = pd.DataFrame({
            "Guesses": session_counts.index,
            "Number of Games": session_counts.values
        })

        # Create a bar chart using Plotly
        fig = px.bar(
            session_data,
            x="Guesses",
            y="Number of Games",
            title="Guesses Per Game",
            labels={"Guesses": "Number of Guesses", "Number of Games": "Games Played"},
        )

        # Show the chart
        st.plotly_chart(fig)
    else:
        st.write("No games played yet this session. Play some games to see statistics!")

       # Feedback stats
    st.subheader("Guess Quality Distribution")

    # Calculate total guesses
    total_guesses = sum(st.session_state.guess_feedback.values())

    # Create a dataframe for feedback stats with percentages
    feedback_data = pd.DataFrame({
        "Feedback": list(st.session_state.guess_feedback.keys()),
        "Count": list(st.session_state.guess_feedback.values()),
    })

    # Add percentage column
    feedback_data["Percentage"] = (
        (feedback_data["Count"] / total_guesses * 100).fillna(0).round(2)
        if total_guesses > 0
        else 0
    )

    # Plot feedback stats using Plotly
    fig = px.bar(
        feedback_data,
        x="Feedback",
        y="Count",
        title="Guess Quality Distribution",
        labels={"Feedback": "Feedback Type", "Count": "Number of Guesses"},
    )
    st.plotly_chart(fig)

    # Show detailed stats including percentages
    st.dataframe(feedback_data.set_index("Feedback"))
