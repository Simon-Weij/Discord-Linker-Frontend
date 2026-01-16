# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import discord
import asyncpg
from dotenv import load_dotenv
from discord.ext import commands

from discord_linker_frontend.commands.configure import configure_bot
from discord_linker_frontend.database.database import get_guild_setting

load_dotenv()

intents = discord.Intents.default()
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

@bot.tree.command(name='ping', description='Responds with pong')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('pong')

@bot.tree.command(name='configure', description='Configures the bot')
async def configure(interaction: discord.Interaction, channel: discord.TextChannel, server_ip: str):
    await configure_bot(channel, server_ip)
    await interaction.response.send_message(f'Started configuring {channel.mention}.')

@bot.tree.command(name='settings', description='Shows the current bot settings for this guild')
async def settings(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    try:
        server_ip = await get_guild_setting(conn, guild_id)
        if server_ip:
            await interaction.response.send_message(f"Server IP: {server_ip}")
        else:
            await interaction.response.send_message("No settings configured for this guild.")
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}")
    finally:
        await conn.close()

bot.run(token)