import sys
import socket
import select

PORT = 49152
IP = "0.0.0.0"
BUF_SIZE = 1024

class Server():
    def __init__(self, ADDRESS: tuple) -> None:
        self.ADDRESS = ADDRESS
        # create an AF_INET, TCP socket
        self.socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
        # let the socket reuse the same address if it's already bound but not in use
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Set the socket to non-blocking
        self.socket.setblocking(False)

        # store all active connections
        self.connections: dict[socket.socket, str] = {}

    def _broadcast(self, message: bytes) -> None:
        # broadcast the message to all clients
        for sock in self.connections:
            try:
                sock.sendall(message)
            except:
                self._handle_error(sock)

    def _handle_error(self, sock: socket.socket) -> None:
        print(f"[-] Connection to {self.connections.get(sock)} {sock.getpeername()} lost")

        # remove the connection
        name = self.connections.get(sock)
        self.connections.pop(sock)
        sock.close()

        # announce the client left the chat
        self._broadcast(f"[-] {name} left the chat".encode())

    def accept_connection(self) -> None:
        # Accept new connection
        try:
            client_sock, client_addr = self.socket.accept()
            print(f"[+] New connection from {client_addr}")

            # receive client name
            client_name = client_sock.recv(BUF_SIZE).decode()
            self.connections[client_sock] = client_name

            # send message to all the clients
            self._broadcast(f"[+] {client_name} joined the chat".encode())
        except:
            print("[!] Failed to accept the connection")

    def receive_data(self, sock: socket.socket) -> None:
        try:
            # Receive data from the client
            data = sock.recv(BUF_SIZE)

            if not data:
                raise ConnectionError
        except:
            self._handle_error(sock)
            return

        name = self.connections.get(sock)
        print(f"[+] New message from {name} {sock.getpeername()}: {data.decode()}")
        self._broadcast(f"{name}: ".encode() + data)

    def run(self) -> None:
        # bind the address and listen for connections
        try:
            self.socket.bind(self.ADDRESS)
            self.socket.listen()
            print("[+] Listening for incoming connections")
        except:
            print(f"[!] Port {PORT} already in use")
            exit(-1)

        while True:
            try:
                # Use select to check for readable sockets
                connections = list(self.connections.keys()) + [self.socket]
                readable, _, _ = select.select(connections, [], [])
                for sock in readable:
                    if sock == self.socket:
                        self.accept_connection()
                    else:
                        # Receive data from existing connection
                        self.receive_data(sock)
            except KeyboardInterrupt:
                print("\n[!] Closing the server")
                self.socket.close()
                exit(0)
            # except:
            #     print("[!] Error occurred during operation")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])

    s = Server((IP, PORT))
    s.run()
