# Set environment variables
RESOURCE_GROUP="cst8919-lab3-rg"
LOCATION="eastus"
APP_SERVICE_PLAN="Ren00055AppServicePlan"
WEB_APP_NAME="lab3-app$(date +%s)"  # Ensure unique name

# Step 1: Create a Resource Group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Step 2: Create an App Service Plan (Linux-based)
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Step 3: Create a Web App with Python 3.11 runtime
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $WEB_APP_NAME \
  --runtime "PYTHON|3.10"

# Step 4: Deploy your app using ZIP package (app.zip must contain your code)
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --src app.zip

# Step 5: Print the deployed URL
echo "Deployment complete. Visit: https://$WEB_APP_NAME.azurewebsites.net"