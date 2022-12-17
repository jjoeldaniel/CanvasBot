import canvasapi.exceptions
import discord
import os
import sqlite3
from dotenv import load_dotenv
from canvas import *

# Libraries I installed:
# pip install -U discord.py
# pip install python-dotenv
# pip install discord.ext.context <- haven't used this library

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

token = os.getenv('BOT_TOKEN')


def get_api_key(guild_id):
    """Returns Canvas API key"""

    con = sqlite3.connect("bot.db")

    try:
        with con:
            cur = con.cursor()
            cur.execute(f"SELECT api_key FROM keys WHERE guild_id = {guild_id}")

        return cur.fetchone()[0]
    except (AttributeError, TypeError):
        return "401"
    finally:
        con.close()


def simple_embed(title_text):
    """Returns Discord embed and sets title_text as embed title"""

    embed = discord.Embed(title=title_text, color=0x00000)
    embed.set_author(
        name=client.user.display_name, icon_url=client.user.avatar)
    embed.set_footer(
        text="Use .help for the complete commands list")

    return embed


@client.event
async def on_ready():
    print(f"{client.user} bot is online")

    con = sqlite3.connect("bot.db")
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS keys(guild_id int UNIQUE, api_key string, class_name string)")
    con.close()


@client.event
async def on_message(message):
    user_message = str(message.content)

    if message.author == client.user:
        return
    if message.guild is None:
        return

    if user_message.lower().startswith(".register"):
        api_key = user_message[9::].strip()
        await _register(message, api_key)
    elif user_message.lower().startswith(".setcourse"):
        query = user_message[10::].strip()
        await _set_course(message, query)
    elif user_message.lower().startswith(".search"):
        query = user_message[7::].strip()
        await _search(message, query)
    elif user_message.lower() == ".assignments":
        await _assignments(message)
    elif user_message.lower() == ".courses":
        await _courses(message)
    elif user_message.lower() == ".help":
        await _help(message)

async def _register(message, key):
    """Register (register API key)"""

    # Validates API key
    if key == "":
        await message.channel.send(embed=simple_embed("No API key inputted, try again!"))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=simple_embed("Invalid API key!"))
        return

    # Insert key into DB
    con = sqlite3.connect("bot.db")
    with con:
        cur = con.cursor()
        cur.execute(f"REPLACE "
                    f"INTO keys (guild_id, api_key) "
                    f"VALUES (({message.guild.id}), (\"{key}\"))")

    con.close()
    await message.channel.send(embed=simple_embed("API key registered!"))

async def _set_course(message, query):
    """Set Guild-Canvas course"""

    api_key = get_api_key(message.guild.id)

    # Validates API key
    if api_key == "401":
        await message.channel.send(embed=simple_embed("No API key found!"))
        return
    try:
        test_key(api_key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=simple_embed("Invalid API key!"))
        return

    if query == "" or query is None:
        await message.channel.send(embed=simple_embed("Invalid query, try again!"))
        return

    courses = search_course(api_key, query)
    if len(courses) == 0:
        await message.channel.send(embed=simple_embed(f"No courses found for: **{query}**"))
        return

    # Set course
    course = courses[0].name

    con = sqlite3.connect("bot.db")
    with con:
        cur = con.cursor()
        cur.execute(f"REPLACE "
                    f"INTO keys (guild_id, api_key, class_name) "
                    f"VALUES (({message.guild.id}), (\"{api_key}\"), (\"{course}\"))")
    con.close()

    await message.channel.send(embed=simple_embed(f"Course set as {course}"))

async def _search(message, query):
    """Search (returns matching course name)"""

    api_key = get_api_key(message.guild.id)

    # Validates API key
    if api_key == "401":
        await message.channel.send(embed=simple_embed("No API key found!"))
        return
    try:
        test_key(api_key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=simple_embed("Invalid API key!"))
        return

    if query == "":
        await message.channel.send(embed=simple_embed("Invalid query, try again!"))
        return

    courses = search_course(api_key, query)
    search_results = ""
    for course in courses:
        search_results += course.name + "\n\n"

    embed = discord.Embed(title=f"Found `{len(courses)}` courses containing: **{query}**", color=0x00000)
    embed.set_author(
        name=client.user.display_name, icon_url=client.user.avatar)
    embed.description = search_results
    embed.set_footer(
        text="Use .help for the complete commands list")

    await message.channel.send(embed=embed)

async def _help(message):
    """Returns list of commands"""

    embed = discord.Embed(title="Commands List", color=0x00000)
    embed.set_author(name=client.user.display_name, icon_url=client.user.avatar)
    embed.description = (f"`.register (api_key)` Registers your Canvas API key with the bot."
                         f" This step is required for the bot to function.\n\n"
                         f"`.courses` Intended for use during setup to list all possible "
                         f"Canvas courses for the bot to pair with.\n\n"
                         f"`.search (query)` Intended for use during setup to search for a "
                         "Canvas course to pair the bot pair with.\n\n"
                         f"`.setcourse (course_name)` This command pairs {client.user.display_name} with your "
                         f"Canvas class\n\n"
                         f"`.assignments` Lists all assignments for paired course")

    await message.channel.send(embed=embed)

async def _assignments(message):
    """List assignments"""

    api_key = get_api_key(message.guild.id)

    # Validates API key
    if api_key == "401":
        await message.channel.send(embed=simple_embed("No API key found!"))
        return
    try:
        test_key(api_key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=simple_embed("Invalid API key!"))
        return

    # Get course from DB
    con = sqlite3.connect("bot.db")
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT class_name FROM keys WHERE guild_id = {message.guild.id}")
        course_name = cur.fetchone()[0]
    con.close()

    if course_name is None:
        await message.channel.send(embed=simple_embed("No course set for guild!"))
        return

    course = search_course(api_key, course_name)[0]
    assignments = list_assignments(course)

    assignment_message = "**Assignments**\n"
    for assignment in assignments:
        assignment_message += (assignment + "\n\n")

    await message.channel.send(assignment_message)

async def _courses(message):
    """Lists all enrolled Canvas classes with guild API key"""

    api_key = get_api_key(message.guild.id)

    # Validates API key
    if api_key == "401":
        await message.channel.send(embed=simple_embed("No API key found!"))
        return
    try:
        test_key(api_key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=simple_embed("Invalid API key!"))
        return

    course_list = list_courses(api_key)
    course_message = ""
    for courses in course_list:
        course_message += courses + "\n\n"

    embed = discord.Embed(title="Course List", color=0x00000)
    embed.set_author(
        name=client.user.display_name, icon_url=client.user.avatar)
    embed.description = course_message
    embed.set_footer(
        text="Use .help for the complete commands list")

    await message.channel.send(embed=embed)

client.run(token)