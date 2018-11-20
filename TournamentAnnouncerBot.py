import discord
import asyncio
import time
import datetime
from discord.ext import commands
import os
import time
from datetime import datetime
from rlbot.utils import rate_limiter
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.game_interface import GameInterface
from rlbot.utils.structures import game_data_struct

GAME_TICK_PACKET_REFRESHES_PER_SECOND = 120  # 2*60. https://en.wikipedia.org/wiki/Nyquist_rate

client = discord.Client()
botToken= ##TOKEN##
#chat=discord.Object(id='369871532861816833')
chat=discord.Object(id='474710564627808287')
num = 0
elapsed = 0
overtime = 0
ended = 0
team = 0
name = ''
goals = 0
own_goals = 0

class GameTickReader:
    def __init__(self):
        self.logger = get_logger('packet reader')
        self.game_interface = GameInterface(self.logger)
        self.game_interface.inject_dll()
        self.game_interface.load_interface()
        self.game_tick_packet = game_data_struct.GameTickPacket()
        self.rate_limit = rate_limiter.RateLimiter(GAME_TICK_PACKET_REFRESHES_PER_SECOND)
        self.last_call_real_time = datetime.now()  # When we last called the Agent
    def get_packet(self):
        now = datetime.now()
        self.rate_limit.acquire(now - self.last_call_real_time)
        self.last_call_real_time = now
        self.pull_data_from_game()
        return self.game_tick_packet
    def pull_data_from_game(self):
        self.game_interface.update_live_data_packet(self.game_tick_packet)
if __name__ == '__main__':
    packet_reader = GameTickReader()
    while True:
        packet = packet_reader.get_packet()
    async def my_background_task():
        await client.wait_until_ready()
        while not client.is_closed:
            prev_bot_num = bot_num
            prev_overtime = overtime
            prev_ended = ended
            prev_total_goals = total_goals

            bot_num = packet.game_cars.num_cars
            elapsed = packet.game_info.seconds_elapsed
            overtime = packet.game_info.is_overtime
            ended = packet.game_info.is_match_ended

            for n in range(bot_num):
                team = packet.game_info.game_cars[n].team
                name = packet.game_info.game_cars[n].name
                goals = packet.game_info.game_cars[n].goals
                own_goals = packet.game_info.game_cars[n].own_goals
                bot_list[n][team][0]=name
                bot_list[n][team][1]=goals
                bot_list[n][team][2]=own_goals

            b_goal=0
            r_goal=0
            for n in range(bot_num):
                if bot_list[n][0]==0:
                    b_goal = b_goal + bot_list[n][0][1]
                    r_goal = r_goal + bot_list[n][0][2]
                else:
                    r_goal = r_goal + bot_list[n][1][1]
                    b_goal = b_goal + bot_list[n][0][2]
            total_goals = r_goal + b_goal

            b_team_str = ''
            r_team_str = ''
            for n in range(bot_num):
                if bot_list[n][0]==0:
                    if b_team_str != '':
                        b_team_str = ' and ' + b_team_str + bot_list[n][0][0]
                    else: b_team_str = bot_list[n][0][0]
                if bot_list[n][0]==1:
                    if r_team_str != '':
                        r_team_str = ' and ' + r_team_str + bot_list[n][1][0]
                    else: r_team_str = bot_list[n][0][0]

            if prev_total_goals != total_goals:
                message = b_team_str + ' ' + b_goal + ' **V** ' + r_goal + ' ' + r_team_str
                await client.send_message(chat, message)

            if ended and not prev_ended:
                message = 'Game ended\n' + b_team_str + ' ' + b_goal + ' **V** ' + r_goal + ' ' + r_team_str
                await client.send_message(chat, message)

            if overtime and not prev_overtime:
                message = 'Overtime\n' + b_team_str + ' ' + b_goal + ' **V** ' + r_goal + ' ' + r_team_str
                await client.send_message(chat, message)

            await asyncio.sleep(1) # task runs every 60 seconds


    #may not work
    @client.event
    async def on_message(message):
        print('message')
        works = True
        if works:
            if message.content.lower().startswith('!score'):
                message = b_team_str + ' ' + b_goal + ' **V** ' + r_goal + ' ' + r_team_str
                await client.send_message(chat, message)

    client.loop.create_task(my_background_task())
    client.run(botToken)
