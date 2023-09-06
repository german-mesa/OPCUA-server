FROM python:3.7-slim

RUN pip install pymacnet

WORKDIR /opt/maccor_mockup

COPY ./maccor /opt/maccor_mockup

CMD [ "python" ,"./maccorserver.1.py"]