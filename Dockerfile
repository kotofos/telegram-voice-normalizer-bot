FROM python:3.9 

RUN apt-get update && apt-get install ffmpeg -y && rm -rf /var/lib/apt/lists/*

ADD bot.py requirements.txt /
RUN pip install -r requirements.txt --no-cache-dir

CMD [ "python", "bot.py" ]
