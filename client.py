import sys
import socket
import tkinter as tkt
import threading

SERVER_PORT = 49152
SERVER_IP = "0.0.0.0"
BUF_SIZE = 1024

class Client():
    EXIT = "exit"
    TITLE = "Chat Room"

    def __init__(self, SERVER_ADDR: tuple) -> None:
        self.SERVER_ADDR = SERVER_ADDR

        # create an AF_INET, TCP socket
        self.socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        # create a window and set the title
        self.window = tkt.Tk()
        self._build_ui()

    def _build_ui(self) -> None:
        # set window title
        self.window.title(self.TITLE)

        # create frame for the chat messages
        messages_frame = tkt.Frame(self.window)

        # message bar
        my_msg = tkt.StringVar()
        my_msg.set("Scrivi...")

        # msg list with scrollbar
        scrollbar = tkt.Scrollbar(messages_frame)
        scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
        msg_list = tkt.Listbox(messages_frame, height=20, width=70, yscrollcommand=scrollbar.set)
        msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)

        msg_list.pack()
        messages_frame.pack()

        # insert welcome message
        msg_list.insert(tkt.END, "Benvenuto! Inserisci il tuo nome e premi invio per entrare nella chat.")

        # lambda function for appending messages
        self._append_message = lambda message: msg_list.insert(tkt.END, message)

        # lambda function for sending messages
        send_msg = lambda: self.send_data(my_msg.get())

        # field for message input
        entry_field = tkt.Entry(self.window, textvariable=my_msg)
        entry_field.bind(
            "<Return>",
            lambda event: [
                send_msg(),
                event.widget.delete(0, tkt.END) # clear the message field
            ]
        )
        entry_field.pack()

        # send button
        send_button = tkt.Button(
            self.window,
            text="Invio",
            command=lambda: [
                send_msg(),
                entry_field.delete(0, tkt.END) # clear the message field
            ]
        )
        send_button.pack()

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

        return message

    def receive_loop(self) -> None:
        while True:
            message = self.receive_data()

            # print the message
            print(message)
            self._append_message(message)

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
            print("[+] Connected to the server")
        except:
            print(f"[!] Failed to connect to the server {self.SERVER_ADDR}")
            exit(-1)

        # create receiving thread
        receive_t = threading.Thread(target=self.receive_loop, daemon=True)

        try:
            # start the receiving thread
            receive_t.start()

            # start ui thread
            tkt.mainloop()
        except KeyboardInterrupt:
            print("[!] Exiting the chat")

        # close the socket and exit
        self.socket.close()
        exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        SERVER_PORT = int(sys.argv[1])

    c = Client((SERVER_IP, SERVER_PORT))
    c.run()
