import socket
import sys
import ctypes
import uuid
Computer_name = socket.gethostname()

ctypes.windll.kernel32.SetConsoleTitleW("Client")
# print("The MAC address in formatted way is : ", end="")
MAC_address = '-'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                        for ele in range(0, 8*6, 8)][::-1])
# print(MAC_address)

s = socket.socket()
name_shared = False
mac_shared = False


def encryption(text):
    global shift_key
    shift = shift_key
    encryption = ""
    for c in text:
        if c.isupper():
            c_unicode = ord(c)
            c_index = ord(c) - ord("A")
            new_index = (c_index + shift) % 26
            new_unicode = new_index + ord("A")
            new_character = chr(new_unicode)
            encryption = encryption + new_character
        elif c.islower():
            c_unicode = ord(c)
            c_index = ord(c) - ord("a")
            new_index = (c_index + shift) % 26
            new_unicode = new_index + ord("a")
            new_character = chr(new_unicode)
            encryption = encryption + new_character
        else:
            encryption += c

    # print("Plain text:", text)
    #print("Encrypted text:", encryption)
    return encryption


def decryption(text):
    global shift_key
    shift = shift_key
    decryption = ""
    for c in text:
        if c.isupper():
            c_unicode = ord(c)
            c_index = ord(c) - ord("A")
            new_index = (c_index - shift) % 26
            new_unicode = new_index + ord("A")
            new_character = chr(new_unicode)
            decryption = decryption + new_character
        elif c.islower():
            c_unicode = ord(c)
            c_index = ord(c) - ord("a")
            new_index = (c_index - shift) % 26
            new_unicode = new_index + ord("a")
            new_character = chr(new_unicode)
            decryption = decryption + new_character
        else:
            decryption += c
    # print("Encrypted text:", text)
    # print("Decrypted text:", decryption)
    return decryption


def generateKey(computer_name):
    sum = 0
    count = 0
    # print(sum)
    for c in computer_name:
        ASCII_of_c = ord(c)
        sum += ASCII_of_c
        count += 1
        # print(+sum)
    # print(+sum)

    Avg = sum/count
    # print(+Avg)
    global shift_key
    shift_key = round(Avg) % 26

    # print(shift_key)


def list_of_int_mac_address(mac_add):
    # mac_add = "98-40-bb-2e-95-Cd"
    numbers = []
    mac_add = mac_add.lower()
    for word in mac_add:
        if(word.isalpha() or word.isdigit()):
            numbers.append(int(word, 16))
    # print(numbers)
    return numbers


def update_key(mac_add, index):
    mac_add_list = list_of_int_mac_address(mac_add)
    global shift_key
    shift_key = (shift_key + mac_add_list[index]) % 26

    # print("Key updated: ")
    # print(shift_key)


c = 0
message_count = 0
index = 0

s.connect(("localhost", 9999))
print("Client Side Started")
name = input("Enter your name: ")
s.send(bytes(name, "utf-8"))
server_response = "start"
while True:
    data = s.recv(1024).decode()
    print("Server: "+data)
    while True:
        # print(message_count)

        if(message_count == 0):
            # print("First message")
            pass
        elif((message_count % 5) == 0):
            # print("5th messgae completed")
            update_key(MAC_address, index)
            index = (index+1) % 12

        # if cmd == MAC_address:
        #     pass
        if "mac address" in server_response:
            cmd = MAC_address
            mac_shared = True
        elif "computer name" in server_response:
            generateKey(Computer_name)
            cmd = Computer_name
            name_shared = True
        else:
            cmd = input("You: ")
            if cmd == 'quit':
                msg = "I am Quiting!!!"
                if(c > 1):
                    msg = encryption(msg)
                s.send(str.encode(msg))
                break

        if(mac_shared and name_shared):
            c = c + 1

        if(c > 1):
            cmd = encryption(cmd)
            message_count += 1

        if len(str.encode(cmd)) > 0:
            s.send(str.encode(cmd))
            print("WAIT its Server's turn!!!!")

        if(message_count == 0):
            # print("First message")
            pass
        elif((message_count % 5) == 0):
            # print("5th messgae completed")
            update_key(MAC_address, index)
            index = (index+1) % 12

        server_response = str(s.recv(1024), "utf-8")

        if(c >= 1):
            server_response = decryption(server_response)
            message_count += 1

        if server_response == 'Disconnected':
            print("Server Disconnected...closing client...")
            break
        print("Server: "+server_response+"\n", end="")

        # if "mac address" in server_response:
        #     cmd = MAC_address

    sys.exit()
