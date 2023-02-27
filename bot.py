import telebot
import openai
import requests
from gtts import gTTS
import speech_recognition as sr
import os
#import subprocess
import ffmpeg
#from pydub import AudioSegment

# Definir token do bot do Telegram e chave de API da OpenAI
keybot = 'BOTTOKEN'
keyoai = 'OAITOKEN'
TELEGRAM_BOT_TOKEN = os.getenv(keybot)
OPENAI_API_KEY = os.getenv(keyoai)

# Conectar-se à API da OpenAI
openai.api_key = OPENAI_API_KEY

# Criar um cliente do Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Definir a mensagem de boas-vindas do bot
WELCOME_MESSAGE = "Olá! Eu sou o ChatGPT. Como posso ajudá-lo hoje?"

# Função que convert OGA em WAV
def ogg2wav(ofn):
    wfn = ofn.replace('.oga','.wav')
    x = AudioSegment.from_file(ofn)
    x.export(wfn, format='wav') 
    
# Função que converte áudio em texto usando a biblioteca SpeechRecognition
def audio_to_text(audio):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="pt-BR") # Ajuste o idioma de acordo com sua necessidade
            return text
    except Exception:
        return ""

# Definir a função de resposta do OpenAI
def reply_to_message(message):
    # Obter a mensagem do usuário
    user_message = message
# Enviar a mensagem do usuário para a OpenAI e obter uma resposta
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=user_message,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0,
    )
    return response

# Função que converte texto em áudio usando a biblioteca gTTS
def text_to_audio(text):
    tts = gTTS(text=text, lang='pt-br')
    filename = 'audio.mp3'
    tts.save(filename)
    return filename

# Comando que responde ao usuário com o áudio convertido
@bot.message_handler(content_types=['voice'])
def handle_audio(message):
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get(f'https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}')
    # file = bot.download_file(file_info.file_path) #alternativa ao comando acima
    open('audiouser.oga', 'wb').write(file.content) #savar audio
#converter audio usando ffmped    
    # subprocess.run(['ffmpeg', '-i', 'audiouser.oga', 'audiouser.wav', '-y'])  # formatting ogg file in to wav format
#converter audio usando pydub
#    sound = AudioSegment.from_ogg('audiouser.oga')
#    sound.export('audiouser.wav', format='wav')
#    stream = ffmpeg.input('audiouser.oga')
#    stream = ffmpeg.output(stream, 'audiouser.wav', format='wav')
    (
    ffmpeg
        .input('audiouser.oga')
        .output('audiouser.wav', format='wav')
        .run()
    )
# Converte o áudio em texto usando a função audio_to_text
    text = audio_to_text('audiouser.wav')
    if text=="":
        bot.reply_to(message, 'Não consegui entender o que você falou...')        
    else:
        bot.reply_to(message, 'Você disse: ' + text)
# Usa o ChatGPT para gerar uma resposta em texto
        response = reply_to_message(text)
        responseText = response.choices[0].text
# Enviar a resposta do ChatGPT de volta ao usuário
        bot.send_message(message.chat.id,responseText)
# Converte a resposta do ChatGPT em áudio usando a função text_to_audio
        audio_file = text_to_audio(responseText)
# Envia a resposta em áudio para o usuário
        audio = open(audio_file, 'rb')
        bot.send_audio(message.chat.id, audio=audio)
        audio.close()
# Exclui o arquivo de áudio do disco
        os.remove(audio_file)
    os.remove('audiouser.oga')
    os.remove('audiouser.wav')

#mensagem de boas-vindas ao iniciar o bot
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,WELCOME_MESSAGE)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # print(message.text)
    response = reply_to_message(message.text)
    responseText = response.choices[0].text
# Enviar a resposta do ChatGPT de volta ao usuário
#    bot.send_message(message.chat.id,responseText)
    bot.reply_to(message, responseText)

# Definir a função principal do bot
def main():
    bot.infinity_polling()
    # bot.polling()

if __name__ == "__main__":
    main()
