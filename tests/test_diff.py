import unittest
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.stats.diff import StateDiff
from core.stats.project_state import ProjectState


class TestStateDiff(unittest.TestCase):
    def test_window_matching_by_class_and_directory(self):
        project = {
            "name": "sellora",
            "windows": {
                "editor": {
                    "command": "code ~/Documents/neer/sellora",
                    "class": "code",
                    "workspace": 2,
                    "directory": str(Path("~/Documents/neer/sellora").expanduser())
                }
            }
        }
        desired = ProjectState(project)

        # Current clients: one code instance in sellora (on workspace 4), one in doom (workspace 1)
        current = {
            "clients": [
                {
                    "address": "0x111",
                    "class": "code",
                    "workspace": {"id": 1},
                    "cwd": str(Path("~/Documents/neer/doom").expanduser())
                },
                {
                    "address": "0x222",
                    "class": "code",
                    "workspace": {"id": 4},
                    "cwd": str(Path("~/Documents/neer/sellora").expanduser())
                }
            ]
        }

        diff = StateDiff(current, desired)
        actions = diff.calculate()

        # Should produce a move action for 0x222 to workspace 2 (not a launch action)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["action"], "move")
        self.assertEqual(actions[0]["address"], "0x222")
        self.assertEqual(actions[0]["workspace"], 2)

    def test_window_launch_when_directory_differs(self):
        project = {
            "name": "sellora",
            "windows": {
                "editor": {
                    "command": "code ~/Documents/neer/sellora",
                    "class": "code",
                    "workspace": 2,
                    "directory": str(Path("~/Documents/neer/sellora").expanduser())
                }
            }
        }
        desired = ProjectState(project)

        # Current clients: code instance in another directory
        current = {
            "clients": [
                {
                    "address": "0x111",
                    "class": "code",
                    "workspace": {"id": 2},
                    "cwd": str(Path("~/Documents/neer/other").expanduser())
                }
            ]
        }

        diff = StateDiff(current, desired)
        actions = diff.calculate()

        # Should produce a launch action because directory doesn't match
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["action"], "launch")
        self.assertEqual(actions[0]["command"], "code ~/Documents/neer/sellora")


if __name__ == "__main__":
    unittest.main()
