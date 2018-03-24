"""
This script runs on the RPI devices to send their images over a socket connection to the awaiting web server.
"""
import io
import socket
import struct
import time
import picamera
import gnupg

remote_host = "localhost" # "frankhucek.com"
remote_host_port = 3001 # port forwarded and ready to go
passphrase_file = "pathfinder_gpg_passphrase.txt"

def send_photo(filename):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((remote_host, remote_host_port))
    
    # send signed data to server and wait for response
    detached_sig_data = signed_connection_data(filename)
    s.send(detached_sig_data)
    ack = s.recv(1024)
    if ack == b"ACK":
        file_to_send = open(filename, "rb")
        data_to_send= file_to_send.read(2048)
        while data_to_send:
            s.send(data_to_send)
            data_to_send = file_to_send.read(2048)
        #file_to_send.close()
    s.close()
    return

def signed_connection_data(filename):
    gpg = gnupg.GPG(gnupghome='~/.gnupg')
    with open(passphrase_file) as f:
        with open(filename, "rb") as file_to_sign:
            password = f.read().splitlines()[0]
            detached_sig = gpg.sign_file(file_to_sign, detach=True, binary=True, passphrase=password)
            return detached_sig.data
