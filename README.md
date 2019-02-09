# TSTB
HTTP server to respond to WebHooks from the Telegram API. Most of the code comes from [djangostars](https://djangostars.com/blog/how-to-create-and-deploy-a-telegram-bot/).

## Requirements
* A Mongo instance
* A Telegram API key
* An URL that can be POST-ed to by Telegram webhooks
* Python modules : `bottle`, `requests`

## Installation
* Rename `commands.sample.py` to `commands.py`
* Rename `config.sample.py` to `config.py`
* Rename `answers.sample.py` to `answers.py`
* And fill in your commands, config, answers

__NOTE:__ Dictionary keys must correspond between commands and answers.

## How to start the bot
`python3 main.py`