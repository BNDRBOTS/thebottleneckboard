FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
COPY . .
EXPOSE 5000
# Use the PORT environment variable, default to 5000 for local dev
CMD gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} app:app
