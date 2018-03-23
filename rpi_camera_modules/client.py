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
    signed_data = signed_connection_data()
    s.send(signed_data)
    was_i_verified = s.recv(1024)
    if was_i_verified == b"VERIFIED":
        print("I was verified, so let's send some photos")
        #s.send(filename)
        f = open(filename, "rb")
        data_to_send= f.read(2048)
        while data_to_send:
            s.send(data_to_send)
            data_to_send = f.read(2048)
        f.close()
    s.close()
    return

def signed_connection_data():
    date = time.ctime()
    gpg = gnupg.GPG(gnupghome='~/.gnupg')
    with open(passphrase_file) as f:
        password = f.read().splitlines()[0]
        signed_data = gpg.sign(date, passphrase=password)
        return signed_data.data
