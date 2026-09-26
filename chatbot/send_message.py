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
    client = discord.Client(intents=intents, max_messages=2)

    @client.event
    async def on_ready():
        await client.change_presence(status=discord.Status.online,
                                     activity=discord.CustomActivity(
                                         emoji=discord.PartialEmoji.from_str("<:E_bleh:1502228749226217604>", client=client),
                                         name="o jogo, vc perdeu"
                                    ))
        #emoji="<:E_bleh:1502228749226217604>"

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith(f"<@{client.user.id}>"):
            msg = message.content.removeprefix(f"<@{client.user.id}>").lstrip(" ")

            answer = msg

            reply = await message.reply(
                "espera, eu to pensando, não me judia pufavo"
            )

            content, historymsgs = ai_answer(answer)

            print(f"{'-' * 60}\n{historymsgs}")

            await reply.edit(content=f"```{content}```\n" \
                                        "-# eu só falo merda, não escuta nada do que eu digo"
            )

            # print("acabou")

    client.run(TOKEN)

def main():
    send_message()

if __name__ == "__main__":
    main()




