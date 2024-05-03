import sys
import socket
import select

SERVER_PORT = 49152
SERVER_IP = "0.0.0.0"
BUF_SIZE = 1024

class Client():
    EXIT = "exit"

    def __init__(self, SERVER_ADDR: tuple, CLIENT_NAME: str) -> None:
        self.SERVER_ADDR = SERVER_ADDR
        self.CLIENT_NAME = CLIENT_NAME

        # create an AF_INET, TCP socket
        self.socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

    def receive_data(self) -> None:
        try:
            # receive the message from the server
            message = self.socket.recv(BUF_SIZE).decode()

            if not message:
                raise ConnectionError
        except:
            print("[!] Connection to server lost")
            self.socket.close()
            exit(-1)

        # print the message
        print(message)

    def send_data(self, message: str) -> None:
        try:
            # send the message to the server
            self.socket.sendall(message.encode())
        except:
            print("[!] Failed to send the message")
            self.socket.close()
            exit(-1)

    def run(self) -> None:
        # connect to the server
        try:
            self.socket.connect(self.SERVER_ADDR)
            self.socket.sendall(f"{self.CLIENT_NAME}".encode())
            print("[+] Connected to the server")
        except:
            print(f"[!] Failed to connect to the server {self.SERVER_ADDR}")
            exit(-1)

        # set the socket to non-blocking mode
        self.socket.setblocking(False)

        while True:
            try:
                # use select to check if there's data to read
                # from stdin or from the server
                inputs = [sys.stdin, self.socket]
                readable, _, _ = select.select(inputs, [], [])
                for source in readable:
                    # if there's data to read from the server
                    if source == self.socket:
                        self.receive_data()

                    # if there's data to read from stdin
                    if source == sys.stdin:
                        user_input = input()
                        if user_input.lower() == self.EXIT:
                            self.socket.close()
                            exit(0)

                        self.send_data(user_input)
            except KeyboardInterrupt:
                print("[!] Exiting the chat")
                self.socket.close()
                exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]

        if len(sys.argv) > 2:
            SERVER_PORT = int(sys.argv[2])
    else:
        name = input("Enter your name: ")

    c = Client((SERVER_IP, SERVER_PORT), name)
    c.run()
