import streamlit as st
import random
import pandas as pd
import json
import os

# JSON File for persistent storage
STATS_FILE = "global_stats.json"

# Function to load global stats from a JSON file
def load_global_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    else:
        return {"games_played": 0, "guesses_per_game": []}

# Function to save global stats to a JSON file
def save_global_stats(global_stats):
    with open(STATS_FILE, "w") as f:
        json.dump(global_stats, f)

# Load global stats
global_stats = load_global_stats()

# Initialize session state variables
if "games_played" not in st.session_state:
    st.session_state.games_played = 0
if "guesses_per_game" not in st.session_state:
    st.session_state.guesses_per_game = []
if "current_game_guesses" not in st.session_state:
    st.session_state.current_game_guesses = 0
if "target_number" not in st.session_state:
    st.session_state.target_number = random.randint(1, 100)
if "low_limit" not in st.session_state:
    st.session_state.low_limit = 1
if "high_limit" not in st.session_state:
    st.session_state.high_limit = 100

# Function to reset game state
def reset_game():
    st.session_state.games_played += 1
    st.session_state.guesses_per_game.append(st.session_state.current_game_guesses)
    
    # Update global stats
    global_stats["games_played"] += 1
    global_stats["guesses_per_game"].append(st.session_state.current_game_guesses)
    save_global_stats(global_stats)

    st.session_state.current_game_guesses = 0
    st.session_state.target_number = random.randint(1, 100)
    st.session_state.low_limit = 1
    st.session_state.high_limit = 100

# Sidebar navigation
page = st.sidebar.selectbox("Select a page:", ["Play", "Stats"])

# "Play" Page
if page == "Play":
    st.title("Number Guessing Game")
    st.write("Guess a number between 1 and 100. I'll help you narrow it down!")

    # Chat component for guessing
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("Enter your guess here:")
    if user_input:
        try:
            user_guess = int(user_input)
            if user_guess < 1 or user_guess > 100:
                response = "Your guess is out of range! Please guess a number between 1 and 100."
            else:
                st.session_state.current_game_guesses += 1
                if user_guess < st.session_state.target_number:
                    # Update the lower bound for hints
                    st.session_state.low_limit = max(st.session_state.low_limit, user_guess + 1)
                    response = f"Too low! Try guessing between {st.session_state.low_limit} and {st.session_state.high_limit}."
                elif user_guess > st.session_state.target_number:
                    # Update the upper bound for hints
                    st.session_state.high_limit = min(st.session_state.high_limit, user_guess - 1)
                    response = f"Too high! Try guessing between {st.session_state.low_limit} and {st.session_state.high_limit}."
                else:
                    response = "🎉 Congratulations! You've guessed the number!"
                    reset_game()
        except ValueError:
            response = "Invalid input. Please enter a valid number."

        # Append the conversation to the chat history
        st.session_state.chat_history.append({"user": user_input, "response": response})

    # Display chat history
    for entry in st.session_state.chat_history:
        st.chat_message("user").write(entry["user"])
        st.chat_message("assistant").write(entry["response"])

# "Stats" Page
elif page == "Stats":
    st.title("Game Statistics")
    
    # Display total games played and average guesses per game
    session_avg_guesses = (
        sum(st.session_state.guesses_per_game) / st.session_state.games_played
        if st.session_state.games_played > 0
        else 0
    )
    global_avg_guesses = (
        sum(global_stats["guesses_per_game"]) / global_stats["games_played"]
        if global_stats["games_played"] > 0
        else 0
    )

    st.metric("Games Played (This Session)", st.session_state.games_played)
    st.metric("Average Guesses (This Session)", round(session_avg_guesses, 2))
    st.metric("Games Played (Global)", global_stats["games_played"])
    st.metric("Average Guesses (Global)", round(global_avg_guesses, 2))

    # Bar chart for session stats
    st.subheader("Session Stats")
    if st.session_state.games_played > 0:
        session_counts = pd.Series(st.session_state.guesses_per_game).value_counts().sort_index()
        session_data = pd.DataFrame({
            "Guesses": session_counts.index,
            "Number of Games": session_counts.values
        })
        st.bar_chart(session_data.set_index("Guesses"))
    else:
        st.write("No games played yet this session. Play some games to see statistics!")

    # Bar chart for global stats
    st.subheader("Global Stats")
    if global_stats["games_played"] > 0:
        global_counts = pd.Series(global_stats["guesses_per_game"]).value_counts().sort_index()
        global_data = pd.DataFrame({
            "Guesses": global_counts.index,
            "Number of Games": global_counts.values
        })
        st.bar_chart(global_data.set_index("Guesses"))
    else:
        st.write("No global stats available yet. Play some games to start tracking!")


