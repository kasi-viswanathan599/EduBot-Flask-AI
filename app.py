from flask import Flask, render_template, request, session, redirect, url_for
import google.generativeai as genai
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret in production

# Load environment variables from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Server-side flag to reset session on server restart
server_started = False

# Chatbot logic
def get_gemini_response(user_input):
    prompt = f"""You are EduBot, a helpful assistant that answers questions about schools and 
    colleges in Tamil Nadu. Provide clear, concise info on institutions, rankings, courses, and 
    admission details. If unsure, politely ask for clarification or suggest where users can find more.

User: {user_input}
Chatbot:"""
    chat = model.start_chat(history=[])
    response = chat.send_message(prompt)
    return response.text

# Home page and chat logic
@app.route("/", methods=["GET", "POST"])
def index():
    global server_started

    # Clear chat session on first run after server restart
    if not server_started:
        session.clear()
        server_started = True

    # Initialize session chat history
    if "chat_history" not in session:
        session["chat_history"] = []

    # Handle user input
    if request.method == "POST":
        user_input = request.form["user_input"]
        if user_input.strip():
            bot_response = get_gemini_response(user_input)
            session["chat_history"].append(("user", user_input))
            session["chat_history"].append(("bot", bot_response))
            session.modified = True  # Ensure session updates are saved
        return redirect(url_for("index"))

    return render_template("index.html", chat_history=session["chat_history"])

if __name__ == "__main__":
    app.run(debug=True)
