import telebot
import os
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)
manager = None  # Инициализируем глобально, чтобы использовать в функциях


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    manager.create_user_table()  # Убедимся, что таблица создана при первом запуске
    bot.send_message(user_id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")


@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = '''Доступные команды: 
- `/start` - начать работу с ботом.
- `/help` - получить список доступных команд.
- `/show_city <city_name>` - отобразить указанный город на карте.
- `/remember_city <city_name>` - сохранить город в список избранных.
- `/show_my_cities` - показать все сохраненные города.
- `/distance <city1> <city2>` - показать расстояние между двумя городами.
'''
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    try:
        city_name = message.text.split(maxsplit=1)[1].title()
    except IndexError:
        bot.send_message(message.chat.id, 'Укажите название города после команды. Пример: /show_city London')
        return

    coordinates = manager.get_coordinates(city_name)
    if not coordinates:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')
        return

    temp_file = f"temp_{message.chat.id}_{city_name}.png"
    manager.create_graph(temp_file, [city_name])
    
    with open(temp_file, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f'Вот где находится {city_name}')
    
    os.remove(temp_file)


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    try:
        city_name = message.text.split(maxsplit=1)[1].title()
    except IndexError:
        bot.send_message(message.chat.id, 'Укажите название города после команды.')
        return

    if manager.add_city(user_id, city_name):
        bot.send_message(user_id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(user_id, 'Такого города я не знаю. Убедись, что он написан на английском!')


@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    user_id = message.chat.id
    cities = manager.select_cities(user_id)

    if not cities:
        bot.send_message(user_id, 'Ваш список городов пуст. Сохраните города командой /remember_city <название>.')
        return

    temp_file = f"user_map_{user_id}.png"
    manager.create_graph(temp_file, cities)

    city_list = "\n".join([f"- {city}" for city in cities])
    caption = f"Ваши сохраненные города:\n{city_list}"

    with open(temp_file, 'rb') as photo:
        bot.send_photo(user_id, photo, caption=caption)
    
    os.remove(temp_file)


@bot.message_handler(commands=['distance'])
def handle_distance(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(message.chat.id, 'Используйте формат: /distance City1 City2')
        return

    city1, city2 = parts[1].title(), parts[2].title()
    coords1 = manager.get_coordinates(city1)
    coords2 = manager.get_coordinates(city2)

    if not coords1 or not coords2:
        bot.send_message(message.chat.id, 'Не удалось найти один из городов.')
        return

    # Используем доработанный метод создания графика расстояния
    manager.draw_distance(city1, city2)
    
    with open("map_distance.png", 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f'Расстояние между {city1} и {city2}')
    
    os.remove("map_distance.png")


if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    print("Бот запущен...")
    bot.infinity_polling(skip_pending=True)