# Assignment 1: Securing and Monitoring an Authenticated Flask App

A production-ready secure Flask application that demonstrates SSO authentication with Auth0, comprehensive user activity logging, and Azure Monitor integration for security monitoring and alerting.

## Project Overview

This project combines the SSO implementation from Lab 1 with Azure deployment and monitoring from Lab 2 to create a secure, production-ready application. The app demonstrates secure integration between identity management (Auth0) and observability systems (Azure Monitor) for detecting suspicious user activities.

## Features

- **SSO Authentication**: Secure single sign-on using Auth0
- **Comprehensive Logging**: Detailed user activity tracking
- **Security Monitoring**: Real-time detection of suspicious activities
- **Azure Integration**: Full deployment and monitoring on Azure
- **Alert System**: Automated notifications for security events
- **Production Ready**: Secure configuration and best practices

## Architecture

![Architecture](images/architecture.png)

## 📋 Prerequisites

- Python 3.10+
- Azure subscription
- Auth0 account
- GitHub account
- Azure CLI (optional)

## Setup Instructions

### 1. Auth0 Configuration

1. Create an Auth0 application:
   - Go to [Auth0 Dashboard](https://manage.auth0.com/)
   - Create a new "Regular Web Application"
   - Configure callback URLs: `http://your-app-name.azurewebsites.net/callback`
   - Note down: `Domain`, `Client ID`, `Client Secret`

2. Configure Auth0 settings:
   - Allowed Callback URLs: `http://your-app-name.azurewebsites.net/callback`
   - Allowed Logout URLs: `http://your-app-name.azurewebsites.net`
   - Allowed Web Origins: `http://your-app-name.azurewebsites.net`

#### Auth0 Basic Settings
![Auth0 Basic Settings](images/auth0-basic.png)

#### Auth0 URL Configuration
![Auth0 URL Configuration](images/auth0-url.png)

### 2. Azure Setup

1. Create Azure App Service:

2. Enable Application Logging:

3. Configure Log Analytics:
   - Create Log Analytics workspace
   - Enable AppServiceConsoleLogs collection
   - Link to App Service

#### App Service Environment variables Configuration
![App Service Environment](images/app-environments.png)

#### Diagnostic Settings
![Diagnostic Settings](images/Diagnostic setting.png)

### 3. Environment Configuration

1. Create `.env` file in Local environment:
   ```env
   AUTH0_CLIENT_ID=your_auth0_client_id
   AUTH0_CLIENT_SECRET=your_auth0_client_secret
   AUTH0_DOMAIN=your-tenant.auth0.com
   APP_SECRET_KEY=your_secure_secret_key
   ```

2. Set Azure App Settings:

### 4. Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/RyanRen2023/cst8919assign1.git
   cd cst8919assign1
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run locally:
   ```bash
   python app.py
   ```

## Logging Implementation

The application implements comprehensive logging for security monitoring:

### Login Events
```python
# Successful login
app.logger.info(f"cst8919-assign-1: Successful login - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")


# Failed login
app.logger.error(f"cst8919-assign-1: Auth0 login failed - Error: {error}, Description: {error_description}, IP: {client_ip}, Timestamp: {timestamp}")

```

### Protected Route Access
```python
# Authorized access
app.logger.info(f"cst8919-assign-1: Authorized access to /protected - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")

# Unauthorized access
app.logger.warning(f"cst8919-assign-1: Unauthorized access attempt to /protected - IP: {client_ip}, Timestamp: {timestamp}")

```

### Log Levels
- **INFO**: Successful logins, authorized access, user logout
- **WARNING**: Unauthorized access attempts, login errors
- **ERROR**: Login failures, system exceptions

## Security Monitoring

### KQL Query for Excessive Access Detection

**Authorized access**
```kql
AppServiceConsoleLogs
| where TimeGenerated > ago(15m)
| where ResultDescription has "Authorized access to /protected"
| extend user_id = extract("User ID: ([^,]+)", 1, ResultDescription)
| extend timestamp = extract("Timestamp: ([^,]+)", 1, ResultDescription)
| summarize access_count = count(), latest_access = max(TimeGenerated) by user_id
| where access_count > 10
| project user_id, latest_access, access_count
```

**Unauthorized access attempt to /protected**
```kql
AppServiceConsoleLogs
| where TimeGenerated > ago(15m)
| where ResultDescription has "Unauthorized access attempt to /protected"
| extend ip = extract("IP: ([^:]+)", 1, ResultDescription)
| summarize attempt_count = count(), latest_attempt = max(TimeGenerated) by ip
| where attempt_count > 10
| project ip, latest_attempt, attempt_count
```

This query:
1. Monitors the last 15 minutes of logs
2. Filters for authorized access to `/protected` route
3. Extracts user ID and email from log messages
4. Groups by user and counts accesses
5. Alerts when any user exceeds 10 accesses in 15 minutes

### Azure Alert Configuration

1. **Alert Rule**:
   - Resource: Log Analytics workspace
   - Condition: Custom log search
   - Query: Use the KQL query above
   - Threshold: 0 (alert on any result)

2. **Action Group**:
   - Email notifications
   - Severity: 3 (information)
   - Recipients: my email address

3. **Alert Details**:
   - Name: "Unauthorized Protected access attempt"
   - Description: "User accessed /protected route more than 10 times in 15 minutes"
   - Severity: Low

#### Alert Rules Configuration
![Alert Rules](images/Alert%20rules.png)

#### Alert Fired Notification
![Alert Fired](images/Alert%20fired.png)

## Testing

### Test File: `test-app.http`

The repository includes a comprehensive test file with scenarios:

```http
### Test 1: Access home page (should redirect to login)
GET http://localhost:3000/

### Test 2: Access login page
GET http://localhost:3000/login

### Test 3: Access protected route without authentication (should redirect to login)
GET http://localhost:3000/protected

### Test 4: Simulate multiple access attempts (for testing alerts)
# Run this multiple times to test the KQL query
GET http://localhost:3000/protected
Authorization: Bearer your_auth_token_here
```

### Testing Scenarios

1. **Normal Usage**:
   - Login with valid Auth0 credentials
   - Access protected routes normally
   - Verify logging works correctly

2. **Security Testing**:
   - Attempt unauthorized access to `/protected`
   - Test multiple rapid access attempts
   - Verify alerts are triggered

3. **Monitoring Validation**:
   - Check Azure Monitor logs
   - Run KQL queries manually
   - Verify alert notifications

## Demo Video

[Watch the demo video](https://youtu.be/qcb6nnM-joQ) 


