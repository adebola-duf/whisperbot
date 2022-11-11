import telebot
import whisper
from pathlib import Path
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

API_KEY = Path("token.txt").read_text()
bot = telebot.TeleBot(API_KEY)
model = whisper.load_model("medium")
language_file = Path("languages.json")
languages_json = json.loads(language_file.read_text())
languages_text = Path("languages.txt").read_text()


def markup_inline():
    markup = InlineKeyboardMarkup()
    markup.width = 2
    markup.add(
        InlineKeyboardButton("Transcribe", callback_data="transcribe"),
        InlineKeyboardButton("Translate", callback_data="translate")

    )
    return markup


def markup_inline2():
    markup = InlineKeyboardMarkup()
    markup.width = 2
    markup.add(
        InlineKeyboardButton("Transcribe", callback_data="transcribe2"),
        InlineKeyboardButton("Translate", callback_data="translate2")

    )
    return markup


@bot.message_handler(commands=['start', 'hello', 'hi'])
def introduction(message):
    bot.send_message(
        message.chat.id, "Hello, my name is Whisper Bot, and I'm an implementation of Open AI Whisper. Send me a voice message to see my magic.")


@bot.message_handler(commands=['languages'])
def language_list(message):
    bot.send_message(message.chat.id, languages_text)


@bot.message_handler(content_types=['voice'])
def voice_note_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('voice_note.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.send_message(
        message.chat.id, "Do you want to translate or transcribe", reply_markup=markup_inline())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'transcribe2' or call.data == 'translate2':
        callback_query2(call)

    elif call.data == "transcribe":
        bot.send_message(call.message.chat.id,
                         "VN saved. Please wait a minute for your transcription")
        output = model.transcribe("/content/voice_note.ogg")
        bot.send_message(call.message.chat.id,
                         f"The transcription is - '{output['text']}'")

    elif call.data == "translate":
        markup_reply = ReplyKeyboardMarkup(one_time_keyboard=True)
        for language in languages_json:
            item_id = KeyboardButton(language)
            markup_reply.add(item_id)
        markup_reply.one_time_keyboard = True

        bot.send_message(
            call.message.chat.id, "What language would you like to translate this audio to?", reply_markup=markup_reply)

        def language(message):
            if call.data == 'translate' and languages_json.get(message.text.lower(), 0):
                return True
            elif call.data == 'neither':
                return False
            else:
                bot.send_message(
                    message.chat.id, f"{message.text} isn't available click on one of the languages in your keyboard.", reply_markup=markup_reply)

        @bot.message_handler(func=language)
        def jkkn(message):
            bot.send_message(
                message.chat.id, "VN saved please wait a minute for your translation")
            output = model.transcribe(
                "/content/voice_note.ogg", language=languages_json.get(message.text.lower()))
            bot.send_message(
                message.chat.id, f"The transcription is - '{output['text']}'")
            call.data = 'neither'


@bot.message_handler(content_types=['audio'])
def audio_files(message):
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('audio.mp3', 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(
        message.chat.id, "Do you want to translate or transcribe", reply_markup=markup_inline2())


def callback_query2(call):
    if call.data == "transcribe2":
        bot.send_message(
            call.message.chat.id, "Audio saved. Please wait a minute for your transcription")
        output = model.transcribe("/content/audio.mp3")
        bot.send_message(call.message.chat.id,
                         f"The transcription is - '{output['text']}'")

    elif call.data == "translate2":
        markup_reply2 = ReplyKeyboardMarkup(one_time_keyboard=True)
        for language in languages_json:
            item_id = KeyboardButton(language)
            markup_reply2.add(item_id)

        bot.send_message(
            call.message.chat.id, "What language would you like to translate this audio to?", reply_markup=markup_reply2)

        def language(message):
            if call.data == 'translate2' and languages_json.get(message.text.lower(), 0):
                return True
            elif call.data == 'neither2':
                return False
            else:
                bot.send_message(
                    message.chat.id, f"{message.text} isn't available click on one of the languages in your keyboard.", reply_markup=markup_reply2)

        @bot.message_handler(func=language)
        def jkkn(message):
            bot.send_message(
                message.chat.id, "Audio saved please wait a minute for your translation")
            output = model.transcribe(
                "/content/audio.mp3", language=languages_json.get(message.text.lower()))
            bot.send_message(
                message.chat.id, f"The transcription is - '{output['text']}'")
            call.data = 'neither2'


bot.polling()
