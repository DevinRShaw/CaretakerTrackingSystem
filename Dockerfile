FROM python:3.12.3

WORKDIR /app/ 

COPY main.py /app/ 
COPY requirements.txt /app/ 
COPY templates/ /app/templates/

RUN pip install -r /app/requirements.txt 


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]