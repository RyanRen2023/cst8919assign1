# Assignment 1: Securing and Monitoring an Authenticated Flask App

A production-ready secure Flask application that demonstrates SSO authentication with Auth0, comprehensive user activity logging, and Azure Monitor integration for security monitoring and alerting.

## 🎯 Project Overview

This project combines the SSO implementation from Lab 1 with Azure deployment and monitoring from Lab 2 to create a secure, production-ready application. The app demonstrates secure integration between identity management (Auth0) and observability systems (Azure Monitor) for detecting suspicious user activities.

## ✨ Features

- **SSO Authentication**: Secure single sign-on using Auth0
- **Comprehensive Logging**: Detailed user activity tracking
- **Security Monitoring**: Real-time detection of suspicious activities
- **Azure Integration**: Full deployment and monitoring on Azure
- **Alert System**: Automated notifications for security events
- **Production Ready**: Secure configuration and best practices



## 🏗️ Architecture

![Archtecture](images/architecture.png)


## 📋 Prerequisites

- Python 3.10+
- Azure subscription
- Auth0 account
- GitHub account
- Azure CLI (optional)

## 🚀 Setup Instructions

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

### 2. Azure Setup

1. Create Azure App Service:
  
2. Enable Application Logging:

3. Configure Log Analytics:
   - Create Log Analytics workspace
   - Enable AppServiceConsoleLogs collection
   - Link to App Service

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

## 📊 Logging Implementation

The application implements comprehensive logging for security monitoring:

### Login Events
```python
# Successful login
app.logger.info(f"cst8919-lab3: Successful login - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")

# Failed login
app.logger.error(f"cst8919-lab3: Login failed - Error: {error_message}, IP: {client_ip}, Timestamp: {timestamp}")
```

### Protected Route Access
```python
# Authorized access
app.logger.info(f"cst8919-lab3: Authorized access to /protected - User ID: {user_id}, Email: {email}, IP: {client_ip}, Timestamp: {timestamp}")

# Unauthorized access
app.logger.warning(f"cst8919-lab3: Unauthorized access attempt to /protected - IP: {client_ip}, Timestamp: {timestamp}")
```

### Log Levels
- **INFO**: Successful logins, authorized access, user logout
- **WARNING**: Unauthorized access attempts, login errors
- **ERROR**: Login failures, system exceptions

## 🔍 Security Monitoring

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

## 🧪 Testing

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

## 📈 Demo Video

[Watch the demo video](https://youtu.be/your-demo-video-id) showing:

1. **Application Demo** (2 min):
   - App deployed on Azure with working Auth0 login
   - User authentication flow
   - Access to protected routes

2. **Logging Behavior** (3 min):
   - Real-time log generation
   - Different log levels and formats
   - User activity tracking

3. **Azure Monitor** (3 min):
   - Log Analytics workspace
   - Running KQL queries
   - Query results and analysis

4. **Alert System** (2 min):
   - Alert configuration
   - Triggered alert demonstration
   - Email notification (if possible)

## 🤔 Reflection

### What Worked Well
- Seamless integration between Auth0 and Flask
- Comprehensive logging captured all required events
- KQL queries effectively detected suspicious patterns
- Azure Monitor provided excellent observability
- Alert system responded quickly to security events

### Challenges Faced
- Coordinating Auth0 callback URLs with Azure deployment
- Fine-tuning KQL query to reduce false positives
- Ensuring consistent log format for parsing
- Managing environment variables securely

### Improvements for Production
1. **Enhanced Security**:
   - Implement rate limiting at application level
   - Add IP-based blocking after multiple failed attempts
   - Use Azure Key Vault for secret management
   - Implement session timeout and management

2. **Better Monitoring**:
   - Add more sophisticated detection patterns
   - Implement user behavior analytics
   - Create dashboards for security metrics
   - Add automated response actions

3. **Operational Excellence**:
   - Implement CI/CD pipeline
   - Add automated testing
   - Use infrastructure as code
   - Implement backup and disaster recovery

## 📁 Project Structure

```
cst8919-assignment1/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── protected.html
│   └── success.html
├── test-app.http         # HTTP test scenarios
├── deploy.sh             # Azure deployment script
├── gunicorn.conf.py      # Production server config
├── startup.sh            # Application startup script
├── .env.example          # Environment variables template
├── README.md             # This file
└── login_attempts.log    # Local log file (development)
```

## 🔧 Deployment

### Azure App Service Deployment

1. **Using Azure CLI**:
   ```bash
   az webapp deployment source config-local-git --name your-app-name --resource-group cst8919-assignment1
   git remote add azure <git-url-from-above-command>
   git push azure main
   ```

2. **Using GitHub Actions** (recommended):
   - Create `.github/workflows/deploy.yml`
   - Configure Azure credentials
   - Enable automatic deployment on push

### Production Considerations

- Use production-grade WSGI server (Gunicorn)
- Configure proper SSL/TLS certificates
- Set up monitoring and alerting
- Implement backup strategies
- Use Azure Application Insights for additional monitoring

## 📞 Support

For issues or questions:
- Check the demo video for detailed walkthrough
- Review Azure Monitor documentation
- Consult Auth0 documentation for authentication issues
- Check Flask and Azure App Service logs

## 📄 License

This project is created for educational purposes as part of CST8919 Cloud Security course.

---

**Note**: This application is designed for educational demonstration. For production use, implement additional security measures and follow security best practices.

