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
    request_packet = struct.pack('!H', opcode) + filename.encode('utf-8') + b'\0' + mode.encode('utf-8') + b'\0'
    if blksize != 512:
        request_packet += "blksize".encode("utf-8") + b'\0' + str(blksize).encode("utf-8") + b'\0'
    print(len(request_packet))
    print(request_packet)
    socket.sendto(request_packet, serverAddress)

def receive_packet(sock, blksize):
    data, address = sock.recvfrom(blksize + 4)
    opcode = struct.unpack('!H', data[:2])[0]
    print(opcode)
    print(len(data))
    if opcode == 3:
        return opcode, data[4:], address, len(data)
    return opcode, data[2:]

def send_packet(sock, data, blknum, serverAddress):
    data_packet = struct.pack('!H', 3) + struct.pack('!H', blknum) + data
    sock.sendto(data_packet, serverAddress)

def receive_oack(sock):
    data, address = sock.recvfrom(516)
    opcode = struct.unpack('!H', data[:2])[0]
    if opcode == 6:
        options = data[2:].decode('utf-8').split('\0')
        return int(options[1]), address
    print(data[2:].decode('utf-8'))
    return None, address

def receive_ack(sock, expectedblknum):
    ack, address = sock.recvfrom(4)
    print(ack)
    opcode, blknum = struct.unpack('!HH',ack)
    if opcode == 4 and blknum == expectedblknum:
        return True
    return False

def send_ack(sock, blknum, server_address):
    ack_packet = struct.pack('!HH', 4, blknum)
    sock.sendto(ack_packet, server_address)


def downloadfile(sock, sa):
    clientSocket = sock
    server_address = sa
    filename = input("Please enter filename of file to download: ")
    blknum = 1
    bfile = open(filename, 'wb')
    try:
        while True:
            blksize = int(input("Enter desired block size (Default - 512): "))
            if blksize >= 8 and blksize <= 65464:
                break
            else:
                print("Invalid Block Size! Input another value between 8 and 65464.")
        send_request(clientSocket, RRQ, filename, server_address, blksize)
        if blksize != 512:
                blksize, server_address = receive_oack(clientSocket)
                send_ack(clientSocket, 0, server_address)
        if blksize == None:
            os.remove(filename)

        while True and blksize != None:
            # Receive data packet from the server
            opcode, received_data, server_address, size = receive_packet(clientSocket, blksize)
            if opcode == 3:  # Data packet
                print(f"Received data block {blknum}")
                bfile.write(received_data)

                send_ack(clientSocket, blknum, server_address)

                blknum += 1

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

            if size >= 0 and size < blksize:
                bfile.close()
                break
    except KeyboardInterrupt:
        print("Client interrupted by user")
    except Exception as e:
        print(e)

def uploadfile(sock, sa):
    clientSocket = sock
    server_address = sa
    filename = input("Please enter filename of file to upload: ")
    try:
        file = open(filename, 'rb')
        filedata = file.read()
        print(type(filedata))

        while True:
            blksize = int(input("Enter desired block size (Default - 512): "))
            if blksize >= 8 and blksize <= 65464:
                break
            else:
                print("Invalid Block Size! Input another value between 8 and 65464.")
        send_request(clientSocket, WRQ, filename, server_address, blksize)
        if blksize != 512:
            blksize, server_address = receive_oack(clientSocket)
        if blksize != None:
            #Split to multiple segments depending on block size
            curr_block = 1
            for i in range(0, len(filedata), blksize):
                data = filedata[i:i+blksize]
                send_packet(clientSocket, data, curr_block, server_address)
                while not receive_ack(clientSocket, curr_block):
                    send_packet(clientSocket, data, curr_block, server_address)
                
                print(f'Block #: {curr_block}')
                print(f'Data Length: {len(data)}')
                curr_block += 1
    except Exception as e:
            print(e)
   
        



def tftp_client(clientAddress, port):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = input("Please enter IP address of server: ")
    while True:
        server_address = (server_ip, TFTP_PORT)
        try:
            print(f'[1] Download File\n[2] Upload File\n[3] Exit')
            choice = int(input("Input: "))
        except Exception as e:
            choice = 4
        match choice:
            case 1:
                downloadfile(clientSocket, server_address)

            case 2:
                uploadfile(clientSocket, server_address)

            case 3:
                print("Closing client application")
                break
            case _:
                print("Invalid Input! Try again!")
        

if __name__ == '__main__':
    tftp_client('127.0.0.1', 0)