# python-app/Dockerfile
FROM python:3.8

# Add your application files
COPY . /app

# Set the working directory
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port your application runs on
EXPOSE 3000



# Command to run your application
CMD ["python", "server.py"]
