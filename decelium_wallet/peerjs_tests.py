import asyncio
from peerjs_connector import PeerJSConnector
print(PeerJSConnector)


async def main():
    inst = PeerJSConnector.get_instance()
    await inst.connect()
    
asyncio.run(main())