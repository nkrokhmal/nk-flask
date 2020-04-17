from python:3.6

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

EXPOSE 5000

cmd ["python", "hello.py", "-e", "production"]

#cmd ["cmd.sh"]
