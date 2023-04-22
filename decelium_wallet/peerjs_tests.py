import sys
import asyncio
from peerjs_connector import PeerJSConnector

print(PeerJSConnector)

async def main():
    if len(sys.argv) < 3:
        print("Please provide the peer ID and message as arguments.")
        return

    peer_id = sys.argv[1]
    message = sys.argv[2]

    inst = PeerJSConnector.get_instance()
    await inst.connect()

    await inst.send_message(peer_id, message)

asyncio.run(main())

# python3 peerjs_tests.py 26e85136-be3e-4109-8e54-5f6b6064f0ea hello