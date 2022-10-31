FROM python:3.9 

RUN apt-get update && apt-get install ffmpeg -y

ADD . /
RUN pip install -r requirements.txt

CMD [ "python" bot.py" ]
