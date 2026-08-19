import unittest
from unittest.mock import MagicMock
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.executor import Executor


class TestExecutor(unittest.TestCase):
    def test_run_launch_action(self):
        controller = MagicMock()
        executor = Executor(controller)
        actions = [
            {
                "action": "launch",
                "name": "browser",
                "type": "window",
                "command": "brave-browser",
                "workspace": 1,
            }
        ]

        executor.run(actions)

        controller.launch.assert_called_once_with("brave-browser", workspace=1)

    def test_run_move_action(self):
        controller = MagicMock()
        executor = Executor(controller)
        actions = [
            {
                "action": "move",
                "name": "editor",
                "type": "window",
                "address": "0x5649a1b2c3d0",
                "workspace": 2,
            }
        ]

        executor.run(actions)

        controller.move_window.assert_called_once_with("0x5649a1b2c3d0", 2)


if __name__ == "__main__":
    unittest.main()
