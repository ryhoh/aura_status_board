import unittest

from pipeline import Command, Message, Pipeline, PlainText


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

    # def test_parse_command(self):
    #     self.assertEqual(
    #         Pipeline.parse('#ident(AGP092)'),
    #         Message([
    #             Command(name='ident', message=
    #                 Message([
    #                     PlainText(name='AGP092')
    #                 ])
    #             )
    #         ])
    #     )

    def test_parse_mix(self):
        self.assertEqual(
            Pipeline.parse('Alive Device: #alives() / #devices()'),
            Message([
                PlainText(name='Alive Device: '),
                Command(name='alives', message=
                    Message([])
                ),
                PlainText(name=' / '),
                Command(name='devices', message=
                    Message([])
                )
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

    # def test_str_command(self):
    #     self.assertEqual(
    #         str(
    #             Message([
    #                 Command(name='ident', message=
    #                     Message([
    #                         PlainText(name='AGP092')
    #                     ])
    #                 )
    #             ])
    #         ),
    #         'Loooooooooooooong message!'
    #     )

    def test_str_mix(self):
        """
        Note: This testcase only succeeds within 24 hours from initialization of DB.
        (Because of 'alives' command)

        """
        self.assertEqual(
            str(
                Message([
                    PlainText(name='Alive Device: '),
                    Command(name='alives', message=
                        Message([])
                    ),
                    PlainText(name=' / '),
                    Command(name='devices', message=
                        Message([])
                    )
                ])
            ),
            'Alive Device: 3 / 4'
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

    def test_feed_mix(self):
        self.assertEqual(
            Pipeline.feed('Alive Device: #alives() / #devices()'),
            'Alive Device: 3 / 4'
        )


if __name__ == '__main__':
    unittest.main()
