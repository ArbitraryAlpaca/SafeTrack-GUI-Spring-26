import serial.tools.list_ports

def get_microcontroller_port():
    """Returns the port name string if found, else None."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Looking for typical Linux/Pi serial device names
        if 'ttyACM' in port.device or 'ttyUSB' in port.device:
            print(f"Found microcontroller at: {port.device}")
            return port.device
    return None
