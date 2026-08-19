import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from skills.hyprland.controller import HyprlandController


class TestHyprlandController(unittest.TestCase):
    @patch("subprocess.run")
    def test_focus_workspace(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok\n")
        controller = HyprlandController()

        controller.focus_workspace(3)

        mock_run.assert_called_once_with(
            ["hyprctl", "dispatch", 'hl.dsp.focus({workspace = "3"})'],
            capture_output=True,
            text=True
        )

    @patch("subprocess.run")
    def test_launch_with_workspace(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok\n")
        controller = HyprlandController()

        controller.launch("kitty", workspace=3)

        mock_run.assert_called_once_with(
            ["hyprctl", "dispatch", 'hl.dsp.exec_cmd("[workspace 3 silent] kitty")'],
            capture_output=True,
            text=True
        )


    @patch("subprocess.run")
    def test_move_window(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok\n")
        controller = HyprlandController()

        controller.move_window("0x5649a1b2c3d0", 2)

        mock_run.assert_called_once_with(
            ["hyprctl", "dispatch", 'hl.dsp.window.move({workspace = "2", window = "address:0x5649a1b2c3d0", follow = false})'],
            capture_output=True,
            text=True
        )


if __name__ == "__main__":
    unittest.main()
