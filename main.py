from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, RegexHandler, Updater)

import handlers

TOKEN = ""


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', handlers.start))
    dp.add_handler(MessageHandler(Filters.text, handlers.message))

    dp.add_handler(RegexHandler(r'/st_(.*)', handlers.station))
    dp.add_handler(RegexHandler(r'/fav_(.*)', handlers.favorite))

    dp.add_handler(CallbackQueryHandler(handlers.update_schedule))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
