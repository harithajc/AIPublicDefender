import os
import tempfile
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
    cybercrime_portal = 'https://cybercrime.gov.in'

    # Detect cybercrime-related requests from selected situation and free-text context.
    detection_text = f"{situation_type} {user_context}".lower()
    cybercrime_keywords = [
        'cyber', 'online fraud', 'upi fraud', 'phishing', 'scam', 'hacked',
        'otp', 'financial fraud', 'identity theft', 'social media hack', 'ransomware'
    ]
    is_cybercrime_issue = any(keyword in detection_text for keyword in cybercrime_keywords)

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

    cybercrime_instruction = ""
    if is_cybercrime_issue:
        cybercrime_instruction = f"""
    MANDATORY CYBERCRIME RULE:
    - Since this appears to be a cybercrime issue, you MUST include this exact clickable Markdown link in your response:
      [National Cyber Crime Reporting Portal]({cybercrime_portal})
    - Do not replace it with generic wording like 'file a complaint online'.
"""

    prompt = f"""
    You are an AI Legal Assistant for Indian Law. The user is in: {jurisdiction}.
    The user is facing this situation: {situation_type}.
    Additional context from user: {user_context}
    
    IMPORTANT RULES:
    - You MUST respond ENTIRELY in this language: {language}.
    - You must use simple, accessible language. Do not use heavy legal jargon.
    {cybercrime_instruction}
    
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
        ai_text = response.text or ""

        # Safety fallback: ensure the direct portal link is present for cybercrime issues.
        if is_cybercrime_issue and cybercrime_portal not in ai_text:
            ai_text += f"\n\n- [National Cyber Crime Reporting Portal]({cybercrime_portal})"

        return jsonify({"status": "success", "ai_response": ai_text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/analyze-document', methods=['POST'])
def analyze_document():
    uploaded_file = request.files.get('document')
    language = request.form.get('language', 'English')

    if not uploaded_file or uploaded_file.filename == '':
        return jsonify({"status": "error", "message": "Please upload a legal document or image."}), 400

    allowed_mime_types = {
        'application/pdf',
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/webp',
        'text/plain'
    }

    if uploaded_file.mimetype not in allowed_mime_types:
        return jsonify({
            "status": "error",
            "message": "Unsupported file type. Please upload PDF, PNG, JPG, WEBP, or TXT files."
        }), 400

    prompt = f"""
You are a professional legal analyst focused on Indian legal context.
Analyze the uploaded legal document and respond ENTIRELY in {language}.

Use clear, plain language and structure your answer in Markdown with bullet points and bold headings.
Include these sections exactly:

## **Document Purpose**
- Briefly explain what this document is and why it was issued.

## **Critical Deadlines**
- List any exact dates, response windows, or time-sensitive actions.
- If no deadlines are explicit, say "No explicit deadline found".

## **Legal Obligations**
- List duties, restrictions, compliance requirements, or commitments.

## **Financial Amounts**
- Extract and list all important amounts, penalties, interest, fees, or payment terms.
- If not found, say "No financial amounts clearly specified".

## **Red Flags / High-Risk Clauses**
- Identify potentially dangerous terms (penalty, indemnity, termination, admission of liability, waiver, jurisdiction/arbitration disadvantage, broad rights transfer, one-sided obligations).
- Explain why each is risky in simple terms.

## **Recommended Next Steps**
- Provide a practical, prioritized checklist to protect the user's interests.
- Include immediate steps for evidence/document preservation and lawyer consultation where appropriate.

Important:
- Do not provide final legal advice; keep it informational.
- Quote exact clause snippets where possible.
"""

    temp_path = None
    try:
        suffix = os.path.splitext(uploaded_file.filename)[1] or '.tmp'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            uploaded_file.save(temp_file)
            temp_path = temp_file.name

        uploaded_asset = client.files.upload(file=temp_path)

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=[uploaded_asset, prompt],
        )

        return jsonify({"status": "success", "analysis": response.text or "No analysis generated."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(debug=True)