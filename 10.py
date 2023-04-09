import telegram
import sqlite3
import openai
import datetime
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

# Set up the Telegram API token
bot_token = '6222084743:AAEuxhDAqtomW5su5YWt13qOg6R-pTRNYgg'
bot = telegram.Bot(token=bot_token)

# Set up the OpenAI API key and model
openai.api_key = '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'
model_engine = "text-davinci-002"

# Connect to the historical events database
conn = sqlite3.connect('history.db')
c = conn.cursor()

# Define the command handler for the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the Historical Events Bot! Type /help to see the available commands.")

# Define the command handler for the /help command
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Available commands:\n/date - Select a date to see historical events")

# Define the message handler for the /date command
def date(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Enter a date (DD/MM/YYYY):")

# Define the message handler for any text message
def text(update, context):
    # Check if the message is a valid date
    try:
        date_str = update.message.text
        date_obj = datetime.datetime.strptime(date_str, '%d/%m/%Y')
        date_formatted = date_obj.strftime('%B %d, %Y')
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid date format. Please enter a date in DD/MM/YYYY format.")
        return

    # Retrieve historical events for the selected date from the database
    c.execute("SELECT event FROM events WHERE date=?", (date_formatted,))
    events = c.fetchall()

    # Generate a summary of the historical events using OpenAI's GPT-3 neural network
    prompt = "Summarize the historical events of " + date_formatted
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    summary = response.choices[0].text.strip()
    # Send the summary and events as a message to the user
    message = f"Historical events on {date_formatted}:\n"
    for event in events:
        message += f"- {event[0]}\n"
    message += f"\nSummary:\n{summary}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Set up the handlers and start the bot
updater = Updater(bot_token, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('date', date))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text))
updater.start_polling()
updater.idle()




