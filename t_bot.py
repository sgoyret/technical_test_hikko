import logging
import requests

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

keyboard = [
        [KeyboardButton("¡Quiero saber el Clima!")],
        [KeyboardButton("¡Quiero Contar!")],
    ]
chat_ids = {}
reply_markup = ReplyKeyboardMarkup(keyboard, is_persistent=True)


# callback function for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_ids
    # clean counter for specific conversation that started the bot
    if chat_ids.get(update.effective_chat.id):
        chat_ids[update.effective_chat.id] = None

    await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola! ¿Que Necesitas?",
                                   reply_markup=reply_markup)


# callback function for the weather button option
async def weather_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="¿De que Ciudad?", reply_markup=ForceReply())
    # Set state for use in weather conversation
    context.user_data["state"] = "WEATHER"


# function for the weather city call to weatherAPI
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Buscando clima para {update.effective_message.text}")

    try:
        response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={update.effective_message.text}&limit=1&appid=524aab097fad800100547ee28aba858f")

        if response.status_code == 200:
            city_info = response.json()
            if not city_info:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Clima inválido para: {update.effective_message.text}",
                                               reply_markup=reply_markup)

            else:
                response = requests.get(
                    f"https://api.openweathermap.org/data/2.5/weather?lat={city_info[0]['lat']}&"
                    f"lon={city_info[0]['lon']}&appid=524aab097fad800100547ee28aba858f&units=metric&lang=es")
                city_weather = response.json()

                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"Clima de {update.effective_message.text}: {city_weather['weather'][0]['description']},"
                                                    f" T actual: {city_weather['main']['temp']} C, "
                                                    f" T máxima: {city_weather['main']['temp_max']} C, "
                                                    f" T mínima: {city_weather['main']['temp_min']} C, "
                                                    f" sensación: {city_weather['main']['feels_like']}, "
                                                    f" viento: {city_weather['wind']['speed']} km/h, ",
                                               reply_markup=reply_markup)
        else:
            print('Error:', response.status_code)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Clima invalido para: {update.effective_message.text}",
                                           reply_markup=reply_markup)
    except Exception as e:
        logging.error(e)
    # Clean state when exiting weather conversation
    context.user_data["state"] = None


async def count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_ids
    # specific counter for each conversation
    if chat_ids.get(update.effective_chat.id):
        chat_ids[update.effective_chat.id] += 1
    else:
        chat_ids[update.effective_chat.id] = 1
    await context.bot.send_message(chat_id=update.effective_chat.id, text=chat_ids[update.effective_chat.id],
                                   reply_markup=reply_markup)


# text handlers
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.effective_message.text
    if text == "¡Quiero saber el Clima!":
        await weather_city(update, context)
    elif text == "¡Quiero Contar!":
        await count(update, context)
    elif context.user_data.get("state") == "WEATHER":
        await weather(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                                       reply_markup=reply_markup)


def main() -> None:
    """Run the bot."""
    # restart chat counters upon bot restart
    global chat_ids
    chat_ids = {}

    application = Application.builder().token("7075659775:AAEnm5wFh2xjy9Hxoe5svfcS7-KhSJ1JZnQ").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, text_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
