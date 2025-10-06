# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app ./app

# Make port 8000 available outside this container
EXPOSE 8000

# Run the FastAPI application
CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]