from presentation.flet_ui import S3FileExplorerApp
import flet as ft

if __name__ == "__main__":
    app = S3FileExplorerApp()
    # ft.app(target=app.main, view=ft.AppView.WEB_BROWSER)
    ft.app(target=app.main)
