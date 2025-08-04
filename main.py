from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import os
from datetime import datetime
import json

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
            print(f"Received webhook data: {json.dumps(data, indent=2)}")
            
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
            import traceback
            traceback.print_exc()
            return 'Error', 500

def process_message(message):
    """Process incoming WhatsApp message"""
    try:
        message_type = message.get('type')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Processing message type: {message_type}")
        print(f"Full message structure: {json.dumps(message, indent=2)}")
        
        if message_type == 'text':
            # Handle text message
            text_content = message['text']['body']
            subject = "Tasks"
            print(f"Processing text message: {text_content}")
            send_email(subject, text_content)
            
        elif message_type == 'audio':
            # Handle voice message
            print("Processing audio message...")
            audio_data = message.get('audio', {})
            audio_id = audio_data.get('id')
            print(f"Audio ID: {audio_id}")
            
            if audio_id:
                audio_url = get_media_url(audio_id)
                print(f"Audio URL: {audio_url}")
                
                if audio_url:
                    audio_content = download_media(audio_url)
                    print(f"Audio content downloaded: {len(audio_content) if audio_content else 0} bytes")
                    
                    if audio_content:
                        subject = "Tasks"
                        caption = audio_data.get('caption', 'Voice message from WhatsApp')
                        print(f"Sending audio email with caption: {caption}")
                        send_email_with_attachment(subject, caption, audio_content, 'voice_message.ogg', 'audio/ogg')
                    else:
                        print("Failed to download audio content")
                else:
                    print("Failed to get audio URL")
            else:
                print("No audio ID found in message")
        
        elif message_type == 'image':
            # Handle image message
            print("Processing image message...")
            image_data = message.get('image', {})
            image_id = image_data.get('id')
            print(f"Image ID: {image_id}")
            
            if image_id:
                image_url = get_media_url(image_id)
                print(f"Image URL: {image_url}")
                
                if image_url:
                    image_content = download_media(image_url)
                    print(f"Image content downloaded: {len(image_content) if image_content else 0} bytes")
                    
                    if image_content:
                        subject = "Tasks"
                        caption = image_data.get('caption', 'Image received from WhatsApp')
                        print(f"Sending image email with caption: {caption}")
                        send_email_with_attachment(subject, caption, image_content, 'whatsapp_image.jpg', 'image/jpeg')
                    else:
                        print("Failed to download image content")
                else:
                    print("Failed to get image URL")
            else:
                print("No image ID found in message")
        
        elif message_type == 'document':
            # Handle document message
            print("Processing document message...")
            document_data = message.get('document', {})
            document_id = document_data.get('id')
            print(f"Document ID: {document_id}")
            
            if document_id:
                document_url = get_media_url(document_id)
                print(f"Document URL: {document_url}")
                
                if document_url:
                    document_content = download_media(document_url)
                    print(f"Document content downloaded: {len(document_content) if document_content else 0} bytes")
                    
                    if document_content:
                        subject = "Tasks"
                        filename = document_data.get('filename', 'document')
                        caption = document_data.get('caption', f'Document: {filename}')
                        print(f"Sending document email with filename: {filename}")
                        send_email_with_attachment(subject, caption, document_content, filename, 'application/octet-stream')
                    else:
                        print("Failed to download document content")
                else:
                    print("Failed to get document URL")
            else:
                print("No document ID found in message")
        
        elif message_type == 'video':
            # Handle video message
            print("Processing video message...")
            video_data = message.get('video', {})
            video_id = video_data.get('id')
            print(f"Video ID: {video_id}")
            
            if video_id:
                video_url = get_media_url(video_id)
                print(f"Video URL: {video_url}")
                
                if video_url:
                    video_content = download_media(video_url)
                    print(f"Video content downloaded: {len(video_content) if video_content else 0} bytes")
                    
                    if video_content:
                        subject = "Tasks"
                        caption = video_data.get('caption', 'Video received from WhatsApp')
                        print(f"Sending video email with caption: {caption}")
                        send_email_with_attachment(subject, caption, video_content, 'whatsapp_video.mp4', 'video/mp4')
                    else:
                        print("Failed to download video content")
                else:
                    print("Failed to get video URL")
            else:
                print("No video ID found in message")
        
        else:
            print(f"Unsupported message type: {message_type}")
        
        print(f"Processed {message_type} message successfully")
        
    except Exception as e:
        print(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()

def get_media_url(media_id):
    """Get media URL from WhatsApp API"""
    try:
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        print(f"Requesting media URL from: {url}")
        
        response = requests.get(url, headers=headers)
        print(f"Media URL response status: {response.status_code}")
        print(f"Media URL response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            media_url = response_data.get('url')
            print(f"Extracted media URL: {media_url}")
            return media_url
        else:
            print(f"Failed to get media URL. Status: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"Error getting media URL: {e}")
        import traceback
        traceback.print_exc()
        return None

def download_media(url):
    """Download media file from WhatsApp"""
    try:
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        print(f"Downloading media from: {url}")
        
        response = requests.get(url, headers=headers)
        print(f"Download response status: {response.status_code}")
        print(f"Download response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content = response.content
            print(f"Successfully downloaded {len(content)} bytes")
            return content
        else:
            print(f"Failed to download media. Status: {response.status_code}")
            print(f"Response text: {response.text}")
            return None
        
    except Exception as e:
        print(f"Error downloading media: {e}")
        import traceback
        traceback.print_exc()
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
        import traceback
        traceback.print_exc()

def send_email_with_attachment(subject, body, attachment_data, filename, mime_type):
    """Send email with attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment with proper MIME type
        part = MIMEBase(mime_type.split('/')[0], mime_type.split('/')[1])
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
        
        print(f"Email with attachment sent successfully: {subject} - {filename}")
        
    except Exception as e:
        print(f"Error sending email with attachment: {e}")
        import traceback
        traceback.print_exc()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting WhatsApp Webhook Server...")
    print(f"Verify Token: {VERIFY_TOKEN}")
    print("Supported message types: text, audio, image, document, video")
    app.run(host='0.0.0.0', port=5000, debug=True)
