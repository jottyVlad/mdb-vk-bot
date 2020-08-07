from vkbottle import User as vkBottleUser, Bot, Message
from vkbottle.rule import AttachmentRule
from vkbottle.branch import Branch, ExitBranch 
from vkbottle.rule import ChatActionRule
from config import ACCESS_TOKEN, USER_ACCESS_TOKEN
from rules import *
import random
import ujson
import urllib.request
from pydub import AudioSegment
import speech_recognition as sr
import os
from loguru import logger
import re
import asyncio
from tortoise import Tortoise, run_async
from models import Conversation, User, GlobalUser, GlobalRole
import typing

logger.info("IMPORTED MODULES")
async def init():

    await Tortoise.init(
        db_url='mysql://root:@localhost/bot_codeblog',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
run_async(init())
logger.info("DATABASE CONNECTED")

admins_in_conv = [444944367, 10885998, 26211044, 500101793]

bot = Bot(ACCESS_TOKEN)
user = vkBottleUser(USER_ACCESS_TOKEN)
logger.info("BOT AND USER CONNECTED")

with open('settings.json', 'r') as read_file:
    data = ujson.load(read_file)
    access_for_all = data['access']


logger.info("SETTINGS READ")

async def check_in_db_and_add_if_not_exist(user_id : int, peer_id : int, warns : int=0) -> typing.Tuple[User, GlobalUser]:
    profile = await User.get_or_none(user_id=user_id, peer_id=peer_id)
    global_profile = await GlobalUser.get_or_none(user_id=user_id)
    if profile == None:
        await User(user_id=user_id, peer_id=peer_id, warns=warns).save()
        profile = await User.get(user_id=user_id, peer_id=peer_id)

    if global_profile == None:
        default_role = await GlobalRole.get(name="Default")
        await GlobalUser(user_id=user_id, global_role=default_role).save()
        global_profile = GlobalUser.get(user_id=user_id)

    return (profile, global_profile)

@bot.on.chat_invite()
async def invite_message(action : Message):
    await bot.api.request('messages.send', {
        'message': 'Всем привет! Для того, чтобы я отвечал на сообщения, выдайте мне "Доступ ко всей переписке". Для доступа ко всем функциям выдайте мне права "Администратора"',
        'random_id': random.randint(1, 100000000000000),
        'peer_id': action.peer_id
    })
    await init()
    await Conversation(peer_id=action.peer_id).save()
    await Tortoise.close_connections()

@bot.on.message_handler(OnlyAdminAccess(), OnlyBotAdminAccess(), text="тест", lower=True)
async def test_message(ans : Message):
    await ans("Привет, чувачелла")

@bot.on.message_handler(AccessForAllRule(), text="привет", lower=True)
async def hi_message(ans : Message):
    await init()
    await check_in_db_and_add_if_not_exist(ans.from_id, ans.peer_id)
    await ans("Привет, чувачелла")

@bot.on.message_handler(AccessForAllRule(), text="максим", lower=True)
async def maxim_message(ans : Message):
    await init()
    await check_in_db_and_add_if_not_exist(ans.from_id, ans.peer_id)
    await user.api.request('messages.send', 
                            { 'message': "Максим админ тут да ага бота создаватель в беседе повеливатель ага да м-да...",  
                            'group_id': bot.group_id,
                            'peer_id': ans.peer_id,
                            'expire_ttl': '20',
                            'random_id': random.randint(1, 1000000000000000) })

@bot.on.message_handler(AccessForAllRule(), text="мда", lower=True)
async def mda_message(ans : Message):
    await init()
    await check_in_db_and_add_if_not_exist(ans.from_id, ans.peer_id)
    await user.api.request('messages.send', 
                            { 'message': "Да мда конечно это такое мда что прямо м-да...",  
                            'group_id': bot.group_id,
                            'peer_id': ans.peer_id,
                            'expire_ttl': '20',
                            'random_id': random.randint(1, 1000000000000000) })

@bot.on.message_handler(AccessForAllRule(), text="/профиль", lower=True)
async def profile_message(message : Message):
    await init()
    if message.reply_message and message.from_id in admins_in_conv:
        profile = (await check_in_db_and_add_if_not_exist(message.reply_message.from_id, message.peer_id))[0]

    elif message.reply_message and message.from_id not in admins_in_conv:
        await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
        await message("Доступ запрещен!")
        await Tortoise.close_connections()
        return 
    else:
        profile = (await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id))[0]
        
    global_user = await GlobalUser.get_or_none(user_id=message.from_id)
    global_role = await GlobalRole.get(global_userss=global_user.id)
    
    await message("Ваш ID пользователя: {0}\nГлобальная роль: {1}\nКоличество предупреждений: {2}".format(profile.user_id, global_role, profile.warns))
    await Tortoise.close_connections()

@bot.on.chat_message(OnlyAdminAccess(), text="/пред <mention> <count>", lower="True")
async def warn_with_mention_message(message : Message, mention : str, count : str):
    if all(char in mention for char in '[|]') and any(word in mention for word in ('id', 'club')):
        if 'club' in mention:
            mention = mention[5:]
        else:
            mention = mention[3:]
        mention = int(mention.split("|")[0])
    else:
        await message("Я не вижу упоминания! Упоминание обязательно!")
        return

    if (not count.isdigit()) and not (count.startswith('-') and count[1:].isdigit()):
        await message("Текст вместо цифры?.. М-да...")
    else:
        await init()
        count = int(count)
        if count > 4:
            await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
            await message("Да куда ты разогнался, больше 4 варнов кидать чуваку, тут максимум 4 варна есть, конч админ кароч")
        else:
            user_in_db = await User.get_or_none(user_id=mention, peer_id=message.peer_id)
            if user_in_db == None and count < 0:
                await check_in_db_and_add_if_not_exist(mention, message.peer_id)
                await message("Ну нет у этого юзера предов. Ну не могу я забрать то, чего НЕТУ!!")
            elif user_in_db == None and count > 0:
                await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id, count)
                await message(f"Предупреждение выдано пользователю с ID {mention}, общее количество: {count}")
            elif user_in_db != None:
                await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
                current_warns = user_in_db.warns
                if current_warns + count < 0:
                    await message(f"Предупреждение НЕ выдано, т.к. при забирании такого кол-ва варнов у него будет меньше 0 варнов, что невозможно! Общее количество предов: {current_warns}")
                else:
                    updated_user = await User.get(user_id=mention, peer_id=message.peer_id).update(warns=current_warns+count)
                    if current_warns + count >= 4:
                        await message(f"Предупреждение выдано, общее количество больше или равно 4, требуется бан пользователя! Общее количество предов: {current_warns+count}")
                    else:
                        await message(f"Предупреждение выдано, общее количество: {current_warns+count}")
            await Tortoise.close_connections()

@bot.on.chat_message(OnlyAdminAccess(), text="/пред <count>", lower="True")
async def warn_with_reply_message(message : Message, count : str):
    if message.reply_message:
        await init()
        await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
        if (not count.isdigit()) and not (count.startswith('-') and count[1:].isdigit()):
            await message("Текст вместо цифры?.. М-да...")
        else:
            count = int(count)
            if count > 4:
                await message("Да куда ты разогнался, больше 4 варнов кидать чуваку, тут максимум 4 варна есть, конч админ кароч")
            else:
                user_in_db = await User.get_or_none(user_id=message.reply_message.from_id, peer_id=message.peer_id)
                if user_in_db == None and count < 0:
                    await check_in_db_and_add_if_not_exist(mention, message.peer_id)
                    await message("Ну нет у этого юзера предов. Ну не могу я забрать то, чего НЕТУ!!")
                elif user_in_db == None and count > 0:
                    await check_in_db_and_add_if_not_exist(message.reply_message.from_id, message.peer_id, count)
                    await message(f"Предупреждение выдано пользователю с ID {message.reply_message.from_id}, общее количество: {count}")
                elif user_in_db != None:
                    await check_in_db_and_add_if_not_exist(message.reply_message.from_id, message.peer_id)
                    current_warns = user_in_db.warns
                    if current_warns + count < 0:
                        await message(f"Предупреждение НЕ выдано, т.к. при забирании такого кол-ва варнов у него будет меньше 0 варнов, что невозможно! Общее количество предов: {current_warns}")
                    else:
                        updated_user = await User.get(user_id=message.reply_message.from_id, peer_id=message.peer_id).update(warns=current_warns+count)
                        if current_warns + count >= 4:
                            await message(f"Предупреждение выдано, общее количество больше или равно 4, требуется бан пользователя! Общее количество предов: {current_warns+count}")
                        else:
                            await message(f"Предупреждение выдано, общее количество: {current_warns+count}")
                await Tortoise.close_connections()

    else:
        await message("Хоть бы сообщение того, кого варнить надо, переслал бы")

@bot.on.chat_message(AccessForAllRule(), text="/всепреды", lower=True)
async def watch_all_warns(message : Message):
    if not message.reply_message:
        await init()
        user_in_db = await User.get_or_none(user_id=message.from_id, peer_id=message.peer_id)
        await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
        if user_in_db == None or user_in_db.count == 0:
            if user_in_db == None:
                user_in_db = await User(user_id=message.reply_message.from_id, peer_id=message.peer_id).save()

            await message(f"У пользователя с ID {message.from_id} отсутствуют предупреждения!\nКоманда предлагается к удалению!")
        else:
            await message(f"Количество предупреждений у пользователя с ID {message.from_id}: {user_in_db.warns}\nКоманда предлагается к удалению!")
        
        await Tortoise.close_connections()


    if message.from_id not in admins_in_conv and message.reply_message.from_id != message.from_id:
        await init()
        await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
        await message("Тебе доступ сюда запрещен, понимаешь? Надеюсь, да. **Тихо* Опять эти дауны меня не по назначению юзают* :(\nКоманда предлагается к удалению!")
    else:
        await init()
        await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
        await check_in_db_and_add_if_not_exist(message.reply_message.from_id, message.peer_id)
        user_in_db = await User.get_or_none(user_id=message.reply_message.from_id, peer_id=message.peer_id)
        if user_in_db != None and user_in_db.warns != 0:
            await message(f"Количество предупреждений у пользователя с ID {message.reply_message.from_id}: {user_in_db.warns}\nКоманда предлагается к удалению!")
        else:
            if user_in_db == None:
                user_in_db = await User(user_id=message.reply_message.from_id, peer_id=message.peer_id).save()
            await message(f"У пользователя с ID {message.reply_message.from_id} отсутствуют предупреждения!\nКоманда предлагается к удалению!")
        await Tortoise.close_connections()

@bot.on.message_handler(AccessForAllRule(), text="/помощь", lower=True)
async def help_message(message : Message):
    await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
    await user.api.request('messages.send', 
                            { 'message': "Привет - и тебе привет!\nМаксим - он тут админ\n/пред - (только для администраторов!) выдать пред. Надо переслать сообщение юзера, которому надо дать пред\n/всепреды - посмотреть все преды. Администраторам доступен просмотр предов всех юзеров, обычным юзерам - только своих. Надо переслать сообщение, преды чьего юзера просмотреть\n/voteban с пересланным сообщением - открыть голосование за бан участника\n/инфодоступ - разрешен ли доступ к написанию сообщений в данный момент\n/профиль - посмотреть свой профиль",  
                            'group_id': bot.group_id,
                            'peer_id': message.peer_id,
                            'expire_ttl': '120',
                            'random_id': random.randint(1, 1000000000000000) })

@bot.on.message_handler(AccessForAllRule(), text="/voteban", lower=True)
async def voteban_message(message : Message):
    await init()
    await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
    if message.reply_message:
        await check_in_db_and_add_if_not_exist(message.reply_message.from_id, message.peer_id)
        if message.reply_message.from_id == message.from_id or message.reply_message.from_id in admins_in_conv or message.reply_message.from_id == -bot.group_id:
            await message("Просто попроси бана себе, а")

        else:
            poll = await user.api.request('polls.create', {
                'question': f'Голосование за бан пользователя с ID {message.reply_message.from_id}',
                'is_anonymous': 1,
                'is_multiply': 0,
                'add_answers': '["За","Против"]',
                "disable_unvote": 0
            })
            await message(attachment=f"poll{poll['owner_id']}_{poll['id']}")
    
    else:
        await message("Перешли сообщение человека, за которого начать голосование за бан!")

@bot.on.message_handler(OnlyBotModerAccess(), text="/доступ", lower=True)
async def access_message(message : Message):
    global access_for_all
    access_for_all = not access_for_all
    with open('settings.json', 'w') as write_file:
        ujson.dump({ 'access': access_for_all }, write_file)

    if access_for_all:
        await message("Доступ разрешен для всех")
    else:
        await message("Доступ разрешен только для администраторов")

@bot.on.message_handler(text="/инфодоступ", lower=True)
async def check_access_message(message : Message):
    await init()
    await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
    global access_for_all
    access = "разрешён" if access_for_all else "запрещён"
    await message(f"Доступ к написанию сообщений {access}")

@bot.on.message_handler(OnlyAdminAccess(), AccessForBotAdmin(), text="бан", lower=True)
async def bot_ban_message(message : Message):
    await init()
    await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
    if message.reply_message:
        await message(f"ПОДТВЕРДИТЕ БАН ПОЛЬЗОВАТЕЛЯ С ID {message.reply_message.from_id}! НАПИШИТЕ 'ЗАБАНИТЬ' (ЗАГЛАВНЫМИ БУКВАМИ) ДЛЯ ТОГО, ЧТОБЫ ЗАБАНИТЬ, ИЛИ 'ВЫЙТИ' (ЗАГЛАВНЫМИ), ЧТОБЫ ВЫЙТИ ИЗ ЭТОГО МЕНЮ!")
        await bot.branch.add(message.peer_id, "bot_ban_branch", user_id=message.reply_message.from_id, admin_id=message.from_id)

@bot.branch.simple_branch("bot_ban_branch")
async def bot_ban_branch(message : Message, user_id, admin_id):
    returning = False
    if message.text == "ЗАБАНИТЬ" and message.from_id == admin_id:
        await bot.api.request('messages.removeChatUser', {
            'chat_id': message.chat_id,
            'user_id': user_id
        })
        await message(f"Пользователь c ID {user_id} был забанен администратором с ID {admin_id}")
        returning = True
        await bot.branch.exit(message.peer_id)
    elif message.text == "ВЫЙТИ" and message.from_id == admin_id:
        await message("Был выполнен выход с меню бана")
        returning = True
        await bot.branch.exit(message.peer_id)

    if message.from_id == admin_id and not returning:
        await message(f"ПОДТВЕРДИТЕ БАН ПОЛЬЗОВАТЕЛЯ С ID {user_id}! НАПИШИТЕ 'ЗАБАНИТЬ' (ЗАГЛАВНЫМИ БУКВАМИ) ДЛЯ ТОГО, ЧТОБЫ ЗАБАНИТЬ, ИЛИ 'ВЫЙТИ' (ЗАГЛАВНЫМИ), ЧТОБЫ ВЫЙТИ ИЗ ЭТОГО МЕНЮ!")

@bot.on.message_handler(OnlyBotAdminAccess(), text="/разослать <text>", lower=True)
async def send_messages(message : Message, text : str):
    await init()
    await bot.api.request('messages.markAsRead', {
        'peer_id': message.peer_id,
        'mark_conversation_as_read': '1'
    })
    convs = await Conversation.all().values_list("peer_id", flat=True)
    if convs:
        for conv in convs:
            await bot.api.messages.send(peer_id=conv, random_id=random.randint(1, 1000000), message=text)

    await message("Выполнено.")
    await Tortoise.close_connections()

@bot.on.message_handler(OnlyBotModerAccess(), text="/mention <mention>", lower=True)
async def mention_test(message : Message, mention : str):
    print(mention.split('|')[0][1:])
    await message("[id{0}|Maxim]".format(message.from_id))

@bot.on.message_handler(AccessForAllRule(), text="/регистрация", lower=True)
async def registr_message(message : Message):
    profile = await User.get_or_none(user_id=user_id, peer_id=peer_id)
    global_profile = await GlobalUser.get_or_none(user_id=user_id)
    if profile != None:
        await message("Локальный профиль обнаружен")
    else:
        await User(user_id=user_id, peer_id=peer_id, warns=warns).save()
        await message("Ваш локальный профиль успешно зарегистрирован")

    if global_profile != None:
        await message("Глобальный профиль обнаружен")
    else:
        default_role = await GlobalRole.get(name="Default")
        await GlobalUser(user_id=user_id, global_role=default_role).save()
        await message("Глобальный профиль успешно зарегистрирован")

@bot.on.message_handler(OnlyBotModerAccess(), text="~ <text>", lower=True)
async def print_or_count(message : Message, text : str):
    try:
        query = ' '.join([a for a in ''.join(text.split())]).split()
        symbols_set = set([str(a) for a in range(10)])
        symbols_set.add('+')
        symbols_set.add('-')
        symbols_set.add('*')
        symbols_set.add('/')
        symbols_set.add('(')
        symbols_set.add(')')
        all_good = all(char in symbols_set for char in query)
        if all_good:
            summ = eval(text)
            await message(summ)
        else:
            await message("Возможно попытка взлома!")

    except ZeroDivisionError as e:
        await message("+-inf")
    except Exception as e:
        print(e)
        await message(text)

@bot.on.message_handler(AttachmentRule("audio_message"))
async def on_voice_message(message : Message):
    await init()
    await check_in_db_and_add_if_not_exist(message.from_id, message.peer_id)
    attachments = message.attachments

    for attachment in attachments:
        if (attachment.dict())['type'] == 'audio_message':
            voice = attachment.dict()

    filedata = urllib.request.urlretrieve(voice['audio_message']['link_ogg'], f"{message.from_id}.ogg")

    sound = AudioSegment.from_ogg(f"{message.from_id}.ogg")
    sound.export(f"{message.from_id}.wav", format="wav")

    file_audio = sr.AudioFile(f"{message.from_id}.wav")
    r = sr.Recognizer()

    with file_audio as source:
        r.adjust_for_ambient_noise(source)
        audio_text = r.record(source)

    name = (await bot.api.users.get(message.from_id))[0].first_name
    try:
        text = r.recognize_google(audio_text, language='ru-RU')
        await user.api.request('messages.send', 
                            { 'message': f"Перевод голосового сообщения пользователя [id{message.from_id}|{name}]:\n{text}",  
                            'group_id': bot.group_id,
                            'peer_id': message.peer_id,
                            'expire_ttl': '150',
                            'random_id': random.randint(1, 1000000000000000) })
        os.remove(f"{message.from_id}.ogg")
        os.remove(f"{message.from_id}.wav")
    except sr.UnknownValueError:
        await user.api.request('messages.send', 
                        { 'message': f"У пользователя [id{message.from_id}|{name}] ничего нет в голосовом сообщении!",  
                        'group_id': bot.group_id,
                        'peer_id': message.peer_id,
                        'expire_ttl': '150',
                        'random_id': random.randint(1, 1000000000000000) })
        os.remove(f"{message.from_id}.ogg")
        os.remove(f"{message.from_id}.wav")
    
logger.info("BOT IS READY TO START")
bot.run_polling(skip_updates=False)