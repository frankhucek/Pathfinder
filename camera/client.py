"""
This script runs on the RPI devices to send their images over a socket connection to the awaiting web server.
"""
import io
import socket
import struct
import time
import picamera
import gnupg
import os
remote_host = "localhost" # "frankhucek.com"
remote_host_port = 3001 # port forwarded and ready to go
passphrase_file = "/home/frank/Code/srproj/2018_spring_395_pathfinder/rpi_camera_modules/pathfinder_gpg_passphrase.txt"

"""
Sends the specified 'filename' to the remote host
host=remote_host, port=remote_host_port, pass_file=passphrase_file
"""
def send_photo(filename):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((remote_host, remote_host_port))
    
    send_sig(filename, passphrase_file, s)
    
    ack = s.recv(1024)
    if ack == b"ACK":
        send_photo_data(filename, s)

    s.shutdown(socket.SHUT_RDWR)
    s.close()
    return

def send_sig(filename, pass_file, conn_socket):
    # send signed data to server and wait for response
    detached_sig_data = signed_data(filename, passphrase_file)
    print("sending detached sig")
    conn_socket.send(detached_sig_data)
    return

def send_photo_data(filename, conn_socket):
    print("sending filename")

    path, file_name = os.path.split(filename)
    
    conn_socket.send(file_name.encode())
    ack = conn_socket.recv(1024)
    if ack == b"SEND_FILE":
        send_photo_file(filename, conn_socket)
    return

"""
Sends the data contained in 'filename' over 'conn_socket'
- sent in 2048 byte chunks
"""
def send_photo_file(filename, conn_socket):
    print("sending file")
    file_to_send = open(filename, "rb")
    data_to_send= file_to_send.read(2048)
    while data_to_send:
        conn_socket.send(data_to_send)
        data_to_send = file_to_send.read(2048)

    file_to_send.flush()
    file_to_send.close()
    return


"""
Signs the data contained in 'filename'
Returns the detached signature in binary bytestring format
"""
def signed_data(filename, pass_file):
    gpg = gnupg.GPG()
    with open(pass_file) as f:
        with open(filename, "rb") as file_to_sign:
            password = f.read().splitlines()[0]
            detached_sig = gpg.sign_file(file_to_sign, detach=True, binary=True,passphrase=password)
            return detached_sig.data
            # return b'gonna get denied'
