FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY model /app/model
COPY main.py /app/main.py

RUN pip install sentence-transformers

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
