# Flask Web Application

A Flask-based web application that demonstrates user authentication, logging, and server information capabilities. This project was created as part of CST8919 Lab 2, focusing on Azure Monitor integration and security monitoring.

## Features

- User authentication system
- Real-time logging with immediate flush
- Server information endpoint
- Flash messaging for user feedback
- Template-based rendering
- Test logging endpoint for debugging
- Azure Monitor integration
- Security alerting system

## Prerequisites

- Python 3.10
- pip (Python package installer)
- Azure subscription
- Azure Monitor workspace

## Setup

1. Clone the repository:
```bash
git clone https://github.com/RyanRen2023/cst8919lab2.git
cd cst8919lab2
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:
```bash
./startup.sh
```

2. Access the application:
- Main URL: `http://localhost:8000`
- Login page: `http://localhost:8000/login`

## Default Credentials

For testing purposes, use the following credentials:
- Username: `admin`
- Password: `password123`

## Logging

The application implements comprehensive logging with immediate flush capabilities:
- All logs are written to stdout/stderr
- Timestamps are included in log messages
- Different log levels (INFO, WARNING) are used for different events
- Logs are immediately flushed to ensure real-time visibility
- Logs are forwarded to Azure Monitor for analysis

## KQL Query

The following KQL query is used to detect potential brute force attacks by monitoring failed login attempts:

```kql
let timeframe = 50m;
let threshold = 5;
AppServiceConsoleLogs
| where TimeGenerated > ago(timeframe)
| where ResultDescription contains "Failed login attempt"
| summarize count() by bin(TimeGenerated, 1m), Username = extract("Username: ([^,]+)", 1, ResultDescription)
| where count_ > threshold
| project TimeGenerated, Username, FailedAttempts = count_
```

This query:
1. Looks at the last 5 minutes of logs
2. Filters for failed login attempts
3. Groups attempts by username and 1-minute intervals
4. Alerts when more than 3 failed attempts occur within a minute

## Testing

A test file `test-app.http` is included in the repository. This file contains HTTP requests to test various endpoints of the application. To use it:

1. Install the "REST Client" extension in VS Code
2. Open `test-app.http`
3. Click "Send Request" above any request to execute it

## Lab Learnings and Challenges

### What I Learned
- Setting up Azure Monitor integration with a Flask application
- Implementing real-time logging with immediate flush
- Writing effective KQL queries for security monitoring
- Configuring Azure alerts for security events
- Using HTTP test files for API testing

### Challenges Faced
- Ensuring logs were properly formatted for Azure Monitor ingestion
- Fine-tuning the KQL query to reduce false positives
- Coordinating alert timing with actual security events

### Improvements for Real-World Scenarios
1. Implement rate limiting at the application level
2. Add IP-based blocking after multiple failed attempts
3. Use more sophisticated detection patterns in KQL
4. Implement multi-factor authentication
5. Add session management and timeout
6. Use Azure Key Vault for credential management
7. Implement proper password hashing and security measures

## Demo Video

[Watch the demo video](https://youtu.be/lowlHTle_ws) showing:
- Application deployment
- Log generation and inspection in Azure Monitor
- KQL query usage
- Alert configuration and triggering

## Project Structure

```
.
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── templates/         # HTML templates
│   ├── login.html
│   └── success.html
├── test-app.http     # HTTP test file
├── startup.sh        # Startup script
└── README.md         # This file
```

## Development

The application runs in debug mode by default. For production deployment:
1. Set `debug=False` in `app.py`
2. Use a production-grade WSGI server
3. Configure proper security measures
4. Update the secret key
5. Configure proper Azure Monitor settings

