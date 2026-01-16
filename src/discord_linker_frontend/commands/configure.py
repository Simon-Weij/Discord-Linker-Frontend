# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncpg
import os

from discord_linker_frontend.database.database import create_guild_settings_table, save_guild_setting

async def configure_bot(channel, server_ip: str, token: str):
    guild_id = str(channel.guild.id)
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    try:
        await create_guild_settings_table(conn)
        await save_guild_setting(conn, guild_id, server_ip, str(channel.id), token)
        await channel.send(f"Configuration saved for {server_ip}")
    except Exception:
        await channel.send("Failed to save configuration")
    finally:
        await conn.close()
