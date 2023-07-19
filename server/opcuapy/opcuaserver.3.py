"""
OPC UA Python Server with Simulated Data

Description:
This script creates an OPC UA server that simulates multiple equipment nodes
with tags for temperature, pressure, torque, humidity, light, voltage, and watts.
Each equipment node contains its own set of tags, and the values are continuously
updated with random simulated data.

https://medium.com/@muhammadfaiznoh/getting-started-with-opc-ua-in-docker-c68a883d5c65

Prerequisites:
- Python 3.6 or higher
- Install the "asyncua" library using pip: pip install asyncua

Instructions:
1. Make sure you have installed the required library.
2. Update the server endpoint, namespace, and other settings in the script, if necessary.
3. Run the script: 
    python opcuaserver.3.py
    docker compose up --build -d
4. The server will start, and you can connect to it using an OPC UA client.
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
    num_equipments = 4
    equipments = {}
    for i in range(num_equipments):
        equipment_name = f"Equipment_{i + 1}"
        equipments[equipment_name] = await create_equipment_node(
            simulated_data_node, equipment_name, idx)

    # Create S/N batch
    buffer_serials = generate_serial_list("123", 1000000)
    buffer_pieces = chop_serial_list(buffer_serials, num_equipments)

    # Start the server
    async with server:
        _logger.info("Starting server!")

        index_pieces = 0

        # Main loop to continuously update the variables with new simulated data
        while True:
            # Generate random time delay (in seconds) based on normal distribution
            time_delay = abs(random.gauss(1, 0.25))

            # Updated variables based on time delay
            for index, (equipment_name, tags) in enumerate(equipments.items()):
                await asyncio.sleep(time_delay)

                data = generate_simulated_data(
                    buffer_pieces[index_pieces][index])
                for tag_name, value in data.items():
                    await tags[tag_name].write_value(value)

                _logger.info("Cell created with SN " + str(data["SN"]))

            # Update index and check if item exists in buffer
            index_pieces = index_pieces + 1


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
