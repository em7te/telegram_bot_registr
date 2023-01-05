from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


user_menu_in = InlineKeyboardMarkup(row_width=1)
btnInProfile = InlineKeyboardButton(text="Profile 👤", callback_data='btnInProfile')
btnInSubscribe = InlineKeyboardButton(text="Subscribe 🧑‍🎨", callback_data='btnInSubscribe')
btnInSendRequest = InlineKeyboardButton(text="Send request 🖼", callback_data='btnInSendRequest')
user_menu_in.add(btnInProfile, btnInSubscribe, btnInSendRequest)


artist_menu_in = InlineKeyboardMarkup(row_width=1)
btnInEditProfile = InlineKeyboardButton(text="Edit profile ✍️", callback_data='btnInEditProfile')
btnInUnSubscribe = InlineKeyboardButton(text="Unsubscribe 😶‍🌫️", callback_data='btnInUnSubscribe')
artist_menu_in.add(btnInProfile, btnInEditProfile, btnInUnSubscribe, btnInSendRequest)


conf_menu = InlineKeyboardMarkup(row_width=2)
btnConfYes = InlineKeyboardButton(text="Yes", callback_data='btnConfYes')
btnConfNo = InlineKeyboardButton(text="No", callback_data='btnConfNo')
conf_menu.add(btnConfYes, btnConfNo)


