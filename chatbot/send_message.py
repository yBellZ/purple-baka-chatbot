from dotenv import load_dotenv
from ai_answer import ai_answer
from collections import defaultdict
from handle_shutdown import handle_shutdown
import logging
import discord
import asyncio
import re
import os

load_dotenv()

TOKEN = os.environ["BOT_TOKEN_ID"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents, max_messages=2)

historymsgs = defaultdict(list) 

def sendto_ai(guild_id, msg):
    content, historymsgs[guild_id] = ai_answer(msg, historymsgs[guild_id])
    traco = '-' * (100 - len(str(guild_id)))
    log = f"Guild: {guild_id} {traco}"

    print(f"{log}\n"
          f"{historymsgs[guild_id]}")
    print('-' * len(str(log)))

    return content

async def send_message():
    @client.event
    async def on_ready():
        await client.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=f"o jogo, vc perdeu",))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith(f"<@{client.user.id}>"):
            msg = message.content.removeprefix(f"<@{client.user.id}>").lstrip(" ")
            mrgx = re.search(r"<@!?(\d+)>", msg)

            if mrgx:
                user_id = int(mrgx.group(1))
                user = await client.fetch_user(user_id)
                replacemrgx = str(f"<@{mrgx.group(1)}>")

                msg = msg.replace(replacemrgx, user.display_name)

            if msg:
                reply = await message.reply("espera, eu to pensando, não me judia pufavo")
                content = sendto_ai(message.guild.id, msg)

                await reply.edit(content=f"```{content}```\n" \
                                            "-# eu só falo merda, não escuta nada do que eu digo"
                )
            else:
                await message.reply("vc tem que escrever algo\nvo deletar a sua mensagem junto pra não ficar feio\né daqui a 5 segundos", delete_after=5)
                await asyncio.sleep(5); await message.delete()

    discord.utils.setup_logging(level=logging.INFO)
    
    async with client:
        handle_shutdown(client)
        await client.start(TOKEN)

async def main():
    await send_message()

if __name__ == "__main__":
    asyncio.run(main())