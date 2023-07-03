FROM python:3.9-slim

ADD scripts ./

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", ":5001", "-t", "60", "-w", "1", "--threads", "4", "app:todo"]

EXPOSE 5001
