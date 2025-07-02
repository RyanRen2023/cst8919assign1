from flask import Flask, redirect, render_template, session, url_for, request
import logging
import sys
from datetime import datetime
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


# Create Flask app first
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)



# Force flush stdout/stderr
sys.stdout.flush()
sys.stderr.flush()

# Configure logging with immediate flush
class FlushStreamHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

# Setup logging
def setup_logging():
    # Remove all existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create handler that flushes immediately
    handler = FlushStreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Configure root logger
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(handler)
    
    # Configure Flask logger
    app.logger.setLevel(logging.INFO)
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.propagate = False

# Call setup_logging() AFTER creating the Flask app
setup_logging()

# Test that logging is working
app.logger.info("Flask application logging configured successfully")

# Dummy user credentials for demonstration
VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/callback')
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect(request.args.get('state', '/'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True),
        state=request.args.get('next', '/')
    )

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            # Multiple logging methods to ensure it works
            message = f"Successful login attempt - Username: {username}"
            app.logger.info(message)
            print(message, file=sys.stdout, flush=True)
            
            flash('Login successful!', 'success')
            return render_template('success.html')
        else:
            message = f"Failed login attempt - Username: {username}"
            app.logger.warning(message)
            print(message, file=sys.stderr, flush=True)
            
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/test-logging')
def test_logging():
    """Test route to verify logging is working"""
    import time
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    messages = [
        f"[{timestamp}] TEST: App logger info",
        f"[{timestamp}] TEST: Direct stderr output"
    ]
    
    for msg in messages:
        app.logger.info(msg)
        print(msg, file=sys.stderr, flush=True)
    
    return f"Logging test completed at {timestamp} - Check your Azure logs!"

@app.route('/server-info')
def server_info():
    import os
    server_software = os.environ.get('SERVER_SOFTWARE', 'Unknown')
    wsgi_server = os.environ.get('WSGI_SERVER', 'Unknown')
    
    # Log and return server info
    info = f"Server Software: {server_software}, WSGI Server: {wsgi_server}"
    app.logger.info(info)
    print(f"SERVER INFO: {info}", file=sys.stderr, flush=True)
    
    return info

if __name__ == '__main__':
    app.run(debug=True)