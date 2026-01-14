import discord
from discord import app_commands
import asyncio
import aiohttp

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Кэш для хранения userId
username_cache = {}

async def get_user_id(username: str):
    """Получаем UserID по никнейму"""
    if username in username_cache:
        return username_cache[username]
    
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [username]}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()
            
            if data['data'] and len(data['data']) > 0:
                user_id = data['data'][0]['id']
                username_cache[username] = user_id
                return user_id
    
    return None

async def get_presence(user_id: int):
    """Получаем статус пользователя"""
    url = "https://presence.roblox.com/v1/presence/users"
    payload = {"userIds": [user_id]}
    
    headers = {
        "Content-Type": "application/json",
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json()
            
            if 'userPresences' in data and len(data['userPresences']) > 0:
                return data['userPresences'][0]
    
    return None

@client.event
async def on_ready():
    print(f'Бот {client.user} запущен!')
    await tree.sync()

@tree.command(name="afk", description="Проверить онлайн-статус игрока в Roblox")
@app_commands.describe(username="Никнейм игрока в Roblox")
async def afk(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    
    try:
        # Получаем UserID
        user_id = await get_user_id(username)
        
        if not user_id:
            await interaction.followup.send(f"❌ Игрок `{username}` не найден!")
            return
        
        # Получаем статус
        presence = await get_presence(user_id)
        
        if not presence:
            await interaction.followup.send(f"⚫ `{username}` is offline.")
            return
        
        # Определяем статус
        user_presence = presence.get('userPresenceType', 0)
        
        if user_presence == 2:  # В игре
            await interaction.followup.send(f"🟢 `{username}` is in game.")
        elif user_presence == 1:  # Онлайн на сайте
            await interaction.followup.send(f"🔵 `{username}` is online.")
        else:  # Оффлайн
            await interaction.followup.send(f"⚫ `{username}` is offline.")
            
    except Exception as e:
        await interaction.followup.send(f"⚠️ Произошла ошибка: {e}")

# ВАЖНО: Вставьте свой токен здесь
TOKEN = "https://discord.com/oauth2/authorize?client_id=1460993123231600786&integration_type=0&scope=applications.commands"

if __name__ == "__main__":
    client.run(TOKEN)    url = f"https://presence.roblox.com/v1/presence/users"
    payload = {"userIds": [user_id]}
    
    headers = {
        "Content-Type": "application/json",
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json()
            
            if 'userPresences' in data and len(data['userPresences']) > 0:
                return data['userPresences'][0]
    
    return None

@client.event
async def on_ready():
    print(f'Бот {client.user} запущен!')
    await tree.sync()

@tree.command(name="afk", description="Проверить онлайн-статус игрока в Roblox")
@app_commands.describe(username="Никнейм игрока в Roblox")
async def afk(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    
    try:
        # Получаем UserID
        user_id = await get_user_id(username)
        
        if not user_id:
            await interaction.followup.send(f"❌ Игрок `{username}` не найден!")
            return
        
        # Получаем статус
        presence = await get_presence(user_id)
        
        if not presence:
            await interaction.followup.send(f"⚫ `{username}` - статус недоступен")
            return
        
        # Определяем статус
        user_presence = presence.get('userPresenceType', 0)
        last_location = presence.get('lastLocation', '')
        
        if user_presence == 2:  # В игре
            game_id = presence.get('rootPlaceId')
            if game_id:
                await interaction.followup.send(f"🟢 `{username}` is in game. (Place ID: {game_id})")
            else:
                await interaction.followup.send(f"🟢 `{username}` is in game.")
        
        elif user_presence == 1:  # Онлайн на сайте
            await interaction.followup.send(f"🔵 `{username}` is online.")
        
        else:  # Оффлайн
            last_online = presence.get('lastOnline', '')
            await interaction.followup.send(f"⚫ `{username}` is offline. (Last seen: {last_online[:10] if last_online else 'N/A'})")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        await interaction.followup.send(f"⚠️ Произошла ошибка при проверке статуса")

# Альтернативный вариант с более простым API (если первый не работает)
async def check_status_simple(username: str):
    """Альтернативный метод проверки статуса"""
    try:
        # Сначала получаем ID пользователя
        async with aiohttp.ClientSession() as session:
            # Получаем user_id
            user_id_url = f"https://api.roblox.com/users/get-by-username?username={username}"
            async with session.get(user_id_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'Id' in data:
                        user_id = data['Id']
                        
                        # Проверяем статус через другую API
                        status_url = f"https://api.roblox.com/users/{user_id}/onlinestatus"
                        async with session.get(status_url) as status_resp:
                            if status_resp.status == 200:
                                status_data = await status_resp.json()
                                
                                if 'IsOnline' in status_data:
                                    if status_data['IsOnline']:
                                        if 'LastLocation' in status_data:
                                            if 'Game' in status_data['LastLocation']:
                                                return "🟢 in game"
                                            else:
                                                return "🔵 online"
                                    else:
                                        return "⚫ offline"
    except:
        pass
    return None

@tree.command(name="afk2", description="Альтернативная проверка статуса")
@app_commands.describe(username="Никнейм игрока в Roblox")
async def afk2(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    
    status = await check_status_simple(username)
    
    if status:
        await interaction.followup.send(f"{status.split()[0]} `{username}` {status[4:]}")
    else:
        await interaction.followup.send(f"❌ Не удалось проверить статус `{username}`")

# Запуск бота
if __name__ == "__main__":
    # Вставьте ваш токен бота Discord здесь
    TOKEN = "https://discord.com/oauth2/authorize?client_id=1460993123231600786&integration_type=0&scope=applications.commands"
    client.run(TOKEN)
