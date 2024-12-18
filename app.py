import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests  # To send messages to Telegram Bot

# Flask application setup
app = Flask(__name__)
CORS(app)

# Configure Google Gemini API with your API key
genai.configure(api_key='AIzaSyC_loy9d-_YrIfJ8iXKGlDNrkqer0J5KE0')
# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = "7896293914:AAGraNrnEcWs95PFHbJk0IwLhbB8ytqZxJw"
TELEGRAM_CHAT_ID = "1104299436"

# Model configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# Define safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize the Generative Model
model = genai.GenerativeModel("gemini-1.5-flash")

# Conversation history store
conversation_history = []

def send_telegram_alert(message):
    """Sends an alert message to the Telegram bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send alert to Telegram: {response.text}")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

@app.route("/", methods=["GET"])
def index():
    """Renders the main chat interface."""
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handles user chat messages and generates responses."""
    user_input = request.json.get("message")
    
    if not user_input:
        return jsonify({"error": "No message provided!"}), 400
    
    try:
        # Start a chat session with conversation history
        chat = model.start_chat(history=conversation_history)
        
        # Generate a response from the model
        response = chat.send_message(user_input)
        
        # Update conversation history
        conversation_history.append({"role": "user", "parts": [user_input]})
        conversation_history.append({"role": "model", "parts": [response.text]})
        
        # Limit conversation history to the last 10 exchanges
        if len(conversation_history) > 10:
            conversation_history.pop(0)
        
        # Send alert to Telegram
        alert_message = f"New User Message: {user_input}\nBot Response: {response.text}"
        send_telegram_alert(alert_message)
        
        return jsonify({"response": response.text})
    
    except Exception as e:
        print(f"Google Gemini API Error: {e}")
        return jsonify({"error": "Sorry, there was an error processing your request."}), 500

if __name__ == "__main__":
    print("Flask server starting...")
    app.run(debug=True, port=5000)