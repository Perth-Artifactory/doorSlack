# doorSlack
This code is designed to create a control interface for DoorBot via Slack.

## Requirements

* [slack_bolt](https://github.com/slackapi/bolt-python)
* serial

### Linux

* TTS via `espeak` https://packages.ubuntu.com/impish/espeak-ng-espeak
* MP3 playback via `mpg123`https://github.com/gypified/libmpg123

### Windows

Windows lacks some basic command line tools used by the script. As the intended final device is a Raspberry Pi running Linux replacements have been provided in the repo.

* TTS via `wsay.exe` https://github.com/p-groarke/wsay
* MP3 playback via `cmdmp3.exe` https://github.com/jimlawless/cmdmp3

## Configuration

Use `config.json.template` as a template.

* `SLACK_APP_TOKEN`: App level token with at least `connections:write`. This is required to open sockets with the Slack event API. Generated on **Basic Information**
* `SLACK_BOT_TOKEN`: Bot level token with at least `chat:write``groups:history`. This is required to listen for and respond to messages in channels the bot has been added to.
* `doorAccess`: `true|false` Does the current script have access to the Arduino controlling the door? Required to make the unlock button work.
* `arduino`:  `{"pointer":"","baudrate":}` How do we communicate with the Arduino? A likely config is `{"pointer":"/dev/ttyACM0","baudrate":9600}`
* `channel`: Channel ID of the channel that the bot should respond to. #security