# Use Python 3.11 slim version as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary Python files
COPY .env .
COPY db_interaction.py .
COPY schedule.py .
COPY custom_logging.py .
COPY bot.py .

# Run the bot.py script
CMD ["python", "bot.py"]

#docker build -t jkuclassnotifier .