import asyncio
import websockets
from datetime import datetime


clients = {}


def get_time():
    return datetime.now().strftime("%H:%M:%S")


async def handle_client(websocket):

    print("[SERVER] Cliente conectado.")

    try:

        name = await websocket.recv()

        clients[websocket] = name

        print(f"[SERVER] {name} entrou no chat.")

        await broadcast(
            f"[{get_time()}] {name} entrou no chat."
        )

        async for message in websocket:

            text = message.strip()

            if not text:
                continue

            formatted_message = (
                f"[{get_time()}] "
                f"{name}: {text}"
            )

            print(formatted_message)

            await broadcast(formatted_message)

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:

        name = clients.pop(websocket, None)

        if name:

            print(f"[SERVER] {name} saiu do chat.")

            await broadcast(
                f"[{get_time()}] {name} saiu do chat."
            )


async def broadcast(message):

    for client in clients:

        try:
            await client.send(message)

        except websockets.exceptions.ConnectionClosed:
            pass


async def main():

    async with websockets.serve(
        handle_client,
        "localhost",
        8765
    ):

        print("================================")
        print("       CHAT WEBSOCKET SERVER")
        print("================================")
        print("[SERVER] Porta: 8765")
        print("[SERVER] Aguardando conexões...\n")

        await asyncio.Future()


asyncio.run(main())