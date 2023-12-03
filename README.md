# Telegram Audio Transcription and Translation Bot
![Project Logo](WhisperBotImg.jpg)
This Telegram bot is designed to transcribe and translate voice messages as well as audio files using the Whisper API. With this bot, you can easily convert spoken words in VNs or audio files into text and even translate them into different languages.

## Usage
If you want to use the bot, simply visit the following link: [WhisperBot](https://t.me/wwhisper_bot)

## Getting Started
If you want to create a similar bot or run it locally, follow these steps:

## Prerequisites
Make sure you have the following installed:
- Python 3.x
- Pip

## Installation
1. Clone the Repository
```sh
git clone git@github.com:adebola-duf/whisperbot.git
```
2. Navigate to the project directory:
```sh
cd whisperbot
```
3. Install the required dependencies:
```sh
pip install -r requirements.txt
```
4. Obtain API keys
- Get your Telegram Bot Token from BotFather.
- Obtain the Whisper API key from Whisper API.

## Configuration
1. Create a .env file in the project directory and add your API keys:
```sh
TELEGRAM_TOKEN=your_telegram_bot_token
WHISPER_API_KEY=your_whisper_api_key
WEBHOOK_URL_BASE=your_deployment_url
```

## Running the bot
```sh
python whisperbot.py
```
## Contributing
If you'd like to contribute to the development of this bot, feel free to submit a pull request or open an issue.

## NOTE
If you want to run the bot locally then you should comment the uvicorn.run code. And uncomment the WhiserBot.polling() line.
