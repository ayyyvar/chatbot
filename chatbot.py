from flask import Flask, render_template, request, jsonify
import openai
import requests
from dotenv import load_dotenv
import os

print("Starting chatbot...")
app = Flask(__name__)

load_dotenv()

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
openai.api_key = OPENAI_API_KEY


def get_movie_info(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data['Response'] == 'True':
        movie_info = {
            'Title': data['Title'],
            'Year': data['Year'],
            'Genre': data['Genre'],
            'Director': data['Director'],
            'Plot': data['Plot'],
            'imdbRating': data['imdbRating'],
        }
        return movie_info
    else:
        return None

# Function to interact with the chatbot using OpenAI's new API interface
def chat_with_bot(user_input):
    # Check if the user input is related to a movie
    if "movie" in user_input.lower():
        movie_title = user_input.replace("movie", "").strip()
        movie_info = get_movie_info(movie_title)
        if movie_info:
            return f"Here's the info about '{movie_info['Title']}':\n" \
                   f"Year: {movie_info['Year']}\n" \
                   f"Genre: {movie_info['Genre']}\n" \
                   f"Director: {movie_info['Director']}\n" \
                   f"Plot: {movie_info['Plot']}\n" \
                   f"IMDb Rating: {movie_info['imdbRating']}"
        else:
            return "Sorry, I couldn't find any movie with that title."
    else:
        # If not movie-related, use the new OpenAI API interface for general queries
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

@app.route('/')
def home():
    return render_template('index.html')  # Render a simple HTML page for the user to interact with

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    response = chat_with_bot(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)