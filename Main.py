from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import os

GOOGLE_API_KEY=""
print("running")

if GOOGLE_API_KEY:
    print("API key loaded successfully")
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("API Key not found plaese ensure it's set hardcoded (FOR TESTING ONLY).")





app = Flask(__name__)

model = genai.GenerativeModel('gemini-1.5-flash-001')


TELEMEDICINE_THEME = """You are a helpful chatbot doctor for a telemedicine website.
Answer questions related to virtual healthcare, remote monitoring, online consultations,
and any other telemedicine-related topics. Keep responses concise and easy to understand. 
You always refer to yourself as Chat Bot Doctor."""


def generate_gemini_response(prompt, theme=TELEMEDICINE_THEME, max_output_tokens=100): # Increased token limit slightly
 
    try:
      
        full_prompt = theme + "\nUser: " + prompt + "\nChatbot:"

   
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_output_tokens
            )
        )
        return response.text

    except Exception as e:
        print(f"Error during Gemini API call: {e}") # More specific error logging
        return f"Error generating response: {str(e)}.  Check your API key and internet connection."

@app.route('/chat', methods=['POST'])
def chat():

    try:
        data = request.get_json()
        user_input = data.get('message')

        if not user_input:
            return jsonify({'response': "Please provide a message."}), 400

  
        chatbot_response = generate_gemini_response(user_input)

        return jsonify({'response': chatbot_response})

    except Exception as e:
        print(f"Error in /chat route: {e}") #More specific error logging
        return jsonify({'response': f"An error occurred: {str(e)}"}), 500

@app.route('/')
def index():
    welcome_message = generate_gemini_response("Introduce yourself and offer assistance.", theme=TELEMEDICINE_THEME)
    return render_template('index.html', welcome_message=welcome_message)

if __name__ == '__main__':
    app.run(debug=True) # Enable debug mode for development
