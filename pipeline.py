from typing import List

from mhpl_functions import available_functions


"""
MHPL (Machine-Hub Pipeline Language) Interpreter

"""
class ParseError(Exception):
    pass


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
    func_map = available_functions
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
        buffer_begin = None
        escaped = False
        idx = 0
        while idx < len(text):
            c = text[idx]
            if c == '\\':
                escaped = not escaped
            elif c == '#' and not escaped:  # Begining of Function
                if buffer_begin is not None:
                    res.append(PlainText(replace_escape(text[buffer_begin: idx])))
                begin_idx = idx
                success = False
                for left_paren_idx, left_c in enumerate(text[idx + 1:], start=idx + 1):
                    if left_c == '(':
                        opened_paren_num = 1
                        for right_paren_idx, right_c in enumerate(text[left_paren_idx + 1:], start=left_paren_idx + 1):
                            if right_c == '(':
                                opened_paren_num += 1
                                continue
                            if right_c == ')':
                                opened_paren_num -= 1
                                if opened_paren_num == 0:
                                    name = replace_escape(text[begin_idx + 1: left_paren_idx])
                                    param = replace_escape(text[left_paren_idx + 1: right_paren_idx])
                                    if ',' in param:
                                        messages = [Pipeline.parse(p) for p in param.replace(' ', '').split(',')]
                                    else:
                                        messages = [Pipeline.parse(param)]
                                    res.append(Function(name=name, messages=messages))
                                    idx = right_paren_idx + 1
                                    success = True
                                    buffer_begin = None
                                    break
                        if success:
                            break
                if success:
                    continue
                raise ParseError('Parse failed with:', text)
            else:
                escaped = False

            if buffer_begin is None:
                buffer_begin = idx
            idx += 1
        
        if buffer_begin is not None:
            res.append(PlainText(replace_escape(text[buffer_begin:])))
        return Message(tokens=res)

    @staticmethod
    def feed(return_message: str):
        return str(Pipeline.parse(return_message))
