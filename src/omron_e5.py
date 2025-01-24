import binascii
import time

import serial


def calculate_bcc(command: str):
    bcc = 0
    for character in command:
        bcc ^= ord(character)
    return bcc


def command_frame(node_number: int, command_text):
    calc_range_text = f'{node_number:02}000{command_text}' + chr(3)
    frame = chr(2) + calc_range_text + chr(calculate_bcc(calc_range_text))
    return frame


class E5:
    def __init__(self):
        self.port = serial.Serial()

    def connect(self, port_name: str, baud_rate: int=9600, data_length: int=7,
                parity = serial.PARITY_EVEN, stop_bits = serial.STOPBITS_TWO, timeout: int = 1):
        self.port = serial.Serial(port=port_name, baudrate=baud_rate, bytesize=data_length,
                                  parity=parity, stopbits=stop_bits, timeout=timeout)

    def send_command(self, node: int, text: str):
        frame = command_frame(node, text)
        return  self.send_command_frame(frame)

    def send_command_frame(self, frame: str):
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()
        self.port.write(frame.encode('utf-8'))
        time.sleep(.1)
        response = self.port.read_all()
        return response.decode('utf-8')


    def disconnect(self):
        self.port.close()