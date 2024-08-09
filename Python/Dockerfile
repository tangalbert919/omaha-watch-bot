 FROM docker.io/python:3.12.4-bullseye

 WORKDIR /src
 ENV TOKEN=
 ENV WEBHOOK_URL=
 ADD bot.py /src
 ADD requirements.txt /src
 ADD android.json /src
 ADD utils.py /src
 ADD checkin/checkin_generator_pb2.py /src/checkin
 RUN python -m pip install -r requirements.txt

 VOLUME [ "/src" ]
 EXPOSE 4000
 ENTRYPOINT python bot.py --token ${TOKEN} --webhook-url ${WEBHOOK_URL}