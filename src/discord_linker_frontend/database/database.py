async def create_guild_settings_table(conn):
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id TEXT PRIMARY KEY,
            server_ip TEXT
        )
    ''')

async def save_guild_setting(conn, guild_id: str, server_ip: str):
    await conn.execute('''
        INSERT INTO guild_settings (guild_id, server_ip)
        VALUES ($1, $2)
        ON CONFLICT (guild_id) DO UPDATE SET server_ip = EXCLUDED.server_ip
    ''', guild_id, server_ip)

async def get_guild_setting(conn, guild_id: str):
    row = await conn.fetchrow('SELECT server_ip FROM guild_settings WHERE guild_id = $1', guild_id)
    return row['server_ip'] if row else None