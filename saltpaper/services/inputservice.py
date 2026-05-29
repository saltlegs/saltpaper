import sys
from pathlib import Path
from typing import Callable
import pygame
import pygame.locals as pl
import pygame._sdl2.controller as ctrl

from saltpaper.services.event import Event

KEY_VALUE_TO_NAME = {
    value: name
    for name, value in vars(pl).items()
    if name.startswith("K_")
}

BUTTON_VALUE_TO_NAME = {
    value: name
    for name, value in vars(pl).items()
    if name.startswith("CONTROLLER_BUTTON_")
}

MOUSE_VALUE_TO_NAME = {
    1: "MOUSE_LEFT",
    2: "MOUSE_MIDDLE",
    3: "MOUSE_RIGHT",
    4: "MOUSE_SCROLL_UP",
    5: "MOUSE_SCROLL_DOWN"
}

OTHER_EVENTS = {
    0x5000: "MOUSE_MOVE",
}

EVENT_TYPES_LISTENING = {
    pygame.KEYDOWN: "key",
    pygame.KEYUP: "key",
    pygame.CONTROLLERBUTTONDOWN: "button",
    pygame.CONTROLLERBUTTONUP: "button",
    pygame.MOUSEBUTTONDOWN: "mouse",
    pygame.MOUSEBUTTONUP: "mouse",
}

if __name__ == "__main__":
    with open("validevents.txt", "w") as f:
        f.write("=== KEY EVENTS ===\n")
        for item in KEY_VALUE_TO_NAME.values():
            f.write(f"{item}\n")
        f.write("=== BUTTON EVENTS ===\n")
        for item in BUTTON_VALUE_TO_NAME.values():
            f.write(f"{item}\n")
        f.write("=== MOUSE EVENTS ===\n")
        for item in MOUSE_VALUE_TO_NAME.values():
            f.write(f"{item}\n")

class InputService():
    def __init__(self):
        self.gamepad = None
        self.input_roster = {}
        self.events = []
        self.mouse_relative_movement = (0, 0)
        try:
            ctrl.init()
        except Exception:
            pass
        for item in KEY_VALUE_TO_NAME.values():
            self.input_roster[item] = 0
        for item in BUTTON_VALUE_TO_NAME.values():
            self.input_roster[item] = 0
        for item in MOUSE_VALUE_TO_NAME.values():
            self.input_roster[item] = 0
        for item in OTHER_EVENTS.values():
            self.input_roster[item] = 0

    @property
    def mouse_pos(self):
        return pygame.mouse.get_pos()


    def register_event(self, event: Event):
        self.events.append(event)

    def check_events(self):
        for trigger, frames in self.input_roster.items():
            if frames == 0:
                continue
            for event in self.events:
                if trigger not in event.triggers:
                    continue
                if event.criteria(frames):
                    event.callback(frames, *event.args)


    def controllercheck(self):
        try:
            count = ctrl.get_count()
        except pygame.error:
            count = 0

        if count > 0 and self.gamepad is None:
            try:
                self.gamepad = ctrl.Controller(0)
            except Exception:
                self.gamepad = None
        elif count == 0:
            self.gamepad = None

    def mouse_move(self):
        self.mouse_relative_movement = pygame.mouse.get_rel()
        if self.mouse_relative_movement == (0,0):
            self.input_roster["MOUSE_MOVE"] = -1
        else:
            self.input_roster["MOUSE_MOVE"] = 1

    def tick(self, events):
        self.controllercheck()
        self.process_events(events)
        self.check_events()
        self.mouse_move()
        for item in self.input_roster:

            if self.input_roster[item] == 0:    # never pressed
                continue
            if self.input_roster[item] > 0:     # positive / pressed
                self.input_roster[item] += 1
            elif self.input_roster[item] < 0:   # negative / unpressed after first press
                self.input_roster[item] -= 1
        
        self.input_roster["MOUSE_SCROLL_UP"] = 0
        self.input_roster["MOUSE_SCROLL_DOWN"] = 0


    def process_events(self, events):
        for event in events:
            event_type = event.type
            if not event_type in EVENT_TYPES_LISTENING.keys():
                continue
            target = EVENT_TYPES_LISTENING[event.type]
            value = event.button if target == "mouse" else getattr(event, target, None)
            if target == "key":
                name = KEY_VALUE_TO_NAME.get(value, "unknown")
            elif target == "button":
                name = BUTTON_VALUE_TO_NAME.get(value, "unknown")
            elif target == "mouse":
                name = MOUSE_VALUE_TO_NAME.get(value, "unknown")
                if value in [4, 5] and event_type == pygame.MOUSEBUTTONUP:
                    continue
            else:
                name = "unknown"
            updown = -1 if event_type in [pygame.KEYUP, pygame.CONTROLLERBUTTONUP, pygame.MOUSEBUTTONUP] else 1
            self.input_roster[name] = updown
        
