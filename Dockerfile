FROM python:3.8.0-slim

# Copy local code to the container image
COPY templates /app/templates
COPY .env /app/.env
COPY main.py /app/main.py
COPY get_relevant_page.py /app/get_relevant_page.py
COPY requirements.txt /app/requirements.txt
COPY function.py /app/function.py
COPY constant.py /app/constant.py
COPY client_secret.json /app/client_secret.json
COPY medical-docu-dec5db602577.json /app/medical-docu-dec5db602577.json
COPY static/images/google-logo.png /app/static/images/google-logo.png
# Sets the working directory
WORKDIR /app

# Upgrade PIP
RUN pip install --upgrade pip
# RUN pip3 install --user -U nltk
# RUN python -m nltk.downloader all-corpora
#Install python libraries from requirements.txt
RUN pip3 install -r requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/medical-docu-dec5db602577.json
# Set $PORT environment variable
ENV PORT 8080
EXPOSE 8080
# Run the web service on container startup
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 600 main:app