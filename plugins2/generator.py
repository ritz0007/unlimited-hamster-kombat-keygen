from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
import asyncio
import os
import sys
import httpx
import random
import time
import uuid
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx
import json
from collections import defaultdict

game_keys = defaultdict(list)

user_key_limits = {}

# Add these constants at the top of your file
MAX_RETRIES = 5
INITIAL_WAIT = 1
MAX_WAIT = 60
TIMEOUT = 30  # in seconds

from asyncio import Lock

class IPRateLimiter:
    def __init__(self, requests_per_minute=30):
        self.requests_per_minute = requests_per_minute
        self.ip_requests = {}
        self.lock = Lock()

    async def wait_if_needed(self, ip):
        async with self.lock:
            current_time = time.time()
            if ip not in self.ip_requests:
                self.ip_requests[ip] = []
            
            # Remove requests older than 1 minute
            self.ip_requests[ip] = [t for t in self.ip_requests[ip] if current_time - t < 60]
            
            if len(self.ip_requests[ip]) >= self.requests_per_minute:
                wait_time = 60 - (current_time - self.ip_requests[ip][0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            
            self.ip_requests[ip].append(time.time())

ip_rate_limiter = IPRateLimiter()


# @retry(
#     stop=stop_after_attempt(MAX_RETRIES),
#     wait=wait_exponential(multiplier=1, min=INITIAL_WAIT, max=MAX_WAIT),
#     retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ReadTimeout))
# )
# async def make_request(method, url, proxy=None, **kwargs):
#     logger.info(f"Making request to {url} with proxy: {proxy}")
#     async with httpx.AsyncClient(timeout=TIMEOUT, proxies=proxy) as client:
#         try:
#             if proxy:
#                 proxy_url = next(iter(proxy.values()))  # Get the first (and only) value from the proxy dict
#                 proxy_ip = proxy_url.split('@')[-1].split(':')[0]
#                 await ip_rate_limiter.wait_if_needed(proxy_ip)
#             response = await client.request(method, url, **kwargs)
#             response.raise_for_status()
#             return response.json()
#         except httpx.HTTPStatusError as e:
#             error_text = e.response.text
#             logger.error(f"HTTP error occurred: {error_text}")
#             if "TooManyIpRequest" in error_text:
#                 logger.warning("TooManyIpRequest error. Switching proxy and retrying.")
#                 raise  # This will trigger the retry mechanism
#             raise
#         except httpx.ReadTimeout:
#             logger.error("Read timeout occurred")
#             raise
#         except Exception as e:
#             logger.error(f"An unexpected error occurred: {str(e)}")
#             raise

# Disable logging for httpx
httpx_log = logger.bind(name="httpx").level("WARNING")
logger.remove()
logger.add(sink=sys.stdout, format="<white>{time:YYYY-MM-DD HH:mm:ss}</white>"
                                   " | <level>{level: <8}</level>"
                                   " | <cyan><b>{line}</b></cyan>"
                                   " - <white><b>{message}</b></white>")
logger = logger.opt(colors=True)

games = {
    1: {
        'name': 'Chain Cube 2048',
        'appToken': 'd1690a07-3780-4068-810f-9b5bbf2931b2',
        'promoId': 'b4170868-cef0-424f-8eb9-be0622e8e8e3',
        'timing': 25000 / 1000,
        'attempts': 20,
    },
    2: {
        'name': 'Train Miner',
        'appToken': '82647f43-3f87-402d-88dd-09a90025313f',
        'promoId': 'c4480ac7-e178-4973-8061-9ed5b2e17954',
        'timing': 20000 / 1000,
        'attempts': 15,
    },
    3: {
        'name': 'Merge Away',
        'appToken': '8d1cc2ad-e097-4b86-90ef-7a27e19fb833',
        'promoId': 'dc128d28-c45b-411c-98ff-ac7726fbaea4',
        'timing': 20000 / 1000,
        'attempts': 25,
    },
    4: {
        'name': 'Twerk Race 3D',
        'appToken': '61308365-9d16-4040-8bb0-2f4a4c69074c',
        'promoId': '61308365-9d16-4040-8bb0-2f4a4c69074c',
        'timing': 20000 / 1000,
        'attempts': 20,
    },
    5: {
        'name': 'Polysphere',
        'appToken': '2aaf5aee-2cbc-47ec-8a3f-0962cc14bc71',
        'promoId': '2aaf5aee-2cbc-47ec-8a3f-0962cc14bc71',
        'timing': 20000 / 1000,
        'attempts': 20,
    },
    6: {
        'name': 'Mow and Trim',
        'appToken': 'ef319a80-949a-492e-8ee0-424fb5fc20a6',
        'promoId': 'ef319a80-949a-492e-8ee0-424fb5fc20a6',
        'timing': 20000 / 1000,
        'attempts': 20,
    },
    7: {
        'name': 'Tile Trio',
        'appToken': 'e68b39d2-4880-4a31-b3aa-0393e7df10c7',
        'promoId': 'e68b39d2-4880-4a31-b3aa-0393e7df10c7',
        'timing': 20000 / 1000,
        'attempts': 20,
    },
    8: {
        'name': 'Zoopolis',
        'appToken': 'b2436c89-e0aa-4aed-8046-9b0515e1c46b',
        'promoId': 'b2436c89-e0aa-4aed-8046-9b0515e1c46b',
        'timing': 20000 / 1000,
        'attempts': 20,
    },
    9: {
        'name': 'Fluff Crusade',
        'appToken': '112887b0-a8af-4eb2-ac63-d82df78283d9',
        'promoId': '112887b0-a8af-4eb2-ac63-d82df78283d9',
        'timing': 30000 / 1000,
        'attempts': 20,
    },
    10: {
        'name': 'Stone Age',
        'appToken': '04ebd6de-69b7-43d1-9c4b-04a6ca3305af',
        'promoId': '04ebd6de-69b7-43d1-9c4b-04a6ca3305af',
        'timing': 20000 / 1000,
        'attempts': 20,
    },
   11: {
        'name': 'Bouncemasters',
        'appToken': 'bc72d3b9-8e91-4884-9c33-f72482f0db37',
        'promoId': 'bc72d3b9-8e91-4884-9c33-f72482f0db37',
        'timing': 20000 / 1000,
        'attempts': 20,
    },
    12: {
        'name': 'Hide Ball',
        'appToken': '4bf4966c-4d22-439b-8ff2-dc5ebca1a600',
        'promoId': '4bf4966c-4d22-439b-8ff2-dc5ebca1a600',
        'timing': 40000 / 1000,
        'attempts': 20,
    },
}

# Global variable to store the keys
game_keys = defaultdict(list)

async def background_key_generator(client):
    game_list = list(games.values())
    running_tasks = []
    LOG_CH = os.getenv('LOG_CH')

    async def create_task():
        game = min(game_list, key=lambda g: len(game_keys[g['name']]))
        task = asyncio.create_task(generate_key_process(
            game['appToken'],
            game['promoId'],
            game['timing'],
            game['attempts']
        ))
        return game['name'], task

    for _ in range(15):
        running_tasks.append(await create_task())

    while True:
        done, pending = await asyncio.wait(
            [task for _, task in running_tasks],
            return_when=asyncio.FIRST_COMPLETED
        )

        for completed_task in done:
            for i, (game_name, task) in enumerate(running_tasks):
                if task == completed_task:
                    del running_tasks[i]
                    break

            try:
                result = completed_task.result()
                if result:
                    game_keys[game_name].append(result)
                    logger.info(f"New key generated for {game_name}: {result}")
                    await update_json_file()
                    
                    # Log the generated key to the LOG_CH
                    if LOG_CH:
                        log_text = f"Background process generated key for {game_name}:\n`{result}`"
                        await client.send_message(LOG_CH, log_text)
                else:
                    logger.error(f"Failed to generate key for {game_name}")
            except Exception as e:
                logger.error(f"Error generating key for {game_name}: {repr(e)}")

            new_game_name, new_task = await create_task()
            running_tasks.append((new_game_name, new_task))

        await asyncio.sleep(1)

        for game_name, keys in game_keys.items():
            logger.info(f"Current keys for {game_name}: {len(keys)}")


# Function to load keys from JSON file
def load_keys_from_file():
    try:
        with open('game_keys.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Load existing keys when starting the script
game_keys.update(load_keys_from_file())

from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def update_json_file():
    try:
        with open('game_keys.json', 'w') as f:
            json.dump(game_keys, f)
        with open('user_key_limits.json', 'w') as f:
            json.dump({str(k): {
                'timestamp': v['timestamp'].isoformat(),
                'count': v['count']
            } for k, v in user_key_limits.items()}, f, cls=DateTimeEncoder)
        logger.info("Updated game_keys.json and user_key_limits.json")
    except Exception as e:
        logger.error(f"Error writing to JSON files: {str(e)}")

async def load_proxies(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                proxies = []
                for line in file:
                    try:
                        proxy_url = line.strip()
                        if proxy_url.startswith('http://'):
                            proxies.append({"http://": proxy_url})
                        elif proxy_url.startswith('https://'):
                            proxies.append({"https://": proxy_url})
                        elif proxy_url.startswith('socks4://'):
                            proxies.append({"socks4://": proxy_url})
                        elif proxy_url.startswith('socks5://'):
                            proxies.append({"socks5://": proxy_url})
                        else:
                            logger.warning(f"Skipping invalid proxy format: {proxy_url}")
                    except Exception as e:
                        logger.warning(f"Error processing proxy: {line.strip()}. Error: {e}")
                random.shuffle(proxies)
                return proxies
        else:
            logger.info(f"Proxy file {file_path} not found. No proxies will be used.")
            return []
    except Exception as e:
        logger.error(f"Error reading proxy file {file_path}: {e}")
        return []

class ProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
        self.current_index = 0
        self.proxy_cooldowns = {}

    def get_next_proxy(self):
        if not self.proxies:
            return None
        
        current_time = time.time()
        for _ in range(len(self.proxies)):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            proxy_key = frozenset(proxy.items())  # Convert dict to frozenset
            
            if proxy_key not in self.proxy_cooldowns or current_time - self.proxy_cooldowns[proxy_key] > 60:
                self.proxy_cooldowns[proxy_key] = current_time
                return proxy
        
        # If all proxies are on cooldown, wait and return the least recently used one
        least_recent_proxy_key = min(self.proxy_cooldowns, key=self.proxy_cooldowns.get)
        time_to_wait = 60 - (current_time - self.proxy_cooldowns[least_recent_proxy_key])
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        self.proxy_cooldowns[least_recent_proxy_key] = time.time()
        return dict(least_recent_proxy_key)  # Convert frozenset back to dict
    
proxy_rotator = None

async def initialize_proxy_rotator():
    global proxy_rotator
    proxies = await load_proxies('proxies.txt')
    proxy_rotator = ProxyRotator(proxies)

async def generate_client_id():
    timestamp = int(time.time() * 1000)
    random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(19))
    return f"{timestamp}-{random_numbers}"

async def login(client_id, app_token):
    logger.info(f"Attempting to log in with client ID: {client_id}")
    data = await make_request(
        'POST',
        'https://api.gamepromo.io/promo/login-client',
        # proxy=proxy,
        json={'appToken': app_token, 'clientId': client_id, 'clientOrigin': 'deviceid'}
    )
    logger.info(f"Login successful for client ID: {client_id}")
    return data['clientToken']

import random
import time

async def emulate_progress(client_token, promo_id):
    logger.info(f"Emulating progress for promo ID: {promo_id}")
    for i in range(MAX_RETRIES):
        try:
            data = await make_request(
                'POST',
                'https://api.gamepromo.io/promo/register-event',
                headers={'Authorization': f'Bearer {client_token}'},
                json={'promoId': promo_id, 'eventId': str(uuid.uuid4()), 'eventOrigin': 'undefined'}
            )
            return data['hasCode']
        except httpx.HTTPStatusError as e:
            if "TooManyRegister" in str(e):
                logger.warning(f"TooManyRegister error. Retrying with backoff. Attempt {i + 1}/{MAX_RETRIES}")
                backoff_time = INITIAL_WAIT * (2 ** i)
                jitter = random.uniform(0, backoff_time / 2)
                wait_time = backoff_time + jitter
                await asyncio.sleep(wait_time)
                continue
            else:
                raise
        except Exception as e:
            logger.error(f"Error emulating progress: {str(e)}")
            if i == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(random.uniform(1, 3))

async def generate_key(client_token, promo_id):
    logger.info(f"Generating key for promo ID: {promo_id}")
    data = await make_request(
        'POST',
        'https://api.gamepromo.io/promo/create-code',
        # proxy=proxy,
        headers={'Authorization': f'Bearer {client_token}'},
        json={'promoId': promo_id}
    )
    return data['promoCode']

def create_game_buttons():
    buttons = []
    for i, game in enumerate(games.values(), 1):
        emoji = random.choice(["🎮", "🕹️", "🎯", "🏆"])
        buttons.append([InlineKeyboardButton(f"{emoji} {game['name']}", callback_data=f"game_{game['name']}")])
    return InlineKeyboardMarkup(buttons)



from datetime import datetime, timedelta

@Client.on_message(filters.command("getkeys"))
async def get_keys_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if the user is a member, admin, or owner of @xibots_india
    try:
        member = await client.get_chat_member("@xibots_india", user_id)
        logger.info(f"User {user_id} status in @xibots_india: {member.status}")
        if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await message.reply_text("You must be a member of @xibots_india to use this command.")
            return
    except UserNotParticipant:
        await message.reply_text("You must be a member of @xibots_india to use this command. Please join the channel and try again.")
        return
    except Exception as e:
        logger.error(f"Error checking membership for user {user_id}: {str(e)}")
        await message.reply_text("An error occurred while checking your membership. Please try again later.")
        return

    # Check if the user is a PRO_ADMIN
    pro_admin = os.getenv('PRO_ADMIN')
    is_pro_admin = str(user_id) == pro_admin

    logger.info(f"User {user_id} PRO_ADMIN status: {is_pro_admin}")

    if not is_pro_admin:
        # Check if the user has reached their daily limit
        if user_id in user_key_limits:
            if datetime.now() - user_key_limits[user_id]['timestamp'] > timedelta(days=1):
                # Reset the counter if it's been more than a day
                user_key_limits[user_id] = {'timestamp': datetime.now(), 'count': {}}
        else:
            user_key_limits[user_id] = {'timestamp': datetime.now(), 'count': {}}

    keyboard = create_game_buttons()
    text = (
        "🎮 Welcome to Hamster Game Key Generator! 🎮\n\n"
        "<b>Select a game to get your keys:</b>\n"
    )
    if is_pro_admin:
        text += "🔑 Unlimited keys (PRO_ADMIN)\n"
    else:
        text += "🔑 4 keys per game per day\n"
    await message.reply_text(text, reply_markup=keyboard)


def load_user_key_limits():
    global user_key_limits
    try:
        with open('user_key_limits.json', 'r') as f:
            data = json.load(f)
            user_key_limits = {
                int(k): {
                    'timestamp': datetime.fromisoformat(v['timestamp']),
                    'count': v['count']
                } for k, v in data.items()
            }
    except FileNotFoundError:
        user_key_limits = {}
        with open('user_key_limits.json', 'w') as f:
            json.dump(user_key_limits, f)
    except json.JSONDecodeError:
        user_key_limits = {}
        with open('user_key_limits.json', 'w') as f:
            json.dump(user_key_limits, f)

@Client.on_callback_query(filters.regex(r'^game_'))
async def handle_game_selection(client: Client, callback_query):
    game_name = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    
    pro_admin = os.getenv('PRO_ADMIN')
    LOG_CH = os.getenv('LOG_CH', '')
    is_pro_admin = str(user_id) == pro_admin

    logger.info(f"User {user_id} selected game: {game_name}. PRO_ADMIN status: {is_pro_admin}")

    if not is_pro_admin:
        if user_id in user_key_limits:
            if game_name in user_key_limits[user_id]['count']:
                if user_key_limits[user_id]['count'][game_name] >= 4:
                    await callback_query.answer("You've reached your daily limit for this game.")
                    return
            else:
                user_key_limits[user_id]['count'][game_name] = 0

    if game_name in game_keys and game_keys[game_name]:
        keys = game_keys[game_name][:4]
        game_keys[game_name] = game_keys[game_name][4:]
        
        if not is_pro_admin:
            user_key_limits[user_id]['count'][game_name] = user_key_limits[user_id]['count'].get(game_name, 0) + len(keys)

        key_text = "\n".join([f"`{key}`" for key in keys])
        response_text = (
            f"🎉 Here are your keys for {game_name}:\n\n"
            f"{key_text}\n\n"
            "Enjoy your game! 🕹️\n"
            "Follow @xibot_india for more updates and games!"
        )
        await callback_query.message.reply_text(response_text)
        
        # Log the generated keys in LOG_CH
        if LOG_CH:
            log_text = f"User {callback_query.from_user.mention} ({user_id}) generated keys for {game_name}:\n{key_text}"
            if is_pro_admin:
                log_text += "\n(PRO_ADMIN)"
            await client.send_message(LOG_CH, log_text)
        
        # Update JSON file
        await update_json_file()
    else:
        await callback_query.message.reply_text(
            f"Sorry, no keys available for {game_name} at the moment. 😢\n"
            "Please try again later or choose another game.\n"
            "Follow @xibot_india for updates on key availability!"
        )

    await callback_query.answer()


# async def generate_key_process(app_token, promo_id, timing, attempts):
#     for _ in range(MAX_RETRIES):
#         client_id = await generate_client_id()
#         logger.info(f"Generated client ID: {client_id}")
#         try:
#             login_proxy = proxy_rotator.get_next_proxy()
#             client_token = await login(client_id, app_token, login_proxy)
            
#             await asyncio.sleep(random.uniform(1, 3))
            
#             for i in range(attempts):
#                 logger.info(f"Emulating progress event {i + 1}/{attempts} for client ID: {client_id}")
#                 await asyncio.sleep(timing + random.uniform(0, 2))
#                 try:
#                     progress_proxy = proxy_rotator.get_next_proxy()
#                     has_code = await emulate_progress(client_token, promo_id, progress_proxy)
#                     if has_code:
#                         logger.info(f"Progress event triggered key generation for client ID: {client_id}")
#                         break
#                 except httpx.HTTPStatusError as e:
#                     if "TooManyRegister" in str(e):
#                         logger.warning(f"TooManyRegister error. Retrying with backoff.")
#                         await asyncio.sleep(random.uniform(5, 10))
#                         continue
#                     else:
#                         raise
            
#             await asyncio.sleep(random.uniform(1, 3))
            
#             key_proxy = proxy_rotator.get_next_proxy()
#             key = await generate_key(client_token, promo_id, key_proxy)
#             logger.info(f"Generated key: {key} for client ID: {client_id}")
#             return key
#         except Exception as e:
#             logger.error(f"Error in generate_key_process: {str(e)}")
#             if _ == MAX_RETRIES - 1:
#                 return None
#             await asyncio.sleep(random.uniform(5, 10))

# @Client.on_message(filters.command("generate"))
# async def generate_command(client: Client, message: Message):
#     status_message = await message.reply_text("Starting key generation process...")
#     proxies = await load_proxies('proxies.txt')
#     selected_games = random.sample(list(games.values()), 4)  # Increase to 4 games again

#     async def generate_and_update(game):
#         try:
#             key = await generate_key_process(
#                 game['appToken'],
#                 game['promoId'],
#                 proxies,
#                 game['timing'],
#                 game['attempts']
#             )
#             if key:
#                 await status_message.edit_text(f"{status_message.text}\n{game['name']}: `{key}`")
#             return (game['name'], key) if key else None
#         except Exception as e:
#             logger.error(f"Error generating key for {game['name']}: {str(e)}")
#             return None

#     tasks = [generate_and_update(game) for game in selected_games]
#     all_keys = await asyncio.gather(*tasks)
#     all_keys = [key for key in all_keys if key]

#     if all_keys:
#         result_message = "Generated keys:\n\n" + "\n".join(f"{name}: `{key}`" for name, key in all_keys)
#     else:
#         result_message = "Failed to generate any keys."

#     await status_message.edit_text(result_message)


def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=INITIAL_WAIT, max=MAX_WAIT),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ReadTimeout))
)
async def make_request(method, url, **kwargs):
    logger.info(f"Making request to {url}")
    fake_ip = generate_random_ip()
    headers = kwargs.get('headers', {})
    headers.update({
        'X-Forwarded-For': fake_ip,
        'X-Real-IP': fake_ip,
    })
    kwargs['headers'] = headers

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            logger.error(f"HTTP error occurred: {error_text}")
            if "TooManyIpRequest" in error_text:
                logger.warning("TooManyIpRequest error. Retrying with a new fake IP.")
                raise  # This will trigger the retry mechanism
            raise
        except httpx.ReadTimeout:
            logger.error("Read timeout occurred")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            raise

async def generate_key_process(app_token, promo_id, timing, attempts):
    max_retries = 10
    base_delay = 5
    for retry in range(max_retries):
        client_id = await generate_client_id()
        logger.info(f"Generated client ID: {client_id}")
        try:
            client_token = await login(client_id, app_token)
            
            await asyncio.sleep(random.uniform(2, 5))
            
            for i in range(attempts):
                logger.info(f"Emulating progress event {i + 1}/{attempts} for client ID: {client_id}")
                await asyncio.sleep(timing + random.uniform(1, 3))
                try:
                    has_code = await emulate_progress(client_token, promo_id)
                    if has_code:
                        logger.info(f"Progress event triggered key generation for client ID: {client_id}")
                        break
                except httpx.HTTPStatusError as e:
                    if "TooManyRegister" in str(e):
                        backoff_time = base_delay * (2 ** i)
                        jitter = random.uniform(0, backoff_time / 2)
                        wait_time = backoff_time + jitter
                        logger.warning(f"TooManyRegister error. Waiting for {wait_time:.2f} seconds before retry.")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise
            
            await asyncio.sleep(random.uniform(2, 5))
            
            key = await generate_key(client_token, promo_id)
            logger.info(f"Generated key: {key} for client ID: {client_id}")
            
            # Store the key and update the JSON file
            game_name = next((game['name'] for game in games.values() if game['appToken'] == app_token), None)
            if game_name:
                game_keys[game_name].append(key)
                await update_json_file()
            
            return key
        except Exception as e:
            logger.error(f"Error in generate_key_process: {str(e)}")
            if retry == max_retries - 1:
                return None
            wait_time = base_delay * (2 ** retry) + random.uniform(0, 5)
            logger.info(f"Retrying in {wait_time:.2f} seconds...")
            await asyncio.sleep(wait_time)