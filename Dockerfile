# Use Python image with Azure Functions
FROM mcr.microsoft.com/azure-functions/python:4-python3.14

# Set working directory
WORKDIR /home/site/wwwroot

# Copy function code into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt azure-functions

# Enable console logging
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    PYTHONUNBUFFERED=1

# Start the Azure Functions host
CMD ["func", "start", "--python"]