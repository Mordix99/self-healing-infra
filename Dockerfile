FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app


COPY requirments.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN ansible-galaxy collection install kubernetes.core

COPY app.py remediate_nginx.yml ./

EXPOSE 5000

CMD ["python", "app.py"]


