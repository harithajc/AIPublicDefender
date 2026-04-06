import os
from flask import Flask, request, jsonify, render_template
from google import genai
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/roadmap')
def roadmap():
    return render_template('roadmap.html')

@app.route('/api/analyze-case', methods=['POST'])
def analyze_case():
    data = request.json
    situation_type = data.get('situation', 'General Legal Inquiry')
    jurisdiction = data.get('jurisdiction', 'India')
    user_context = data.get('context', 'No specific details provided.')
    language = data.get('language', 'English') 

    prompt = f"""
    You are an AI Legal Assistant for Indian Law. The user is in: {jurisdiction}.
    The user is facing this situation: {situation_type}.
    Additional context from user: {user_context}
    
    IMPORTANT RULES:
    - You MUST respond ENTIRELY in this language: {language}.
    - You must use simple, accessible language. Do not use heavy legal jargon.
    
    Format your response EXACTLY using these sections:
    
    ### ⚠️ Disclaimer
    Explicitly state that you are an AI, not a lawyer, and this is informational only.

    ### ⚖️ Your Rights & What Authorities Can Do
    Briefly explain what the authorities (police, courts, etc.) can and cannot do.

    ### 🗺️ Step-by-Step Procedure
    Break down the exact next steps into a clear flow (Step 1 -> Step 2 -> Step 3).

    ### 📄 Required Documents
    List the specific documents the user needs to gather.

    ### 🚫 Common Mistakes to Avoid
    List 2-3 common pitfalls people make in this situation.
    
    ### 🔗 Official Government Resources
    Provide 1-2 relevant official Indian government website links or portals (e.g., e-Daakhil, state police portal, e-Courts).
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
        )
        return jsonify({"status": "success", "ai_response": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)