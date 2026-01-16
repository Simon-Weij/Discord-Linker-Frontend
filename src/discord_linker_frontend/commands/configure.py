import asyncpg
import os

from discord_linker_frontend.database.database import create_guild_settings_table, save_guild_setting, get_guild_setting

async def configure_bot(channel, server_ip: str):
    guild_id = str(channel.guild.id)
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    try:
        await create_guild_settings_table(conn)
        await save_guild_setting(conn, guild_id, server_ip)
        await channel.send(f"Bot configuration saved for server IP: {server_ip} in guild {channel.guild.name}.")
    except Exception as e:
        await channel.send(f"An error occurred while saving configuration: {e}")
    finally:
        await conn.close()