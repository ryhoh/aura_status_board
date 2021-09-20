import unittest

from pipeline import Command, CommandNotFoundError, CommandParamUnmatchError, Message, Pipeline, PlainText


class TestPipeline(unittest.TestCase):
    """
    Tests for parsing to AST

    """
    def test_parse_normal(self):
        self.assertEqual(
            Pipeline.parse('Hello!'),
            Message(tokens=[
                PlainText(name='Hello!')
            ])
        )

    def test_parse_escaped(self):
        self.assertEqual(
            Pipeline.parse('\\\\\\#\\#Hello\\\\world!\\#\\#'),  # means '\\\#\#Hello\\world!\#\#'
            Message(tokens=[
                PlainText(name='\\##Hello\\world!##')  # means '\##Hello\world!##'
            ])
        )

    def test_parse_command_report(self):
        self.assertEqual(
            Pipeline.parse('#report(GPU480)'),
            Message([
                Command(name='report', messages=[
                    Message([
                        PlainText(name='GPU480')
                    ])
                ])
            ])
        )

    def test_parse_command_multi_params(self):
        self.assertEqual(
            Pipeline.parse('#plus(1, 2)'),
            Message([
                Command(name='plus', messages=[
                    Message([PlainText(name='1')]),
                    Message([PlainText(name='2')])
                ])
            ])
        )

    def test_parse_mix(self):
        self.assertEqual(
            Pipeline.parse('Alive Device: #alives() / #devices()'),
            Message([
                PlainText(name='Alive Device: '),
                Command(name='alives', messages=[
                    Message([])
                ]),
                PlainText(name=' / '),
                Command(name='devices', messages=[
                    Message([])
                ])
            ])
        )

    """
    Tests for transforming into str.
    
    """

    def test_str_normal(self):
        self.assertEqual(
            str(
                Message(tokens=[
                    PlainText(name='Hello!')
                ])
            ),
            'Hello!'
        )

    def test_str_escaped(self):
        self.assertEqual(
            str(
                Message(tokens=[
                    PlainText(name='\\##Hello\\world!##')  # means '\##Hello\world!##'
                ])
            ),
            '\\##Hello\\world!##'  # means '\##Hello\world!##'
        )

    def test_str_command_report(self):
        self.assertEqual(
            str(
                Message([
                    Command(name='report', messages=[
                        Message([
                            PlainText(name='GPU480')
                        ])
                    ])
                ])
            ),
            'GPU Information Here.'
        )

    def test_str_command_multi_params(self):
        self.assertEqual(
            str(
                Message([
                    Command(name='plus', messages=[
                        Message([PlainText(name='1')]),
                        Message([PlainText(name='2')])
                    ])
                ])
            ),
            '3'
        )

    def test_str_mix(self):
        """
        Note: This testcase only succeeds within 24 hours from initialization of DB.
        (Because of 'alives' command)

        """
        self.assertEqual(
            str(
                Message([
                    PlainText(name='Alive Device: '),
                    Command(name='alives', messages=[
                        Message([])
                    ]),
                    PlainText(name=' / '),
                    Command(name='devices', messages=[
                        Message([])
                    ])
                ])
            ),
            'Alive Device: 3 / 4'
        )

    def test_invalid_command_error(self):
        self.assertRaises(
            CommandNotFoundError,
            str,
            Message([
                Command(name='not_exist_command', messages=[
                    Message([])
                ])
            ])
        )

    def test_extra_param_error(self):
        self.assertRaises(
            CommandParamUnmatchError,
            str,
            Message([
                Command(name='devices', messages=[
                    Message([
                        PlainText(name='extra_word')
                    ])
                ])
            ])
        )

    def test_lack_param_error(self):
        self.assertRaises(
            CommandParamUnmatchError,
            str,
            Message([
                Command(name='report', messages=[
                    Message([])  # param needed but it's empty
                ])
            ])
        )


    """
    Feeding tests

    """
    def test_feed_normal(self):
        self.assertEqual(
            Pipeline.feed('Hello!'),
            'Hello!'
        )

    def test_feed_escaped(self):
        self.assertEqual(
            Pipeline.feed('\\\\\\#\\#Hello\\\\world!\\#\\#'),  # means '\\\#\#Hello\\world!\#\#'
            '\\##Hello\\world!##'  # means '\##Hello\world!##'
        )

    def test_feed_command_report(self):
        self.assertEqual(
            Pipeline.feed('#report(GPU480)'),
            'GPU Information Here.'
        )

    def test_feed_command_multi_params(self):
        self.assertEqual(
            Pipeline.feed('#plus(1, 2)'),
            '3'
        )

    def test_feed_mix(self):
        self.assertEqual(
            Pipeline.feed('Alive Device: #alives() / #devices()'),
            'Alive Device: 3 / 4'
        )


if __name__ == '__main__':
    unittest.main()
