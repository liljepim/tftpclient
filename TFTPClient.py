import socket
import os
import sys
import struct

# Global Variables for TFTP op code

RRQ = 1
WRQ = 2
DATA = 3
ACK = 4
ERROR = 5

# Global Variables for Error Code

ERR_NOT_DEFINED = 0
ERR_FILE_NOT_FOUND = 1
ERR_ACC_VIOLATION = 2
ERR_DISK_FULL = 3
ERR_ILLEGAL_TFTP_OP = 4
ERR_UNNKOWN_ID = 5
ERR_FILE_EXISTS = 6
ERR_NO_USER = 7

# Error messages
ERR_MESSAGE = {
    0 : "Not Defined",
    1 : "File not found",
    2 : "Access Violation",
    3 : "Disk full or allocation exceeded",
    4 : "Illegal TFTP Operation",
    5 : "Unkown Transfer ID",
    6 : "File already exists",
    7 : "No such user"
}

# Ports and Default TFTP Configurations

TFTP_PORT = 69
BLK_SIZE = 512
TIMEOUT = 5



# Request Format: opcode - 0 - filename - 0 - modes
def send_request(socket, opcode, filename, serverAddress, mode='octet'):
    request_packet = struct.pack('!H', opcode) + filename.encode('utf-8') + b'\0' + mode.encode() + b'\0'
    socket.sendto(request_packet, (serverAddress, 69))

def tftp_client(serverAddress, port):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.bind((serverAddress, port))
    
    while True:
        print(f'[1] Download File\n[2] Upload File\n[3] Exit')
        choice = int(input("Input: "))
        match choice:
            case 1:
                print("Download File")
                send_request(clientSocket, RRQ, 'new.txt', "192.168.0.20")
            case 2:
                print("Upload File")
            case 3:
                print("Closing client application")
                break
            case _:
                print("Invalid Input! Try again!")
        

if __name__ == '__main__':
    tftp_client('localhost', 69)