# Import necessary libraries
import logging
import pymacnet
import pymacnet.maccorspoofer
import pymacnet.messages

# Create a logger for this module
_logger = logging.getLogger(__name__)

# Configuration for the Maccor Spoofer server
MACCOR_SPOOFER_CONFIG = {
    "server_ip": "127.0.0.1",  # IP address of the Maccor Spoofer server
    "json_port": 7889,         # Port for JSON messages
    "tcp_port": 7890,          # Port for TCP messages
    "num_channels": 128        # Number of channels
}

# Configuration for the testing interface
CYCLER_INTERFACE_CONFIG = {
    'server_ip': MACCOR_SPOOFER_CONFIG['server_ip'],        # IP of the server
    'json_msg_port': MACCOR_SPOOFER_CONFIG['json_port'],    # Port for JSON messages
    'bin_msg_port': MACCOR_SPOOFER_CONFIG['tcp_port'],      # Port for binary messages
    'msg_buffer_size_bytes': 4096                           # Size of the message buffer in bytes
}


def main():
    # Create an instance of the Maccor Spoofer using the configuration
    maccor_spoofer = pymacnet.maccorspoofer.MaccorSpoofer(MACCOR_SPOOFER_CONFIG)

    # Start the Maccor Spoofer server
    _logger.info("Starting server...")
    maccor_spoofer.start()
    
     # Run the server continuously
    while True: 
        try:
            # Create a CyclerInterface for testing
            _logger.info("Creating CyclerInterface instance...")
            cycler_interface = pymacnet.CyclerInterface(CYCLER_INTERFACE_CONFIG)

            # Read system information from the CyclerInterface
            _logger.info("Reading system information....")    
            system_info = cycler_interface.read_system_info()
            assert (system_info == pymacnet.messages.rx_system_info_msg['result'])

            # Read general information from the CyclerInterface
            _logger.info("Reading general information...")    
            general_info = cycler_interface.read_general_info()
            assert (general_info == pymacnet.messages.rx_general_info_msg['result'])

            # Read channel statuses from the CyclerInterface
            _logger.info("Reading channel statuses...")    
            channel_statues = cycler_interface.read_all_channel_statuses()
            assert (channel_statues ==
                    pymacnet.messages.rx_channel_status_multiple_channels['result']['Status'])

        except KeyboardInterrupt:
            _logger.info("Received KeyboardInterrupt. Stopping server...")
            maccor_spoofer.stop()
            break  # Exit the loop on Ctrl+C


if __name__ == "__main__":
    # Configure logging to display INFO-level messages
    logging.basicConfig(level=logging.INFO)

    # Run the main function when the script is executed
    main()
