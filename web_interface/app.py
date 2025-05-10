from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()

# Get configuration from environment variables
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")

# Initialize Vertex AI
vertexai.init(
    project=project_id,
    location=location,
    staging_bucket=bucket,
)

app = Flask(__name__)
# Habilitar CORS para permitir solicitudes desde cualquier origen
CORS(app)

# Configuration - these would typically come from environment variables
RESOURCE_ID = "575132542257070080"  # Your AgentEngine resource ID
DEFAULT_USER_ID = "web_user"  # A default user ID for web interface users

# Keep a simple in-memory store of sessions (not suitable for production)
user_sessions = {}

@app.route('/')
def index():
    """Render the chat interface."""
    return render_template('index.html')

@app.route('/api/start_session', methods=['POST'])
def start_session():
    """Start a new session for a user."""
    user_id = request.json.get('user_id', DEFAULT_USER_ID)
    
    # Get the agent
    remote_app = agent_engines.get(RESOURCE_ID)
    
    # Create a new session
    session = remote_app.create_session(user_id=user_id)
    session_id = session['id']
    
    # Store the session ID for this user
    user_sessions[user_id] = session_id
    
    return jsonify({
        'session_id': session_id,
        'user_id': user_id
    })

@app.route('/api/send_message', methods=['POST'])
def chat():
    """Send a message to the agent and get a response."""
    try:
        user_id = request.json.get('user_id', DEFAULT_USER_ID)
        message = request.json.get('message', '')
        
        print(f"Received message from user {user_id}: {message}")
        
        # Get session ID or create a new one
        if user_id not in user_sessions:
            print(f"Creating new session for user {user_id}")
            response = start_session()
            session_id = response.json['session_id']
        else:
            session_id = user_sessions[user_id]
            print(f"Using existing session {session_id} for user {user_id}")
        
        # Send the message to the agent
        print(f"Sending message to agent using resource_id={RESOURCE_ID}, session_id={session_id}")
        remote_app = agent_engines.get(RESOURCE_ID)
        
        # Get the response from the agent
        # Note: We're using the streaming API but collecting all responses into a single response
        all_responses = []
        for event in remote_app.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message
        ):
            all_responses.append(event)
        
        # Just use the last response for simplicity
        response = all_responses[-1] if all_responses else {}
        
        print(f"Received response from agent: {response}")
        
        # Extract the text response
        response_text = ""
        if 'content' in response and 'parts' in response['content']:
            for part in response['content']['parts']:
                if 'text' in part:
                    response_text += part['text']
        
        return jsonify({
            'response': response_text or "No se recibió respuesta del agente.",
            'session_id': session_id,
            'user_id': user_id
        })
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'response': "Error al comunicarse con el agente. Por favor, intenta de nuevo.",
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    # Usa el puerto que Google Cloud proporciona o el 8080 por defecto
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
