# Flask application with Auth0 SSO authentication and comprehensive security logging
# This application demonstrates secure authentication, user activity monitoring, and Azure integration
from flask import Flask, redirect, render_template, session, url_for, request
import logging
import sys
from datetime import datetime
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

# Load environment variables from .env file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# Initialize OAuth client for Auth0 integration
oauth = OAuth(app)

# Register Auth0 as OAuth provider
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",  # Request user profile and email information
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# Force flush stdout/stderr to ensure immediate output in Azure App Service
sys.stdout.flush()
sys.stderr.flush()

# Custom logging handler that flushes immediately for real-time log output
class FlushStreamHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()  # Ensure logs are written immediately

# Configure comprehensive logging for security monitoring
def setup_logging():
    # Remove all existing handlers to avoid duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create handler that flushes immediately for real-time monitoring
    handler = FlushStreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Configure root logger for application-wide logging
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(handler)
    
    # Configure Flask logger specifically for web application events
    app.logger.setLevel(logging.INFO)
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.propagate = False  # Prevent duplicate logs

# Initialize logging system after Flask app creation
setup_logging()

# Verify logging configuration is working
app.logger.info("cst8919-assign-1: Flask application logging configured successfully")

# Register OAuth with Auth0 (duplicate registration for clarity)
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
    """
    Home page route - redirects users based on authentication status
    Logs user access for security monitoring
    """
    app.logger.info("cst8919-assign-1: Home page accessed")
    if "user" in session:
        # User is authenticated, redirect to protected content
        app.logger.info("success: User is logged in redirecting to protected page")
        return redirect(url_for('protected'))
    else:
        # User is not authenticated, redirect to login
        app.logger.info("failed: User is not logged in redirecting to login page")
        return redirect(url_for('login'))

@app.route('/callback')
def callback():
    """
    Auth0 callback route - handles authentication response
    Processes successful logins and authentication errors
    Logs all authentication attempts for security monitoring
    """
    app.logger.info("cst8919-assign-1: Callback page accessed")
    
    # Get client IP address for security logging and monitoring
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Check for Auth0 error parameters first (authentication failures)
    error = request.args.get('error')
    error_description = request.args.get('error_description', '')
    
    if error:
        # Auth0 returned an authentication error
        timestamp = datetime.now().isoformat()
        app.logger.error(f"cst8919-assign-1: Auth0 login failed - Error: {error}, Description: {error_description}, IP: {client_ip}, Timestamp: {timestamp}")
        return redirect(url_for('login', error='auth0_error'))
    
    try:
        # Exchange authorization code for access token
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        print("cst8919-assign-1: Auth0 Token:", token['access_token'])
        
        # Extract user information from token for logging and security monitoring
        user_info = token.get('userinfo', {})
        user_id = user_info.get('sub', 'unknown')
        email = user_info.get('email', 'unknown')
        timestamp = datetime.now().isoformat()
        
        # Log successful login with comprehensive user details for security monitoring
        app.logger.info(f"cst8919-assign-1: Successful login - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")
        
        # Redirect to the originally requested page or home
        return redirect(request.args.get('state', '/'))
        
    except Exception as e:
        # Log failed login attempt due to application error
        timestamp = datetime.now().isoformat()
        error_message = str(e)
        app.logger.error(f"cst8919-assign-1: Login failed - Error: {error_message}, IP: {client_ip}, Timestamp: {timestamp}")
        
        # Redirect to login page with error indication
        return redirect(url_for('login', error='authentication_failed'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route - initiates Auth0 authentication flow
    Handles authentication errors and redirects to Auth0
    """
    app.logger.info("cst8919-assign-1: Login page accessed")
    
    # Check if there was an authentication error from previous attempts
    error = request.args.get('error')
    if error:
        app.logger.warning(f"cst8919-assign-1: Login page accessed with error: {error}")
        
        # Log additional error details if available for debugging
        error_description = request.args.get('error_description', '')
        if error_description:
            app.logger.warning(f"cst8919-assign-1: Error description: {error_description}")
    
    # Redirect user to Auth0 for authentication
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True),
        state=request.args.get('next', '/')  # Preserve intended destination
    )

@app.route("/logout")
def logout():
    """
    Logout route - terminates user session and logs out from Auth0
    Logs logout events for security monitoring and audit trails
    """
    # Get client IP address for security logging
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.now().isoformat()
    
    # Log user details before clearing session for audit purposes
    if "user" in session:
        user_info = session.get("user", {}).get('userinfo', {})
        user_id = user_info.get('sub', 'unknown')
        email = user_info.get('email', 'unknown')
        app.logger.info(f"cst8919-assign-1: User logged out - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")
    else:
        app.logger.info(f"cst8919-assign-1: Logout attempted without active session - IP: {client_ip}, Timestamp: {timestamp}")
    
    # Clear local session
    session.clear()
    
    # Redirect to Auth0 logout endpoint to terminate Auth0 session
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
    """
    Protected route - requires authentication to access
    Implements security logging for both authorized and unauthorized access attempts
    Supports both session-based and token-based authentication
    """
    # Get client IP address for security monitoring
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.now().isoformat()
    
    # Check for Bearer token in Authorization header (API access)
    auth_header = request.headers.get("Authorization", None)
    hasToken = auth_header and auth_header.startswith("Bearer ")
    
    # Verify user authentication (session or token)
    if "user" not in session and not hasToken:
        # Log unauthorized access attempt for security monitoring
        app.logger.warning(f"cst8919-assign-1: Unauthorized access attempt to /protected - IP: {client_ip}, Timestamp: {timestamp}")
        return redirect(url_for('login', next=request.path))
    
    # Log authorized access to protected route with user details
    user_info = session.get("user", {}).get('userinfo', {})
    user_id = user_info.get('sub', 'unknown')
    email = user_info.get('email', 'unknown')
    
    app.logger.info(f"cst8919-assign-1: Authorized access to /protected - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")
    
    # Render protected content with user session information
    return render_template("protected.html", session=session.get("user"), pretty=json.dumps(session.get("user"), indent=4))

# Application entry point
if __name__ == "__main__":
    # Run Flask development server
    # In production, use Gunicorn or similar WSGI server
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))