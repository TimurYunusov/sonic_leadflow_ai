FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
