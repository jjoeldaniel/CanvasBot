# CanvasBot

    A Discord bot meant to integrate with your Canvas class!

Go to:
[Features](#features),
[Setup](#setup),
[Commands](#commands)

## Features

- List all publically available assignments for a Canvas course

## Setup

*Note*: It's best practice to use a virtual enviroment! Learn more [**here**](https://realpython.com/python-virtual-environments-a-primer/)

1) Install necessary dependencies with `pip install -r requirements.txt`

2) Create a `.env` file in the main directory (copy the template provided in [.env.example](.env.example))

3) Run

## Commands

| Command                    | Description                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| `.register (api_key)`      | Registers your Canvas API key with the bot                                                  |
| `.courses`                 | Lists all possible Canvas courses for the bot to pair with. |
| `.search (query)`          | Search for a Canvas course to pair the bot pair with.      |
| `.setcourse (course_name)` | Pairs the bot with your Canvas class                                           |
| `.assignments`             | Lists all assignments for paired course                                                     |
