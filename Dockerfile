# Use an official Python runtime as a parent image
FROM python:3.12

# Setting environment variable for Python to not write .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# Setting environment variable for Python to not spam the container with unnecessary output
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY venv /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run main.py when the container launches
CMD ["python", "main.py"]