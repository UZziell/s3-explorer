import sys
from presentation.flet_ui import S3FileExplorerApp
from presentation.click_cli import cli
import flet as ft

if __name__ == "__main__":
    if len(sys.argv) > 1:  # If there are arguments, assume CLI mode
        cli()  # Call the CLI entry point from cli.py
    else:
        app = S3FileExplorerApp()
        # ft.app(target=app.main, view=ft.AppView.WEB_BROWSER)
        ft.app(target=app.main)
