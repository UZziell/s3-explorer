import flet as ft
import os
from application.use_cases.bucket_use_cases import BucketUseCases
from application.use_cases.object_use_cases import ObjectUseCases
from adapters.boto3_s3_repository import Boto3S3Repository


class S3FileExplorerApp:
    def __init__(self):
        self.current_bucket = None
        self.page = None
        self.repository = Boto3S3Repository()
        self.bucket_use_cases = BucketUseCases(self.repository)
        self.object_use_cases = ObjectUseCases(self.repository)

    def main(self, page: ft.Page):
        self.page = page
        page.title = "S3 File Explorer"
        page.scroll = ft.ScrollMode.AUTO
        page.on_route_change = self.route_change
        page.on_view_pop = self.view_pop
        page.go("/buckets")  # Start with the bucket view

    def route_change(self, route):
        self.page.views.clear()
        if self.page.route == "/buckets":
            self.page.views.append(self.buckets_view())
        elif self.page.route == "/objects":
            self.page.views.append(self.objects_view())
        self.page.update()

    def view_pop(self, view):
        self.page.views.pop()
        self.page.update()

    def buckets_view(self):
        bucket_list_view = ft.ListView(expand=True, spacing=10, padding=10)

        def load_buckets():
            try:
                bucket_list_view.controls.clear()
                buckets = self.bucket_use_cases.get_buckets()
                for bucket in buckets:
                    bucket_control = ft.ListTile(
                        title=ft.Text(bucket.name),
                        on_click=lambda e, b=bucket.name: self.open_objects_view(b),
                    )
                    bucket_list_view.controls.append(bucket_control)
                bucket_list_view.update()
            except Exception as e:
                print(f"Error loading buckets: {e}")

        def add_bucket_dialog(e):
            def submit_dialog(e):
                bucket_name = bucket_input.value.strip()
                if bucket_name:
                    try:
                        self.bucket_use_cases.create_bucket(bucket_name)
                        load_buckets()
                        self.page.close(dialog)
                    except Exception as ex:
                        print(f"Error adding bucket: {ex}")
                else:
                    print("Bucket name cannot be empty.")

            bucket_input = ft.TextField(label="Bucket Name")
            dialog = ft.AlertDialog(
                title=ft.Text("Add Bucket"),
                content=bucket_input,
                actions=[
                    ft.TextButton("Cancel", on_click=lambda _: dialog.close()),
                    ft.TextButton("Add", on_click=submit_dialog),
                ],
            )
            self.page.open(dialog)

        load_buckets()
        return ft.View(
            "/buckets",
            [
                ft.AppBar(title=ft.Text("Buckets"), bgcolor=ft.colors.INDIGO_800),
                ft.Text("S3 Buckets", size=24, weight="bold"),
                bucket_list_view,
                ft.Row(
                    [
                        ft.ElevatedButton("Add Bucket", on_click=add_bucket_dialog),
                    ]
                ),
            ],
        )

    def objects_view(self):
        object_list_view = ft.ListView(expand=True, spacing=10, padding=10)

        def load_objects():
            if not self.current_bucket:
                print("No bucket selected.")
                return
            try:
                object_list_view.controls.clear()
                objects = self.object_use_cases.get_objects(self.current_bucket)
                for obj in objects:
                    object_control = ft.ListTile(
                        title=ft.Text(obj.key),
                        trailing=ft.Text(
                            obj.last_modified.strftime("%Y-%m-%d %H:%M:%S")
                        ),
                        on_click=lambda e, o=obj.key: self.on_object_click(o),
                    )
                    object_list_view.controls.append(object_control)
                object_list_view.update()
            except Exception as e:
                print(f"Error loading objects: {e}")

        def add_object_dialog(e):
            file_picker = ""

            def file_picker_result(e):
                upload_list = []
                if file_picker.result != None and file_picker.result.files != None:
                    for f in file_picker.result.files:
                        url = self.object_use_cases.generate_presigned_url(
                            self.current_bucket, f.name
                        )
                        upload_list.append(
                            ft.FilePickerUploadFile(
                                f.name,
                                upload_url=url,
                            )
                        )
                try:
                    file_picker.upload(upload_list)
                    load_objects()
                except Exception as ex:
                    print(f"Error uploading object: {ex}")

            file_picker = ft.FilePicker(on_result=file_picker_result)

            self.page.overlay.append(file_picker)
            self.page.update()
            file_picker.pick_files(allow_multiple=True)

        load_objects()
        return ft.View(
            "/objects",
            [
                ft.AppBar(title=ft.Text(f"Objects"), bgcolor=ft.colors.INDIGO_800),
                ft.Text(
                    f"Current Bucket: {self.current_bucket}", size=24, weight="bold"
                ),
                object_list_view,
                ft.Row(
                    [
                        ft.ElevatedButton("Add Object", on_click=add_object_dialog),
                        ft.ElevatedButton(
                            "Back to Buckets",
                            on_click=lambda _: self.page.go("/buckets"),
                        ),
                    ]
                ),
            ],
        )

    def open_objects_view(self, bucket_name):
        self.current_bucket = bucket_name
        self.page.go("/objects")

    def on_object_click(self, object_key):
        print(f"Object selected: {object_key}")


if __name__ == "__main__":
    app = S3FileExplorerApp()
    ft.app(target=app.main, view=ft.AppView.WEB_BROWSER)
