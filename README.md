# OPCUA-server
OPCUA-server simulation using asyncua

This code is an implementation of an OPC UA server in Python using the asyncua library. 
The server simulates multiple equipment nodes with various tags for temperature, pressure, torque, 
humidity, light, voltage, and watts. The values of these tags are continuously updated with random 
simulated data.

The code does the following:
1.Imports the necessary libraries: asyncio, logging, and random.
2.Defines a function to calculate the check digit for GS1 serial numbers.
3.Defines a function to slice a list into equally sized pieces.
4.Defines a function to generate GS1 serial numbers for each cell.
5.Defines a function to generate simulated data for each tag.
6.Defines a function to create an equipment node under a parent node and add tags for the equipment.
7.Defines a function to update tags for each equipment.
8.Defines the main function that initializes the OPC UA server, sets up the server's endpoint, registers a namespace, and creates equipment nodes and their respective tags.
9.Starts the server and continuously updates the variables with new simulated data.

To run the code, you need to have Python 3.6 or higher installed and install the "asyncua" library 
using pip. Then, update the server endpoint, namespace, and other settings if necessary, and run 
the script.
    python opcuaserver.4.py

To deploy in your Docker environment just go to the server folder and execute:
    docker compose up --build -d

For additional details, you can read this blog:
https://medium.com/@muhammadfaiznoh/getting-started-with-opc-ua-in-docker-c68a883d5c65
