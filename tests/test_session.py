import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from core.router import save_project_session, stop_project


class TestSessionManagement(unittest.TestCase):
    @patch("core.router._read_normal_clients")
    @patch("core.router.save_project_file")
    def test_save_project_session(self, mock_save_file, mock_read_clients):
        mock_read_clients.return_value = [
            {
                "class": "brave-browser",
                "title": "Google",
                "workspace": {"id": 1},
                "cwd": "/home/user"
            },
            {
                "class": "code",
                "title": "sellora",
                "workspace": {"id": 2},
                "cwd": "/home/user/Documents/neer/sellora"
            },
            {
                "class": "kitty",
                "title": "doom:demo:root",
                "workspace": {"id": 3},
                "cwd": "/home/user/Documents/neer/sellora"
            }
        ]
        mock_save_file.return_value = Path("/tmp/demo.yaml")

        result = save_project_session("demo")

        self.assertEqual(result, 0)
        mock_save_file.assert_called_once()
        saved_data = mock_save_file.call_args[0][1]
        self.assertEqual(saved_data["name"], "demo")
        self.assertIn("brave-browser", saved_data["windows"])
        self.assertIn("terminals", saved_data)

    @patch("core.router._read_normal_clients")
    def test_save_project_with_path_cwd(self, mock_read_clients):
        from core.project import save_project as save_project_real
        import tempfile

        mock_read_clients.return_value = [
            {
                "class": "code",
                "title": "demo",
                "workspace": {"id": 2},
                "cwd": Path("/home/llyod")  # PosixPath object
            }
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("core.project.PROJECT_DIR", Path(tmp_dir)):
                with patch("core.router.save_project_file", side_effect=lambda name, data: save_project_real(name, data)):
                    result = save_project_session("path_test")
                    self.assertEqual(result, 0)
                    saved_file = Path(tmp_dir) / "path_test.yaml"
                    self.assertTrue(saved_file.exists())



    @patch("core.router._load_project_or_error")
    @patch("core.router._read_normal_clients")
    @patch("core.router._read_scratchpad_clients")
    @patch("core.router.HyprlandController")
    def test_stop_project(self, mock_controller_cls, mock_scratchpad, mock_normal, mock_load_project):
        mock_load_project.return_value = {
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
        mock_normal.return_value = [
            {
                "address": "0x12345",
                "class": "code",
                "workspace": {"id": 2},
                "cwd": str(Path("~/Documents/neer/sellora").expanduser())
            }
        ]
        mock_scratchpad.return_value = []

        mock_controller_instance = MagicMock()
        mock_controller_cls.return_value = mock_controller_instance

        result = stop_project("sellora")

        self.assertEqual(result, 0)
        mock_controller_instance.close_window.assert_called_once_with("0x12345")


if __name__ == "__main__":
    unittest.main()
