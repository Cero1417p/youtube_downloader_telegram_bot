import telebot
#from telebot import types
import os
import pytube
from dotenv import load_dotenv


# carga las variables del archivo .env
load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


def main():
    bot.polling()


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    if message.text == '/start' or message.text == '/help':
        init_message = """
¡Hola, soy un bot para descargar mp3 de youtube !

Puedes usar los siguientes comandos:

<b>/start</b> - Iniciar el bot
<b>/help</b> - Mostrar este menú de ayuda
<b>/download</b> [youtube.com] - Para descargar audio.
        """
        bot.send_message(message.chat.id, init_message, parse_mode="HTML")


@bot.message_handler(commands=['download'])
def download(message):
    text = message.text
    url = text.split(" ")[1]
    chat = message.chat.id
    print("text:", url)
    try:
        yt = pytube.YouTube(url)
        imagen = yt.thumbnail_url

        # Filtramos las descargas por audio solamente, orden descendiente de calidad y
        # el primero que será el que tiene la calidad más alta
        stream = yt.streams.get_audio_only()
        name = stream.default_filename
        # quitamos espacios y paréntesis y cambiamos el tipo de fichero a mp3
        name = name.replace("mp4", "mp3")
        print("name:", name)
        # Descargamos el audio seleccionado en el directorio escogido
        stream.download(filename=name)
        # enviar imagen del audio (portada, es el thumbnail del video);
        bot.send_photo(chat_id=chat, photo=imagen)
        # enviar audio:
        bot.send_document(chat_id=chat, document=open(name, 'rb'))

        # borrar archivo de musica (solo pasa si se envia sin error)
        operation = 'rm \"' + name+'\"'
        os.system(operation)

    except pytube.exceptions.RegexMatchError:
        bot.send_message(chat, 'URL de vídeo no existe')
        print("URL no encontrada")
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        bot.send_message(chat, 'Se ha producido un error')


if __name__ == '__main__':
    main()
