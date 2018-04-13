"""
This script runs on the remote server to receive an image from a raspberry pi running the client script.
"""

import io
import socket
import struct
import gnupg # python-gnupg package NOT gnupg package
import os
import re

import jobmanager
local_host = "localhost"
local_host_port = 3001 # port forwarded and ready to go
verified_usernames = ["pathfinder_camera <pathfinder_camera@frankhucek.com>", "pathfinder_cam_0 <pathfinder_cam_0@frankhucek.com>"]
#verified_usernames = "pathfinder_cam_0"
client_sig_file = "client.sig"
base_job_dir = "/home/frank/Code/srproj/2018_spring_395_pathfinder/jobs/"
TIMEOUT = 10

def recv_photo(filename, sigfile, client_socket):
    # create gpg instance
    gpg = gnupg.GPG()
    
    data_recv = client_socket.recv(16)
    data = b''
    print("receiving photo data")
    while data_recv:
        data += data_recv
        data_recv = client_socket.recv(2048)
        
    verified = gpg.verify_data(sigfile, data)
    print("username of sign: " + str(verified.username))
    if verified.valid and verified.username in ":".join(verified_usernames):
        job_num = re.search(r'\d+', verified.username).group()
        job_dir = base_job_dir + job_num + "/"
        if not job_num:
            job_num = '0'
        if not os.path.exists(job_dir):
            os.makedirs(job_dir)
        print("received file: " + job_dir + filename)    
        f = open(job_dir + filename, "wb")
        f.write(data)
        f.close()
        return job_dir
    
### temp sig file gets written no matter what is sent in
def listen_for_photos():
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    s.bind((local_host, local_host_port))
    s.listen(5) # only queue 5 connections right now
    
    while True:
        (client_socket, addr) = s.accept()
        client_socket.settimeout(TIMEOUT) # set timeout to prevent ddos
        # client_socket.setblocking(0)
        try:
            # get sig data and write to sig file
            handle_sig_data(client_sig_file, client_socket)

            # ACK for signature receieved
            client_socket.send(b"ACK")

            # get filename
            filename = client_socket.recv(1024)
            filename = filename.decode("utf-8")
            print("received filename")
            
            # ACK for filename received
            client_socket.send(b"SEND_FILE")

            # get photo data and write to file if verified
            job_dir = recv_photo(filename, client_sig_file, client_socket)
            
            if os.path.exists(client_sig_file):
                os.remove(client_sig_file)
                
            client_socket.close()

            #### INVOKE JOB MANAGER HERE ####
            print("invoking job manager in directory " + job_dir)
            jobmanager.update_job(0,job_dir+filename)
            
            #################################
            
            
        except socket.timeout:
            print("connection timed out")
            client_socket.close()
            continue;
        except socket.error as e:
            print("socket error")
            client_socket.close()
            continue;
        except:
            print("weird error")
            continue;
        
    s.close()
    return

def handle_sig_data(sigfile, client_socket):
    detached_sig_data = client_socket.recv(2048)
    print("received signature data")
    sig_file = open(sigfile, "wb")
    sig_file.write(detached_sig_data)
    sig_file.close()
    return

listen_for_photos()
