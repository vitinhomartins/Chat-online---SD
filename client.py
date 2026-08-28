import socket

HOST = "127.0.0.1"
PORT = 6000


def receive_messages(client):
    while True:
        try:
            message = client.recv(1024)

            if not message:
                break

            print(message.decode())

        except:
            break


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((HOST, PORT))

    message = client.recv(1024).decode()
    print(message)

    name = input("> ")
    client.send(name.encode())

    # Thread responsável pelas mensagens
    import threading

    thread = threading.Thread(
        target=receive_messages,
        args=(client,),
        daemon=True
    )

    thread.start()

    while True:
        text = input()

        if text.lower() == "/sair":
            break

        client.send(text.encode())

    client.close()


if __name__ == "__main__":
    start_client()