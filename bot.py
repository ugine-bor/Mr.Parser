import os
from time import sleep

import discord
from dotenv import load_dotenv
from discord.ext import commands

from bs4 import BeautifulSoup
import requests

from fake_useragent import UserAgent
import pyttsx3
import asyncio

import speech_recognition as sr
from pydub import AudioSegment

from pypresence import Presence

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=";", intents=intents)

ua = UserAgent()
header = {'User-Agent': str(ua.firefox)}
vc = None

RPC = Presence(os.getenv('ID'))
RPC.connect()
RPC.update(state="Это я", large_image="me", large_text="Кто?",
           buttons=[{"label": "-=-=-=-=-=-=-=-=-", "url": "https://github.com/ugine-bor"}])


class MainMenuView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Habr последняя статья", style=discord.ButtonStyle.blurple)
    async def blue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.article(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="Habr последние статьи", style=discord.ButtonStyle.blurple)
    async def blue2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.articles(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="Последние переводы scp", style=discord.ButtonStyle.grey)
    async def grey_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.scp(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="Слуйчайный scp", style=discord.ButtonStyle.grey)
    async def grey2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rscp(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="Играть", style=discord.ButtonStyle.red)
    async def red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.game(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="test", style=discord.ButtonStyle.green)
    async def green_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.vc(interaction)
        await interaction.response.defer()

    async def article(self, interaction: discord.Interaction):
        response = None
        while response is None:
            try:
                response = requests.get('https://habr.com/ru/all/', verify=False, headers=header, timeout=1)
                break
            except requests.ConnectionError as e:
                await interaction.channel.send(content='Ошибка соединения ' + str(e))
                sleep(1)
                continue
            except requests.Timeout as e:
                await interaction.channel.send(content="Таймаут " + str(e))
                sleep(1)
                continue
            except requests.RequestException as e:
                await interaction.channel.send(content='Неизвестная ошибка ' + str(e))
                sleep(1)
                continue
        soup = BeautifulSoup(response.text, "html.parser")
        temp = soup.find_all("a", {"class": "tm-title__link"}, href=True)[0]
        content = 'https://habr.com' + temp['href'] + '\n'
        try:
            await interaction.channel.send(content=content)
        except Exception as e:
            await interaction.channel.send(content=str(e))

    async def articles(self, interaction: discord.Interaction):
        response = None
        while response is None:
            try:
                response = requests.get('https://habr.com/ru/all/', verify=False, headers=header, timeout=2)
                break
            except requests.ConnectionError as e:
                await interaction.channel.send(content='Ошибка соединения ' + str(e))
                sleep(1)
                continue
            except requests.Timeout as e:
                await interaction.channel.send(content="Таймаут " + str(e))
                sleep(1)
                continue
            except requests.RequestException as e:
                await interaction.channel.send(content='Неизвестная ошибка ' + str(e))
                sleep(1)
                continue
        soup = BeautifulSoup(response.text, "html.parser")
        content, href = "", ""
        for temp in soup.find_all("a", {"class": "tm-title__link"}, href=True):
            href = temp['href']
            if len(content) + len(href) + len(temp.text) + 21 < 2000:
                content += temp.text + '\n' + '<https://habr.com' + href + '>' + '\n\n'
        await interaction.channel.send(content=content)

    async def scp(self, interaction: discord.Interaction):
        response = requests.get('https://scpfoundation.net/')
        soup = BeautifulSoup(response.text, "html.parser")
        content = ""
        for temp in soup.find_all('div', 'fb-new-translation'):
            ch = temp.findChildren()
            content += temp.text + '\n' + '<https://scpfoundation.net' + ch[0].get('href') + '>' + '\n\n'
        await interaction.channel.send(content=content)

    async def rscp(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = requests.get('https://scpfoundation.net/random:random-page')
        data = response.url
        await interaction.channel.send(content=data)

    async def game(self, interaction: discord.Interaction):
        import textgame
        await interaction.channel.send("Доступна {одна} игра", view=textgame.GameMenu())

    async def vc(self, interaction: discord.Interaction):
        await interaction.channel.send("Ждёт", view=musMenu())


class musMenu(discord.ui.View):  # класс описывает набор кнопок
    def __init__(self, *, timeout=200):  # конструктор класса
        super().__init__(timeout=timeout)
        self.red_button.disabled = True
        self.grey_button.disabled = True

    # этому методу будет сопоставлена кнопка. По клику метод будет вызван.
    @discord.ui.button(label="Выйти", style=discord.ButtonStyle.red)
    async def red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.red_button.disabled = True
        self.grey_button.disabled = True
        self.green_button.disabled = False

        self.grey_button.label = "Пауза"
        await resum(interaction)

        voice_clients = discord.utils.get(interaction.client.voice_clients)
        await voice_clients.disconnect(force=True)
        await interaction.response.edit_message(view=self)
        await interaction.response.defer()

    @discord.ui.button(label="Музыка", style=discord.ButtonStyle.green)
    async def green_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            return await interaction.response.send_message("Тебя нет в голосовом чате", ephemeral=True)

        if not discord.utils.get(interaction.client.voice_clients):
            channel = interaction.user.voice.channel
            vc = await channel.connect()
            await interaction.guild.change_voice_state(channel=channel, self_deaf=True)
        else:
            vc = discord.utils.get(interaction.client.voice_clients)

        try:
            vc.play(discord.FFmpegPCMAudio(
                executable=r'C:/Pycharm/Projects/Discord_Ultimate_Bot/ffmpeg/bin/ffmpeg.exe',
                source=r'fffire.mp3'), after=lambda e: print('done', e))
        except Exception as e:
            return await interaction.response.send_message(content="убей меня!!! " + str(e))

        self.green_button.disabled = True
        self.red_button.disabled = False
        self.grey_button.disabled = False
        await interaction.response.edit_message(view=self)
        await interaction.response.defer()

    @discord.ui.button(label="Пауза", style=discord.ButtonStyle.grey)
    async def grey_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.grey_button.label == "Пауза":
            self.grey_button.label = 'Продолжить'
            await paus(interaction)
            await interaction.response.edit_message(content=f"Музыка остановлена", view=self)
        else:
            self.grey_button.label = "Пауза"
            await resum(interaction)
            await interaction.response.edit_message(content=f"Играет музыку", view=self)
        await interaction.response.defer()


@bot.event
async def on_ready():
    print(f'{bot.user.name} Started')


@bot.command()
async def start(ctx):
    view = MainMenuView()
    await ctx.send(view=view)


@bot.command(name="article")
async def article(ctx):
    response = requests.get('https://habr.com/ru/all/')
    soup = BeautifulSoup(response.text, "html.parser")
    temp_element = soup.find('a', 'tm-article-snippet__title-link')
    if temp_element:
        temp = temp_element['href']
        temp_title = temp_element.text
        content = temp_title + '\n' + 'https://habr.com' + temp
        await ctx.send(content=content)
    else:
        await ctx.send("Не удалось найти статью.")


@bot.command(name="articles")
async def articles(ctx):
    response_data = requests.get('https://habr.com/ru/all/')
    soup = BeautifulSoup(response_data.text, "html.parser")
    content = ""
    for temp in soup.find_all('a', 'tm-article-snippet__title-link'):
        if len(content) + len(temp.get('href')) + len(temp.text) + 21 < 2000:
            content += temp.text + '\n' + '<https://habr.com' + temp.get('href') + '>' + '\n\n'
    try:
        await ctx.send(content=content)
    except:
        await ctx.send(content=content)


@bot.command(name="scp")
async def scp(ctx):
    response_data = requests.get('https://scpfoundation.net/')
    soup = BeautifulSoup(response_data.text, "html.parser")
    content = ""
    for temp in soup.find_all('div', 'fb-new-translation'):
        ch = temp.findChildren()
        content += temp.text + '\n' + '<https://scpfoundation.net' + ch[0].get('href') + '>' + '\n\n'
    try:
        await ctx.send(content=content)
    except:
        await ctx.send(content=content)


@bot.command(name="rscp")
async def rscp(ctx):
    response_data = requests.get('https://scpfoundation.net/random:random-page')
    data = response_data.url
    try:
        await ctx.send(content=data)
    except:
        original_message = ctx.message.reference.resolved if ctx.message.reference else ctx.message
        await original_message.edit(content=data)


@bot.command(name="vc")
async def vc(ctx):
    try:
        await ctx.send_message("Ждёт", view=musMenu())
    except:
        await ctx.send("Ждёт", view=musMenu())


@bot.command(name="paus")
async def paus(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.pause()


@bot.command(name="resum")
async def resum(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.resume()


def check(author):
    def inner_check(message):
        return message.author == author

    return inner_check


@bot.command()
async def chngnm(ctx, member: discord.Member, new_name: str):
    if ctx.author.guild_permissions.administrator:  # Проверяем, имеет ли автор команды права администратора
        try:
            await member.edit(nick=new_name)
            await ctx.send(f'Имя пользователя {member.display_name} успешно изменено на {new_name}')
        except discord.Forbidden:
            await ctx.send("У меня нет прав на изменение имени этого участника.")
    else:
        await ctx.send("У вас нет прав на использование этой команды.")


@bot.listen()
async def on_message(msg):
    if not msg.content:
        vcmsg = requests.get(msg.attachments[0].url)

        with open('voice.ogg', 'wb') as f:
            f.write(vcmsg.content)

        # convert mp3 to wav
        sound = AudioSegment.from_ogg(r"voice.ogg")
        sound.export(r"voice.wav", format="wav")

        with sr.AudioFile(r"voice.wav") as source:
            r = sr.Recognizer()
            audio_text = r.record(source)

        await msg.channel.send(r.recognize_google(audio_text, language="ru-RU"))

    if msg.author.mention == os.getenv('HE') and not msg.content.startswith(';') and msg.content.startswith('!'):
        global vc
        try:
            text_to_say = msg.content
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0])
            engine.save_to_file(text_to_say, 'output.mp3')
            engine.runAndWait()

            if not bot.voice_clients:
                channel = msg.author.voice.channel
                vc = await channel.connect()

            vc.play(discord.FFmpegPCMAudio(
                executable=r'ffmpeg.exe',
                source=r'output.mp3'))

            while vc.is_playing():
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Ошибка чтения чата: {e}")


bot.run(TOKEN)
