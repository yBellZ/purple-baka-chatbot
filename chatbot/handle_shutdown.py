import win32con
import win32api
import discord
import asyncio
import signal
import os

events = {
    win32con.CTRL_C_EVENT,
    win32con.CTRL_BREAK_EVENT,
    win32con.CTRL_CLOSE_EVENT,
    win32con.CTRL_LOGOFF_EVENT,
    win32con.CTRL_SHUTDOWN_EVENT,
}

async def change_presence(client):
    try:
        await client.change_presence(
            status=discord.Status.offline,
            activity=discord.Game("Desligando...")
        )
    except Exception as e:
        print("Falha ao mudar status:", e)

    await client.close()

def handle_shutdown(client):
    loop = asyncio.get_running_loop()

    if os.name == "posix":
        loop.add_signal_handler(
            signal.SIGTERM,
            lambda: asyncio.create_task(change_presence(client))
        )

    if os.name == "nt":
        def handler(ctrl_type):
            if ctrl_type in events:
                futuro = asyncio.run_coroutine_threadsafe(change_presence(client), loop)
                try:
                    futuro.result(timeout=4)
                except Exception:
                    pass
                return True
            return False

        win32api.SetConsoleCtrlHandler(handler, True)