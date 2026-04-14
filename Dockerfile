FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Tell Waitress to listen on the port Google Cloud provides
CMD ["python", "-c", "from waitress import serve; from main import app; import os; serve(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))"]