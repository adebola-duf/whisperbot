import telebot
import whisper
from pathlib import Path

API_KEY = Path("token.txt").read_text()
bot = telebot.TeleBot(API_KEY)
model = whisper.load_model("medium.en")


@bot.message_handler(commands=['start', 'hello', 'hi'])
def hello_reply(message):
    bot.send_message(
        message.chat.id, "Hello, my name is Whisper Bot, and I'm an implementation of Open AI Whisper. Send me a voice message to see my magic.")


@bot.message_handler(content_types=['voice'])
def voice_note_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    bot.send_message(
        message.chat.id, "VN saved. Please wait a minute for your transcription")
    downloaded_file = bot.download_file(file_info.file_path)
    with open('voice_note.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)

    output = model.transcribe("voice_note.ogg")
    bot.send_message(
        message.chat.id, f"The transcription is - '{output['text']}'")


@bot.message_handler(content_types=['audio'])
def audio_files(message):
    bot.send_message(
        message.chat.id, "Audio file saved. Please wait a minute for your transcription")
    file_info = bot.get_file(message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('audio.mp3', 'wb') as new_file:
        new_file.write(downloaded_file)
    output = model.transcribe("audio.mp3")
    bot.send_message(
        message.chat.id, f"The transcription is - '{output['text']}'")


bot.polling()
