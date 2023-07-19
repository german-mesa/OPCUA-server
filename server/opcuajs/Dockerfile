FROM node:14-slim

WORKDIR /opt/opc_mockup/datagenerator

COPY ./opcuajs /opt/opc_mockup/datagenerator

RUN npm install node-opcua
RUN npm install logging
RUN npm install random

CMD [ "node", "./opcuaserver.4.js" ]
