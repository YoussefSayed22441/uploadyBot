from flask import request, jsonify
from app import app
from app.whatsapp.whatsapp_handler import WhatsAppHandler
from app.facebook.facebook_client import FacebookClient
from app.scheduler.post_scheduler import PostScheduler

whatsapp_handler = WhatsAppHandler()
facebook_client = FacebookClient()
post_scheduler = PostScheduler()

# Start the scheduler when the application starts
post_scheduler.start_scheduler()

@app.route('/')
def index():
    return jsonify({'status': 'ok', 'message': 'UploadyBot is running'})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    # Handle WhatsApp messages
    if 'entry' in data and 'changes' in data['entry'][0]:
        message = whatsapp_handler.parse_message(data)
        if message:
            response = whatsapp_handler.process_command(message)
            return jsonify(response or {'status': 'ok'})
    
    return jsonify({'status': 'ok'})

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == app.config['WHATSAPP_TOKEN']:
            return challenge
        return 'Forbidden', 403

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'scheduled_posts': post_scheduler.get_scheduled_posts(),
        'facebook_token_valid': bool(facebook_client.verify_token())
    }) 