import uvicorn
from fastapi import FastAPI
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup  # states
from telebot.storage import StateMemoryStorage
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import telebot
import whisper
from pathlib import Path
import json
import os
from dotenv import load_dotenv
load_dotenv(".env")


# bot initialization

state_storage = StateMemoryStorage()
WhisperBot_api_key = os.getenv("WHISPERBOT_API_KEY")
WhisperBot = telebot.TeleBot(WhisperBot_api_key, state_storage=state_storage)


class MyStates(StatesGroup):
    translate = State()
    audio = State()


# whisper intitialization
model = whisper.load_model("small")
languages: dict = json.loads(
    Path("/content/drive/MyDrive/languages.json").read_text())
language_list: list = [x + "\n" for x in languages.keys()]
languages_output: str = ""
for i in language_list:
    languages_output += i

audio_and_vn_dir = "Audio and VN"
os.makedirs(audio_and_vn_dir, exist_ok=True)

WEBHOOK_URL_BASE = os.getenv("WEBHOOK_URL_BASE")
app = FastAPI()


@app.post(path=f"/{WhisperBot_api_key}")
def process_webhook_text_pay_bot(update: dict):
    """
    Process webhook calls for textpay
    """
    if update:
        update = telebot.types.Update.de_json(update)
        WhisperBot.process_new_updates([update])
    else:
        return


def markup_inline():
    markup = InlineKeyboardMarkup()
    markup.width = 2
    markup.add(
        InlineKeyboardButton("Transcribe", callback_data="transcribe"),
        InlineKeyboardButton("Translate", callback_data="translate")

    )
    return markup


@WhisperBot.message_handler(commands=['start'])
def introduction(message):
    WhisperBot.send_message(
        message.chat.id, f"""
Hello 👋 @{message.from_user.username}
My name is Whisper Bot, and I'm an implementation of Open AI Whisper. Send me a voice note or an audio file to see my magic.
This is a list of my commands
/start - to start
/languages - to see the list of languages i support.""")


@WhisperBot.message_handler(commands=["cancel"])
def cancel_all_ops(message):
    WhisperBot.delete_state(user_id=message.from_user.id,
                            chat_id=message.chat.id)
    WhisperBot.reply_to(message, "cancelled")


@WhisperBot.message_handler(commands=['languages'])
def language_list(message):
    WhisperBot.send_message(message.chat.id, text=languages_output)


@WhisperBot.message_handler(content_types=['voice'])
def voice_notes_handler(voice_note):
    WhisperBot.set_state(voice_note.from_user.id,
                         MyStates.audio, voice_note.chat.id)
    with WhisperBot.retrieve_data(user_id=voice_note.from_user.id, chat_id=voice_note.chat.id) as user_data:
        # now we are setting this audio_file to True if the user sent an audio file. Else False (if they sent a voice note instead.)
        user_data['audio_file'] = False
    file_info = WhisperBot.get_file(voice_note.voice.file_id)
    downloaded_file = WhisperBot.download_file(file_info.file_path)
    with open(f'{audio_and_vn_dir}/vn{voice_note.from_user.id}.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)

    WhisperBot.send_message(
        voice_note.chat.id, "Do you want to translate or transcribe", reply_markup=markup_inline())


@WhisperBot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    if call.data == "transcribe":
        # I am using a next step handler so i don't have to do all the logic from within this callback query function
        with WhisperBot.retrieve_data(user_id=user_id, chat_id=chat_id) as user_data:
            # now we are setting this audio_file to True if the user sent an audio file. Else False (if they sent a voice note instead.)
            audio_file_y_n = user_data['audio_file']
        # if user sent an audio file and not a voice note
        if audio_file_y_n:
            WhisperBot.send_message(
                chat_id, "Audio saved. Please wait a minute for your transcription")
            output = model.transcribe(f"{audio_and_vn_dir}/audio{user_id}.mp3")
            WhisperBot.send_message(
                chat_id, f"The transcription is - '{output['text']}'")
        else:
            WhisperBot.send_message(
                chat_id, text="VN saved. Please wait a minute for your transcription")
            transcribed_vn = model.transcribe(
                f"{audio_and_vn_dir}/vn{user_id}.ogg")
            WhisperBot.send_message(
                chat_id, f"The transcription is - '{transcribed_vn['text']}'")
        WhisperBot.delete_state(user_id=user_id, chat_id=chat_id)

    elif call.data == "translate":
        # The difference between ReplyKeyboardRemove and one_time_keyboard is that ReplyKeyboardRemove remove the custom keyboard totally but one_time_keyboard just hides the keyboard but it can still be accessed by the client
        # markup_reply = ReplyKeyboardMarkup(one_time_keyboard=True)
        markup_reply = ReplyKeyboardMarkup()
        for language in languages:
            item_id = KeyboardButton(language)
            markup_reply.add(item_id)

        WhisperBot.send_message(
            call.message.chat.id, "What language would you like to translate this audio to?", reply_markup=markup_reply)
        WhisperBot.set_state(user_id=call.from_user.id,
                             state=MyStates.translate, chat_id=call.message.chat.id)


@WhisperBot.message_handler(state=MyStates.translate)
def translate_to_x_language(message):
    with WhisperBot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as user_data:
        # now we are setting this audio_file to True if the user sent an audio file. Else False (if they sent a voice note instead.)
        audio_file_y_n = user_data['audio_file']
    chosen_language = message.text.lower()
    # if the language the user sent is available
    if languages.get(chosen_language, False):
        # if user sent an audio file and not a voice note
        if audio_file_y_n:
            WhisperBot.send_message(
                message.chat.id, "Audio saved please wait a minute for your translation")
            output = model.transcribe(
                f"{audio_and_vn_dir}/audio{message.from_user.id}.mp3", language=chosen_language)
            WhisperBot.send_message(
                message.chat.id, f"The translation is - '{output['text']}'", reply_markup=ReplyKeyboardRemove())
        else:
            WhisperBot.send_message(
                message.chat.id, "VN saved please wait a minute for your translation",  reply_markup=ReplyKeyboardRemove())
            output = model.transcribe(
                f"{audio_and_vn_dir}/vn{message.from_user.id}.ogg", language=chosen_language)
            WhisperBot.send_message(
                message.chat.id, f"The translation is - '{output['text']}'")
        WhisperBot.delete_state(user_id=message.from_user.id,
                                chat_id=message.chat.id)
    else:
        # What happens if the person enters a comman like /start, I think the state would still be preserved.
        WhisperBot.reply_to(
            message, text=f"{chosen_language} is an invalid language. You can click on one of the languages on your keyboard or click /cancel")


@WhisperBot.message_handler(content_types=['audio'])
def audio_files_handler(message):
  # i think before you can create any data, you have to first be in a state
    WhisperBot.set_state(message.from_user.id, MyStates.audio, message.chat.id)
    with WhisperBot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as user_data:
        # now we are setting this audio_file to True if the user sent an audio file. Else False (if they sent a voice note instead.)
        user_data['audio_file'] = True

    file_info = WhisperBot.get_file(message.audio.file_id)
    downloaded_file = WhisperBot.download_file(file_info.file_path)
    with open(f'{audio_and_vn_dir}/audio{message.from_user.id}.mp3', 'wb') as new_file:
        new_file.write(downloaded_file)
    WhisperBot.send_message(
        message.chat.id, "Do you want to translate or transcribe", reply_markup=markup_inline())


WhisperBot.add_custom_filter(
    custom_filter=custom_filters.StateFilter(WhisperBot))

# WhisperBot.polling()

WhisperBot.remove_webhook()

# Set webhook
WhisperBot.set_webhook(
    url=WEBHOOK_URL_BASE + WhisperBot_api_key
)

uvicorn.run(app=app,
            host="0.0.0.0")
