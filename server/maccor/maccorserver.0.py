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


def main():
    # Create an instance of the Maccor Spoofer using the configuration
    maccor_spoofer = pymacnet.maccorspoofer.MaccorSpoofer(MACCOR_SPOOFER_CONFIG)

    # Start the Maccor Spoofer server
    _logger.info("Starting server...")
    maccor_spoofer.start()
    
     # Run the server continuously
    while True: 
        try:
            pass

        except KeyboardInterrupt:
            _logger.info("Received KeyboardInterrupt. Stopping server...")
            maccor_spoofer.stop()
            break  # Exit the loop on Ctrl+C


if __name__ == "__main__":
    # Configure logging to display INFO-level messages
    logging.basicConfig(level=logging.INFO)

    # Run the main function when the script is executed
    main()
