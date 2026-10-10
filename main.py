"""
Entry point for the Faker CSV Generator desktop application.
"""

import sys
import logging
import wx
from fcv_app import MainFrame

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def main():
    app = wx.App(False)
    frame = MainFrame()
    frame.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    main()