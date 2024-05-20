import json

from time import sleep
from random import randint
from sys import stdout


def bycharacter(s, speed=0.03):
    print()
    for char in s:
        stdout.write(char)
        stdout.flush()
        sleep(speed)
    print()


class State:
    _loop = 0

    def __init__(self, state_name, game):
        self.state_name = state_name
        self.variants = []
        self.to_answer = None
        if '|' in state_name:
            self.state_name, self.to_answer = state_name.split('|')

        # if state_name is exit then just exit
        if self.state_name == "exit":
            game.change_state(EndState())

        # Answer
        sleep(0.5)
        with open("states.json", "r", encoding="utf-8") as f:
            states = json.load(f)
        self.answer = states[self.state_name]["answer"]

        if type(self.answer) == list:
            if self.to_answer:
                self.answer = self.answer[int(self.to_answer)]
            else:
                self.answer = self.answer[randint(0, len(self.answer) - 1)]

        bycharacter(self.answer)

        # getting Variants
        i = 0
        for var, link in states[self.state_name].items():
            if var == "answer" or var == "hidden":
                continue
            self.variants.append((i, var, link))
            i += 1

        # if already gone through loop, add hidden variant
        if "hidden" in states[self.state_name]:
            if State.loop() >= 1:
                self.variants.append(
                    (i, list(states[self.state_name]["hidden"].keys())[0], list(states[self.state_name]["hidden"].values())[0]))
        sleep(0.5)

    # loop getter
    @classmethod
    def loop(cls):
        return cls._loop

    # loop setter
    @classmethod
    def set_loop(cls, value):
        cls._loop = value

    def update(self, game):
        # Print variants and listen choice
        listener = KeyListener(*(x[1] for x in self.variants))
        choice = listener.listen_key()
        bycharacter(f"\n> {self.variants[choice][1]}")

        # add loop counter
        if self.variants[choice][2] == "neuv":
            State.set_loop(State.loop() + 1)

        # next state
        game.change_state(State(self.variants[choice][2], game))


# prints all variants and listens for choice
class KeyListener:
    def __init__(self, *args):
        self.variants = list(args)
        self.chosen_option = None

    def on_press(self, key):
        try:
            key_index = int(key.char) - 1
            if key_index < len(self.variants) and self.variants[key_index] is not None:
                self.chosen_option = key_index
                return False
        except (AttributeError, ValueError):
            pass

    def listen_key(self):
        for i in range(1, len(self.variants) + 1):
            print(f"{i} - {self.variants[i - 1]}")

        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

        return self.chosen_option


# state manager
class Game:
    def __init__(self, start_state):
        self.current_state = start_state

    def change_state(self, new_state):

        if hasattr(self.current_state, "exit"):
            self.current_state.exit(self)
        self.current_state = new_state

        if hasattr(self.current_state, "enter"):
            self.current_state.enter(self)

    def update(self):
        while True:
            self.current_state.update(self)


# start
class StartState:
    def __init__(self):
        with open("states.json", "r", encoding="utf-8") as f:
            states = json.load(f)
        self.name = states["intro"]["name"]
        self.author = states["intro"]["author"]
        self.description = states["intro"]["description"]
        self.additional = states["intro"]["additional"]

    def update(self, game):
        print(self.name)
        print(self.description)
        if self.additional:
            print(self.additional)

        print("-================================-")
        bycharacter("Начать игру?", speed=0.05)
        choice = KeyListener("Начать", "Выход", "Авторы").listen_key()
        if choice == 1:
            game.change_state(EndState())
        elif choice == 0:
            game.change_state(State("choose_character", game))
        elif choice == 2:
            bycharacter("Авторы:" + self.author + '\n', speed=0.01)
            game.update()


# end
class EndState:
    def __init__(self):
        print("Выход из игры")

    def update(self, game):
        exit()