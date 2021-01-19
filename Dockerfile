FROM python
WORKDIR /mydir
ADD . /mydir
RUN pip install -r requirements.txt
ENV NAME packages 
CMD ["python3", "package-sql.py"]