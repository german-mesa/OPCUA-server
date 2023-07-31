FROM node:14-slim AS base

RUN npm install node-opcua
RUN npm install logging
RUN npm install random

FROM base AS final

WORKDIR /opt/opc_mockup/datagenerator
COPY ./opcuajs /opt/opc_mockup/datagenerator

CMD [ "node", "./opcuaserver.1.js" ]
