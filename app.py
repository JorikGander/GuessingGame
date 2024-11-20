import streamlit as st
import random
import pandas as pd

# Initialize session state variables for stats and game logic
if "games_played" not in st.session_state:
    st.session_state.games_played = 0
if "guesses_per_game" not in st.session_state:
    st.session_state.guesses_per_game = []
if "current_game_guesses" not in st.session_state:
    st.session_state.current_game_guesses = 0
if "target_number" not in st.session_state:
    st.session_state.target_number = random.randint(1, 100)

# Function to reset game state
def reset_game():
    st.session_state.games_played += 1
    st.session_state.guesses_per_game.append(st.session_state.current_game_guesses)
    st.session_state.current_game_guesses = 0
    st.session_state.target_number = random.randint(1, 100)

# Sidebar navigation
page = st.sidebar.selectbox("Select a page:", ["Play", "Stats"])

# "Play" Page
if page == "Play":
    st.title("Number Guessing Game")
    st.write("Guess a number between 1 and 100. I'll give you hints!")

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
                    response = "Too low! Try again."
                elif user_guess > st.session_state.target_number:
                    response = "Too high! Try again."
                else:
                    response = "Congratulations! You've guessed the number!"
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
    total_games = st.session_state.games_played
    avg_guesses = (
        sum(st.session_state.guesses_per_game) / total_games
        if total_games > 0
        else 0
    )
    st.metric("Games Played", total_games)
    st.metric("Average Guesses per Game", round(avg_guesses, 2))

    # Bar chart for guesses per game
    if total_games > 0:
        df = pd.DataFrame({
            "Game": [f"Game {i+1}" for i in range(total_games)],
            "Guesses": st.session_state.guesses_per_game
        })
        st.bar_chart(df.set_index("Game"))
    else:
        st.write("No games played yet. Play some games to see statistics!")


