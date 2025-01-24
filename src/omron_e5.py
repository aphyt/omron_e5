__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import binascii
import time
import serial


def calculate_bcc(command: str):
    bcc = 0
    for character in command:
        bcc ^= ord(character)
    return bcc

class CWFPDUStructureCommand:
    def __init__(self, main_request_code: int, sub_request_code: int, data: str=''):
        self.main_request_code = main_request_code
        self.sub_request_code = sub_request_code
        self.data = data
        self.pdu_string = f'{main_request_code:02X}{sub_request_code:02X}{data}'


class CWFCommandFrame:
    def __init__(self, node_number: int, sub_address: int, sid: int, command_text: str):
        self.node_number = node_number
        self.sub_address = sub_address
        self.sid = sid
        self.command_text = command_text
        self.calc_range_text = f'{node_number:02}{sub_address:02}{sid:01}{command_text}' + chr(3)
        self.frame = chr(2) + self.calc_range_text + chr(calculate_bcc(self.calc_range_text))


class CWFPDUStructureResponse:
    def __init__(self, process_data: bytes):
        self.main_request_code = process_data[0:2]
        self.sub_request_code = process_data[2:4]
        self.main_response_code = process_data[4:6]
        self.sub_response_code = process_data[6:8]
        self.data = process_data[8:]


class CWFResponseFrame:
    def __init__(self, response_frame: bytes):
        self.node_number = int(response_frame[1:3])
        self.sub_address = int(response_frame[3:5])
        self.end_code = int(response_frame[5:7])
        self.service_response_pdu = CWFPDUStructureResponse(response_frame[7:-2])
        self.bcc = response_frame[-1:]


class E5:
    def __init__(self):
        self.port = serial.Serial()

    def connect(self, port_name: str, baud_rate: int=9600, data_length: int=7,
                parity = serial.PARITY_EVEN, stop_bits = serial.STOPBITS_TWO, timeout: int = 1):
        self.port = serial.Serial(port=port_name, baudrate=baud_rate, bytesize=data_length,
                                  parity=parity, stopbits=stop_bits, timeout=timeout)

    def read_process_value(self, node):
        pv = self.read_variable_area(node, 'C0',0, 1)
        return int(pv.service_response_pdu.data, 16)

    def read_variable_area(self, node: int, variable_type: str, start_address: int,
                      number_of_elements: int, bit_position: int=0):
        if variable_type in ['C0', 'C1', 'C2']:
            number_of_elements = f'{number_of_elements:04X}'
        elif variable_type in ['80', '81', '82']:
            number_of_elements = f'{number_of_elements:04X}'
        else:
            raise ValueError('variable_type must be: CO, C1, C2, 80, 81, or 82')
        data = f'{variable_type}{start_address:04X}{bit_position:02X}{number_of_elements}'
        pdu_command = CWFPDUStructureCommand(1, 1, data)
        response = self._send_command(node, pdu_command.pdu_string)
        return response


    def write_variable_area(self, variable_type: str, start_address: int,
                            write_data: bytes, bit_position: int=0):
        pass

    def read_controller_attributes(self, node: int):
        pdu_command = CWFPDUStructureCommand(5,3)
        response = self._send_command(node, pdu_command.pdu_string)
        model_number = response.service_response_pdu.data[0:10].decode('utf-8')
        buffer_size_hex_text = response.service_response_pdu.data[10:].decode('utf-8')
        buffer_size = int(buffer_size_hex_text, 16)
        return model_number, buffer_size

    def _send_command(self, node: int, text: str, read_delay=.1):
        command_frame = CWFCommandFrame(node, 0, 0, text)
        response = self._send_command_frame(command_frame.frame, read_delay)
        response_frame = CWFResponseFrame(response)
        return response_frame

    def _send_command_frame(self, frame: str, read_delay):
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()
        self.port.write(frame.encode('utf-8'))
        time.sleep(read_delay)
        response = self.port.read_all()
        return response


    def disconnect(self):
        self.port.close()