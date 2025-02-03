import flet as ft
import os
from application.use_cases.bucket_use_cases import BucketUseCases
from application.use_cases.object_use_cases import ObjectUseCases
from adapters.boto3_s3_repository import Boto3S3Repository


class ITEM(ft.Row):
    def __init__(self, text: str, datetime, on_delete, on_rename, object_bucket=None):
        """
        UI Component for displaying an S3 Bucket or Object.

        :param text: Name of the bucket/object
        :param datetime: Timestamp of creation/modification
        :param on_delete: Callback function for delete action
        :param on_rename: Callback function for rename action
        """
        super().__init__()
        self.text_value = text
        self.object_bucket = object_bucket
        self.text_view = ft.Text(text)
        self.date_view = ft.Text(datetime.strftime("%Y-%m-%d %H:%M:%S"))
        self.text_edit = ft.TextField(value=text, visible=False)

        self.edit_button = ft.IconButton(icon=ft.icons.EDIT, on_click=self.edit)
        self.save_button = ft.IconButton(
            icon=ft.icons.SAVE, on_click=self.save, visible=False
        )
        self.delete_button = ft.IconButton(icon=ft.icons.DELETE, on_click=self.delete)

        self.on_delete = on_delete
        self.on_rename = on_rename

        self.controls = [
            self.text_view,
            self.date_view,
            self.text_edit,
            # self.edit_button,
            # self.save_button,
            self.delete_button,
        ]

    def edit(self, e):
        """Switch to edit mode."""
        self.edit_button.visible = False
        self.save_button.visible = True
        self.text_view.visible = False
        self.text_edit.visible = True
        self.update()

    def save(self, e):
        """Save new name and update view."""
        new_name = self.text_edit.value.strip()
        if new_name and new_name != self.text_value:
            self.on_rename(self.text_value, new_name)  # Call rename handler
            self.text_value = new_name

        self.edit_button.visible = True
        self.save_button.visible = False
        self.text_view.visible = True
        self.text_view.value = self.text_value
        self.text_edit.visible = False
        self.update()

    def delete(self, e):
        """Call delete handler."""
        if self.object_bucket:
            self.on_delete(bucket_name=self.object_bucket, object_key=self.text_value)
        else:
            self.on_delete(bucket_name=self.text_value)


class S3FileExplorerApp:
    def __init__(self):
        self.current_bucket = None
        self.page = None
        self.repository = Boto3S3Repository()
        self.bucket_use_cases = BucketUseCases(self.repository)
        self.object_use_cases = ObjectUseCases(self.repository)

    def main(self, page: ft.Page):
        self.page = page
        page.title = "S3 Explorer"
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
                        title=ITEM(
                            text=bucket.name,
                            datetime=bucket.creation_date,
                            on_delete=delete_bucket,
                            on_rename=rename_bucket,
                        ),
                        on_click=lambda e, b=bucket.name: self.open_objects_view(b),
                    )
                    bucket_list_view.controls.append(bucket_control)
                bucket_list_view.update()
            except Exception as e:
                print(f"Error loading buckets: {e}")

        def delete_bucket(bucket_name):
            """Delete bucket from use case and refresh list."""
            self.bucket_use_cases.delete_bucket(bucket_name)
            load_buckets()

        def rename_bucket(old_name, new_name):
            """Rename bucket using use case."""
            self.bucket_use_case.rename_bucket(old_name, new_name)
            load_buckets()

        def add_bucket_dialog(e):
            def handle_add(e):
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
                    ft.TextButton("Cancel", on_click=lambda _: self.page.close(dialog)),
                    ft.TextButton("Add", on_click=handle_add),
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
                        title=ITEM(
                            text=obj.key,
                            datetime=obj.last_modified,
                            on_delete=delete_object,
                            on_rename=rename_object,
                            object_bucket=self.current_bucket,
                        ),
                        on_click=lambda e, o=obj.key: self.on_object_click(o),
                    )

                    object_list_view.controls.append(object_control)
                object_list_view.update()
            except Exception as e:
                print(f"Error loading objects: {e}")

        def delete_object(bucket_name, object_key):
            """Delete object from use case and refresh list."""
            self.object_use_cases.delete_object(bucket_name, object_key)
            load_objects()

        def rename_object(old_name, new_name):
            """Rename object using use case."""
            self.object_use_cases.rename_object(old_name, new_name)
            load_objects()

        def add_object_dialog(e):
            file_picker = ""

            def file_picker_result(e):
                if self.page.web:
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
                else:
                    if file_picker.result != None and file_picker.result.files != None:
                        for f in file_picker.result.files:
                            try:
                                self.object_use_cases.upload_object(
                                    bucket_name=self.current_bucket, file_path=f.path
                                )
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
                    f"Current Bucket: '{self.current_bucket}'", size=24, weight="bold"
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
