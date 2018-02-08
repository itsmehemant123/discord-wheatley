import re
import io
import sys
import json
import time
import discord
from string import ascii_letters
from os import listdir
from os.path import isfile, join
from discord.ext import commands
from random import *
import logging
from chatterbot import ChatBot

class Wheatley:

    def __init__(self, bot):
        logging.basicConfig(level=logging.INFO)

        self.bot = bot
        self.ping_replace = re.compile(r"<@![0-9]{2,}>", re.IGNORECASE)

        with open('./config/wheatley.json') as data_file:
            self.wheatley_config = json.load(data_file)

        self.chatbot = ChatBot('akhrot', logic_adapters=["chatterbot.logic.BestMatch"], trainer='chatterbot.trainers.ChatterBotCorpusTrainer', storage_adapter='chatterbot.storage.MongoDatabaseAdapter', database=self.wheatley_config['database'], database_uri=self.wheatley_config['database_uri'])
        self.admin_roles = self.wheatley_config['admin-roles']

    def write_to_yaml(self, messages):
        file_handle = open(self.wheatley_config['corpus-folder'] + str(time.time()) + '.yml', 'w+', encoding = 'utf-8')
        file_handle.write('categories:\n- discord-chat\nconversations:\n')
        alt = True
        for message in messages:
            msg = self.ping_replace.sub('', message.content).replace('"', "'").replace('\\', '\\\\') 
            if alt:
                file_handle.write('- - "' + msg + '"\n')
            else:
                file_handle.write('  - "' + msg + '"\n')
            alt = not alt
        file_handle.close()

    async def download_messages(self, channel, limit, is_all, current_count, last_msg, msg_handle):
        before = None
        dwnld_limit = 100

        if last_msg is not None:
            before = last_msg

        if (not is_all and current_count >= limit):
            await self.bot.edit_message(msg_handle, 'Finished downloading messages.')
            return current_count

        batch_size = 0
        msg_set = []
        async for message in self.bot.logs_from(channel, limit=dwnld_limit, before=before):
            batch_size += 1
            last_msg = message
            msg_set.append(message)

        self.write_to_yaml(msg_set)

        await self.bot.edit_message(msg_handle, 'Downloaded ' + str(current_count) + ' messages.')
        current_count += batch_size
        if batch_size < 100:
            await self.bot.edit_message(msg_handle, 'Finished downloading messages.')
            return current_count
        else:
            return current_count + await self.download_messages(channel, limit, is_all, current_count, last_msg, msg_handle)

    @commands.command(pass_context=True, no_pm=True)
    async def dwnld(self, ctx, limit: str, channel: discord.Channel):
        if (len(set([role.name.lower() for role in ctx.message.author.roles]).intersection(set(self.admin_roles))) == 0):
            await self.bot.send_message(ctx.message.channel, 'Unauthorized to issue this command.')
            return
        logging.info('issued download with: ' + limit + ', in :' + channel.name + '.')
        resp = await self.bot.send_message(ctx.message.channel, 'Downloading messages.')
        is_all = False
        if (limit == 'all'):
            is_all = True
            limit = None
        else:
            limit = int(limit)
        await self.download_messages(channel, limit, is_all, 0, None, resp)

    @commands.command(pass_context=True, no_pm=True)
    async def train(self, ctx):
        if (len(set([role.name.lower() for role in ctx.message.author.roles]).intersection(set(self.admin_roles))) == 0):
            await self.bot.send_message(ctx.message.channel, 'Unauthorized to issue this command.')
            return
        logging.info('issued train command.')
        msg_handle = await self.bot.say('Issued the train command.')
        self.chatbot.train(self.wheatley_config['corpus-folder'])
        await self.bot.edit_message(msg_handle, 'Finished training.')


    async def talk(self, message):
        logging.info('MSG: ' + message.content)

        luck = random()
        if ('hey wheatley' in message.content.lower()):
            if (luck < 0.33):
                await self.bot.send_message(message.channel, 'yes bby')
            elif (luck >= 0.33 and luck < 0.66):
                await self.bot.send_message(message.channel, 'idk man')
            else:
                await self.bot.send_message(message.channel, 'fuck no my dewd')
        elif ('magnet' in message.content.lower()):
            await self.bot.send_message(message.channel, ''.join(choice(ascii_letters) for x in range(15)))
        else:
            if (luck > 0.33):
                logging.info('trigerred')
                start_time = time.time()


                if (message.channel.is_private and message.author.id == '<your_id>'):
                    logging.info('IN DMS')
                elif (not message.channel.is_private):
                    logging.info('IN CHANNEL:' + message.channel.name)
                else:
                    logging.info('UNAUTHORIZED DMS FROM:' + message.author.name + ' #' + message.author.id)
                    return

                try:
                    await self.bot.send_typing(message.channel)
                except:
                    pass #fuck it

                if (message.channel.name != 'general'):
                    _, response = self.chatbot.generate_response(self.chatbot.input.process_input_statement(message.content), self.chatbot.default_session.uuid)
                else:
                    response = self.chatbot.get_response(message.content)

                end_time = time.time()
                logging.info('Time taken for response:' + str(end_time - start_time))

                clean_msg = self.ping_replace.sub('', response.text)
                await self.bot.send_message(message.channel, clean_msg)
