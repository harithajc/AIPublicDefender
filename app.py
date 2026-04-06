import os
from flask import Flask, request, jsonify, render_template
from google import genai
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route('/')
def signin():
    return render_template('signin.html')

@app.route('/app')
def home():
    return render_template('index.html')

@app.route('/roadmap')
def roadmap():
    return render_template('roadmap.html')

@app.route('/signin')
def signin_alias():
    return render_template('signin.html')

@app.route('/api/analyze-case', methods=['POST'])
def analyze_case():
    data = request.json
    situation_type = data.get('situation', 'General Legal Inquiry')
    jurisdiction = data.get('jurisdiction', 'India')
    user_context = data.get('context', 'No specific details provided.')
    language = data.get('language', 'English')

    # Language-specific headings and instructions
    headings = {
        'English': {
            'disclaimer': '### ⚠️ Disclaimer',
            'rights': '### ⚖️ Your Rights & What Authorities Can Do',
            'procedure': '### 🗺️ Step-by-Step Procedure',
            'documents': '### 📄 Required Documents',
            'mistakes': '### 🚫 Common Mistakes to Avoid',
            'resources': '### 🔗 Official Government Resources'
        },
        'Kannada': {
            'disclaimer': '### ⚠️ ಎಚ್ಚರಿಕೆ',
            'rights': '### ⚖️ ನಿಮ್ಮ ಹಕ್ಕುಗಳು ಮತ್ತು ಅಧಿಕಾರಿಗಳು ಏನು ಮಾಡಬಹುದು',
            'procedure': '### 🗺️ ಹಂತ-ಹಂತದ ಪ್ರಕ್ರಿಯೆ',
            'documents': '### 📄 ಅಗತ್ಯ ದಾಖಲೆಗಳು',
            'mistakes': '### 🚫 ಸಾಮಾನ್ಯ ತಪ್ಪುಗಳನ್ನು ತಪ್ಪಿಸಿ',
            'resources': '### 🔗 ಸರಕಾರಿ ಸಂಪನ್ಮೂಲಗಳು'
        },
        'Hindi': {
            'disclaimer': '### ⚠️ अस्वीकरण',
            'rights': '### ⚖️ आपके अधिकार और अधिकारी क्या कर सकते हैं',
            'procedure': '### 🗺️ चरण-दर-चरण प्रक्रिया',
            'documents': '### 📄 आवश्यक दस्तावेज़',
            'mistakes': '### 🚫 बचने के लिए सामान्य गलतियाँ',
            'resources': '### 🔗 आधिकारिक सरकारी संसाधन'
        },
        'Marathi': {
            'disclaimer': '### ⚠️ अस्वीकरण',
            'rights': '### ⚖️ तुमचे अधिकार आणि अधिकारी काय करू शकतात',
            'procedure': '### 🗺️ चरण-दर-चरण प्रक्रिया',
            'documents': '### 📄 आवश्यक कागदपत्रे',
            'mistakes': '### 🚫 टाळण्यासाठी सामान्य त्रुटी',
            'resources': '### 🔗 अधिकृत सरकारी संसाधने'
        }
    }

    # Get language-specific headings, default to English
    lang_headings = headings.get(language, headings['English'])

    prompt = f"""
    You are an AI Legal Assistant for Indian Law. The user is in: {jurisdiction}.
    The user is facing this situation: {situation_type}.
    Additional context from user: {user_context}
    
    IMPORTANT RULES:
    - You MUST respond ENTIRELY in this language: {language}.
    - You must use simple, accessible language. Do not use heavy legal jargon.
    
    Format your response EXACTLY using these sections with the EXACT headings below:
    
    {lang_headings['disclaimer']}
    Explicitly state that you are an AI, not a lawyer, and this is informational only.

    {lang_headings['rights']}
    Briefly explain what the authorities (police, courts, etc.) can and cannot do.

    {lang_headings['procedure']}
    Break down the exact next steps into a clear flow (Step 1 -> Step 2 -> Step 3).

    {lang_headings['documents']}
    List the specific documents the user needs to gather.

    {lang_headings['mistakes']}
    List 2-3 common pitfalls people make in this situation.
    
    {lang_headings['resources']}
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