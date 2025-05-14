from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
import os
from groq import Groq
import re
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load environment variables from .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")  # e.g., "edusparkacademy@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASS")  # Use Gmail App Password

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Enhanced system prompt for Groq
GROQ_SYSTEM_PROMPT = """
You are Grok 3, a friendly and professional assistant for EduSpark Academy, a top tuition center in Hyderabad, Pakistan, offering expert-led tutoring for nursery to 10th class in subjects like Computer Science, Mathematics, Biology, English, Islamiyat, Pakistan Studies, and Physics. Provide concise, attractive, and well-formatted responses using bullet points (e.g., * item *) and bold italic text (e.g., **_text_**) for emphasis. Keep replies short, engaging, and tailored to inspire or assist students and parents. Avoid lengthy explanations unless asked.
"""

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Send email to admin
        msg = MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}")
        msg['Subject'] = 'New Contact Form Submission from EduSpark Academy'
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        # Generate and send automated HTML response
        response = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style type="text/css">
        body {{ font-family: 'Arial', sans-serif; background-color: #FAFBFF; color: #1F2937; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 20px auto; background-color: #FFFFFF; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }}
        .header {{ background: linear-gradient(135deg, #1E3A8A 0%, #152B65 100%); color: #FFFFFF; text-align: center; padding: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: bold; }}
        .content {{ padding: 30px; color: #1F2937; }}
        .content h2 {{ color: #1E3A8A; font-size: 20px; font-weight: bold; margin-bottom: 15px; }}
        .content p {{ line-height: 1.6; margin-bottom: 20px; color: #4B5563; }}
        .content ul {{ list-style-type: disc; padding-left: 20px; margin-bottom: 20px; }}
        .content ul li {{ margin-bottom: 10px; color: #1F2937; font-size: 16px; }}
        .cta {{ text-align: center; margin: 20px 0; }}
        .cta a {{ background-color: #FBBF24; color: #1E3A8A; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; }}
        .cta a:hover {{ background-color: #E5A812; }}
        .footer {{ text-align: center; padding: 15px; background-color: #1E3A8A; color: #FFFFFF; font-size: 12px; }}
        @media (max-width: 600px) {{ .container {{ margin: 10px; width: calc(100% - 20px); }} .content {{ padding: 20px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>EduSpark Academy</h1>
        </div>
        <div class="content">
            <h2>Thank You for Considering EduSpark Academy!</h2>
            <p>Dear {name},</p>
            <p>Thank you for reaching out to <strong>EduSpark Academy</strong>, your premier tuition center in Hyderabad, Pakistan. We’re thrilled by your interest in our services!</p>
            <p>We offer expert-led tutoring for students from <strong>nursery to 10th class</strong> in the following subjects:</p>
            <ul>
                <li>Computer Science</li>
                <li>Mathematics</li>
                <li>Biology</li>
                <li>English</li>
                <li>Islamiyat</li>
                <li>Pakistan Studies</li>
                <li>Physics</li>
            </ul>
            <p>We’d love to tailor our support to your academic goals. Please feel free to contact me, <strong>Ali Hasnain</strong>, at <strong>+923423987710</strong> to discuss further.</p>
            <div class="cta">
                <a href="tel:+923423987710">Connect Now!</a>
            </div>
            <p>Thank you again for considering <strong>EduSpark Academy</strong>. We’re excited to assist you soon!</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 EduSpark Academy. All Rights Reserved.</p>
        </div>
    </div>
</body>
</html>"""
        response_msg = MIMEText(response, 'html')
        response_msg['Subject'] = 'Thank You for Considering EduSpark Academy'
        response_msg['From'] = EMAIL_USER
        response_msg['To'] = email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(response_msg)

        return render_template('contact.html', success=True)
    return render_template('contact.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    if user_message:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": GROQ_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0,
        )
        response = chat_completion.choices[0].message.content
        logger.info(f"Chatbot response: {response}")
        return jsonify({'response': response})
    return jsonify({'response': 'Please ask something! 😊'})

@app.route('/quiz', methods=['POST'])
def quiz():
    subject = request.json.get('subject')
    if subject:
        prompt = f"Generate a short, motivational message for a student needing help in {subject} at EduSpark Academy, Hyderabad, Pakistan. Use bold text and bullet points for a vibrant look."
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": GROQ_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0,
        )
        response = chat_completion.choices[0].message.content
        return jsonify({'response': response})
    return jsonify({'response': 'Pick a subject to get motivated! 🌟'})

if __name__ == '__main__':
    app.run(debug=True)