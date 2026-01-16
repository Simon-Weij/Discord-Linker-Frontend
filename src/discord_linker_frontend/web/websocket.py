# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio
import websockets
import urllib.parse

websocket_connections = {}

async def connect_to_server(server_ip: str, channel, token: str):
    guild_id = str(channel.guild.id)
    uris = [f"wss://{server_ip}:7070/discordlinker/ws?token={urllib.parse.quote(token)}",
            f"ws://{server_ip}:7070/discordlinker/ws?token={urllib.parse.quote(token)}"]
    
    last_exception = None
    for uri in uris:
        try:
            websocket = await asyncio.wait_for(websockets.connect(uri), timeout=5.0)
            websocket_connections[guild_id] = websocket
            async def handler():
                try:
                    async for message in websocket:
                        await channel.send(message)
                except Exception:
                    await channel.send("Connection lost")
                finally:
                    websocket_connections.pop(guild_id, None)
            asyncio.create_task(handler())
            await websocket.send("Discord bot connected")
            return
        except Exception as e:
            last_exception = e
            continue
    if last_exception:
        raise last_exception