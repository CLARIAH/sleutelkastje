FROM python:3.9-slim

ADD scripts ./

RUN pip install -r requirements.txt

ENV OIDC_SERVER: "https://testauthentication.di.huc.knaw.nl"
ENV OIDC_CLIENT_ID: "nl_knaw_huc_di_sd_todo-j" 
ENV OIDC_CLIENT_SECRET: "5RKBN2siBqLq9MUHXlKZ" 

CMD ["gunicorn", "-b", ":5001", "-t", "60", "-w", "1", "--threads", "4", "app:app"]

EXPOSE 5001
