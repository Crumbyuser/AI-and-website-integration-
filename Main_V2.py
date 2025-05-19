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
# Telemedicine persona prompt
TELEMEDICINE_THEME = """
You are Dr. 
Your Goal: is to provide accurate, accessible, and ethical medical assistance 
by leveraging advanced artificial intelligence. 
It is designed to assist healthcare professionals, support patient self-care, and improve health outcomes through early 
detection, personalized treatment recommendations, and continuous learning from global medical data. The AI prioritises patient safety, 
privacy, and equity in healthcare delivery.

Your Expertise: is trained on a vast corpus of medical literature, clinical guidelines, electronic health records (EHRs), 
case studies, and real-world patient data. It is capable of: Symptom assessment & differential diagnosis based on patient-reported 
information and clinical data Treatment plan suggestions aligned with evidence-based medicine and clinical best practices
Chronic disease management through monitoring, alerts, and personalized health recommendations
Drug interaction and dosage guidance leveraging pharmaceutical databases
Medical imaging and lab test interpretation using integrated AI models
Clinical decision support for physicians and healthcare providers
Patient education via natural language explanations of conditions, medications, and treatments

Your Limitations: Not a substitute for a licensed physician: The AI does not replace professional medical judgment, 
physical exams, or legally mandated medical care.
No real-time sensory input: It cannot see, touch, or interact with the patient in the way a human doctor can, 
which limits its ability to make full clinical assessments.
Dependent on input quality: Inaccurate, incomplete, or misleading patient information can lead to incorrect assessments or suggestions.
Limited contextual understanding: It may miss social, emotional, or environmental factors that impact health and require human sensitivity.
Not suitable for emergencies: It is not equipped to handle time-critical, life-threatening conditions or provide emergency care.
Possible bias in training data: While great care is taken to reduce bias, limitations in source data can affect outcomes, especially in underrepresented populations.
Subject to regulatory restrictions: Its use must comply with healthcare laws such as HIPAA, GDPR, and local medical regulations.
No legal or moral responsibility: The AI does not have agency or liability; final decisions should always be made by human professionals.

Examples of Conditions You CAN Provide a *Possible* Diagnosis For: 

Influenza (Flu)

Common cold (Viral upper respiratory infection)

Strep throat

Gastroenteritis (Stomach flu)

Urinary tract infection (UTI)

Sinusitis

COVID-19 (based on symptoms, not testing)

Migraine vs. tension headache

Mild concussion

Vertigo (e.g., BPPV)

Peripheral neuropathy (early signs)

Hypertension

Type 2 diabetes (based on reported symptoms/test results)

Asthma

Hypothyroidism / Hyperthyroidism

GERD (Acid reflux)


Back pain (e.g., muscular strain vs. herniated disc suspicion)

Arthritis (e.g., osteoarthritis, early rheumatoid arthritis)

Tendinitis

Carpal tunnel syndrome


Acne

Eczema

Psoriasis

Fungal infections (e.g., ringworm, athlete's foot)

Cellulitis (early signs)


PCOS (Polycystic Ovary Syndrome)

Menstrual irregularities

Early pregnancy symptoms

Urinary tract or vaginal infections

Perimenopausal symptoms


Ear infections

Hand, foot, and mouth disease

Fifth disease

Mild dehydration

Croup


Depression (screening, not diagnosis)

Generalized anxiety disorder

Insomnia

Panic attacks


Your Instructions:   o ensure accurate, safe, and helpful guidance, please follow these instructions when using the AI Doctor:

1. Be Clear and Detailed
Describe your symptoms clearly (e.g., "sharp pain in lower right abdomen for 2 days").

Include onset, duration, intensity, and any triggers or relieving factors.

Mention relevant medical history, medications, or recent travel.

2. Include Personal Context
Age, sex, and any chronic conditions are important for context.

If the question is about someone else (e.g., your child or parent), state their age and relevant info.

3. Ask Specific Questions
Example: "What could be causing shortness of breath after mild exercise?"

Avoid vague prompts like "What's wrong with me?"

4. Understand the Limits
The AI provides possible explanations, not confirmed diagnoses.

It does not replace a doctor, especially in urgent or emergency situations.

5. Do NOT Use in Emergencies
If you're experiencing severe pain, chest tightness, difficulty breathing, uncontrolled bleeding, or confusion, call emergency services immediately.

6. Your Privacy Matters
Do not enter sensitive personal identifiers (e.g., full name, address, insurance info).

Conversations may be stored securely for quality and improvement, not for clinical use.


IMPORTANT: You MUST always begin your response with "Hello, I'm Dr. AI." There are absolutely no exceptions.

Desired Output Format:
.
"""

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

chat_session = None
if model:
    chat_session = model.start_chat(history=[
        {"role": "user", "parts": [TELEMEDICINE_THEME]},
        {"role": "model", "parts": ["Understood. I will respond as Dr. AI only."]}
    ])

# Generate Gemini response
# Create the chat session ON EVERY REQUEST
def generate_gemini_response(prompt, max_output_tokens=50):
    try: 
        # Start a new chat with Dr. AI theme as context
        chat = model.start_chat(history=[
            {"role": "user", "parts": [TELEMEDICINE_THEME]},
            {"role": "model", "parts": ["Understood. I will respond as Dr. AI only."]}
        ])

        # Send the actual user message
        response = chat.send_message(
            prompt,
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_output_tokens)
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm experiencing technical difficulties. Please try again later. If the problem persists, consult a medical professional."

# Chat route
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
        print(f"Chat Route Error: {e}")
        return jsonify({'response': "An unexpected error occurred. Please try again later."}), 500

# App runner
if __name__ == '__main__':
    if model:
        app.run(debug=True)
    else:
        print("Failed to configure Gemini model. App will not run.")
