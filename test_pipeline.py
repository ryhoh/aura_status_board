import unittest

from pipeline import Function, FunctionNotFoundError, FunctionParamUnmatchError, Message, Pipeline, PlainText


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

    def test_parse_function_report(self):
        self.assertEqual(
            Pipeline.parse('#report(GPU480)'),
            Message([
                Function(name='report', messages=[
                    Message([
                        PlainText(name='GPU480')
                    ])
                ])
            ])
        )

    def test_parse_function_multi_params(self):
        self.assertEqual(
            Pipeline.parse('#plus(1, 2)'),
            Message([
                Function(name='plus', messages=[
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
                Function(name='alives', messages=[
                    Message([])
                ]),
                PlainText(name=' / '),
                Function(name='devices', messages=[
                    Message([])
                ])
            ])
        )

    def test_parse_deep(self):
        """
        Note: This testcase only succeeds within 24 hours from initialization of DB.
        (Because of 'alives' function)

        """
        self.assertEqual(
            Pipeline.parse('Alive Device Ratio: #divide(#alives(), #devices())'),
            Message([
                PlainText(name='Alive Device Ratio: '),
                Function(name='divide', messages=[
                    Message([
                        Function(name='alives', messages=[
                            Message([])
                        ]),
                    ]),
                    Message([
                        Function(name='devices', messages=[
                            Message([])
                        ]),
                    ]),
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

    def test_str_function_report(self):
        self.assertEqual(
            str(
                Message([
                    Function(name='report', messages=[
                        Message([
                            PlainText(name='GPU480')
                        ])
                    ])
                ])
            ),
            'GPU Information Here.'
        )

    def test_str_function_multi_params(self):
        self.assertEqual(
            str(
                Message([
                    Function(name='plus', messages=[
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
        (Because of 'alives' function)

        """
        self.assertEqual(
            str(
                Message([
                    PlainText(name='Alive Device: '),
                    Function(name='alives', messages=[
                        Message([])
                    ]),
                    PlainText(name=' / '),
                    Function(name='devices', messages=[
                        Message([])
                    ])
                ])
            ),
            'Alive Device: 3 / 4'
        )

    def test_str_deep(self):
        """
        Note: This testcase only succeeds within 24 hours from initialization of DB.
        (Because of 'alives' function)

        """
        self.assertEqual(
            str(
                Message([
                    PlainText(name='Alive Device Ratio: '),
                    Function(name='divide', messages=[
                        Message([
                            Function(name='alives', messages=[
                                Message([])
                            ]),
                        ]),
                        Message([
                            Function(name='devices', messages=[
                                Message([])
                            ]),
                        ]),
                    ])
                ])
            ),
            'Alive Device Ratio: 0.75'
        )

    def test_invalid_function_error(self):
        self.assertRaises(
            FunctionNotFoundError,
            str,
            Message([
                Function(name='not_exist_function', messages=[
                    Message([])
                ])
            ])
        )

    def test_extra_param_error(self):
        self.assertRaises(
            FunctionParamUnmatchError,
            str,
            Message([
                Function(name='devices', messages=[
                    Message([
                        PlainText(name='extra_word')
                    ])
                ])
            ])
        )

    def test_lack_param_error(self):
        self.assertRaises(
            FunctionParamUnmatchError,
            str,
            Message([
                Function(name='report', messages=[
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

    def test_feed_function_report(self):
        self.assertEqual(
            Pipeline.feed('#report(GPU480)'),
            'GPU Information Here.'
        )

    def test_feed_function_multi_params(self):
        self.assertEqual(
            Pipeline.feed('#plus(1, 2)'),
            '3'
        )

    def test_feed_mix(self):
        """
        Note: This testcase only succeeds within 24 hours from initialization of DB.
        (Because of 'alives' function)

        """
        self.assertEqual(
            Pipeline.feed('Alive Device: #alives() / #devices()'),
            'Alive Device: 3 / 4'
        )

    def test_feed_deep(self):
        """
        Note: This testcase only succeeds within 24 hours from initialization of DB.
        (Because of 'alives' function)

        """
        self.assertEqual(
            Pipeline.feed('Alive Device Ratio: #divide(#alives(), #devices())'),
            'Alive Device Ratio: 0.75'
        )


if __name__ == '__main__':
    unittest.main()
