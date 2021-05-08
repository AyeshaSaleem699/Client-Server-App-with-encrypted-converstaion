import socket
import sys
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("Server")


def create_socket():   # Create a Socket ( connect two computers)
    try:
        global host
        global port
        global s
        host = "localhost"
        port = 9999
        s = socket.socket()
        print("Server Socket created...")

    except socket.error as msg:
        print("Socket creation error: " + str(msg))


def bind_socket():  # Binding the socket and listening for connections
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))

        s.bind((host, port))
        s.listen(1)
        print("Wating for connection...")

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()


def socket_accept():  # Establish connection with a client (socket must be listening)
    conn, address = s.accept()
    name = conn.recv(1024).decode()
    print("Connection has been established! |" + " IP " +
          address[0] + " | Port " + str(address[1])+"|Client name "+name)
    conn.send(bytes("Hey! Welcome "+name, "utf-8"))
    communcation(conn)


def encryption(text):
    global shift_key
    shift = shift_key  # defining the shift count
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
    #print("Encrypted text:", text)
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


def communcation(conn):
    got_mac = False
    got_name = False
    cmd = "start"
    message_count = 0
    index = 0
    mac_add = ""
    while True:
        if(message_count == 0):
            pass
            # print("First message")
        elif((message_count % 5) == 0):
            update_key(mac_add, index)
            index = (index+1) % 12

        client_response = str(conn.recv(1024), "utf-8")

        if(got_name and got_mac):
            client_response = decryption(client_response)
            message_count += 1

        if "mac address" in cmd:
            mac_add = client_response
            got_mac = True
            # print(mac_add)

        if "computer name" in cmd:
            got_name = True
            computer_name = client_response
            generateKey(computer_name)
            # print(computer_name)

        if client_response.__eq__("I am Quiting!!!"):
            conn.close
            print("Client Disconnected...\nWaiting for new Connection...")
            break

        if(message_count == 0):
            # print("First message")
            pass
        elif((message_count % 5) == 0):
            # print("5th messgae completed")
            update_key(mac_add, index)
            index = (index+1) % 12

        print("Client: " + client_response+"\n", end="")
        cmd = input("You: ")
        if cmd == 'quit':
            msg = "Disconnected"
            if(got_name and got_mac):
                msg = encryption(msg)
            conn.send(str.encode(msg))
            s.close()
            sys.exit()

        if(got_name and got_mac):
            cmd = encryption(cmd)
            message_count += 1

        if len(str.encode(cmd)) > 0:
            conn.send(str.encode(cmd))
            print("!!!WAIT Clients turn!!!!")
    socket_accept()


def main():
    create_socket()
    bind_socket()
    socket_accept()


main()
