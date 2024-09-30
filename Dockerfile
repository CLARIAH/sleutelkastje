FROM node:alpine AS frontend-build

WORKDIR /app
COPY ./frontend/ /app
#RUN npm install && npm run build

FROM python:3.9-slim

ADD sleutelkastje ./sleutelkastje
ADD entrypoint.sh ./
ADD migrations ./migrations
#COPY --from=frontend-build /app/dist /frontend

RUN pip install -r sleutelkastje/requirements.txt


#CMD ["gunicorn", "-b", ":5000", "-t", "60", "-w", "1", "--threads", "4", "sleutelkastje:app"]

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 5000
