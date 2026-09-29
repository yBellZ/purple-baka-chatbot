from datetime import time, timezone, timedelta
from zoneinfo import ZoneInfo
from discord.ext import tasks
from dotenv import load_dotenv
from ai_answer import ai_answer
from collections import defaultdict
from daily_message import ai_msg
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

# histórico de conversa por servidor (usado quando mencionam o bot)
historymsgs = defaultdict(list)

# histórico das perguntas geradas na mensagem diária
daily_history = []


def sendto_ai(guild_id, msg):
    content, historymsgs[guild_id] = ai_answer(msg, historymsgs[guild_id])
    traco = "-" * (100 - len(str(guild_id)))
    log = f"Guild: {guild_id} {traco}"

    print(f"{log}\n{historymsgs[guild_id]}")
    print("-" * len(log))

    return content


def find_channel(guild):
    return discord.utils.find(
        lambda c: "geral" in c.name
        and "staff" not in c.name
        and "log" not in c.name
        and c.permissions_for(guild.me).send_messages,
        guild.text_channels,
    )


@tasks.loop(time=time(hour=12, tzinfo=timezone(timedelta(hours=-3))))
async def mensagem_diaria():
    try:
        pergunta, resposta = await asyncio.to_thread(ai_msg, daily_history)
    except Exception:
        logging.exception("Falha ao gerar a mensagem diária")
        return

    if not pergunta or not resposta:
        logging.warning("Mensagem diária vazia, nada enviado")
        return

    texto = f"**{pergunta}**\n```{resposta[:1800]}```"

    for guild in client.guilds:
        channel = find_channel(guild)
        if not channel:
            continue
        try:
            await channel.send(texto)
        except discord.HTTPException:
            logging.exception("Falha ao enviar em %s", guild.id)


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="o jogo, vc perdeu"),
    )
    if not mensagem_diaria.is_running():
        mensagem_diaria.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # ignora DMs (message.guild seria None)
    if message.guild is None:
        return

    if not message.content.startswith(f"<@{client.user.id}>"):
        return

    msg = message.content.removeprefix(f"<@{client.user.id}>").lstrip(" ")

    mrgx = re.search(r"<@!?(\d+)>", msg)
    if mrgx:
        user_id = int(mrgx.group(1))
        try:
            user = await client.fetch_user(user_id)
            msg = msg.replace(mrgx.group(0), user.display_name)
        except discord.HTTPException:
            pass

    if msg:
        reply = await message.reply("espera, eu to pensando, não me judia pufavo")
        try:
            content = await asyncio.to_thread(sendto_ai, message.guild.id, msg)
        except Exception:
            logging.exception("Falha ao responder em %s", message.guild.id)
            await reply.edit(content="deu algo errado")
            return

        await reply.edit(
            content=f"```{content[:1800]}```\n"
                    "-# eu só falo merda, não escuta nada do que eu digo"
        )
    else:
        await message.reply(
            "vc tem que escrever algo\n"
            "vo deletar a sua mensagem junto pra não ficar feio\n"
            "é daqui a 5 segundos",
            delete_after=5,
        )
        await asyncio.sleep(5)
        try:
            await message.delete()
        except discord.HTTPException:
            pass


async def main():
    discord.utils.setup_logging(level=logging.INFO)

    async with client:
        handle_shutdown(client)
        await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())