FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

# IMPORTANT: run inference.py, NOT app.py
CMD ["python", "inference.py"]