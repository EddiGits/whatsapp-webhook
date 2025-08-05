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
import logging

# Configure logging to show in Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
VERIFY_TOKEN = "myVerifyToken123"
ACCESS_TOKEN = "EAAKsBtQLuC8BPAtfmCJlfEkjf98D6ObdNsngrrdhnSSfVHaiVbOYKBd4bY8C61iO8xBIcNLJtI935wPpIhjxxvA1tjjfRUbpxagyZBaIHZBZBWkUa0baAXJZA8ygdJgFslvGR5otzFND19DVTOPIhHpG0mYRxMcTixoscJACtQveZCZBOCzCUwKb2SjgZC46MwuQ2Mr4ZBUvvj6TjUPuHC7xlMcLQehZCHiQS1HZClxlrjTOUZD"

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "EdwinPhaku@Gmail.com"
TO_EMAIL = "EdwinPhaku@Gmail.com"
EMAIL_PASSWORD = "poet nhdw oywe woyb"  # Use App Password for Gmail

# Global variable to store last webhook data for debugging
last_webhook_data = None
last_error = None

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    global last_webhook_data, last_error
    
    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        logger.info(f"Verification request: mode={mode}, token={token}, challenge={challenge}")
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return challenge, 200
        else:
            logger.error("Webhook verification failed!")
            return 'Forbidden', 403
    
    elif request.method == 'POST':
        # Handle incoming messages
        try:
            data = request.get_json()
            last_webhook_data = data
            logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")
            
            if data and 'entry' in data:
                for entry in data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if 'value' in change and 'messages' in change['value']:
                                for message in change['value']['messages']:
                                    process_message(message)
            
            return 'OK', 200
            
        except Exception as e:
            last_error = str(e)
            logger.error(f"Error processing webhook: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return 'Error', 500

def process_message(message):
    """Process incoming WhatsApp message"""
    try:
        message_type = message.get('type')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"Processing message type: {message_type}")
        logger.info(f"Full message structure: {json.dumps(message, indent=2)}")
        
        if message_type == 'text':
            # Handle text message
            text_content = message['text']['body']
            subject = "Tasks"
            logger.info(f"Processing text message: {text_content}")
            send_email(subject, text_content)
            
        elif message_type == 'audio':
            # Handle voice message
            logger.info("Processing audio message...")
            audio_data = message.get('audio', {})
            audio_id = audio_data.get('id')
            logger.info(f"Audio ID: {audio_id}")
            
            if audio_id:
                # Get media URL using the correct approach
                media_url, mime_type = get_media_url_and_type(audio_id)
                logger.info(f"Audio URL: {media_url}")
                logger.info(f"Audio MIME type: {mime_type}")
                
                if media_url:
                    audio_content = download_media_with_auth(media_url)
                    logger.info(f"Audio content downloaded: {len(audio_content) if audio_content else 0} bytes")
                    
                    if audio_content:
                        subject = "Tasks"
                        logger.info(f"Sending audio email")
                        send_email_with_attachment(subject, "", audio_content, 'voice_message.ogg', 'audio/ogg')
                    else:
                        logger.error("Failed to download audio content")
                else:
                    logger.error("Failed to get audio URL")
            else:
                logger.error("No audio ID found in message")
        
        elif message_type == 'image':
            # Handle image message
            logger.info("Processing image message...")
            image_data = message.get('image', {})
            image_id = image_data.get('id')
            logger.info(f"Image ID: {image_id}")
            
            if image_id:
                # Get media URL using the correct approach
                media_url, mime_type = get_media_url_and_type(image_id)
                logger.info(f"Image URL: {media_url}")
                logger.info(f"Image MIME type: {mime_type}")
                
                if media_url:
                    image_content = download_media_with_auth(media_url)
                    logger.info(f"Image content downloaded: {len(image_content) if image_content else 0} bytes")
                    
                    if image_content:
                        subject = "Tasks"
                        logger.info(f"Sending image email")
                        # Use the actual MIME type from WhatsApp
                        file_extension = mime_type.split('/')[-1] if mime_type else 'jpg'
                        filename = f'whatsapp_image.{file_extension}'
                        send_email_with_attachment(subject, "", image_content, filename, mime_type or 'image/jpeg')
                    else:
                        logger.error("Failed to download image content")
                else:
                    logger.error("Failed to get image URL")
            else:
                logger.error("No image ID found in message")
        
        elif message_type == 'document':
            # Handle document message
            logger.info("Processing document message...")
            document_data = message.get('document', {})
            document_id = document_data.get('id')
            logger.info(f"Document ID: {document_id}")
            
            if document_id:
                media_url, mime_type = get_media_url_and_type(document_id)
                logger.info(f"Document URL: {media_url}")
                logger.info(f"Document MIME type: {mime_type}")
                
                if media_url:
                    document_content = download_media_with_auth(media_url)
                    logger.info(f"Document content downloaded: {len(document_content) if document_content else 0} bytes")
                    
                    if document_content:
                        subject = "Tasks"
                        filename = document_data.get('filename', 'document')
                        logger.info(f"Sending document email with filename: {filename}")
                        send_email_with_attachment(subject, "", document_content, filename, mime_type or 'application/octet-stream')
                    else:
                        logger.error("Failed to download document content")
                else:
                    logger.error("Failed to get document URL")
            else:
                logger.error("No document ID found in message")
        
        elif message_type == 'video':
            # Handle video message
            logger.info("Processing video message...")
            video_data = message.get('video', {})
            video_id = video_data.get('id')
            logger.info(f"Video ID: {video_id}")
            
            if video_id:
                media_url, mime_type = get_media_url_and_type(video_id)
                logger.info(f"Video URL: {media_url}")
                logger.info(f"Video MIME type: {mime_type}")
                
                if media_url:
                    video_content = download_media_with_auth(media_url)
                    logger.info(f"Video content downloaded: {len(video_content) if video_content else 0} bytes")
                    
                    if video_content:
                        subject = "Tasks"
                        logger.info(f"Sending video email")
                        file_extension = mime_type.split('/')[-1] if mime_type else 'mp4'
                        filename = f'whatsapp_video.{file_extension}'
                        send_email_with_attachment(subject, "", video_content, filename, mime_type or 'video/mp4')
                    else:
                        logger.error("Failed to download video content")
                else:
                    logger.error("Failed to get video URL")
            else:
                logger.error("No video ID found in message")
        
        else:
            logger.warning(f"Unsupported message type: {message_type}")
        
        logger.info(f"Processed {message_type} message successfully")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def get_media_url_and_type(media_id):
    """Get media URL and MIME type from WhatsApp API using the correct approach"""
    try:
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        logger.info(f"Requesting media URL from: {url}")
        
        response = requests.get(url, headers=headers)
        logger.info(f"Media URL response status: {response.status_code}")
        logger.info(f"Media URL response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            media_url = response_data.get('url')
            mime_type = response_data.get('mime_type')
            logger.info(f"Extracted media URL: {media_url}")
            logger.info(f"Extracted MIME type: {mime_type}")
            return media_url, mime_type
        else:
            logger.error(f"Failed to get media URL. Status: {response.status_code}")
            return None, None
        
    except Exception as e:
        logger.error(f"Error getting media URL: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None, None

def download_media_with_auth(url):
    """Download media file from WhatsApp with proper authentication"""
    try:
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        logger.info(f"Downloading media from: {url}")
        
        response = requests.get(url, headers=headers, stream=True)
        logger.info(f"Download response status: {response.status_code}")
        logger.info(f"Download response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content = response.content
            logger.info(f"Successfully downloaded {len(content)} bytes")
            return content
        else:
            logger.error(f"Failed to download media. Status: {response.status_code}")
            logger.error(f"Response text: {response.text}")
            return None
        
    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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
        
        logger.info(f"Email sent successfully: {subject}")
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def send_email_with_attachment(subject, body, attachment_data, filename, mime_type):
    """Send email with attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        
        # Keep body empty for media attachments
        msg.attach(MIMEText("", 'plain'))
        
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
        
        logger.info(f"Email with attachment sent successfully: {subject} - {filename}")
        
    except Exception as e:
        logger.error(f"Error sending email with attachment: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check what's happening"""
    return jsonify({
        "status": "debug_info",
        "last_webhook_data": last_webhook_data,
        "last_error": last_error,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/test-email', methods=['GET'])
def test_email():
    """Test endpoint to verify email functionality"""
    try:
        send_email("Test Email", "This is a test email from WhatsApp webhook server")
        return jsonify({"status": "success", "message": "Test email sent"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    logger.info("Starting WhatsApp Webhook Server...")
    logger.info(f"Verify Token: {VERIFY_TOKEN}")
    logger.info("Supported message types: text, audio, image, document, video")
    app.run(host='0.0.0.0', port=5000, debug=False)  # Set debug=False for production
