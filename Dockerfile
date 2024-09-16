FROM python:3.9-slim

ADD sleutelkastje ./sleutelkastje

RUN pip install -r sleutelkastje/requirements.txt


#CMD ["gunicorn", "-b", ":5000", "-t", "60", "-w", "1", "--threads", "4", "sleutelkastje:app"]

ENTRYPOINT sleutelkastje/entrypoint.sh

EXPOSE 5000
