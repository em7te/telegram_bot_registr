from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


user_menu_in = InlineKeyboardMarkup(row_width=1)
btnInProfile = InlineKeyboardButton(text="Profile 👤", callback_data='btnInProfile')
btnInSubscribe = InlineKeyboardButton(text="Subscribe 🧑‍🎨", callback_data='btnInSubscribe')
btnInSendRequest = InlineKeyboardButton(text="Send request 🖼", callback_data='btnInSendRequest')
btnInBack = InlineKeyboardButton(text="Back", callback_data='btnInBack')
user_menu_in.add(btnInProfile, btnInSubscribe, btnInSendRequest)


artist_menu_in = InlineKeyboardMarkup(row_width=1)
btnInEditProfile = InlineKeyboardButton(text="Edit profile ✍️", callback_data='btnInEditProfile')
btnInUnSubscribe = InlineKeyboardButton(text="Unsubscribe 😶‍🌫️", callback_data='btnInUnSubscribe')
btnInShowRequests = InlineKeyboardButton(text="Show requests 🗄", callback_data='btnInShowRequests')
btnInShowAcceptedRequests = InlineKeyboardButton(text="Show accepted requests 🗄",
                                                 callback_data='btnInShowAcceptedRequests')
artist_menu_in.add(btnInProfile, btnInEditProfile, btnInUnSubscribe, btnInShowRequests, btnInShowAcceptedRequests,
                   btnInSendRequest)


conf_menu = InlineKeyboardMarkup(row_width=2)
btnConfYes = InlineKeyboardButton(text="Yes", callback_data='btnConfYes')
btnConfNo = InlineKeyboardButton(text="No", callback_data='btnConfNo')
conf_menu.add(btnConfYes, btnConfNo)


request_menu_in_not_accept = InlineKeyboardMarkup(row_width=2)
btnInAccept = InlineKeyboardButton(text="Accept", callback_data='btnInAccept')
btnInClose = InlineKeyboardButton(text="Close", callback_data='btnInClose')
request_menu_in_not_accept.add(btnInAccept, btnInClose, btnInBack)

request_menu_in_accepted = InlineKeyboardMarkup(row_width=2)
btnInCompleted = InlineKeyboardButton(text="Completed", callback_data='btnInCompleted')
request_menu_in_accepted.add(btnInCompleted, btnInClose, btnInBack)




