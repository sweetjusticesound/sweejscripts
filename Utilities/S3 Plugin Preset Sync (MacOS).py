import os
import boto3
import logging
import pathlib
import threading
import configparser
import tkinter as tk
from datetime import datetime, timezone
from tkinter import messagebox, ttk, simpledialog
from botocore.exceptions import NoCredentialsError, ClientError

logging.basicConfig(level=logging.DEBUG)


class SweejS3Syncer:
    def __init__(self, root):
        self.root = root
        self.loading = False
        self.s3_paths = ["/"]
        self.s3_client = boto3.client("s3")
        self.current_path = pathlib.Path.home()
        self.s3_bucket_name = ""
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.s3_root_folder = ""
        self.local_root_folder = ""

        self.load_credentials_from_config()
        self.setup_ui()
        self.populate_local_tree(self.current_path)
        self.populate_s3_tree()

    def setup_ui(self):
        self.root.title("Sweej S3 Syncer")
        self.center_window(1000, 800, self.root)

        self.pane = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        self.pane.pack(fill=tk.BOTH, expand=True)

        # Local filesystem frame
        self.local_frame = ttk.Frame(self.pane)
        self.pane.add(self.local_frame, weight=1)
        self.tree_local = ttk.Treeview(self.local_frame, selectmode="browse")
        self.scrollbar_local = ttk.Scrollbar(
            self.local_frame, orient=tk.VERTICAL, command=self.tree_local.yview
        )
        self.tree_local.configure(yscrollcommand=self.scrollbar_local.set)
        self.tree_local.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.scrollbar_local.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_local["columns"] = ("Name", "Modified")
        self.tree_local.column("#0", width=0, stretch=tk.NO)
        self.tree_local.column("Name", anchor=tk.W, width=200)
        self.tree_local.column("Modified", anchor=tk.W, width=120)
        self.tree_local.heading("Name", text="Name", anchor=tk.W)
        self.tree_local.heading("Modified", text="Modified", anchor=tk.W)
        self.tree_local.bind("<Double-1>", self.on_local_item_double_click)

        # S3 frame
        self.s3_frame = ttk.Frame(self.pane)
        self.pane.add(self.s3_frame, weight=1)
        self.tree_s3 = ttk.Treeview(self.s3_frame, selectmode="browse")
        self.scrollbar_s3 = ttk.Scrollbar(
            self.s3_frame, orient=tk.VERTICAL, command=self.tree_s3.yview
        )
        self.tree_s3.configure(yscrollcommand=self.scrollbar_s3.set)
        self.tree_s3.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.scrollbar_s3.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_s3["columns"] = ("Name", "Modified")
        self.tree_s3.column("#0", width=0, stretch=tk.NO)
        self.tree_s3.column("Name", anchor=tk.W, width=200)
        self.tree_s3.column("Modified", anchor=tk.W, width=120)
        self.tree_s3.heading("Name", text="Name", anchor=tk.W)
        self.tree_s3.heading("Modified", text="Modified", anchor=tk.W)
        self.tree_s3.bind("<Double-1>", self.on_s3_item_double_click)

        # Sync buttons
        self.sync_frame = ttk.Frame(self.root)
        self.sync_frame.pack(fill=tk.X, padx=5, pady=5)
        # Sync Up
        self.btn_sync_up = ttk.Button(
            self.sync_frame,
            text="Sync Up",
            command=lambda: self.sync_with_loading(self.sync_up),
        )
        self.btn_sync_up.pack(side=tk.LEFT, padx=(0, 5))
        # Sync Down
        self.btn_sync_down = ttk.Button(
            self.sync_frame,
            text="Sync Down",
            command=lambda: self.sync_with_loading(self.sync_down),
        )
        self.btn_sync_down.pack(side=tk.LEFT)
        # Sync Up Local to S3
        self.btn_sync_up_local = ttk.Button(
            self.sync_frame,
            text=f"Sync Up {self.local_root_folder}(Local) to {self.s3_root_folder}(S3)",
            command=lambda: self.sync_with_loading(self.sync_up_local),
        )
        self.btn_sync_up_local.pack(side=tk.LEFT, padx=(0, 5))
        # Sync Up S3 to Local
        self.btn_sync_down_local = ttk.Button(
            self.sync_frame,
            text=f"Sync Down {self.s3_root_folder}(S3) to {self.local_root_folder}(Local)",
            command=lambda: self.sync_with_loading(self.sync_down_local),
        )
        self.btn_sync_down_local.pack(side=tk.LEFT)

    def center_window(self, width, height, root):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        root.geometry(f"{width}x{height}+{x}+{y}")

    def load_credentials_from_config(self):
        config_path = pathlib.Path("aws_config.ini")

        config = configparser.ConfigParser()
        if config_path.exists():
            config.read(config_path)

            # Retrieve AWS credentials and bucket name
            aws_access_key_id = config.get(
                "Credentials", "aws_access_key_id", fallback=None
            )
            aws_secret_access_key = config.get(
                "Credentials", "aws_secret_access_key", fallback=None
            )
            s3_bucket_name = config.get("Bucket", "s3_bucket_name", fallback=None)
            local_root_folder = config.get(
                "Settings", "local_root_folder", fallback=None
            )
            s3_root_folder = config.get("Settings", "s3_root_folder", fallback=None)

            if all(
                [
                    aws_access_key_id,
                    aws_secret_access_key,
                    s3_bucket_name,
                    local_root_folder,
                    s3_root_folder,
                ]
            ):
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                )
                self.s3_bucket_name = s3_bucket_name
                self.local_root_folder = local_root_folder
                self.s3_root_folder = s3_root_folder
            else:
                self.prompt_for_credentials()
                self.load_credentials_from_config()
        else:
            self.prompt_for_credentials()
            self.load_credentials_from_config()

    def prompt_for_credentials(self):
        aws_access_key_id = simpledialog.askstring(
            "AWS Credentials", "+++++++++++++++ Enter AWS Access Key ID +++++++++++++++"
        )
        aws_secret_access_key = simpledialog.askstring(
            "AWS Credentials",
            "+++++++++++++++ Enter AWS Secret Access Key +++++++++++++++",
        )
        s3_bucket_name = simpledialog.askstring(
            "Bucket Name", "+++++++++++++++ Enter S3 Bucket Name +++++++++++++++"
        )
        local_root_folder = simpledialog.askstring(
            "Bucket Name",
            "+++++++++++++++ Enter Local Root Folder Path +++++++++++++++",
        )
        s3_root_folder = simpledialog.askstring(
            "Bucket Name", "+++++++++++++++ Enter S3 Root Folder  Path +++++++++++++++"
        )

        self.save_credentials_to_config(
            aws_access_key_id,
            aws_secret_access_key,
            s3_bucket_name,
            local_root_folder,
            s3_root_folder,
        )

    def save_credentials_to_config(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        s3_bucket_name,
        local_root_folder,
        s3_root_folder,
    ):
        config = configparser.ConfigParser()
        config["Credentials"] = {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
        }
        config["Bucket"] = {"s3_bucket_name": s3_bucket_name}
        config["Settings"] = {
            "local_root_folder": local_root_folder,
            "s3_root_folder": s3_root_folder,
        }

        with open("aws_config.ini", "w") as config_file:
            config.write(config_file)

    def clear_local_tree(self):
        for item in self.tree_local.get_children():
            self.tree_local.delete(item)

    def populate_local_tree(self, path):
        self.clear_local_tree()

        if self.current_path != pathlib.Path.home():
            self.tree_local.insert("", tk.END, text="", values=("..", ""))

        directories = sorted(
            [p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
        files = sorted(
            [p for p in path.iterdir() if p.is_file() and not p.name.startswith(".")],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        for p in directories + files:
            mod_time = datetime.fromtimestamp(p.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.tree_local.insert("", tk.END, text="", values=(p.name, mod_time))

    def on_local_item_double_click(self, event):
        try:
            item = self.tree_local.selection()
            if item:
                item = item[0]
                name = self.tree_local.item(item, "values")[0]
                if name == "..":
                    parent_path = self.current_path.parent
                    self.current_path = parent_path
                    self.populate_local_tree(parent_path)
                else:
                    next_path = self.current_path / name
                    if next_path.is_dir():
                        self.current_path = next_path
                        self.populate_local_tree(next_path)

        except Exception as e:
            print("Error:", e)

    def clear_s3_tree(self):
        for item in self.tree_s3.get_children():
            self.tree_s3.delete(item)

    def populate_s3_tree(self, folder="/"):
        self.clear_s3_tree()
        threading.Thread(target=self.fetch_s3_data_async, args=(folder,)).start()

    def fetch_s3_data_async(self, folder):
        try:
            self.loading = True
            self.root.config(cursor="watch")
            paginator = self.s3_client.get_paginator("list_objects_v2")
            params = {}
            if folder == "/":
                params = {"Bucket": self.s3_bucket_name, "Delimiter": "/"}
                self.s3_paths = ["/"]
            else:
                self.tree_s3.insert(
                    "",
                    tk.END,
                    text="A",
                    values=(f"< {''.join(self.s3_paths)}", f"current folder: {folder}"),
                )

                prefix = "".join(self.s3_paths[1:]) + folder
                params = {
                    "Bucket": self.s3_bucket_name,
                    "Delimiter": "/",
                    "Prefix": prefix,
                }
                self.s3_paths.append(folder)

            result = paginator.paginate(**params)

            for page in result:
                # Add any sub-folders
                for prefix in page.get("CommonPrefixes", []):
                    folder_name = prefix["Prefix"]
                    folder_name = (
                        folder_name.rstrip("/")
                        if folder_name.endswith("/")
                        else folder_name
                    )
                    folder_name = folder_name.split("/")[-1]
                    folder_name = f"folder: {folder_name}"
                    self.tree_s3.insert("", tk.END, text="A", values=(folder_name, ""))

                # Add files
                for obj in page.get("Contents", []):
                    mod_time = obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
                    file_name = obj["Key"].split("/")[-1]
                    if file_name:
                        file_name = f"file: {file_name}"
                        self.tree_s3.insert(
                            "", tk.END, text="A", values=(file_name, mod_time)
                        )
        except Exception as e:
            self.tree_s3.insert(
                "",
                tk.END,
                text="A",
                values=(
                    f"Please provide valid keys/bucket to show data...",
                    "Connection Error",
                ),
            )
            print(f"Unexpected error:", e)
        finally:
            self.root.config(cursor="")

    def on_s3_item_double_click(self, event):
        try:
            item = self.tree_s3.selection()[0]
            name = self.tree_s3.item(item, "values")[0]
            parts = name.split()
            name = " ".join(parts[1:])
            if parts[0] == "folder:":
                self.populate_s3_tree(name + "/")
            elif parts[0] == "<":
                self.s3_paths.pop()
                folder = self.s3_paths.pop()
                self.populate_s3_tree("/" if name == "/" else folder)

        except Exception as e:
            logging.error(e)

    def sync_up(self, progress_var):
        selected_item = self.tree_local.selection()
        if selected_item:
            selected_item = selected_item[0]
            file_name = self.tree_local.item(selected_item, "values")[0]
            local_path = self.current_path / file_name

            if os.path.isfile(local_path):
                print("local_path", local_path)
                self._upload_file(local_path, progress_var)
            elif os.path.isdir(local_path):
                self._sync_directory(local_path, progress_var)

            self.populate_s3_tree()

    def sync_up_local(self, progress_var):
        self._sync_directory(self.local_root_folder, progress_var, True)
        self.populate_s3_tree()

    def _upload_file(self, local_file_path, progress_var, sync_root=False):
        try:
            s3_key = os.path.relpath(local_file_path, self.current_path).replace(
                "\\", "/"
            )
            if sync_root:
                s3_key = f"{self.s3_root_folder}/{s3_key}"
                keys = s3_key.split("/")
                keys.pop(len(self.s3_root_folder.split("/")))
                s3_key = "/".join(keys)

            local_last_modified = datetime.utcfromtimestamp(
                os.path.getmtime(local_file_path)
            ).replace(tzinfo=timezone.utc)

            try:
                s3_object = self.s3_client.head_object(
                    Bucket=self.s3_bucket_name, Key=s3_key
                )
                s3_last_modified = s3_object["LastModified"].replace(
                    tzinfo=timezone.utc
                )
                if s3_last_modified >= local_last_modified:
                    print(f"[{s3_key}] Skipped (already up-to-date).")
                    progress_var.set(100)
                    self.root.update_idletasks()
                    return
            except Exception as e:
                pass

            print(f"[{s3_key}] Uploading...")
            self.s3_client.upload_file(local_file_path, self.s3_bucket_name, s3_key)
            print(f"Uploading complete...")
            progress_var.set(100)
            self.root.update_idletasks()

        except NoCredentialsError:
            print("No AWS credentials found.")
        except ClientError as e:
            print(f"Failed to upload {local_file_path}: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def _sync_directory(self, local_path, progress_var, sync_root=False):
        total_files = sum(len(files) for _, _, files in os.walk(local_path))
        files_processed = 0

        try:
            for root, _, files in os.walk(local_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    self._upload_file(local_file_path, progress_var, sync_root)
                    files_processed += 1
                    progress_var.set(round(files_processed / total_files * 100, 2))
                    self.root.update_idletasks()

        except NoCredentialsError:
            print("No AWS credentials found.")
        except ClientError as e:
            print(f"Failed to upload files: {e}")

    def sync_down_local(self, progress_var):
        self.sync_down_directory("folder: " + self.s3_root_folder, progress_var, True)
        self.populate_local_tree(self.current_path)

    def sync_down(self, progress_var):
        selected_item = self.tree_s3.selection()
        if selected_item:
            selected_item = selected_item[0]
            name = self.tree_s3.item(selected_item, "values")[0]
            self.sync_down_directory(name, progress_var)

    def sync_down_directory(self, name, progress_var, sync_root=False):
        parts = name.split()
        name = " ".join(parts[1:])

        s3_path = f'{"".join(self.s3_paths)}{name}/'[1:]
        local_path = self.local_root_folder if sync_root else self.current_path

        if parts[0] == "file:":
            s3_path = s3_path[:-1]

        prefix = self.s3_root_folder + "/" if sync_root else s3_path
        objects = self.s3_client.list_objects_v2(
            Bucket=self.s3_bucket_name, Prefix=prefix
        )

        if parts[0] == "folder:":
            folder_root = os.path.join(str(local_path), name)
            local_path = folder_root

        files = objects.get("Contents", [])
        total_files = len(list(filter(lambda x: x["Size"] > 0, files)))
        files_processed = 0

        print(files)
        for obj in files:
            if obj["Size"] <= 0:
                continue

            s3_key = obj["Key"]
            local_file_path = os.path.join(
                local_path,
                s3_path if s3_path == s3_key else os.path.relpath(s3_key, s3_path),
            )
            if sync_root:
                local_file_path = local_file_path.replace(self.s3_root_folder, "")

            local_directory = os.path.dirname(local_file_path)
            if not os.path.exists(local_directory):
                os.makedirs(local_directory, exist_ok=True)

            if os.path.exists(local_file_path):
                local_last_modified = datetime.utcfromtimestamp(
                    os.path.getmtime(local_file_path)
                ).replace(tzinfo=timezone.utc)
                s3_last_modified = obj["LastModified"].replace(tzinfo=timezone.utc)

                if s3_last_modified < local_last_modified:
                    print(f"[{s3_key}] Skipped (already up-to-date).")
                    files_processed += 1
                    progress_var.set(files_processed / total_files * 100)
                    self.root.update_idletasks()
                    continue

            print(f"[{s3_key}] Downloading...")
            self.s3_client.download_file(self.s3_bucket_name, s3_key, local_file_path)
            print(f"Downloading complete...")

            files_processed += 1
            progress_var.set(files_processed / total_files * 100)
            self.root.update_idletasks()

        self.populate_local_tree(self.current_path)

    def set_ui_loading(self):
        for widget in self.root.winfo_children():
            widget.state(["disabled"])

        loading_window = tk.Toplevel(self.root)
        loading_window.title("Syncing...")

        progress_label = ttk.Label(loading_window, text="Syncing...")
        progress_label.pack(pady=10)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            loading_window, mode="determinate", length=300, variable=progress_var
        )
        progress_bar.pack(padx=10, pady=10)
        self.center_window(400, 100, loading_window)

        return loading_window, progress_var

    def sync_with_loading(self, handler):
        loading_window, progress_var = self.set_ui_loading()
        self.root.after(100, lambda: handler(progress_var))
        self.root.after(1000, lambda: self.close_loading_screen(loading_window))

    def close_loading_screen(self, loading_window):
        self.root.grab_release()
        messagebox.showinfo("Syncing Complete", "Syncing completed successfully.")
        self.root.update()
        loading_window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SweejS3Syncer(root)
    root.mainloop()
