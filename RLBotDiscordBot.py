import json
import discord
import requests
import sys

try:
    from config import TOKEN
except ImportError:
    print('Unable to run bot, as token does not exist!')
    sys.exit()

settings = open('settings.json', 'r')
data = json.load(settings)
modding_author = ''
trigger_mode = False
output_mode = False
choose_mode = False
delete_mode = False
update_game_mode = False

client = discord.Client()


@client.event
async def on_ready():
    print('READY')
    await client.change_presence(activity=discord.Game(name=data['Status_message']))


@client.event
async def on_message(message):
    global modding_author
    global trigger_mode
    global output_mode
    global trigger
    global data
    global choose_mode
    global delete_mode
    global update_game_mode
    author = message.author

    if message.author == client.user:
        return

    elif message.content.lower() == '!botmaker add' or message.content.lower() == '!botmaker':
        botmaker_role = discord.utils.get(message.guild.roles, name='BotMaker')
        await author.add_roles(botmaker_role)
        return

    elif message.content.lower() == '!botmaker remove' or message.content.lower() == '!botmaker off':
        botmaker_role = discord.utils.get(message.guild.roles, name='BotMaker')
        await author.remove_roles(botmaker_role)
        return

    elif message.content.lower().startswith('!add command'):
        allow_edit = False
        for roles in author.roles:
            if roles.name == 'Contributor' or roles.name == 'Moderator':
                if message.channel.name == 'discord-bots':
                    allow_edit = True
        if allow_edit:
            blocks = message.content.split("'")
            valid_command = False
            if len(blocks) == 5:
                valid_command = True
            else:
                blocks = message.content.split('"')
                if len(blocks) == 5:
                    valid_command = True
            if valid_command:
                trigger = blocks[1]
                output = blocks[3]
                new = True
                for command in data['commands']:
                    if trigger == command:
                        new = False
                        previous_text = 'Previous output:\n' + str(data['commands'][command])
                        await client.send_message(message.channel, previous_text)
                data['commands'][trigger] = output
                settings = open('settings.json', 'w')
                json.dump(data, settings, indent=4)
                settings = open('settings.json', 'r')
                data = json.load(settings)
                if new:
                    await message.channel.send('Command added')
                else:
                    await message.channel.send('Command edited')

    elif message.content.lower().startswith('!del command'):
        allow_edit = False
        for roles in author.roles:
            if roles.name == 'Contributor' or roles.name == 'Moderator':
                if message.channel.name == 'discord-bots':
                    allow_edit = True
        if allow_edit:
            blocks = message.content.split("'")
            valid_command = False
            if len(blocks) == 3:
                valid_command = True
            else:
                blocks = message.content.split('"')
                if len(blocks) == 3:
                    valid_command = True
            if valid_command:
                trigger = blocks[1]
                for command in data['commands']:
                    if trigger == command:
                        exists = True
                        previous_text = 'Previous output:\n' + str(data['commands'][command])
                        await message.channel.send(previous_text)
                if not exists:
                    await message.channel.send('Command does not exist')
                if exists:
                    del data['commands'][trigger]
                    settings = open('settings.json', 'w')
                    json.dump(data, settings, indent=4)
                    settings = open('settings.json', 'r')
                    data = json.load(settings)
                    await message.channel.send('Command deleted')

    elif message.content.lower().startswith('!edit game'):
        allow_edit = False
        for roles in author.roles:
            if roles.name == 'Contributor' or roles.name == 'Moderator':
                if message.channel.name == 'discord-bots':
                    allow_edit = True
        if allow_edit:
            blocks = message.content.split("'")
            valid_command = False
            if len(blocks) == 3:
                valid_command = True
            else:
                blocks = message.content.split('"')
                if len(blocks) == 3:
                    valid_command = True
            if valid_command:
                game = blocks[1]
                data['Status_message'] = game
                settings = open('settings.json', 'w')
                json.dump(data, settings, indent=4)
                settings = open('settings.json', 'r')
                data = json.load(settings)
                await client.change_presence(activity=discord.Game(name=data['Status_message']))
                await message.channel.send('Game updated')
                return

    elif message.content.lower().startswith('!give settings'):
        allow_edit = False
        for roles in author.roles:
            if roles.name == 'Contributor' or roles.name == 'Moderator':
                if message.channel.name == 'discord-bots':
                    allow_edit = True
        if allow_edit:
            await message.channel.send(file=discord.File('settings.json'))
            return

    elif message.content.lower().startswith('!take settings'):
        allow_edit = False
        for roles in author.roles:
            if roles.name == 'Contributor' or roles.name == 'Moderator':
                if message.channel.name == 'discord-bots':
                    allow_edit = True
        if allow_edit:
            attachment = message.attachments
            if len(attachment) > 0:
                url = attachment[0].url
                name = attachment[0].filename
                r = requests.get(url, allow_redirects=True)
                f = open(name, 'wb')
                f.write(r.content)
                f.close()
                settings = open('settings.json', 'r')
                data = json.load(settings)
                await message.channel.send('Settings updated')
            else:
                await message.channel.send('You know very well you should provide a file!')
            return

    elif message.content.lower().startswith('!commands'):
        allow_edit = False
        for roles in author.roles:
            if roles.name == 'Contributor' or roles.name == 'Moderator':
                if message.channel.name == 'discord-bots':
                    allow_edit = True
        if allow_edit:
            all_commands = ''
            for command in data['commands']:
                all_commands = all_commands + '\n' + command
            await message.channel.send(all_commands)
            return

    else:
        for command in data['commands']:
            string_divided = message.content.lower().split(' ')
            for triggers in string_divided:
                if triggers.startswith(command):
                    await message.channel.send(str(data['commands'][command]))
                    return


client.run(TOKEN)
