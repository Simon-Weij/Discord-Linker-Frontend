# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

async def create_guild_settings_table(conn):
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id TEXT PRIMARY KEY,
            server_ip TEXT,
            channel_id TEXT,
            token TEXT
        )
    ''')

async def save_guild_setting(conn, guild_id: str, server_ip: str, channel_id: str, token: str):
    await conn.execute('''
        INSERT INTO guild_settings (guild_id, server_ip, channel_id, token)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (guild_id) DO UPDATE SET server_ip = EXCLUDED.server_ip, channel_id = EXCLUDED.channel_id, token = EXCLUDED.token
    ''', guild_id, server_ip, channel_id, token)

async def get_guild_setting(conn, guild_id: str):
    row = await conn.fetchrow('SELECT server_ip, channel_id, token FROM guild_settings WHERE guild_id = $1', guild_id)
    return {'server_ip': row['server_ip'], 'channel_id': row['channel_id'], 'token': row['token']} if row else None