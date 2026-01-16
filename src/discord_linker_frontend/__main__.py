# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import discord
import asyncpg
import asyncio
import websockets
from urllib.parse import urlparse
from dotenv import load_dotenv
from discord.ext import commands

from discord_linker_frontend.commands.configure import configure_bot
from discord_linker_frontend.database.database import get_guild_setting, create_guild_settings_table
from discord_linker_frontend.web.websocket import connect_to_server, websocket_connections

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

token = os.getenv("TOKEN")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)
    
    database_url = os.getenv('DATABASE_URL')
    parsed = urlparse(database_url)
    db_name = parsed.path.lstrip('/')
    postgres_url = database_url.replace(f'/{db_name}', '/postgres')
    
    try:
        conn = await asyncpg.connect(database_url)
    except asyncpg.exceptions.InvalidCatalogNameError:
        conn = await asyncpg.connect(postgres_url)
        try:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
        finally:
            await conn.close()
        conn = await asyncpg.connect(database_url)
    
    try:
        await create_guild_settings_table(conn)
    finally:
        await conn.close()

@bot.tree.command(name='ping', description='Responds with pong')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('pong')

@bot.tree.command(name='configure', description='Configures the bot')
async def configure(interaction: discord.Interaction, channel: discord.TextChannel, server_ip: str, token: str):
    await configure_bot(channel, server_ip, token)
    await interaction.response.send_message(f'Started configuring {channel.mention}.')

@bot.tree.command(name='settings', description='Shows the current bot settings for this guild')
async def settings(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    try:
        settings = await get_guild_setting(conn, guild_id)
        if settings:
            await interaction.response.send_message(f"Server IP: {settings['server_ip']}, Channel: <#{settings['channel_id']}>")
        else:
            await interaction.response.send_message("No settings configured for this guild.")
    except Exception:
        await interaction.response.send_message("An error occurred")
    finally:
        await conn.close()

@bot.tree.command(name='start', description='Connects to the server')
async def start(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    try:
        settings = await get_guild_setting(conn, guild_id)
        if settings and settings['server_ip'] and settings['token']:
            try:
                await connect_to_server(settings['server_ip'], interaction.channel, settings['token'])
                await interaction.response.send_message("Connection successful!")
            except Exception as e:
                await interaction.response.send_message(f"Connection failed: {str(e)}")
        else:
            await interaction.response.send_message("No server IP or token configured.")
    except Exception:
        await interaction.response.send_message("An error occurred")


@bot.tree.command(name='stop', description='Disconnects from the server')
async def stop(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    if guild_id in websocket_connections:
        websocket = websocket_connections.pop(guild_id)
        await websocket.close()
        await interaction.response.send_message("Connection stopped.")
    else:
        await interaction.response.send_message("No active connection.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    guild_id = str(message.guild.id)
    if guild_id in websocket_connections:
        try:
            await websocket_connections[guild_id].send(f"{message.author}: {message.content}")
        except Exception:
            await message.channel.send("Failed to send message")
            websocket_connections.pop(guild_id, None)

bot.run(token)