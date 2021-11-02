#!/usr/bin/python3

import os
import json
import serial
from shlex import quote

import pyttsx3

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler



# play an mp3
def play(sound,OS="UNIX"):
    if OS == "WIN":
        print('cmdmp3.exe "./sounds/{}.mp3"'.format(sound))
        os.system('cmdmp3.exe "./sounds/{}.mp3"'.format(sound))

    elif OS == "UNIX":
        os.system ("mpg123 -q {}.mp3 &".format(sound))

# Feed a string into OS tts
def tts(s,OS="UNIX"):
    s = quote(s)
    if OS == "WIN":
        os.system('wsay.exe "{}"'.format(s))
    elif OS == "UNIX":
        os.system("say '{}' &".format(s))

# Check whether a user/channel is authorised
def checkAuth(b):
    if b['channel']['id'] == config["channel"]:
        return True
    return False
    #print("Action was sent in {} by {}".format(b['channel']['id'],b['user']['id']))

# Find a particular response in an action payload
def findValue(b,id):
    for block in b['state']['values']:
        if id in b['state']['values'][block].keys():
            if 'selected_option' in b['state']['values'][block][id].keys():
                return b['state']['values'][block][id]['selected_option']['value']
            elif 'value' in b['state']['values'][block][id].keys():
                return b['state']['values'][block][id]['value']


def unlock_door(relays, t=5):
    if relays != "TESTING":
    # Unlock door for t seconds
        relays.write('C'.encode())
        time.sleep(t)
        relays.write('c'.encode())
        return True
    else:
        return False

with open("config.json","r") as f:
    config = json.load(f)

doorAccess=config["doorAccess"]

os.environ["SLACK_APP_TOKEN"] = config["SLACK_APP_TOKEN"]
os.environ["SLACK_BOT_TOKEN"] = config["SLACK_BOT_TOKEN"]

# Testing envrionment?
if doorAccess:
    door = serial.Serial(config["arduino"]["pointer"], baudrate=config["arduino"]["baudrate"])
else:
    door = "TESTING"

# Initialise slack
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Main control info
@app.message("control")
def controlPanel(message, say):
    # send control panel
    say(
        blocks=[
		{
			"type": "actions",
			"elements": [
				{
					"type": "static_select",
					"placeholder": {
						"type": "plain_text",
						"text": "Select a message to send",
						"emoji": True
					},
					"options": [
						{
							"text": {
								"type": "plain_text",
								"text": "Your key has been disabled",
								"emoji": True
							},
							"value": "key_disabled"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "A volunteer will contact you shortly",
								"emoji": True
							},
							"value": "volunteer_contact"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "COVID shutdown notice",
								"emoji": True
							},
							"value": "covid"
						},
						{
							"text": {
								"type": "plain_text",
								"text": "I know you're there",
								"emoji": True
							},
							"value": "notice_you"
						}
					],
					"action_id": "sendMessage"
				}
			]
		},
		{
			"dispatch_action": True,
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "ttsMessage"
			},
			"label": {
				"type": "plain_text",
				"text": "Send a custom message via text-to-speech",
				"emoji": True
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Manually unlock the door, a sound notification will be played automatically"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Unlock for 30 seconds",
					"emoji": True
				},
				"value": "30",
				"action_id": "unlock"
			}
		}
	],
        text="DoorBot manual control"
    )

# Unlock the door
@app.action("unlock")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    if unlock_door(door,30):
        say("<@{}> unlocked the door for 30 seconds".format(body['user']['id']))
    else:
        say("<@{}> tried to unlock the door remotely but either the listener is running on a server not connected to the door or there was a technical error.".format(body['user']['id']))

# Prewritten message
@app.action("sendMessage")
def handle_some_action(ack, body, say):
    ack()
    if checkAuth(body):
        messages = {"key_disabled":"noticeDisabled",
                    "volunteer_contact":"noticeContact",
                    "covid":"noticeCOVID",
                    "notice_you":"noticePresence"}
        value = findValue(body,"sendMessage")
        say("<@{}> sent the predefined message '{}'".format(body['user']['id'], value))
        play(messages[value],OS="WIN")

    #print(findValue(body,"sendMessage"))

# tts
@app.action("ttsMessage")
def handle_some_action(ack, body, say):
    ack()
    if checkAuth(body):
        value = findValue(body,"ttsMessage")
        say("<@{}> sent a custom tts message '{}'".format(body['user']['id'], value))
        tts(s=value,OS="WIN")

# Ignore other messages
@app.event("message")
def handle_message_events(body):
    pass

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
