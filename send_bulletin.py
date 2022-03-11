import requests
import json
import telepot
import argparse
import time

# Create bot (see https://medium.com/@ManHay_Hong/how-to-create-a-telegram-bot-and-send-messages-with-python-4cf314d9fa3e):
# - On Telegram, search @ BotFather, send him a “/start” message
# - Send another “/newbot” message, then follow the instructions to setup a name and a username
# - Copy API token
# - Go to bot in Telegram, and press /start
# - Bot can be accessed by others as well.
# - Once activated, user_id will be added to getUpdates response

def send_bulletin(token,bulletin,method):

	file = bulletin

	url = 'https://api.telegram.org/bot' + token + '/getUpdates'

	print('url:')
	print(url)

	resp = requests.get(url)

	r_json = json.loads(resp.text)

	print('r_json:')
	print(r_json)

	chatIdList = []

	for ii in range(len(r_json['result'])):
		chat_id = r_json['result'][ii]['message']['chat']['id']
		if chat_id not in chatIdList:
			chatIdList.append(chat_id)
		
	print('chatIdList:')
	print(chatIdList)

	bot = telepot.Bot(token)

	for jj in range(len(chatIdList)):
		print('chatIdList[jj]:')
		print(chatIdList[jj])

		# Method options are file and url
		if method == 'file':
			bot.sendPhoto(chatIdList[jj], photo=open(file, 'rb'))
		else:
			# bot.sendPhoto(chatIdList[jj], file) --> seems to give problems with https url
			with open('bulletin.png', 'wb') as f:
				f.write(requests.get(file).content)
				f.close()
				time.sleep(3)

			bot.sendPhoto(chatIdList[jj], photo=open('bulletin.png', 'rb'))

if __name__ == '__main__':

	# Get input from command line arguments
	parser = argparse.ArgumentParser(description = "Description for my parser")
	parser.add_argument("-T", "--token", help = "Telegram API token", required = True, default = "")
	parser.add_argument("-B", "--bulletin", help = "Bulletin to be send", required = True, default = "")
	parser.add_argument("-M", "--method", help = "Specify file or URL as input", required = False, default = "url")

	argument = parser.parse_args()

	if argument.token:
		token = argument.token
		print('API token = ' + token)
	if argument.bulletin:
		bulletin = argument.bulletin
		print('Bulletin filename = ' + bulletin)
	if argument.method:
		method = argument.method
		print('Method = ' + method)

	send_bulletin(token,bulletin,method)
