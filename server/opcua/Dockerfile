FROM python:3.7-slim

RUN pip install asyncua==1.0.2

WORKDIR /opt/opc_mockup/datagenerator

COPY ./opcua /opt/opc_mockup/datagenerator

CMD [ "python" ,"./opcuaserver.4.py"]