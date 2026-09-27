from dotenv import load_dotenv
from ai_answer import ai_answer
from collections import defaultdict
import discord
import asyncio
import os

load_dotenv()

TOKEN = os.environ["BOT_TOKEN_ID"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents, max_messages=2)

historymsgs = defaultdict(list)

def sendto_ai(guild_id, msg):
    content, historymsgs[guild_id] = ai_answer(msg, historymsgs[guild_id])
    print(guild_id)
    print(f"{'-' * 60}\n{historymsgs[guild_id]}")

    return content, historymsgs[guild_id]

def send_message():
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

            if msg:
                reply = await message.reply("espera, eu to pensando, não me judia pufavo")
                content, history = sendto_ai(message.guild.id, msg)

                await reply.edit(content=f"```{content}```\n" \
                                            "-# eu só falo merda, não escuta nada do que eu digo"
                )
            else:
                await message.reply("vc tem que escrever algo\nvo deletar a sua mensagem junto pra não ficar feio\né daqui a 5 segundos", delete_after=5)
                await asyncio.sleep(5); await message.delete()

    client.run(TOKEN)

def main():
    send_message()

if __name__ == "__main__":
    main()