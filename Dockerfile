FROM python

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y sqlite3 libsqlite3-dev

WORKDIR /db
ADD . /db
CMD ["python3", "packages-sql.py"]
