FROM python

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y sqlite3 libsqlite3-dev
RUN pip install -r requirements.txt

WORKDIR /db
ADD . /db
CMD ["python3", "package-sql.py"]
