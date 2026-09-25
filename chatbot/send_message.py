from dotenv import load_dotenv
from ai_answer import ai_answer
import discord
import os

load_dotenv()

TOKEN = os.environ["BOT_TOKEN_ID"]

intents = discord.Intents.all()
intents.message_content = True

messages =  []

def send_message():
    # # payload_message = payload(message)
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        await client.change_presence(status=discord.Status.online)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith(f"<@{client.user.id}>"):
            displayname = client.get_user(message.author.id).display_name
            msg = message.content.removeprefix(f"<@{client.user.id}>").lstrip(" ")

            answer = msg

            await message.channel.send(
                "espera, ele tá pensando"
            )

            content = ai_answer(answer)

            await message.channel.edit(content=f"```{content}```\n" \
                                                "-# ele só diz merda, não confie em nada do que ele diz"
            )

    client.run(TOKEN)

def main():
    send_message()

if __name__ == "__main__":
    main()




