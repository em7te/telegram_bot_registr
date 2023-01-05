from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


menu = InlineKeyboardMarkup(row_width=1)
btnProfile = InlineKeyboardButton(text="Profile 👤", callback_data='btnProfile')
btnRequests = InlineKeyboardButton(text="Requests 🗄", callback_data='btnRequests')
menu.add(btnProfile, btnRequests)


btnBack = InlineKeyboardButton(text="Back", callback_data='btnBack')

back_user_requests = InlineKeyboardMarkup(row_width=1)
btnBackUserRequests = InlineKeyboardButton(text="Back", callback_data='btnBackUserRequests')
back_user_requests.add(btnBackUserRequests)

back_artist_requests = InlineKeyboardMarkup(row_width=1)
btnBackArtistRequests = InlineKeyboardButton(text="Back", callback_data='btnBackArtistRequests')
back_artist_requests.add(btnBackArtistRequests)


user_profile_menu = InlineKeyboardMarkup(row_width=1)
btnSubscribe = InlineKeyboardButton(text="Subscribe 🧑‍🎨", callback_data='btnSubscribe')
user_profile_menu.add(btnSubscribe, btnBack)

user_requests_menu = InlineKeyboardMarkup(row_width=1)
btnShowMyRequests = InlineKeyboardButton(text="Show my requests 🗃", callback_data='btnShowMyRequests')
btnSendRequest = InlineKeyboardButton(text="Send request 🖼", callback_data='btnSendRequest')
user_requests_menu.add(btnShowMyRequests, btnSendRequest, btnBack)


artist_profile_menu = InlineKeyboardMarkup(row_width=1)
btnEditProfile = InlineKeyboardButton(text="Edit profile ✍️", callback_data='btnEditProfile')
btnUnSubscribe = InlineKeyboardButton(text="Unsubscribe 😶‍🌫️", callback_data='btnUnSubscribe')
artist_profile_menu.add(btnEditProfile, btnUnSubscribe, btnBack)

artist_requests_menu = InlineKeyboardMarkup(row_width=1)
btnShowFreeRequests = InlineKeyboardButton(text="Show free requests 🗄", callback_data='btnShowFreeRequests')
btnShowAcceptedRequests = InlineKeyboardButton(text="Show accepted requests 📇", callback_data='btnShowAcceptedRequests')
artist_requests_menu.add(btnShowFreeRequests, btnShowAcceptedRequests, btnShowMyRequests, btnSendRequest, btnBack)


conf_menu = InlineKeyboardMarkup(row_width=2)
btnConfYes = InlineKeyboardButton(text="Yes", callback_data='btnConfYes')
btnConfNo = InlineKeyboardButton(text="No", callback_data='btnConfNo')
conf_menu.add(btnConfYes, btnConfNo)


not_accepted_request = InlineKeyboardMarkup(row_width=2)
btnAccept = InlineKeyboardButton(text="Accept", callback_data='btnAccept')
btnClose = InlineKeyboardButton(text="Close", callback_data='btnClose')
not_accepted_request.add(btnAccept, btnClose)

accepted_request = InlineKeyboardMarkup(row_width=2)
btnCompleted = InlineKeyboardButton(text="Completed", callback_data='btnCompleted')
accepted_request.add(btnCompleted, btnClose)
