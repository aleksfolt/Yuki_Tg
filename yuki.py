import importlib
import sys
import time
from datetime import timedelta
import requests
from pyrogram import Client, filters
import os

start_time = time.time()
file_name = "Yuki.bot"

if not os.path.exists("modules.bot"):
    with open("modules.bot", "w") as file:
        pass

if not os.path.exists(file_name):
    api_id = input("Введите API ID: ")
    api_hash = input("Введите API Hash: ")
    prefix = input("Введите префикс который будет использоваться для команд, пример: !help или .help: ")
    user_id = input("Введите ваш user id (программа будет работать только с тем человеком чей id вы указали):")

    with open(file_name, 'w') as file:
        file.write(f"api_id={api_id}\n")
        file.write(f"api_hash={api_hash}\n")
        file.write(f"prefix={prefix}\n")
        file.write(f"user_id={user_id}\n")

    app = Client("telery_userbot", api_id=api_id, api_hash=api_hash)
    yuki_prefix = prefix
    OWNER_ID = int(user_id)
else:
    with open(file_name, 'r') as file:
        data = {}
        for line in file:
            key, value = line.strip().split('=')
            data[key] = value
    app = Client("telery_userbot", api_id=data['api_id'], api_hash=data['api_hash'])
    yuki_prefix = data['prefix']
    OWNER_ID = int(data['user_id'])


def is_owner(_, __, message):
    return message.from_user.id == OWNER_ID


def load_modules():
    modules = []
    with open("modules.bot", "r") as file:
        for line in file:
            module_name = line.strip()
            module = importlib.import_module(module_name)
            modules.append(module)
    return modules


@app.on_message(filters.create(is_owner) & filters.command("help", prefixes=yuki_prefix))
async def help_command(_, message):
    modules = load_modules()
    help_text = "**Модулей загружено: {}**\n".format(len(modules))
    for module in modules:
        help_text += f"{module.cinfo} - {module.ccomand}\n"
    help_text += (f"**Стандартные команды:**\n"
                  f"ℹ`{yuki_prefix}info` - инфо о юзерботе\n"
                  f"⌛`{yuki_prefix}ping` - Пишет пинг юб.\n"
                  f"💤`{yuki_prefix}off` - Отключает юзербота.\n"
                  f"🔄`{yuki_prefix}restart` - Перезагрузка юзербота\n"
                  f"🔽`{yuki_prefix}dm` - `{yuki_prefix}dm` <ссылка на загрузку файла>. Установка модуля на Yuki.\n"
                  f"🗑`{yuki_prefix}`delm = ``{yuki_prefix}`delm` <имя модуля>. Удаление модуля из Yuki.")
    await message.reply_text(help_text)


@app.on_message(filters.create(is_owner) & filters.command("info", prefixes=yuki_prefix))
async def info_command(_, message):
    current_time = time.time()
    uptime_seconds = int(round(current_time - start_time))
    uptime = str(timedelta(seconds=uptime_seconds))
    ping_start_time = time.time()
    await message.delete()
    ping_end_time = time.time()
    ping_time = round((ping_end_time - ping_start_time) * 1000, 1)
    user = message.from_user
    user_last = user.last_name if user.last_name else ""
    username = f"[{user.first_name} {user_last}](https://t.me/{user.username})"
    await app.send_photo(
        chat_id=message.chat.id,
        photo="https://github.com/user-attachments/assets/aecc7f9e-98b8-449e-83f2-74c3ab412df9",
        caption=f"**❄️ 雪 Yuki**\n"
                f"__🔧Version: 1.1__\n"
                f"Source: @YukiTgUserBot\n"
                f"**Ping: {ping_time}ms**\n"
                f"**Uptime: {uptime}**\n"
                f"User: {username}"
    )


@app.on_message(filters.create(is_owner) & filters.command(["ping"], prefixes=yuki_prefix))
async def ping(_, message):
    ping_start_time = time.time()
    msg = await message.edit("🌕")
    ping_end_time = time.time()
    ping_time = round((ping_end_time - ping_start_time) * 1000)
    uptime_seconds = int(round(time.time() - start_time))
    uptime = str(timedelta(seconds=uptime_seconds))
    await msg.edit(f"**🕛Ваш пинг: {ping_time} мс**\n**Uptime: {uptime}**")


@app.on_message(filters.create(is_owner) & filters.command("dm", prefixes=yuki_prefix))
async def download_py_file(_, message):
    if len(message.command) < 2:
        await message.reply_text("❗Пожалуйста, укажите ссылку на файл.")
        return

    url = message.command[1]
    if not url.endswith(".py"):
        await message.reply_text("❗Файл не является Python скриптом (.py).")
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
        file_name = os.path.basename(url)
        module_name = file_name[:-3]

        if os.path.exists("modules.bot"):
            with open("modules.bot", "r") as modules_file:
                existing_modules = modules_file.read().splitlines()
                if module_name in existing_modules:
                    await message.delete()
                    await message.reply_text(f"❗Модуль `{module_name}` уже существует в `modules.bot`.")
                    return

        with open(file_name, "wb") as file:
            file.write(response.content)

        with open("modules.bot", "a") as modules_file:
            modules_file.write(f"{module_name}\n")

        await message.delete()
        await message.reply_text(f"✅ Файл `{file_name}` успешно загружен и сохранен.\n\nLink: `{url}`")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except requests.RequestException as e:
        await message.reply_text(f"Ошибка при скачивании файла: {str(e)}")


@app.on_message(filters.create(is_owner) & filters.command("delm", prefixes=yuki_prefix))
async def delete_module(_, message):
    if len(message.command) < 2:
        await message.reply_text("❗Пожалуйста, укажите имя модуля для удаления.")
        return

    module_name = message.command[1]
    module_file = f"{module_name}.py"

    if not os.path.exists("modules.bot"):
        await message.reply_text("❗Файл `modules.bot` не найден.")
        return

    with open("modules.bot", "r") as modules_file:
        existing_modules = modules_file.read().splitlines()

    if module_name not in existing_modules:
        await message.reply_text(f"❗Модуль `{module_name}` не найден в `modules.bot`.")
        return

    updated_modules = [mod for mod in existing_modules if mod != module_name]

    with open("modules.bot", "w") as modules_file:
        modules_file.write("\n".join(updated_modules) + "\n")

    if os.path.exists(module_file):
        os.remove(module_file)
        await message.reply_text(f"✅ Модуль `{module_name}` успешно удален из `modules.bot` и файл `{module_file}` удален.")
    else:
        await message.reply_text(f"✅ Модуль `{module_name}` успешно удален из `modules.bot`, но файл `{module_file}` не найден.")

    os.execv(sys.executable, [sys.executable] + sys.argv)


@app.on_message(filters.create(is_owner) & filters.command(["off"], prefixes=yuki_prefix))
def turn_off(_, message):
    message.edit("**💤Отключаю юзербота...**")
    exit()


@app.on_message(filters.create(is_owner) & filters.command(["restart"], prefixes=yuki_prefix))
def turn_off(_, message):
    message.edit("**🔄Перезагружаю юзербота...**")
    os.execv(sys.executable, [sys.executable] + sys.argv)


def load_and_exec_modules():
    modules = load_modules()
    for module in modules:
        if hasattr(module, 'register_module'):
            module.register_module(app)


load_and_exec_modules()
app.run()
