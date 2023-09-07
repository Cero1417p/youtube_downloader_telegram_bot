#!/usr/bin/env python
# pylint: disable=unused-argument, import-error

import logging
import os
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import pytube
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("TOKEN")


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!"+
        """¡Hola, soy un bot para descargar mp3 de youtube !

Puedes usar los siguientes comandos:

<b>/start</b> - Iniciar el bot
<b>/help</b> - Mostrar este menú de ayuda
<b>/download</b> &lt;url&gt; - Para descargar audio."""
        ,
        #reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """download video."""
    if len(context.args)>0:
        try:
            url = context.args[0]
            logger.info("url: " + url)
            yt = pytube.YouTube(url)
            imagen = yt.thumbnail_url

            stream = yt.streams.get_audio_only()
            name = stream.default_filename
            name = name.replace("mp4", "mp3")
            logger.info("name "+name)
            stream.download(filename=name)

            await update.message.reply_photo(imagen)
            await update.message.reply_audio(open(name,'rb'))

            operation = 'rm \"' + name + '\"'
            os.system(operation)

        except pytube.exceptions.RegexMatchError:
            ms = "URL de vídeo no existe"
            await update.message.reply_text(ms)
            logger.info(ms)
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            await update.message.reply_text("Se ha producido un error")
    else:
        await update.message.reply_text("/download <url>", )  # parse_mode="HTML")




def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("download", download))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()