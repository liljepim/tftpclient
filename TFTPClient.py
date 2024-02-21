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
def send_request(socket, opcode, filename, serverAddress, blksize, mode='octet'):
    request_packet = struct.pack('!H', opcode) + filename.encode('utf-8') + b'\0' + mode.encode('utf-8') + b'\0' + "blksize".encode('utf-8') + b'\0' + str(blksize).encode('utf-8') + b'\0'
    print(len(request_packet))
    print(request_packet)
    socket.sendto(request_packet, serverAddress)

def receive_packet(sock, blksize):
    data, address = sock.recvfrom(blksize + 4)
    opcode = struct.unpack('!H', data[:2])[0]
    print(len(data))
    return opcode, data[4:], address[1], len(data)

def receive_oack(sock):
    data, address = sock.recvfrom(4)
    opcode = struct.unpack('!H', )

def send_packet(sock, opcode, blknum, data):
    sock.send(data)

def tftp_client(clientAddress, port):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.bind((clientAddress, port))
    server_ip = input("Please enter IP address of server: ")
    server_address = (server_ip, 69)
    while True:
        print(f'[1] Download File\n[2] Upload File\n[3] Exit')
        choice = int(input("Input: "))
        serverPort = 69
        match choice:
            case 1:
                filename = input("Please enter filename of file to download: ")
                blockNumber = 1
                bfile = open(filename, 'wb')
                try:
                    blksize = int(input("Enter desired block size (Default - 512): "))
                    send_request(clientSocket, RRQ, filename, server_address, blksize)
                    while True:
                        # Receive data packet from the server
                        opcode, received_data, serverPort, size = receive_packet(clientSocket, blksize)
                        if opcode == 3:  # Data packet
                            # Process the received data (write to file, print, etc.)
                            print(f"Received data block {blockNumber}")
                            print(received_data)
                            bfile.write(received_data)
                            # ...

                            # Send acknowledgment
                            server_address[1] = serverPort
                            ack_packet = struct.pack('!HH', 4, blockNumber)
                            clientSocket.sendto(ack_packet, server_address)

                            blockNumber += 1

                        elif opcode == 5:  # Error packet
                            error_code = struct.unpack('!H', received_data[:2])[0]
                            error_msg = received_data[2:].decode('utf-8')
                            print(f"Error {error_code}: {error_msg}")
                            bfile.close()
                            os.remove(filename)
                            break
                        elif opcode == 4:
                            print(opcode)
                        else:
                            print(f"Unexpected opcode: {opcode}")
                            break

                        if size >= 0 and size < 516:
                            bfile.close()
                            break
                except KeyboardInterrupt:
                    print("Client interrupted by user")

            case 2:
                filename = input("Please enter filename to upload: ")
                blockNumber = 1
                try:
                    bfile = open(filename, 'rb')
                    send_request(clientSocket, WRQ, filename, server_address)

                except Exception as e:
                    print(e)

            case 3:
                print("Closing client application")
                break
            case _:
                print("Invalid Input! Try again!")
        

if __name__ == '__main__':
    tftp_client('127.0.0.1', 0)