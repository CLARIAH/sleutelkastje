FROM python:3.9-slim

ADD sleutelkastje ./sleutelkastje
ADD entrypoint.sh ./
ADD migrations ./migrations
ADD seeds ./seeds

RUN pip install -r sleutelkastje/requirements.txt

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 5000
