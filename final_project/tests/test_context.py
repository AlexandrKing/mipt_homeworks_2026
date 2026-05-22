import unittest

from gigavibe.context import messages_tokens, trim_messages
from gigavibe.messages import Message


class ContextTests(unittest.TestCase):
    def test_trim_keeps_system_and_newest_messages(self) -> None:
        messages = [
            Message('system', 'system prompt'),
            Message('user', 'old ' * 200),
            Message('assistant', 'old answer ' * 200),
            Message('user', 'new question'),
        ]

        trimmed = trim_messages(messages, max_tokens=80)

        self.assertEqual(trimmed[0].role, 'system')
        self.assertEqual(trimmed[-1].content, 'new question')
        self.assertLessEqual(messages_tokens(trimmed), 90)

    def test_rejects_non_positive_budget(self) -> None:
        with self.assertRaises(ValueError):
            trim_messages([], max_tokens=0)


if __name__ == '__main__':
    unittest.main()
