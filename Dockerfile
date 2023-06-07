FROM python:3.9-slim

ADD scripts ./

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", ":5000", "-t", "60", "-w", "1", "--threads", "4", "app:app"]

EXPOSE 5000
