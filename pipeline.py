import datetime as dt
from typing import List

import db

"""
Functions for Pipeline.

Pipeline:
    A process between devices.
    Pipeline receives payload from device as parameter (which can be empty),
    processes it and return value to device (type).

Pipeline fuction must satisfy below:
    Receive str payload.
    Return one str object exactly.

"""

# def identity(device_name: str) -> str:
#     return db.select_return_message(dev_name=device_name)


def alive_device_n() -> str:
    devices: List[db.Device] = db.select_devices()
    return str(
        sum(
            dt.datetime.now(tz=dt.timezone(offset=dt.timedelta(hours=9)))
            - device.last_heartbeat_timestamp
            < dt.timedelta(hours=24)
            for device in devices
        )
    )

def device_n() -> str:
    return str(len(db.select_devices()))


"""
Pipeline parser and executer

"""

class CommandError(Exception):
    pass


"""
Objects for tokenizing.

BNF below:
    <message> ::= <token>+
    <token> ::= <command> | <plain-text>
    <command> ::= "#" (a-zA-Z0-9)+ "(" <message> ")"
    <plain-text> ::= .*

"""

class Symbol:
    pass

class Message(Symbol):
    def __init__(self, tokens: List["Token"]) -> None:
        self.tokens = tokens

    def __repr__(self) -> str:
        return '%s(tokens=%s)' % (self.__class__.__name__, self.tokens)

    def __eq__(self, o: object) -> bool:
        return self.tokens == o.tokens

    def __str__(self) -> str:
        return ''.join(map(str, self.tokens))


class Token(Symbol):
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return '%s(name="%s")' % (self.__class__.__name__, self.name)

    def __eq__(self, o: object) -> bool:
        return self.name == o.name


class Command(Token):
    func_map = {  # Dict of Avaliable Functions
        'alives': alive_device_n,
        'devices': device_n,
        # 'ident': identity,
    }
    valid_commands = frozenset(func_map.keys())

    def __init__(self, name: str, message: Message) -> None:
        super().__init__(name)
        self.message = message

    def __repr__(self) -> str:
        return '%s(name="%s", message=%s)' % (self.__class__.__name__, self.name, self.message)

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o) and self.message == o.message

    def __str__(self) -> str:
        return self.exec()

    def exec(self):
        if self.name not in self.valid_commands:
            raise CommandError('invalid command: %s' % self.name)
        param = str(self.message)
        if param == '':
            return self.func_map[self.name]()
        return self.func_map[self.name](param)


class PlainText(Token):
    def __str__(self) -> str:
        return self.name


"""
Pileline core object

"""
def replace_escape(text: str) -> str:
    d_bksl_idx = text.find('\\\\')  # means \\
    hash_idx = text.find('\\#')  # means \#

    if -1 < d_bksl_idx < hash_idx:
        return text[: d_bksl_idx] + '\\' + replace_escape(text[d_bksl_idx + 2:])
    if -1 < hash_idx:
        return text[: hash_idx] + '#' + replace_escape(text[hash_idx + 2:])
    return text


class Pipeline:
    @staticmethod
    def parse(text: str) -> Symbol:
        res = []
        begin_idx = 0
        left_parenthesis_idx = None
        is_cmd = False
        escaped = False
        for idx, c in enumerate(text):
            if c == '\\':
                escaped = not escaped
            elif c == '#' and not escaped:  # Begining of Command
                if idx != 0:
                    res.append(PlainText(replace_escape(text[begin_idx: idx])))
                begin_idx = idx
                is_cmd = True
            elif c == '(' and is_cmd:
                left_parenthesis_idx = idx
            elif c == ')' and left_parenthesis_idx is not None:
                res.append(
                    Command(
                        name=replace_escape(text[begin_idx + 1: left_parenthesis_idx]),
                        message=Pipeline.parse(replace_escape(text[left_parenthesis_idx + 1: idx]))
                    )
                )
                begin_idx = idx + 1
                left_parenthesis_idx = None
                is_cmd = False
            else:
                escaped = False
        
        if begin_idx != len(text):
            res.append(PlainText(replace_escape(text[begin_idx:])))

        return Message(tokens=res)

    @staticmethod
    def feed(return_message: str):
        return str(Pipeline.parse(return_message))
