from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
VERIFY_TOKEN = "myVerifyToken123"
ACCESS_TOKEN = "EAAKsBtQLuC8BPJaZC54eMP84Azp1XYpbpmT9u3YVWkoNVVaugx7FqZCQoEhCvHgr0hd4LJV4RYJCOSZCiwqABWRUQctSs73UZAtd9ZCrm04vW5cNGfQQBq60xKcZBeGvUZBUIfmBUB3yZBKi5rWbB1FD34PTmw5SGC8MUbHtBZAj5GjccaLzFcj9M53F6xFJm4bsrvxnp9Qen55ZA6xJOCmYc1GoUHbmXAnSZA8VtBki9Vfjow68QZDZD"

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "EdwinPhaku@Gmail.com"
TO_EMAIL = "EdwinPhaku@Gmail.com"
EMAIL_PASSWORD = "poet nhdw oywe woyb"  # Use App Password for Gmail

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        print(f"Verification request: mode={mode}, token={token}, challenge={challenge}")
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("Webhook verified successfully!")
            return challenge, 200
        else:
            print("Webhook verification failed!")
            return 'Forbidden', 403
    
    elif request.method == 'POST':
        # Handle incoming messages
        try:
            data = request.get_json()
            print(f"Received webhook data: {data}")
            
            if data and 'entry' in data:
                for entry in data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if 'value' in change and 'messages' in change['value']:
                                for message in change['value']['messages']:
                                    process_message(message)
            
            return 'OK', 200
            
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return 'Error', 500

def process_message(message):
    """Process incoming WhatsApp message"""
    try:
        message_type = message.get('type')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if message_type == 'text':
            # Handle text message
            text_content = message['text']['body']
            subject = "Tasks"
            send_email(subject, text_content)
            
        elif message_type == 'audio':
            # Handle voice message
            audio_id = message['audio']['id']
            audio_url = get_media_url(audio_id)
            if audio_url:
                audio_content = download_audio(audio_url)
                if audio_content:
                    subject = "Tasks"
                    send_email_with_attachment(subject, "Voice message attached", audio_content, 'voice_message.ogg')
        
        print(f"Processed {message_type} message successfully")
        
    except Exception as e:
        print(f"Error processing message: {e}")

def get_media_url(media_id):
    """Get media URL from WhatsApp API"""
    try:
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('url')
        return None
        
    except Exception as e:
        print(f"Error getting media URL: {e}")
        return None

def download_audio(url):
    """Download audio file from WhatsApp"""
    try:
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.content
        return None
        
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def send_email(subject, body):
    """Send text email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, TO_EMAIL, text)
        server.quit()
        
        print(f"Email sent successfully: {subject}")
        
    except Exception as e:
        print(f"Error sending email: {e}")

def send_email_with_attachment(subject, body, attachment_data, filename):
    """Send email with attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {filename}')
        msg.attach(part)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(FROM_EMAIL, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, TO_EMAIL, text)
        server.quit()
        
        print(f"Email with attachment sent successfully: {subject}")
        
    except Exception as e:
        print(f"Error sending email with attachment: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting WhatsApp Webhook Server...")
    print(f"Verify Token: {VERIFY_TOKEN}")
    app.run(host='0.0.0.0', port=5000, debug=True)
