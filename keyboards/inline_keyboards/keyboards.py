from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


eat_button = InlineKeyboardButton('Обед', callback_data='eat_btn')
office_button = InlineKeyboardButton('Офис', callback_data='office_btn')
home_button = InlineKeyboardButton('Домой', callback_data='home_btn')


eat_end_button = InlineKeyboardButton('Пообедал', callback_data='eat_end_btn')
end_button = InlineKeyboardButton('Конец', callback_data='end_btn')


next_kbd = InlineKeyboardMarkup().add(eat_button).row(office_button).row(home_button)
alt_next_kbd = InlineKeyboardMarkup().add(office_button)
eat_end_kbd = InlineKeyboardMarkup().add(eat_end_button)
end_kbd = InlineKeyboardMarkup().add(end_button)


cancel_button = InlineKeyboardButton('Закрыть меню', callback_data='cancel_btn')
map_button = InlineKeyboardButton('Узнать местоположение инженера', callback_data='map_btn')
map_kbd = InlineKeyboardMarkup().add(map_button).add(cancel_button)


sav_button = InlineKeyboardButton('Савелий Миронов', callback_data='sav_btn')
vik_button = InlineKeyboardButton('Виктор Сиротин', callback_data='vik_btn')
agents_kbd = InlineKeyboardMarkup().add(sav_button).add(vik_button)
