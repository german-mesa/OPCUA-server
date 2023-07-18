"""
OPC UA Python Server with Simulated Data

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
    docker compose up --build -d

For additional details, you can read this blog:
https://medium.com/@muhammadfaiznoh/getting-started-with-opc-ua-in-docker-c68a883d5c65
"""


# Required imports


import asyncio
import logging
import random
from asyncua import Server, ua

_logger = logging.getLogger(__name__)


# Function to calculate check digit for GS1 serial numbers

def calculate_check_digit(gs1_prefix, serial_number):
    gs1_data = gs1_prefix + serial_number
    total = 0

    for i, digit in enumerate(gs1_data):
        weight = 3 if i % 2 == 0 else 1
        total += int(digit) * weight

    check_digit = (10 - (total % 10)) % 10

    return check_digit

# Function to slice a list in equally sized pieces


def chop_serial_list(serials, piece_size):
    return [serials[i:i + piece_size] for i in range(0, len(serials), piece_size)]


# Function to generate GS1 serial numbers for each cell

def generate_serial_list(gs1_prefix, num_serials):
    gs1_serials = []

    for serial in range(num_serials):
        serial_number = str(serial).zfill(9)
        check_digit = calculate_check_digit(gs1_prefix, serial_number)
        gs1_serial = int(gs1_prefix + serial_number + str(check_digit))
        gs1_serials.append(gs1_serial)

    return gs1_serials


# Function to generate simulated data for each tag


def generate_simulated_data(serial_number=0):
    return {
        "SN": serial_number,
        "Temperature": random.uniform(20, 30),
        "Pressure": random.uniform(1000, 1050),
        "Torque": random.uniform(5, 30),
        "Humidity": random.uniform(40, 60),
        "Light": random.uniform(500, 1000),
        "Voltage": random.uniform(110, 240),
        "Watts": random.uniform(50, 500)
    }

# Function to create an equipment node under the parent_node with the given equipment_name
# and add tags for the equipment using the namespace_idx


async def create_equipment_node(parent_node, equipment_name, namespace_idx):
    # Create an object node for the equipment
    equipment_node = await parent_node.add_object(namespace_idx, equipment_name)
    tags = {}

    # Add variables for each tag to the equipment node
    for tag_name in generate_simulated_data().keys():
        if tag_name == "SN":
            tags[tag_name] = await equipment_node.add_variable(
                namespace_idx, tag_name, 0)
        else:
            tags[tag_name] = await equipment_node.add_variable(
                namespace_idx, tag_name, 0.0)

    return tags

# Function to update tags for each equipment


async def update_tags_for_equipment(equipment_name, tags, serial_number):
    # Generate random time delay (in seconds) based on normal distribution
    time_delay = abs(random.gauss(3, 0.25))
    await asyncio.sleep(time_delay)

    data = generate_simulated_data(serial_number)
    for tag_name, value in data.items():
        await tags[tag_name].write_value(value)

    if data['SN'] != 0:
        _logger.info(
            f"Cell created with SN {data['SN']} for Equipment {equipment_name}")
    else:
        _logger.error(f"Faulty cell created for Equipment {equipment_name}")


async def main():
    # Initialize the OPC UA server
    server = Server()
    await server.init()

    # Set up the server's endpoint
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.set_server_name("Battery Manufacturing Server")

    # set all possible endpoint policies for clients to connect through
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign,
        ]
    )

    # setup our own namespace
    uri = "http://battery.opcua.github.io"
    idx = await server.register_namespace(uri)

    # Set up the object node
    objects = server.get_objects_node()
    simulated_data_node = await objects.add_object(idx, "SimulatedData")

    # Create equipment nodes and their respective tags
    _logger.info("Create equipment nodes and their respective tags")
    num_equipments = 4
    equipments = {}
    for i in range(num_equipments):
        equipment_name = f"Equipment_{i + 1}"
        equipments[equipment_name] = await create_equipment_node(
            simulated_data_node, equipment_name, idx)

    # Create S/N batch
    _logger.info("Create S/N batch")
    buffer_serials = generate_serial_list("123", 1000000)

    # Start the server
    async with server:
        _logger.info("Starting server!")

        # Main loop to continuously update the variables with new simulated data
        while True:
            # Create a list of tasks to run asynchronously
            tasks = []

            for equipment_name, tags in equipments.items():
                # Generate a random number between 0 and 1
                random_number = random.random()

                # Define the condition for popping the first number
                condition = random_number > 0.05

                if condition:
                    # Get and delete the first number from the list
                    serial_number = buffer_serials.pop(0)
                else:
                    # Defective cell
                    serial_number = 0

                task = update_tags_for_equipment(
                    equipment_name, tags, serial_number)
                tasks.append(task)

            # Run the tasks concurrently with different time delays
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # optional: setup logging
    # logger = logging.getLogger("asyncua.address_space")
    # logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger("asyncua.internal_server")
    # logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger("asyncua.binary_server_asyncio")
    # logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger("asyncua.uaprocessor")
    # logger.setLevel(logging.DEBUG)

    asyncio.run(main())
