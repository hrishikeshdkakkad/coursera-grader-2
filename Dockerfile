FROM python:3.9-alpine
# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the dependencies file to the working directory
COPY requirements.txt ./

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script into the container
COPY . .

# Set environment variable
ENV USER_FILE_PATH=/shared/submission/submission.txt
ENV OUTPUT_PATH=/shared/feedback.json

# Command to run on container start
CMD [ "python", "src/main.py" ]
