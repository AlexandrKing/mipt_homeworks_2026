import unittest

from gigavibe.modes import DEFAULT_MODE, MODES, get_mode


class ModesTests(unittest.TestCase):
    def test_default_mode_exists(self) -> None:
        self.assertIn(DEFAULT_MODE, MODES)

    def test_unknown_mode_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            get_mode('unknown')


if __name__ == '__main__':
    unittest.main()
