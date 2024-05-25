import pickle
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import config
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier


# load model
model = pickle.load(open("model.pkl", 'rb'))


# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        """Здравствуйте! Данный телеграм-бот позволяет предсказывать метеорологическую дальность видимости (МДВ), основываясь на других погодных характеристиках.

Чтобы предсказать МДВ, заполните приведённый ниже шаблон example.csv.

Для получения справки о значении столбцов используйте команду '/help'."""
    )
    with open('example.csv', 'r') as f:
        context.bot.send_document(chat_id=update.message.chat_id, document=f)
    update.message.reply_text("⬆️ Используйте вот этот пример ⬆️")


def help(update: Update, context: CallbackContext) -> None:
    msg = """Ниже приведены описания всех используемых в файле столбцов:
      T - Температура воздуха (градусы Цельсия)
      Po - Атмосферное давление (%)
      U - Относительная влажност воздуха (мм. рт. ст.)
      DD - Направление ветра (азимут)
      Ff - Скорость ветра на высоте 10 м
      Td - Температура точки росы (градусы Цельсия)
      clear - Ясная погода (1 - да, 0 - нет)
      fog - Туман (1 - да, 0 - нет)
      smoke - Дым (1 - да, 0 - нет)
      haze - Дымка (1 - да, 0 - нет)
      mist - Мгла (1 - да, 0 - нет)
      cover_dust - Обложная пыль (1 - да, 0 - нет)
      sand - Песок в воздухе (1 - да, 0 - нет)
      dust_storm - Песчаная буря (1 - да, 0 - нет)
      blizzard_storm - Метель/буря (1 - да, 0 - нет)
      drifting_snow - Поземок (1 - да, 0 - нет)
      tornado - Торнадо/смерчи (1 - да, 0 - нет)
      squall - Шквалы (1 - да, 0 - нет)
      snow_grains - Снежные зёрна (1 - да, 0 - нет)
      ice_grains - Ледяная крупа (1 - да, 0 - нет)
      diamond_dust - Алмазная пыль (1 - да, 0 - нет)
      snow - Снег (1 - да, 0 - нет)
      hail - Град (1 - да, 0 - нет)
      rain - Дождь (1 - да, 0 - нет)
      shower - Ливень (1 - да, 0 - нет)
      drizzle - Морось (1 - да, 0 - нет)
      thunderstorm - Гроза (1 - да, 0 - нет)
      partial - Частичный(ая) (1 - да, 0 - нет)
      weak - Слабый(ая) (1 - да, 0 - нет)
      small - Небольшой(ая) (1 - да, 0 - нет)
      shreds - Клочьями (1 - да, 0 - нет)
      lower - Низовой(ая) (1 - да, 0 - нет)
      ground - Поземный(ая) (1 - да, 0 - нет)
      freezing - Замерзающий(ая) (1 - да, 0 - нет)
      strong - Сильный(ая) (1 - да, 0 - нет)
      near - Вблизи (1 - да, 0 - нет)
    """
    update.message.reply_text(msg)
    

# File handler
def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document
    if file:
        file_id = file.file_id
        new_file = context.bot.get_file(file_id)
        file_path = new_file.download()

        # Call your processing function
        print(f"Processing file at: {file_path}")

        try:
            df = pd.read_csv(file_path, sep=",")
            if df.shape[0] == 0:
                update.message.reply_text(f"Ошибка: прикреплённый файл содержит 0 записей.")
            else:
                predicted_visibility_ranges = model.predict(df)
                
        except Exception as e:
            update.message.reply_text(f"Ошибка: не получилось обработать файл. Пожалуйста, прикрепите корректный CSV файл, ориентируясь на приведённый выше пример example.csv.")
            # update.message.reply_text(e)

        if len(list(predicted_visibility_ranges)) == 1:
            update.message.reply_text(f"Предсказанная дальность видимости: {predicted_visibility_ranges[0]:.1f} км.")
        else:
            msg = "Предсказанные дальности видимости:"
            for i in range(len(predicted_visibility_ranges)):
                msg += f"\n{i+1}) {predicted_visibility_ranges[i]:.1f} км"
            update.message.reply_text(msg)
        
    else:
        update.message.reply_text("Пожалуйста, прикрепите корректный CSV файл, ориентируясь на приведённый выше пример example.csv.")


# Main function to start the bot
def main() -> None:
    updater = Updater(config.API_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_file))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
