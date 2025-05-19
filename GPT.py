from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI
import os

OPEN_AI_API_KEY="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"
print("running")

if OPEN_AI_API_KEY:
    print("API key loaded successfully")
    client = OpenAI(api_key=OPEN_AI_API_KEY)
else:
    print("API Key not found plaese ensure it's set hardcoded (FOR TESTING ONLY).")

app = Flask(__name__)




TELEMEDICINE_THEME = """You are a helpful chatbot doctor for a telemedicine website.
Answer questions related to virtual healthcare, remote monitoring, online consultations,
and any other telemedicine-related topics. Keep responses concise and easy to understand. 
You always refer to yourself as Chat Bot Doctor."""



def generate_openai_response(user_input, theme=TELEMEDICINE_THEME):
    try:
        messages = [
            {"role": "system", "content": theme},
            {"role": "user", "content": user_input}
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI Error:", e)
        return "Error generating response. Please try again later."

 
    try:
      
        full_prompt = theme + "\nUser: " + prompt + "\nChatbot:"

   
        response = model.generate_content(
            full_prompt,
            generation_config=OpenAI.types.GenerationConfig(
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

  
        chatbot_response = generate_openai_response(user_input)

        return jsonify({'response': chatbot_response})

    except Exception as e:
        print(f"Error in /chat route: {e}") #More specific error logging
        return jsonify({'response': f"An error occurred: {str(e)}"}), 500

@app.route('/')
def index():
    welcome_message = generate_openai_response("Introduce yourself and offer assistance.", theme=TELEMEDICINE_THEME)
    return render_template('index.html', welcome_message=welcome_message)

if __name__ == '__main__':
    app.run(debug=True) # Enable debug mode for development