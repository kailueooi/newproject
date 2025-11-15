"""A collection of all commands that Angelic Buster can use to interact with the game."""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up


# List of key mappings
class Key:
    # Movement
    JUMP = 'space'
    FLASH_JUMP = 'space'

    # Buffs
    STAR_GAZER = 't'         # Can be reused every loop
    ROLL_OF_DICE = 'u'       # 180s CD

    # Skills
    CELESTIAL_ROAR = 'x'
    SUPERNOVA = 'pgup'       # 60s CD
    ERDA_FOUNTAIN = '5'      # 60s CD


#########################
#       Commands        #
#########################

def step(direction, target):
    """Performs one movement step in the given DIRECTION towards TARGET."""
    num_presses = 2
    if direction == 'up' or direction == 'down':
        num_presses = 1
    if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
        time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    if abs(d_y) > settings.move_tolerance * 1.5:
        if direction == 'down':
            press(Key.JUMP, 3)
        elif direction == 'up':
            press(Key.JUMP, 1)
    press(Key.FLASH_JUMP, num_presses)


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = settings.adjust_tolerance / math.sqrt(2)
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        FlashJump('up').main()
                    else:
                        key_down('down')
                        time.sleep(0.05)
                        press(Key.JUMP, 3, down_time=0.1)
                        key_up('down')
                        time.sleep(0.05)
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class Buff(Command):
    """Casts Angelic Buster buffs."""

    def __init__(self):
        super().__init__(locals())
        self.cd120_buff_time = 0
        self.cd180_buff_time = 0
        self.cd200_buff_time = 0
        self.cd240_buff_time = 0
        self.cd900_buff_time = 0
        self.decent_buff_time = 0

    def main(self):
        now = time.time()

        # Roll of Dice - 180s CD
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 65:
            press(Key.ROLL_OF_DICE, 2)
            self.cd180_buff_time = now

        # Star Gazer - 200s CD (or no cooldown logic needed, adjust as you like)
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            press(Key.STAR_GAZER, 2)
            self.cd200_buff_time = now


class FlashJump(Command):
    """Performs a flash jump in the given direction."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(0.1)
        press(Key.FLASH_JUMP, 1)
        press(Key.FLASH_JUMP, 1)
        key_up(self.direction)
        time.sleep(0.5)


class CelestialRoar(Command):
    """Spams Celestial Roar on the spot."""

    def __init__(self, attacks=2, repetitions=1):
        super().__init__(locals())
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        time.sleep(0.05)
        for _ in range(self.repetitions):
            press(Key.CELESTIAL_ROAR, self.attacks, up_time=0.05)
        if self.attacks > 2:
            time.sleep(0.3)
        else:
            time.sleep(0.2)


class Supernova(Command):
    """Casts Supernova every 60s in a direction or based on player position."""

    def __init__(self, direction=None):
        super().__init__(locals())
        self.timer = 0
        self.direction = settings.validate_horizontal_arrows(direction) if direction else None

    def main(self):
        now = time.time()
        if self.timer == 0 or now - self.timer > 60:
            if self.direction:
                press(self.direction, 1, down_time=0.1, up_time=0.05)
            else:
                if config.player_pos[0] > 0.5:
                    press('left', 1, down_time=0.1, up_time=0.05)
                else:
                    press('right', 1, down_time=0.1, up_time=0.05)

            press(Key.SUPERNOVA, 3)
            self.timer = now


class ErdaFountain(Command):
    """Casts Erda Fountain every 61s in a direction or based on player position."""

    def __init__(self, direction=None):
        super().__init__(locals())
        self.timer = 0
        self.direction = settings.validate_horizontal_arrows(direction) if direction else None

    def main(self):
        now = time.time()
        if self.timer == 0 or now - self.timer > 61:
            if self.direction:
                press(self.direction, 1, down_time=0.1, up_time=0.05)
            else:
                if config.player_pos[0] > 0.5:
                    press('left', 1, down_time=0.1, up_time=0.05)
                else:
                    press('right', 1, down_time=0.1, up_time=0.05)

            press(Key.ERDA_FOUNTAIN, 3)
            self.timer = now
