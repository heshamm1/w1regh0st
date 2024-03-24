import threading
import socket
import sys
import signal
import select

HOST = ''
PORT = 32323
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_running = True  # Flag to control the server loop
client_threads = []  # List to keep track of client handler threads

def start_new_thread(f, args):
    thread = threading.Thread(target=f, args=args)
    thread.start()
    return thread

def main():
    global server_running  # Use the global flag

    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit(1)

    s.listen(10)
    print("Server listening on port " + str(PORT))

    # Print the banner when the server starts
    print("""
                                                                  .                                 
                                                                .::::::.                            
                                                               .::::....::.                         
                                                               .::.       .:.                       
                                                               .::           .                      
                                                               .::                                  
                                                               .::                                  
                                 ....                           ::                                  
                                ........                        ::                                  
                              ............                      :.                                  
                             ...............                    :.                                  
                           ....       .......                   :.                                  
                          ..  .~7?JJ?!:......                   :.                                  
                         ...~B@@@@@@@@@B!.....                  .:                                  
                         ..G#75@@@@G.^@@@P:....                 .:                                  
                        ...&?..#@@@:.~@@@@~.....             ....:.                                 
                         . ?@Y.5@@@~?@&BP7:......................:..                                
                         ...??Y@&@@@@&:.  .......................:...                               
                         ...  ^@GYJ?5?...........................:...                               
                        .......:.. .  ...........................:...                               
                        ........................................ :...                               
                       ......................................... :...                               
                       ...................................... .. :...                               
                      .................................   ...  . :..                                
                      ..   ............................     .  . :.                                 
                      .    .............................       . ..                                 
                      .    .............................         ..                                 
                      .    ..............................        .:                                 
                           ..............................        .:                                 
                           ...............................       .:                                 
                           ...............................        :                                 
                           ................................       :.                                
                           ................................       :.                                
                           ................................       :.                                
                           .  .............................       .                                 
                           .  .. ................    ...  .                                         
                              .  .. ............       .                                            
                              .  .   ...........                                                    
                                     .  ....   .                                                    
                                          ..                                                                                                                                       
		            _    _  __           _____ _     _____      _   
		           | |  | |/  |         |  __ \ |   |  _  |    | |  
		           | |  | |`| | _ __ ___| |  \/ |__ | |/' | ___| |_ 
		           | |/\| | | || '__/ _ \ | __| '_ \|  /| |/ __| __|
		           \  /\  /_| || | |  __/ |_\ \ | | \ |_/ /\__ \ |_ 
 		            \/  \/ \___/_|  \___|\____/_| |_|\___/ |___/\__|
                                                  """)

    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    while server_running:
        try:
            readable, _, _ = select.select([s], [], [], 1)  # 1-second timeout
        except select.error as e:
            print("Error in select:", e)
            continue

        for sock in readable:
            if sock == s:
                try:
                    client, addr = s.accept()
                    print('Connected with ' + addr[0] + ':' + str(addr[1]))
                    thread = start_new_thread(client_handler, (client, addr[0]))
                    client_threads.append(thread)
                except socket.error as e:
                    print("Error accepting client connection:", e)
                except KeyboardInterrupt:
                    server_running = False

    print("Waiting for client threads to finish...")
    for thread in client_threads:
        thread.join()

    print("Server shutting down...")
    s.close()

def client_handler(sock, ip):
    try:
        sock.send(b'You are now connected to the W1regh0st server')

        while True:
            data = sock.recv(1024).decode('utf-8')
            if not data:
                break
            print("[ %s ] %s" % (ip, data))
            reply = 'Received : ' + data
            sock.send(bytes(reply.encode('utf-8')))
    except Exception as e:
        print("Error in client handler:", e)
    finally:
        sock.close()

def signal_handler(sig, frame):
    global server_running  # Set the flag to False when Ctrl+C is pressed
    server_running = False
    print('\nCtrl+C detected. Server will shut down.')

if __name__ == "__main__":
    main()
