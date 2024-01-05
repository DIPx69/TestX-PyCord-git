import discord
import os
import asyncio
import aiohttp
import aiofiles
import json
import sys
import io
import html
import requests
import autopep8
import random
import time
from datetime import datetime, timedelta
import re
from discord.ext import commands
from keep_alive import keep_alive
token = os.environ['token']
intents = discord.Intents.default()
uptime_start = int(time.time())
intents.message_content = True
activity = discord.Activity(name="Dank Memer's Message", type=discord.ActivityType.watching)
bot = discord.Bot(intents=intents,activity=activity)
token = os.environ['token']
adventure = {}
trivia = {}
work = {}
add_mode = "Off"
async def process_data(data, embed):
    for key, value in data.items():
       if isinstance(value, dict):
         await process_data(value, embed)
       elif isinstance(value, list):
         for item in value:
           if isinstance(item, dict):
             await process_data(item, embed)
           elif isinstance(item, str):
             if len(embed) < 5500:
               embed.add_field(name=key.capitalize(), value=item, inline=False)
             else:
               embed.add_field(name="Limit Crossed",value="Limited",inline=False)
               break
       elif isinstance(value, str):
         if len(embed) < 5500:
           embed.add_field(name=key.capitalize(), value=value, inline=False)
         else:
           embed.add_field(name="Limit Crossed",value="Limited",inline=False)
           break
async def safe_eval(code: str) -> str:
    try:
     compiled_code = compile(code, '<string>', 'eval')
     evaluated_result = eval(compiled_code)
     return str(evaluated_result)
    except Exception as e:
       return str(e)
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user.name}")
# Other Utility Code

async def abbreviate_number(number):
    abbreviations = [
        (1e12, 'T'),
        (1e9, 'B'),
        (1e6, 'M'),
        (1e3, 'K')
    ]
    for factor, suffix in abbreviations:
        if number >= factor:
            abbreviated = number / factor
            return f"{abbreviated:.2f}{suffix}"
    return str(number)


async def fetch_data(session, url):
    async with session.get(url) as response:
        data = await response.json()
        return data


async def numfy(a):
    a = a.replace(" ", '')
    replacements = {'kkk': 'k', 'kk': 'k', 'k': '000', 'mmm': 'm', 'mm': 'm', 'm': '000000',
                    'bbb': 'b', 'bb': 'b', 'b': '000000000', 'ttt': 't', 'tt': 't', 't': '000000000000'}
    a = a.lower()
    for old, new in replacements.items():
        a = a.replace(old, new)
    return a

# Class
class MyView(discord.ui.View):
   @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="😎")
   async def button_callback(self, button, interaction):
       await interaction.response.send_message("You clicked the button!")


# Slash Command
@bot.slash_command(name="api", description="Auto Api Fetch Data")
async def modal_slash(ctx: discord.ApplicationContext):
   modal = MyModal(title="Auto Api Fetch Data")
   await ctx.send_modal(modal)
@bot.slash_command(name="math", description="Do Some Noob Math")
async def math(interaction: discord.Interaction,math: discord.Option(str)):
  if any(operator in math for operator in ["+", "-", "*", "/", "%"]):
   try:
     math_solve = await safe_eval(await numfy(math))
     await interaction.response.send_message(f"{math_solve}")
   except Exception as e:
    embed = discord.Embed(title="Math Tool",color=discord.Color.red())
    embed.add_field(name=f"Error Log", value=e, inline=False) 
    await interaction.response.send_message(embed=embed)
  else:
   await interaction.response.send_message("Invalid Math Equation")
@bot.slash_command(name="trivia_adder", description="Add Trivia Question | Dev Only!")
async def trivia_adder(interaction: discord.Interaction,limit:int):
   global add_mode
   owner_id = 833972562210979891
   user_id = interaction.user.id
   if user_id != owner_id:
     embedx = discord.Embed(title="Only Developer Can Run This Command", color=discord.Color.red())
     await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embedx,ephemeral=True)
     return 0
   if add_mode == "On":
     embedx = discord.Embed(title="Already Running...", color=discord.Color.red())
     await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embedx,ephemeral=True)
     return 0
   else:
     url = "https://opentdb.com/api_token.php?command=request"
     async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
           data = await response.json()
           token = data['token']
     request_url = f"https://opentdb.com/api.php?amount={limit}&type=multiple&token={token}"
     async with aiohttp.ClientSession() as session:
        async with session.get(request_url) as response:
           data = await response.json()
           questions = data['results']
     send_message = await interaction.response.send_message(content="Started")
     message_id = send_message.id
     for question in questions:
       async with aiofiles.open("question.json", 'r') as f:
            all_question = json.loads(await f.read())
       trivia_question = html.unescape(question['question'])
       trivia_answer = html.unescape(question['correct_answer'])
       if trivia_question not in all_question:
           print("Add")
           print(trivia_question)
           print(trivia_answer)
           print()
@bot.slash_command(name="status", description="Status Of Dank Hacker")
async def status(interaction: discord.Interaction):
    color = discord.Color.green()
    uptime_seconds = int(time.time() - uptime_start)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    if days > 0:
        uptime_text = f"{days}d:{hours}h:{minutes}m:{seconds}s"
    else:
        uptime_text = f"{hours}h:{minutes}m:{seconds}s"
    embed = discord.Embed(title="Bot Status", color=color)
    embed.add_field(
        name=f"Uptime", value=f"Status: {uptime_text}", inline=True)
    await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embed,view=RefrshStatus())
@bot.slash_command(name="info", description="Global Bot Info")
async def bot_info(interaction: discord.Interaction):
   embed = discord.Embed(title="Bot Info", color=discord.Color.green())
   embed.add_field(
        name=f"Total Server", value=f"**{len(bot.guilds)}**", inline=True)
   embed.add_field(
        name=f"Total Work Assist", value=f"**{await get_total_assist('work')}**", inline=True)
   embed.add_field(
        name=f"Total Trivia Assist", value=f"**{await get_total_assist('trivia')}**", inline=True)
   embed.add_field(
        name=f"Total Fish Reminder", value=f"**{await get_total_assist('fish')}**", inline=True)
   embed.set_footer(text=f'PROJECT BY PROJECTX69')
   await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embed)
@bot.slash_command(name="settings", description="Global Settings | Dev Only!")
async def settings_server(interaction: discord.Interaction):
   owner_id = 833972562210979891
   user_id = interaction.user.id
   color = discord.Color.green()
   if user_id != owner_id:
     embedx = discord.Embed(title="Only Developer Can Run This Command", color=discord.Color.red())
     await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embedx,ephemeral=True)
   else:
     embed = discord.Embed(title="Global Settings", color=color)
     embed.add_field(
        name=f"Trivia", value=f"Status: **{await get_settings_data('trivia')}**", inline=True)
     embed.set_footer(text=f'PROJECT BY PROJECTX69')
     await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embed,view=settings_change())
# Important Function 
async def add_assist(data_name):
  if data_name == 'trivia':
    file_name = "total_assist_trivia.json"
  elif data_name == 'work':
    file_name = "total_assist_work.json"
  elif data_name == 'fish':
    file_name = "total_assist_fish.json"
  async with aiofiles.open(file_name, 'r') as f:
    json_data = json.loads(await f.read())
  json_data["total"] += 1
  async with aiofiles.open(file_name, 'w') as f:
    await f.write(json.dumps(json_data))
async def get_total_assist(data_name:str):
  if data_name == 'trivia':
    file_name = "total_assist_trivia.json"
  elif data_name == 'work':
    file_name = "total_assist_work.json"
  elif data_name == 'fish':
    file_name = "total_assist_fish.json"
  async with aiofiles.open(file_name, 'r') as f:
    json_data = json.loads(await f.read())
  return int(json_data['total'])
async def change_settings(data_name:str):
   async with aiofiles.open("settings.json", 'r') as f:
    json_data = json.loads(await f.read())
   if data_name == "trivia":
     current_mode = json_data['trivia']
     if current_mode == 1:
       json_data['trivia'] = 0
     else:
       json_data['trivia'] = 1
   elif data_name == "adventure":
     current_mode = json_data['adventure']
     if current_mode == 1:
       json_data['adventure'] = 0
     else:
       json_data['adventure'] = 1
   elif data_name == "work":
     current_mode = json_data['work']
     if current_mode == 1:
       json_data['work'] = 0
     else:
       json_data['work'] = 1
   async with aiofiles.open("settings.json", 'w') as f:
     await f.write(json.dumps(json_data))
async def get_settings_data(data_name:str):
  async with aiofiles.open("settings.json", 'r') as f:
    json_data = json.loads(await f.read())
  if json_data[data_name] == 1:
    settings_mode = "On"
  else:
    settings_mode = "Off"
  return settings_mode
# Class
class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
       super().__init__(*args, **kwargs)
       self.add_item(discord.ui.InputText(label="Api Link"))
    async def callback(self, interaction: discord.Interaction):
       value=self.children[0].value
       try:
        if value.startswith('http'):
         async with aiohttp.ClientSession() as session:
           data = await fetch_data(session, value)
         embed = discord.Embed(
            title="API Auto Fetch", color=discord.Color.green())
         await process_data(data,embed)
        else:
         embed = discord.Embed(
            title="API Auto Fetch", color=discord.Color.green())
         embed.add_field(name=f"Error Log", value="Invalid Link", inline=False)
       except Exception as e:
         embed = discord.Embed(title="Invalid Link",color=discord.Color.red())
         embed.add_field(name=f"Error Log", value=e, inline=False)
         embed.set_footer(text=f'PROJECT BY PROJECTX69')
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.send_message(embeds=[embed])

class RefrshStatus(discord.ui.View):
   @discord.ui.button(label="Refresh", style=discord.ButtonStyle.green,emoji='🔃')
   async def button_callback(self, button, interaction):
       color = discord.Color.green()
       uptime_seconds = int(time.time() - uptime_start)
       days = uptime_seconds // (24 * 3600)
       hours = (uptime_seconds % (24 * 3600)) // 3600
       minutes = (uptime_seconds % 3600) // 60
       seconds = uptime_seconds % 60
       if days > 0:
        uptime_text = f"{days}d:{hours}h:{minutes}m:{seconds}s"
       else:
        uptime_text = f"{hours}h:{minutes}m:{seconds}s"
       embed = discord.Embed(title="Bot Status", color=color)
       embed.add_field(name=f"Uptime", value=f"Status: {uptime_text}", inline=True)
       await interaction.response.edit_message(embed=embed)
class settings_change(discord.ui.View):
   @discord.ui.select(
        placeholder = "Choose a Settings",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label="Trivia",
                emoji="1️⃣",
                description="Trivia Settings!"
            ),
            discord.SelectOption(
                label="Adventure",
                emoji = "2️⃣",
                description="Adventure Assistant Settings!"
            ),
            discord.SelectOption(
                label="Work",
                emoji = "3️⃣",
                description="Work Assistant Settings!"
            )
        ]
    )
   async def select_callback(self, select, interaction):
     selected = select.values[0]
     color = discord.Color.green()
     owner_id = 833972562210979891
     user_id = interaction.user.id
     if user_id != owner_id:
      embedx = discord.Embed(title="Only Developer Can Run This Command", color=discord.Color.red())
      await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embedx,ephemeral=True)
      return 0
     if selected == "Trivia":
       embed = discord.Embed(title="Global Settings", color=color)
       embed.add_field(
        name=f"Trivia", value=f"Status: **{await get_settings_data('trivia')}**", inline=True)
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.edit_message(embed=embed,view=settings_change())
     elif selected == "Adventure":
       embed = discord.Embed(title="Global Settings", color=color)
       embed.add_field(
        name=f"Adventure", value=f"Status: **{await get_settings_data('adventure')}**", inline=True)
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.edit_message(embed=embed,view=adventure_change())
     elif selected == "Work":
       embed = discord.Embed(title="Global Settings", color=color)
       embed.add_field(
        name=f"Work", value=f"Status: **{await get_settings_data('work')}**", inline=True)
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.edit_message(embed=embed,view=work_change()) 
   @discord.ui.button(label=f"Trivia", style=discord.ButtonStyle.green)
   async def button_callback(self, button, interaction):
       owner_id = 833972562210979891
       user_id = interaction.user.id
       color = discord.Color.green()
       embed = discord.Embed(title="Global Settings", color=color)
       settings_v2 = await get_settings_data('trivia')
       if settings_v2 == "On":
        await change_settings("trivia")
        self.children[1].style = discord.ButtonStyle.red
       else:
        await change_settings("trivia")
        self.children[1].style = discord.ButtonStyle.green
       embed.add_field(
        name=f"Trivia", value=f"Status: **{await get_settings_data('trivia')}**", inline=True)
       if user_id != owner_id:
         embedx = discord.Embed(title="Only Developer Can Click This Button", color=discord.Color.red())
         await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embedx,ephemeral=True)
       else:
         embed.set_footer(text=f'PROJECT BY PROJECTX69')
         await interaction.response.edit_message(embed=embed,view=settings_change())
class adventure_change(discord.ui.View):
   @discord.ui.select(
        placeholder = "Choose a Settings",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label="Trivia",
                emoji="1️⃣",
                description="Trivia Settings!"
            ),
            discord.SelectOption(
                label="Adventure",
                emoji = "2️⃣",
                description="Adventure Assistant Settings!"
            ),
            discord.SelectOption(
                label="Work",
                emoji = "3️⃣",
                description="Work Assistant Settings!"
            )
        ]
    )
   async def select_callback(self, select, interaction):
     selected = select.values[0]
     color = discord.Color.green()
     owner_id = 833972562210979891
     user_id = interaction.user.id
     if user_id != owner_id:
      embedx = discord.Embed(title="Only Developer Can Click This Command", color=discord.Color.red())
      await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embedx,ephemeral=True)
      return 0
     if selected == "Trivia":
       embed = discord.Embed(title="Global Settings", color=color)
       embed.add_field(
        name=f"Trivia", value=f"Status: **{await get_settings_data('trivia')}**", inline=True)
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.edit_message(embed=embed,view=settings_change())
     elif selected == "Adventure":
       embed = discord.Embed(title="Global Settings", color=color)
       embed.add_field(
        name=f"Adventure", value=f"Status: **{await get_settings_data('adventure')}**", inline=True)
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.edit_message(embed=embed,view=adventure_change())
     elif selected == "Work":
       embed = discord.Embed(title="Global Settings", color=color)
       embed.add_field(
        name=f"Work", value=f"Status: **{await get_settings_data('work')}**", inline=True)
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.edit_message(embed=embed,view=work_change())
   @discord.ui.button(label=f"Adventure", style=discord.ButtonStyle.green)
   async def button_callback(self, button, interaction):
       owner_id = 833972562210979891
       user_id = interaction.user.id
       color = discord.Color.green()
       embed = discord.Embed(title="Global Settings", color=color)
       settings_v2 = await get_settings_data('adventure')
       if settings_v2 == "On":
        await change_settings("adventure")
        self.children[1].style = discord.ButtonStyle.red
       else:
        await change_settings("adventure")
        self.children[1].style = discord.ButtonStyle.green
       embed.add_field(
        name=f"Adventure", value=f"Status: **{await get_settings_data('adventure')}**", inline=True)
       if user_id != owner_id:
         embedx = discord.Embed(title="Only Developer Can Click This Button", color=discord.Color.red())
         await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embedx,ephemeral=True)
       else:
         embed.set_footer(text=f'PROJECT BY PROJECTX69')
         await interaction.response.edit_message(embed=embed,view=adventure_change())
class work_change(discord.ui.View):
   @discord.ui.select(
        placeholder = "Choose a Settings",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label="Trivia",
                emoji="1️⃣",
                description="Trivia Settings!"
            ),
            discord.SelectOption(
                label="Adventure",
                emoji = "2️⃣",
                description="Adventure Assistant Settings!"
            ),
            discord.SelectOption(
                label="Work",
                emoji = "3️⃣",
                description="Work Assistant Settings!"
            )
        ]
    )
   async def select_callback(self, select, interaction):
     selected = select.values[0]
     color = discord.Color.green()
     owner_id = 833972562210979891
     user_id = interaction.user.id
     if user_id != owner_id:
      embedx = discord.Embed(title="Only Developer Can Click This Command", color=discord.Color.red())
      await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embedx,ephemeral=True)
      return 0
     if selected == "Trivia":
       embed = discord.Embed(title="Global Settings", color=color)
       embed.add_field(
        name=f"Trivia", value=f"Status: **{await get_settings_data('trivia')}**", inline=True)
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.edit_message(embed=embed,view=settings_change())
     elif selected == "Adventure":
       embed = discord.Embed(title="Global Settings", color=color)
       embed.add_field(
        name=f"Adventure", value=f"Status: **{await get_settings_data('adventure')}**", inline=True)
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.edit_message(embed=embed,view=adventure_change())
     elif selected == "Work":
       embed = discord.Embed(title="Global Settings", color=color)
       embed.add_field(
        name=f"Work", value=f"Status: **{await get_settings_data('work')}**", inline=True)
       embed.set_footer(text=f'PROJECT BY PROJECTX69')
       await interaction.response.edit_message(embed=embed,view=work_change())
   @discord.ui.button(label=f"Work", style=discord.ButtonStyle.green)
   async def button_callback(self, button, interaction):
       owner_id = 833972562210979891
       user_id = interaction.user.id
       color = discord.Color.green()
       embed = discord.Embed(title="Global Settings", color=color)
       settings_v2 = await get_settings_data('work')
       if settings_v2 == "On":
        await change_settings("work")
        self.children[1].style = discord.ButtonStyle.red
       else:
        await change_settings("work")
        self.children[1].style = discord.ButtonStyle.green
       embed.add_field(
        name=f"Work", value=f"Status: **{await get_settings_data('work')}**", inline=True)
       if user_id != owner_id:
         embedx = discord.Embed(title="Only Developer Can Click This Button", color=discord.Color.red())
         await interaction.response.send_message(f"{(interaction.user.mention)}", embed=embedx,ephemeral=True)
       else:
         embed.set_footer(text=f'PROJECT BY PROJECTX69')
         await interaction.response.edit_message(embed=embed,view=work_change())
class Delete_Message(discord.ui.View):
   @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
   async def button_callback(self, button, interaction):
       await interaction.message.delete()
@bot.event
async def on_message_delete(message):
   global work
   message_embeds = message.embeds
   for embed in message_embeds:
      message_data = embed.to_dict()
   try:
     message_response = message_data["description"]
   except:
     message_response = "Hu"
   if message_response is None:
     return 0
   if any(phrase in message_response for phrase in ["Click the buttons in correct order!", "What was the emoji?", "What color was next to the word"]):
       message_id_get = str(message.id)
       if message_id_get in work.keys() and message.author.id != bot.user.id:
           message_x = await message.channel.fetch_message(int(work[message_id_get]['work']))
           await message_x.delete()
           del work[str(message_id_get)]
           return 0
@bot.event
async def on_message_edit(before, after):
    work_mode = await get_settings_data("work")
    adventure_mode = await get_settings_data("adventure")
    fish_reminder = "None"
    message_id_get = str(after.id)
    async with aiofiles.open("adventure.json", 'r') as f:
        all_adventure = json.loads(await f.read())
    try:
        after_embeds = after.embeds
        for embed in after_embeds:
           after_data = embed.to_dict()
        after_title = after_data["title"]
        if (after_title == "Action Confirmed" or after_title == "Action Canceled") and after.channel.id == 1085301798597820488:
           await after.delete()
           return 0
    except:
        ...
    try:
     name = "No"
     for field in after_data['fields']:
       if field['name'] == 'Interactions':
         name = "Interactions"
    except Exception as e:
       ...
    try:
       after_embeds = after.embeds
       before_embeds = before.embeds
       for embed in after_embeds:
         after_data = embed.to_dict()
         if "You can fish again" in after_data["description"]:
           fish_reminder = after_data["description"]
       for embed in before_embeds:
         before_data = embed.to_dict()
       after_response = after_data["description"]
       before_response = before_data["description"]
    except Exception as e:
        after_response = "None"
        before_response = "None"
        title = "None"
    if after_response in all_adventure.keys() and adventure_mode == "On":
        if message_id_get in adventure.keys() and after.author.id != bot.user.id:
            message_id_int = adventure[message_id_get]["adventure_id"]
            embed = discord.Embed(
                title=f"Adventure Assistant", color=discord.Color.blue())
            embed.add_field(
                name=f"HINT", value=f'{all_adventure[after_response]["text"]}', inline=True)
            embed.set_footer(text=f'{after_data["footer"]["text"]}')
            try:
             retrieved_message = await after.channel.fetch_message(message_id_int)
             await retrieved_message.edit(embed=embed)
            except:
               ...
        elif message_id_get not in adventure.keys() and after.author.id != bot.user.id:
            embed = discord.Embed(
                title=f"Adventure Assistant", color=discord.Color.blue())
            embed.add_field(
                name=f"HINT", value=f'{all_adventure[after_response]["text"]}', inline=True)
            embed.set_footer(text=f'{after_data["footer"]["text"]}')
            a = await after.channel.send(embed=embed,view=Delete_Message())
            adventure[message_id_get] = {
                "adventure_id": a.id}
    if "> You can fish again" in fish_reminder:
       match = re.search(r'<t:(\d+):R>', fish_reminder)
       if match:
         timestamp = int(match.group(1))
       now_time = int(time.time())
       cooldown = timestamp-now_time
       await asyncio.sleep(cooldown-1)
       embed = discord.Embed(
            title=f"You Can Fish Again",color=discord.Color.green())
       await after.channel.send(embed=embed,delete_after=float(3),reference=after)
       await add_assist("fish")
    if "Look at the emoji" in before_response and work_mode == "On":
        emoji = before_response.split('\n')[1]
        embed = discord.Embed(
            title=f"Work Assistant", color=discord.Color.blue())
        embed.add_field(name=f"Emoji", value=f"{emoji}", inline=True)
        embed.set_footer(text=f"Dank Memer Work Assistant || Total Assist: {await get_total_assist('work')+1}")
        a = await after.channel.send(embed=embed, delete_after=float(24),reference=after)
        message_id_get = str(after.id)
        work[message_id_get] = {'work': a.id}
        await add_assist('work')
    if "Look at each color" in before_response and work_mode == "On":
        pattern = r'What color was next to the word `(.+?)`\?'
        match = re.search(pattern, after_response)
        find_text = match.group(1)
        pattern = r'<:(.*?):(\d+)> `(.+?)`'
        matches = re.findall(pattern, before_response)
        color_data = {word: color for color, _, word in matches}
        embed = discord.Embed(
            title=f"Work Assistant", color=discord.Color.blue())
        embed.add_field(
            name=f"Color", value=f"{color_data[find_text]}", inline=True)
        embed.set_footer(text=f"Dank Memer Work Assistant || Total Assist: {await get_total_assist('work')+1}")
        a = await after.channel.send(embed=embed, delete_after=float(24),reference=after)
        message_id_get = str(after.id)
        work[message_id_get] = {'work': a.id}
        await add_assist('work')
    if "Remember words" in before_response and work_mode == "On":
        words = [word.strip('`') for word in before_data['description'].split(
            '\n') if word.startswith('`')]
        order_text = "\n".join(
            [f"[{index + 1}]  {word}" for index, word in enumerate(words)])
        embed = discord.Embed(
            title=f"Work Assistant", color=discord.Color.blue())
        embed.add_field(name=f"Word Order", value=f"{order_text}", inline=True)
        embed.set_footer(text=f"Dank Memer Work Assistant || Total Assist: {await get_total_assist('work')+1}")
        a = await after.channel.send(embed=embed, delete_after=float(24),reference=after)
        message_id_get = str(after.id)
        work[message_id_get] = {'work': a.id}
        await add_assist('work')
    if "**You were given:**" in after_response or "> You lost the mini-game" in after_response:
        message_id_get = str(after.id)
        if message_id_get in work.keys() and after.author.id != bot.user.id:
            message_x = await after.channel.fetch_message(int(work[message_id_get]['work']))
            await message_x.delete()
            del work[str(message_id_get)]
            return 0
    if name == "Interactions":
       message_id_get = str(after.id)
       if message_id_get in adventure.keys() and after.author.id != bot.user.id:
          try: 
           message_x = await after.channel.fetch_message(int(adventure[message_id_get]["adventure_id"]))
           await message_x.delete()
           del adventure[str(message_id_get)]
          except:
            ...
          return 0
    if "You got that answer correct" in after_response:
        message_id_get = str(after.id)
        if message_id_get in trivia.keys() and after.author.id != bot.user.id:
            message_x = await after.channel.fetch_message(int(trivia[message_id_get]['trivia']))
            await message_x.delete()
            del trivia[str(message_id_get)]
            return 0
    if "the correct answer was" in after_response:
        match = re.search(r'\*\*(.*?)\*\*', after_data['description'])
        extracted_answer = match.group(1)
        embeds = before.embeds
        for embed in embeds:
            data = embed.to_dict()
            question = before_data["description"]
            cleaned_question = re.sub(
                r'\*\*|\*You have \d+ seconds to answer\*', '', question)
            lxd = cleaned_question.strip()
        async with aiofiles.open("question.json", 'r') as f:
            all_question = json.loads(await f.read())
            total_answer = len(all_question.keys())
        if lxd not in all_question:
            embed = discord.Embed(
                title=f"New Answer Has Been Add To Database", color=discord.Color.green())
            embed.add_field(name=f"Question", value=f"{lxd}", inline=True)
            embed.add_field(
                name=f"Answer", value=f"{extracted_answer}", inline=True)
            embed.set_footer(text=f"Total Answer {total_answer+1}")
            await before.channel.send(embed=embed)
            payload = {"answer": extracted_answer}
            all_question[question] = payload
            async with aiofiles.open("question.json", 'w') as f:
                await f.write(json.dumps(all_question))
    if before.content.startswith("eval") and before.author.id == 833972562210979891:
        content = after.content
        main = content.replace("eval", "")
        main_test = autopep8.fix_code(main)
        local_variables = {
            "discord": discord,
            "bot": bot,
            "after": after,
            "channel": after.channel,
            "author": after.message.author,
            "guild": after.guild
        }
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        try:
           error = False
           exec(main_test, local_variables)
        except Exception as e:
           error_text = str(e)
           error = True
        finally:
            sys.stdout = old_stdout
        result = redirected_output.getvalue()
        embed = discord.Embed(title=f"Evaluate Run", color=discord.Color.red())
        embed.add_field(name=f"Code", value=f"{main_test}", inline=True)
        embed.add_field(name=f"Result", value=f"{result}", inline=True)
        await before.channel.send(embed=embed,view=Delete_Message())

@bot.event
async def on_message(message):
    if message.content.startswith("rm"):
      try:
       total_text = int(message.content.split()[1])
      except:
       await message.channel.send(content=f"Invalid Command\nExample: ` rm <int> `",reference=message)
       return 0
      permission = message.author.guild_permissions.manage_messages
      if permission and total_text <= 50:
        total = await message.channel.purge(limit=total_text)
        await message.channel.send(content=f"✅ Deleted {len(total)} Message From {message.channel.mention} By {message.author.mention}")
      elif permission == False:
        await message.channel.send(content=f"You Need ` Manage Message ` Permission",reference=message)
        return 0
      elif total_text > 20:
       await message.channel.send(content=f"You Can't Delete More Than ` 20 ` Message",reference=message)
    embeds = message.embeds
    question = "NOR"
    trivia_mode = await get_settings_data("trivia")
    for embed in embeds:
        try:
            data = embed.to_dict()
            question = data["description"]
            cleaned_question = re.sub(
                r'\*\*|\*You have \d+ seconds to answer\*', '', question)
            match = re.search(r'(\d+)\s+seconds', question)
            if match:
              second = int(match.group(1))
              lxd = cleaned_question.strip()
            else:
             second = 15
             lxd = question
            async with aiofiles.open("question.json", 'r') as f:
              all_question = json.loads(await f.read())
            if lxd in all_question.keys():
               question += "\n seconds to answer"
        except Exception as e:
            question = "None"
    async with aiofiles.open("question.json", 'r') as f:
        all_question = json.loads(await f.read())
        total_answer = len(all_question.keys())
    if "seconds to answer" in question and trivia_mode == "On":
        if lxd in all_question.keys():
            answer = all_question[lxd]["answer"]
            embed = discord.Embed(
                title=f"Trivia Question Tracker", color=discord.Color.green())
            embed.add_field(name=f"Answer", value=f"{answer}", inline=True)
            embed.set_footer(text=f"Total Answer {total_answer} || Total Assist: {await get_total_assist('trivia')+1}")
            a = await message.channel.send(embed=embed, delete_after=float(second),reference=message)
            message_id_get = str(message.id)
            trivia[message_id_get] = {
                'trivia': a.id}
            await add_assist('trivia')
        else:
            embed = discord.Embed(
                title=f"Trivia Question Tracker", color=discord.Color.red())
            embed.add_field(
                name=f"Answer", value=f"Answer Not Found In Database", inline=True)
            embed.set_footer(text=f"Total Answer {total_answer}")
            await message.channel.send(embed=embed)
    if any(operator in message.content for operator in ["+", "-", "*", "/", "%"]) and not message.content.startswith("api"):
        input_string = await numfy(message.content)
        try:
          slove = await safe_eval(input_string)
          embed = discord.Embed(title=f"{slove}", color=discord.Color.blue())
          compact = await abbreviate_number(int(slove))
          embed.add_field(
            name=f"Calculated", value=f"**Raw:** {slove}\n**Compact:** {compact}", inline=False)
          await message.channel.send(embed=embed)
        except Exception as e:
           ...
    if message.content.startswith("api"):
       embed = discord.Embed(title="Requesting API...",
                             color=discord.Color.red())
       x = await message.channel.send(embed=embed)
       try:
        url = message.content.split()[1]
        if url.startswith("http"):
         async with aiohttp.ClientSession() as session:
           data = await fetch_data(session, url)
         embed = discord.Embed(
            title="API Auto Fetch", color=discord.Color.green())
         await process_data(data,embed)
         embed.set_footer(text=f'PROJECT BY PROJECTX69')
         retrieved_message = await message.channel.fetch_message(x.id)
         await retrieved_message.edit(embed=embed)
        else:
         raise ValueError('Invalid Link')
       except Exception as e:
         embed = discord.Embed(title="Invalid Link hi",color=discord.Color.red())
         embed.add_field(name=f"Error Log", value=e, inline=False)
         embed.set_footer(text=f'PROJECT BY PROJECTX69')
         retrieved_message = await message.channel.fetch_message(x.id)
         await retrieved_message.edit(embed=embed)
         return 0
    if message.content.startswith("eval") and message.author.id == 833972562210979891:
        content = message.content
        main = content.replace("eval", "")
        main_test = autopep8.fix_code(main)
        local_variables = {
            "discord": discord,
            "bot": bot,
            "message": message,
            "channel": message.channel,
            "author": message.author,
            "guild": message.guild
        }
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        try:
           error = False
           exec(main_test, local_variables)
        except Exception as e:
           error_text = str(e)
           error = True
        finally:
            sys.stdout = old_stdout
        result = redirected_output.getvalue()
        embed = discord.Embed(title=f"Evaluate Run", color=discord.Color.red())
        embed.add_field(name=f"Code", value=f"{main}", inline=True)
        if error:
            embed.add_field(name=f"Result", value=f"{error_text}", inline=True)
        else:
            embed.add_field(name=f"Result", value=f"{result}", inline=True)
        await message.channel.send(embed=embed,view=Delete_Message())

async def capturex(code):
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    try:
        exec(code)
    finally:
        sys.stdout = old_stdout
    return redirected_output.getvalue()
if __name__ == "__main__":
    keep_alive()
    bot.run(token)
