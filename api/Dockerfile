FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY model /app/model
COPY main.py /app/main.py

RUN pip install sentence-transformers gunicorn

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"]
