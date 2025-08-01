from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
VERIFY_TOKEN = "myVerifyToken123"
ACCESS_TOKEN = "EAAKsBtQLuC8BPJaZC54eMP84Azp1XYpbpmT9u3YVWkoNVVaugx7FqZCQoEhCvHgr0hd4LJV4RYJCOSZCiwqABWRUQctSs73UZAtd9ZCrm04vW5cNGfQQBq60xKcZBeGvUZBUIfmBUB3yZBKi5rWbB1FD34PTmw5SGC8MUbHtBZAj5GjccaLzFcj9M53F6xFJm4bsrvxnp9Qen55ZA6xJOCmYc1GoUHbmXAnSZA8VtBki9Vfjow68QZDZD"

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
    """Process incoming WhatsApp message - just log for now"""
    try:
        message_type = message.get('type')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n=== WhatsApp Message Received at {timestamp} ===")
        print(f"Message Type: {message_type}")
        
        if message_type == 'text':
            # Handle text message
            text_content = message['text']['body']
            print(f"Text Message: {text_content}")
            print("📧 EMAIL WOULD BE SENT:")
            print(f"   Subject: WhatsApp Task - {timestamp}")
            print(f"   Body: {text_content}")
            
        elif message_type == 'audio':
            # Handle voice message
            audio_id = message['audio']['id']
            print(f"Voice Message ID: {audio_id}")
            print("📧 EMAIL WITH VOICE ATTACHMENT WOULD BE SENT:")
            print(f"   Subject: WhatsApp Voice Task - {timestamp}")
            print(f"   Attachment: voice_message.ogg")
        
        else:
            print(f"Unsupported message type: {message_type}")
        
        print("=== Message Processing Complete ===\n")
        
    except Exception as e:
        print(f"Error processing message: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "verify_token": VERIFY_TOKEN
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "WhatsApp Webhook", 
        "status": "running",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health"
        }
    })

if __name__ == '__main__':
    print("Starting WhatsApp Webhook Server...")
    print(f"Verify Token: {VERIFY_TOKEN}")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
