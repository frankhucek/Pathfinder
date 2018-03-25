import gnupg

"""
1) create detached binary sig from file
2) write detached sig data to a file
3) to verify, use sig file and file contents as bytestring
"""

gpg = gnupg.GPG()

file_to_sign = open("test.jpg", "rb")
detached_sig = gpg.sign_file(file_to_sign, detach=True, binary=True, passphrase="srproj")
file_to_sign.close()

sig_file = open("testjpg.sig", "wb")
sig_file.write(detached_sig.data)
sig_file.close()

file_to_verify = open("test.jpg", "rb")
file_data = file_to_verify.read()
ver = gpg.verify_data("testjpg.sig", file_data)
print(str(ver.valid))
print(str(ver.username))
