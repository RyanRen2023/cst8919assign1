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
app.logger.info("cst8919-assign-1: Flask application logging configured successfully")

# Register OAuth with Auth0
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
    app.logger.info("cst8919-assign-1: Home page accessed")
    if "user" in session:
        app.logger.info("success: User is logged in redirecting to protected page")
        return redirect(url_for('protected'))
    else:
        app.logger.info("failed: User is not logged in redirecting to login page")
        return redirect(url_for('login'))

@app.route('/callback')
def callback():
    app.logger.info("cst8919-assign-1: Callback page accessed")
    
    # Get client IP address for logging
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Check for Auth0 error parameters first
    error = request.args.get('error')
    error_description = request.args.get('error_description', '')
    
    if error:
        # Auth0 returned an error
        timestamp = datetime.now().isoformat()
        app.logger.error(f"cst8919-assign-1: Auth0 login failed - Error: {error}, Description: {error_description}, IP: {client_ip}, Timestamp: {timestamp}")
        return redirect(url_for('login', error='auth0_error'))
    
    try:
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        print("cst8919-assign-1: Auth0 Token:", token['access_token'])
        
        # Extract user information from token
        user_info = token.get('userinfo', {})
        user_id = user_info.get('sub', 'unknown')
        email = user_info.get('email', 'unknown')
        timestamp = datetime.now().isoformat()
        
        # Log successful login with user details
        app.logger.info(f"cst8919-assign-1: Successful login - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")
        
        return redirect(request.args.get('state', '/'))
        
    except Exception as e:
        # Log failed login attempt
        timestamp = datetime.now().isoformat()
        error_message = str(e)
        app.logger.error(f"cst8919-assign-1: Login failed - Error: {error_message}, IP: {client_ip}, Timestamp: {timestamp}")
        
        # Redirect to login page with error
        return redirect(url_for('login', error='authentication_failed'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.info("cst8919-assign-1: Login page accessed")
    
    # Check if there was an authentication error
    error = request.args.get('error')
    if error:
        app.logger.warning(f"cst8919-assign-1: Login page accessed with error: {error}")
        
        # Log additional error details if available
        error_description = request.args.get('error_description', '')
        if error_description:
            app.logger.warning(f"cst8919-assign-1: Error description: {error_description}")
    
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True),
        state=request.args.get('next', '/')
    )

@app.route("/logout")
def logout():
    # Get client IP address for logging
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.now().isoformat()
    
    # Log user details before clearing session
    if "user" in session:
        user_info = session.get("user", {}).get('userinfo', {})
        user_id = user_info.get('sub', 'unknown')
        email = user_info.get('email', 'unknown')
        app.logger.info(f"cst8919-assign-1: User logged out - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")
    else:
        app.logger.info(f"cst8919-assign-1: Logout attempted without active session - IP: {client_ip}, Timestamp: {timestamp}")
    
    session.clear()
    
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/protected")
def protected():
    # Get client IP address for logging
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.now().isoformat()
    auth_header = request.headers.get("Authorization", None)
    hasToken = auth_header and auth_header.startswith("Bearer ")
    if "user" not in session and not hasToken:
        # Log unauthorized access attempt
        app.logger.warning(f"cst8919-assign-1: Unauthorized access attempt to /protected - IP: {client_ip}, Timestamp: {timestamp}")
        return redirect(url_for('login', next=request.path))
    
    # Log authorized access to protected route
    user_info = session.get("user", {}).get('userinfo', {})
    user_id = user_info.get('sub', 'unknown')
    email = user_info.get('email', 'unknown')
    
    app.logger.info(f"cst8919-assign-1: Authorized access to /protected - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")
    
    return render_template("protected.html", session=session.get("user"), pretty=json.dumps(session.get("user"), indent=4))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))