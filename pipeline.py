from typing import List

import mhpl_functions as f


"""
MHPL (Machine-Hub Pipeline Language) Interpreter

"""
class FunctionNotFoundError(Exception):
    pass


class FunctionParamUnmatchError(Exception):
    pass


"""
BNF for MHPL:
    <message> ::= <token>+
    <token> ::= <function> | <plain-text>
    <function> ::= "#" (a-zA-Z0-9)+ "(" (<message>? | <message> (" "* "," " "* <message>)+) ")"
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

    def __iter__(self):
        return iter(self.tokens)


class Token(Symbol):
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return '%s(name="%s")' % (self.__class__.__name__, self.name)

    def __eq__(self, o: object) -> bool:
        return self.name == o.name


class Function(Token):
    func_map = {  # Dict of Avaliable Functions
        'alives': f.get_alive_device_n,
        'devices': f.get_device_n,
        'deads': f.get_dead_device_n,
        'report': f.get_report,
        'plus': f.culc_plus,
        'minus': f.culc_minus,
        'times': f.culc_times,
        'divide': f.culc_divide,
    }
    valid_functions = frozenset(func_map.keys())

    def __init__(self, name: str, messages: List[Message]) -> None:
        super().__init__(name)
        self.messages = messages

    def __repr__(self) -> str:
        return '%s(name="%s", messages=%s)' % (self.__class__.__name__, self.name, self.messages)

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o) and self.messages == o.messages

    def __str__(self) -> str:
        return self.exec()

    def exec(self):
        if self.name not in self.valid_functions:
            raise FunctionNotFoundError('invalid function: %s' % self.name)
        func = self.func_map[self.name]
        params = list(map(str, self.messages))
        if params == ['']:  # with no params
            try:
                return func()
            except TypeError:
                raise FunctionParamUnmatchError('function %s got extra param %s' % (self.name, params))
        try:
            return func(*params)
        except TypeError:
            raise FunctionParamUnmatchError(
                'function %s called with params %s (it\'s too many or too few).'
                % (self.name, params)
            )


class PlainText(Token):
    def __str__(self) -> str:
        return self.name


"""
Pileline Parser

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
    def parse(text: str) -> Message:
        res = []
        begin_idx = 0
        left_parenthesis_idx = None
        is_cmd = False
        escaped = False
        for idx, c in enumerate(text):
            if c == '\\':
                escaped = not escaped
            elif c == '#' and not escaped:  # Begining of Function
                if idx != 0:
                    res.append(PlainText(replace_escape(text[begin_idx: idx])))
                begin_idx = idx
                is_cmd = True
            elif c == '(' and is_cmd:
                left_parenthesis_idx = idx
            elif c == ')' and left_parenthesis_idx is not None:
                param = replace_escape(text[left_parenthesis_idx + 1: idx])
                if ',' in param:
                    messages = [Pipeline.parse(p) for p in param.replace(' ', '').split(',')]
                else:
                    messages = [Pipeline.parse(param)]
                res.append(
                    Function(
                        name=replace_escape(text[begin_idx + 1: left_parenthesis_idx]),
                        messages=messages
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
