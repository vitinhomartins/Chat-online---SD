import socket
import threading
import asyncio
import websockets
from datetime import datetime


# ==========================================
# CONFIGURAÇÕES
# ==========================================

TCP_HOST = "0.0.0.0"
TCP_PORT = 5000

WS_HOST = "0.0.0.0"
WS_PORT = 8765


# ==========================================
# CLIENTES CONECTADOS
# ==========================================

tcp_clients = {}
ws_clients = set()

lock = threading.Lock()


# Loop do WebSocket
websocket_loop = None


# ==========================================
# HORÁRIO DO SERVIDOR
# ==========================================

def get_time():
    return datetime.now().strftime("%H:%M:%S")


# ==========================================
# BROADCAST
# ==========================================

def broadcast(message):

    # ------------------------------
    # Clientes TCP
    # ------------------------------

    with lock:

        for client in list(tcp_clients):

            try:

                client.sendall(
                    message.encode("utf-8")
                )

            except:

                pass


    # ------------------------------
    # Clientes WebSocket
    # ------------------------------

    if websocket_loop:

        asyncio.run_coroutine_threadsafe(
            websocket_broadcast(message),
            websocket_loop
        )


async def websocket_broadcast(message):

    for client in list(ws_clients):

        try:

            await client.send(message)

        except websockets.exceptions.ConnectionClosed:

            pass


# ==========================================
# SERVIDOR TCP
# ==========================================

def handle_tcp_client(client, address):

    print(f"[TCP] Cliente conectado: {address}")

    name = None

    try:

        # Pedir nome
        client.sendall(
            "Digite seu nome: ".encode("utf-8")
        )

        name = client.recv(1024).decode("utf-8").strip()

        if not name:

            name = f"{address[0]}:{address[1]}"


        # Registrar cliente
        with lock:

            tcp_clients[client] = name


        print(f"[TCP] {name} entrou no chat.")


        # Avisar todos
        broadcast(
            f"[{get_time()}] {name} entrou no chat."
        )


        # Receber mensagens
        while True:

            data = client.recv(1024)

            if not data:

                break


            message = data.decode(
                "utf-8"
            ).strip()


            if not message:

                continue


            formatted = (
                f"[{get_time()}] "
                f"{name}: {message}"
            )


            print(formatted)


            # Enviar para TODOS
            broadcast(formatted)


    except ConnectionResetError:

        pass


    except Exception as error:

        print(f"[TCP] Erro: {error}")


    finally:

        # Remover cliente
        with lock:

            tcp_clients.pop(
                client,
                None
            )


        client.close()


        if name:

            print(
                f"[TCP] {name} saiu do chat."
            )


            broadcast(
                f"[{get_time()}] "
                f"{name} saiu do chat."
            )


def start_tcp_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )


    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )


    server.bind(
        (TCP_HOST, TCP_PORT)
    )


    server.listen()


    print(
        f"[SERVER] TCP iniciado "
        f"na porta {TCP_PORT}"
    )


    while True:

        client, address = server.accept()


        thread = threading.Thread(
            target=handle_tcp_client,
            args=(client, address)
        )


        thread.start()


# ==========================================
# SERVIDOR WEBSOCKET
# ==========================================

async def handle_websocket(websocket):

    print("[WS] Cliente conectado.")

    name = None

    try:

        # Primeira mensagem é o nome
        name = await websocket.recv()

        name = name.strip()


        if not name:

            name = "Anônimo"


        # Registrar cliente
        ws_clients.add(websocket)


        print(
            f"[WS] {name} entrou no chat."
        )


        # Avisar todos
        await websocket_broadcast(
            f"[{get_time()}] "
            f"{name} entrou no chat."
        )


        # Receber mensagens
        async for message in websocket:

            message = message.strip()


            if not message:

                continue


            formatted = (
                f"[{get_time()}] "
                f"{name}: {message}"
            )


            print(formatted)


            # Enviar para TCP e WebSocket
            broadcast(formatted)


    except websockets.exceptions.ConnectionClosed:

        pass


    except Exception as error:

        print(f"[WS] Erro: {error}")


    finally:

        # Remover cliente
        ws_clients.discard(websocket)


        if name:

            print(
                f"[WS] {name} saiu do chat."
            )


            broadcast(
                f"[{get_time()}] "
                f"{name} saiu do chat."
            )


async def start_websocket_server():

    print(
        f"[SERVER] WebSocket iniciado "
        f"na porta {WS_PORT}"
    )


    async with websockets.serve(
        handle_websocket,
        WS_HOST,
        WS_PORT
    ):

        await asyncio.Future()


# ==========================================
# LOOP DO WEBSOCKET
# ==========================================

def start_websocket_loop():

    global websocket_loop


    websocket_loop = (
        asyncio.new_event_loop()
    )


    asyncio.set_event_loop(
        websocket_loop
    )


    websocket_loop.run_until_complete(
        start_websocket_server()
    )


# ==========================================
# INICIAR SERVIDOR
# ==========================================

if __name__ == "__main__":

    print("========================================")
    print("              CHAT SERVER")
    print("========================================")


    # Thread do WebSocket
    websocket_thread = threading.Thread(
        target=start_websocket_loop,
        daemon=True
    )


    websocket_thread.start()


    # Servidor TCP
    start_tcp_server()