import discord

from time import sleep
from random import randint
import json


def create_button(link, val):
    async def button_grey(self, interaction: discord.Interaction):
        await sendmsg(channel, f"> {val}")
        await game.change_state(State(link, game))
        await self.update(game)

    return button_grey


class GameMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Начать", style=discord.ButtonStyle.grey)
    async def grey1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global channel
        channel = interaction.channel
        global game
        game = Game(StartState())

        with open("states.json", "r", encoding="utf-8") as f:
            states = json.load(f)
        name = states["intro"]["name"]
        description = states["intro"]["description"]
        additional = states["intro"]["additional"]

        await sendmsg(channel, name)
        await sendmsg(channel, description)
        if additional:
            await sendmsg(channel, additional)

        await sendmsg(channel, "-================================-")

        await channel.send("Начать игру?", view=StartState())
        # await game.update()

    @discord.ui.button(label="Выйти", style=discord.ButtonStyle.grey)
    async def grey2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.exit(interaction)

    async def exit(self, interaction: discord.Interaction):
        await interaction.channel.send("bye")


class State(discord.ui.View):
    _loop = 0

    def __init__(self, state_name, game):
        super().__init__(timeout=None)
        self.state_name = state_name
        self.to_answer = None
        if '|' in state_name:
            self.state_name, self.to_answer = state_name.split('|')
        self.variants = []

    async def enter(self, game):
        # if state_name is exit then just exit
        if self.state_name == "exit":
            await game.change_state(EndState())

        # Answer
        sleep(0.5)
        with open("states.json", "r", encoding="utf-8") as f:
            states = json.load(f)
        self.answer = states[self.state_name]["answer"]

        if isinstance(self.answer, list):
            if self.to_answer:
                self.answer = self.answer[int(self.to_answer)]
            elif self.state_name == "proverka":
                if State.loop() >= 1:
                    self.answer = self.answer[1]
                else:
                    self.answer = self.answer[0]
            else:
                self.answer = self.answer[randint(0, len(self.answer) - 1)]

        # getting Variants
        i = 0
        for var, link in states[self.state_name].items():
            if var == "answer" or var == "hidden":
                continue
            self.variants.append((i, var, link))
            i += 1

        if self.state_name == "neuv":
            State.set_loop(State.loop() + 1)

        # if already gone through loop, add hidden variant
        print(State.loop())
        if "hidden" in states[self.state_name]:
            if State.loop() >= 1:  # Use the loop getter
                self.variants.append(
                    (i, list(states[self.state_name]["hidden"].keys())[0],
                     list(states[self.state_name]["hidden"].values())[0]))
        sleep(0.5)

        # Print variants and listen choice
        await self.generate_buttons(self.variants)
        await sendmsg(channel, self.answer, view=self)

    @classmethod
    def loop(cls):
        return cls._loop

    @classmethod
    def set_loop(cls, value):
        cls._loop = value

    async def generate_buttons(self, variants):
        for idx, (i, var, link) in enumerate(variants):
            if len(self.children) >= 25:
                break

            button = discord.ui.Button(label=var, style=discord.ButtonStyle.grey)
            button.callback = create_button(link, var).__get__(self)
            self.add_item(button)

    async def update(self, game):
        pass


# state manager
class Game:
    def __init__(self, start_state):
        self.current_state = start_state

    async def change_state(self, new_state):

        if hasattr(self.current_state, "exit"):
            await self.current_state.exit(self)
        self.current_state = new_state

        if hasattr(self.current_state, "enter"):
            await self.current_state.enter(self)

    async def update(self):
        while True:
            await self.current_state.update(self)


# start
class StartState(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Начать", style=discord.ButtonStyle.grey)
    async def grey1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await game.change_state(State("choose_character", game))

    @discord.ui.button(label="Выход", style=discord.ButtonStyle.grey)
    async def grey2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.exit_game(interaction)

    @discord.ui.button(label="Авторы", style=discord.ButtonStyle.grey)
    async def grey3_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open("states.json", "r", encoding="utf-8") as f:
            states = json.load(f)
        author = states["intro"]["author"]
        await sendmsg(channel, "Авторы:" + author + '\n')

    async def exit_game(self, interaction: discord.Interaction):
        await interaction.channel.send("bye")

    async def update(self):
        pass


class EndState:
    def __init__(self):
        print("Выход из игры")

    async def update(self, game):
        pass


async def sendmsg(ctx, text, view=None):
    await ctx.send(content=text, view=view)
