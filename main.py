#TheElxan




import logging

import telegram
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ParseMode, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ParseMode

from game import Game
import settings

rating_dict = {}

logger = None

games = {}


def get_or_create_game(chat_id: int) -> Game:
    global games
    game = games.get(chat_id, None)
    if game is None:
        game = Game()
        games[chat_id] = game

    return game


def setup_logger():
    global logger
    file_handler = logging.FileHandler('crocodile.log', 'w', 'utf-8')
    stream_handler = logging.StreamHandler()
    logger = logging.getLogger("main_log")
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def help(update, context):
    update.message.reply_text(︎︎'Nərgiz Söz oyun botunun əmirləri⤵️\n\n📎 /start - Şəxsidə Salam Msj,Qrup daxilində oyunu tətikləyir.\n📎 /game - Oyunda aparıcı olmaq istəyirsinizsə yazın.\n📎 /rating - Qrup üzrə reytinqi görsədir.\n📎 /start - Botu başlat.', reply_to_message_id=True)


def button(update, context):
    user_id = update.callback_query.from_user.id
    chat_id = update.callback_query.message.chat_id
    bot = telegram.Bot(token=settings.TOKEN)

    game = get_or_create_game(chat_id)

    query = update.callback_query

    if query.data == 'offline_deggixm_ali':
        word = game.get_word(user_id)
        if game.is_master(query.from_user.id):
            bot.answer_callback_query(callback_query_id=query.id, text=word, show_alert=True)

    if query.data == 'offline_deggixm':
        word = game.change_word(user_id)
        if game.is_master(query.from_user.id):
            bot.answer_callback_query(callback_query_id=query.id, text=word, show_alert=True)


def command_start(update, context: CallbackContext):
    if update.effective_chat.type == "private":
        
        addme = InlineKeyboardButton(text="➕ Məni Qrupa əlavə ed ➕", url="https://t.me/KMSozOyunBot?startgroup=a")
        sohbet = [[InlineKeyboardButton(text="Kanal 📺 ", url="https://t.me/kohne_mekan_kanal")]] 
        oyun += [[InlineKeyboardButton(text="Qrup 📣", url="https://t.me/kohne_mekan")]] 
        oksi = [[InlineKeyboardButton(text="Sahib 👨‍💻", url="https://t.me/Leytenant_85")]] 
        oksi += [[InlineKeyboardButton(text="K.M Bots 🛠️", url="https://t.me/KMBots")]] 

        keyboard = [[addme],[sohbet],[oyun],[oksi]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Salam. Mənim Adım ︎︎Nərgiz.\nQruplarda Əyləncəli vaxd keçirmək üçün yaradıldım.\n\nℹ️ Qrup Əlavə edərək /game əmrinə toxunun bu sizi aparıcı edəcəkdir.\nSizə gösdəriləm sözü doslarınız izah edməyə başlayın.\nSözü tapan şəxs qalib eylan olunacaq.\n\n📎Ətraflı məlumat almaq üçün /help əmrinə toxunun.', reply_to_message_id=True, reply_markup=reply_markup)
    else:
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        username = update.message.from_user.full_name

        logger.info('Got command /start,'
                    'chat_id={},'
                    'user_id'.format(chat_id,
                                     user_id))

        game = get_or_create_game(chat_id)
        game.start()

        update.message.reply_text('ℹ️ Söz oyunu başladı...🥳'.format(username), reply_to_message_id=True)

        set_master(update, context)


def set_master(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.full_name
    logger.info('chat_id={}, New master is "{}"({})'.format(chat_id,
                                                            username,
                                                            update.message.from_user.id))

    game = get_or_create_game(chat_id)

    game.set_master(update.message.from_user.id)

    show_word_btn = InlineKeyboardButton("ℹ️ Sözə baxmaq. 👀", callback_data='offline_deggixm_ali')
    change_word_btn = InlineKeyboardButton("ℹ️ Sözü dəyişmək. ♻️", callback_data='offline_deggixm')

    keyboard = [[show_word_btn], [change_word_btn]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('[{}](tg://user?id={}) \n\nℹ️ Sözü izah edməyə başlayın...💭'.format(username,user_id), reply_to_message_id=True, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


def command_master(update: Update, context):
    chat_id = update.message.chat.id
    game = get_or_create_game(chat_id)
    username = update.message.from_user.full_name
    user_id = update.message.from_user.id

    if not game.is_game_started():
        return

    if not game.is_master_time_left():
        update.message.reply_text('ℹ️ Aparıcı olmaq üçün {} saniyə qalıb...🎉'.format(game.get_master_time_left()),
                                  reply_to_message_id=True)
        return

    logger.info('Got command /game,'
                'chat_id={},'
                'user="{}"({}),'
                'timedelta={}'.format(chat_id,
                                      username,
                                      user_id,
                                      game.get_master_time_left()))

    set_master(update, context)


def command_show_word(update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    game = get_or_create_game(chat_id)
    word = game.get_word(user_id)

    logger.info('Got command /offline_deggixm_ali, ' 
                'chat_id={}, '
                'user="{}"({}),'
                'is_user_master={},'
                'word={}'.format(chat_id,
                                 update.message.from_user.full_name,
                                 update.message.from_user.id,
                                 game.is_master(user_id),
                                 word))

    update.message.reply_text(word, reply_to_message_id=True)


def command_change_word(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id

    game = get_or_create_game(chat_id)

    word = game.change_word(user_id)

    logger.info('Got command /offline_deggixm,'
                'chat_id={},'
                'user="{}"({}),'
                'is_user_master={},'
                'word={}'.format(chat_id,
                                 update.message.from_user.full_name,
                                 user_id,
                                 game.is_master(user_id),
                                 word))

    update.message.reply_text(word, reply_to_message_id=True)


def command_rating(update, context):
    chat_id = update.message.chat.id

    game = get_or_create_game(chat_id)

    rating_str = game.get_str_rating()

    logger.info('Got command /rating,'
                'chat_id={},'
                'rating={}'.format(update.message.chat.id,
                                   rating_str))

    update.message.reply_text(rating_str, reply_to_message_id=True)


def is_word_answered(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.full_name
    text = update.message.text

    game = get_or_create_game(chat_id)

    word = game.get_current_word()

    if game.is_word_answered(user_id, text):
        update.message.reply_text('*{}*⤵️ \n\nSözünü [{}](tg://user?id={}) tapdı. 🎊'.format(word, username,user_id), reply_to_message_id=True, parse_mode=ParseMode.MARKDOWN)

        game.update_rating(user_id, username)

        set_master(update, context)

    logger.info('Guessing word,'
                'chad_id={},'
                'user="{}"({}),'
                'is_master={},'
                'text="{}",'
                'word="{}"'.format(update.message.chat.id,
                                   update.message.from_user.full_name,
                                   update.message.from_user.id,
                                   game.is_master(user_id),
                                   text,
                                   word))


def main():
    setup_logger()

    updater = Updater(settings.TOKEN, use_context=True)

    bot = updater.bot

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", command_start))
    dp.add_handler(CommandHandler("game", command_master))
    dp.add_handler(CommandHandler("offline_deggixm_ali", command_show_word))
    dp.add_handler(CommandHandler("offline_deggixm", command_change_word))
    dp.add_handler(CommandHandler("rating", command_rating))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", command_start))

    dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(MessageHandler(Filters.text, is_word_answered))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
