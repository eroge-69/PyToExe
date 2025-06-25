import random
from datetime import datetime
import time
class TemperatureSensor:
    def __init__(self, interface_type, port=None, data_format=None, data_length=None, payload_info=None, address=None):
        self.interface_type = interface_type
        self.port = port
        self.data_format = data_format
        self.data_length = data_length
        self.payload_info = payload_info
        self.address = address

    def read_data(self):
        """
        Emulates reading data from a sensor.
        In a real application, this would involve actual hardware interaction.
        """
        temperature = round(random.uniform(18.0, 30.0), 2)
        timestamp = datetime.now() # Store as datetime object for PostgreSQL
        
        sensor_data = {
            "timestamp": timestamp,
            "interface_type": self.interface_type,
            "port": self.port,
            "temperature": temperature,
            "raw_data": f"some_raw_data_for_{self.interface_type}",
            "address": self.address
        }
        return sensor_data

