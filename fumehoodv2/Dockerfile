# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install OpenCV dependencies
RUN apt-get update && \
    apt-get install -y libopencv-dev

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 443

# Run app.py when the container launches
CMD ["python", "app.py"]
