"""
This script runs on the remote server to receive an image from a raspberry pi running the client script.
"""

import io
import socket
import struct
import gnupg # python-gnupg package NOT gnupg package

local_host = "localhost"
local_host_port = 3001 # port forwarded and ready to go
username_to_verify = "pathfinder_camera"

def recv_photo(filename, sigfile, gpg, client_socket):
    #f = open(filename, "wb")
    data_recv = client_socket.recv(2048)
    data = b''
    while data_recv:
        data += data_recv
        data_recv = client_socket.recv(2048)

    verified = gpg.verify_data(sigfile, data)
    print("username of sign: " + str(verified.username))
    if verified.valid and username_to_verify in verified.username:
        f = open(filename, "wb")
        f.write(data)
        f.close()
    
### temp sig file gets written no matter what is sent in
def listen_for_photos():
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((local_host, local_host_port))
    s.listen(1) # only queue 1 connection right now

    # create gpg instance
    gpg = gnupg.GPG(gnupghome='~/.gnupg')
    
    while True:
        (client_socket, addr) = s.accept()
        
        detached_sig_data = client_socket.recv(2048)
        print("client connected with sig: " + str(detached_sig_data))
        sig_file = open("client.sig", "wb")
        sig_file.write(detached_sig_data)
        sig_file.close()

        client_socket.send(b"ACK")
        print("sent ACK to client")

        recv_photo("tempphoto.jpg", "client.sig", gpg, client_socket)

        client_socket.close()
        
    s.close()
    return

listen_for_photos()
