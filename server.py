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
        # let the socket reuse the same address for different connections
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Set the socket to non-blocking
        self.socket.setblocking(False)

        # store all active connections
        self.connections: list[socket.socket] = []

    def broadcast(self, message: bytes, sender: socket.socket) -> None:
        # broadcast the message to all clients
        for conn in self.connections:
            try:
                if conn != sender:
                    conn.sendall(message)
            except:
                print(f"[!] Connection to {conn.getpeername()} lost")
                self.connections.remove(conn)
                conn.close()

    def accept_connection(self) -> None:
        # Accept new connection
        try:
            client_sock, client_addr = self.socket.accept()
            print(f"[+] New connection from {client_addr}")
            self.connections.append(client_sock)
        except:
            print("[!] Failed to accept the connection")

    def receive_data(self, sock: socket.socket) -> None:
        try:
            # Receive data from the client
            data = sock.recv(BUF_SIZE)

            if not data:
                raise ConnectionError
        except:
            print(f"[!] Connection to {sock.getpeername()} lost")
            self.connections.remove(sock)
            sock.close()
            return

        print(f"[+] New message from {sock.getpeername()}: {data.decode()}")
        self.broadcast(data, sock)

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
                readable, _, _ = select.select([self.socket] + self.connections, [], [])
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
            except:
                print("[!] Error occurred during operation")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])

    s = Server((IP, PORT))
    s.run()
