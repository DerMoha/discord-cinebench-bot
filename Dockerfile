# Use an official Python runtime as a parent image
FROM python:3.9
# Set the working directory in the container
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app
# Create a database volume
VOLUME /app/database
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
# Run the bot when the container launches
CMD ["python", "cpu_bot.py"]
