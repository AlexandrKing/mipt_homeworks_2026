import tempfile
import unittest
from pathlib import Path

from gigavibe.messages import Message
from gigavibe.storage import load_history, save_history


class StorageTests(unittest.TestCase):
    def test_save_and_load_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'history.json'
            history = [Message('user', 'Привет'), Message('assistant', 'Здравствуйте')]

            save_history(path, 'assistant', history)
            mode_name, loaded = load_history(path)

            self.assertEqual(mode_name, 'assistant')
            self.assertEqual(
                [message.to_dict() for message in loaded],
                [m.to_dict() for m in history],
            )


if __name__ == '__main__':
    unittest.main()
