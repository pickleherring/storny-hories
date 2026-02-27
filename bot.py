import asyncio
import logging
import os

import dotenv
import stoat

from handlers import hf


# logger = logging.getLogger("storny_hories")

dotenv.load_dotenv()
STOAT_TOKEN = os.environ['STOAT_TOKEN']
HEALTHCHECK_CHANNEL_ID = os.environ['STOAT_HEALTHCHECK_CHANNEL_ID']

url_handlers = (
    hf.HFHandler(),
)


class Client(stoat.Client):
    healthpulse: bool

    def __init__(self):
        self.healthpulse = False
        super().__init__()
    
    async def healthcheck(self) -> None:
        self.healthpulse = False
        channel = await self.fetch_channel(HEALTHCHECK_CHANNEL_ID)
        await channel.send("healthcheck")
        await asyncio.sleep(2)
        if not self.healthpulse:
            # logger.warning("Failed health check")
            print("Failed health check")
            await self.close()
        else:
            # logger.info("Passed health check")
            print("Passed health check")

    async def on_ready(self, event: stoat.ReadyEvent, /) -> None:
        for server in event.servers:
            # logger.info(f"joined '{server.name}'")
            print(f"joined '{server.name}'")
        await self.healthcheck()
    
    async def on_message(self, message: stoat.Message, /) -> None:
        if message.author.relationship is stoat.RelationshipStatus.user:
            if message.channel.id == HEALTHCHECK_CHANNEL_ID:
                self.healthpulse = True
            return
        
        for url_handler in url_handlers:
            try:
                embeds = await url_handler.message_to_embeds(message.content)
                if embeds:
                    await message.channel.send(embeds=embeds)
            except Exception as e:
                # logger.error(repr(e))
                print(repr(e))


# logger.info("starting")
print("starting")


while True:
    try:
        client = Client()
        client.run(
            STOAT_TOKEN,
            log_level=logging.DEBUG,
            asyncio_debug=True
        )
    except KeyboardInterrupt:
        break
    finally:
        async def cleanup():
            await asyncio.gather(client.http.cleanup(), client.shard.cleanup())
        asyncio.run(cleanup())
