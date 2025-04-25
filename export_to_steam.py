import argparse
import datetime
import os
import re
import shutil
from sys import exit

from container_types import ContainerIndex, NotSupportedError

def main():
    print("========== Oblivion Remastered Save File Exporter v1.0.0 based on Starfield Save File Importer v0.0.7 ==========")
    print("WARNING: This tool is experimental. Always manually back up your existing saves!")
    print()
    parser = argparse.ArgumentParser(description="Export save files from Xbox Game Pass to Steam.")
    parser.add_argument(
        "--source",
        default=None,
        help="Source path for Xbox Game Pass save files (default: '%LOCALAPPDATA%\\Packages\\BethesdaSoftworks.ProjectAltar_3275kfvn8vcwc')"
    )
    parser.add_argument(
        "--destination",
        default=None,
        help="Destination path for Steam save files (default: '%UserProfile%\\Documents\\My Games\\Oblivion Remastered\\Saved\\SaveGames')"
    )
    args = parser.parse_args()

    # Prompt for source path if not provided
    if args.source is None:
        default_source = r"%LOCALAPPDATA%\Packages\BethesdaSoftworks.ProjectAltar_3275kfvn8vcwc"
        source_path = input(f"Enter source path or leave blank for default (default: {default_source}): ").strip() or default_source
    else:
        source_path = args.source

    # Prompt for destination path if not provided
    if args.destination is None:
        default_destination = r"%UserProfile%\Documents\My Games\Oblivion Remastered\Saved\SaveGames"
        destination_path = input(f"Enter destination path or leave blank for default (default: {default_destination}): ").strip() or default_destination
    else:
        destination_path = args.destination

    source_path = os.path.expandvars(source_path)
    destination_path = os.path.expandvars(destination_path)

    print(f"Using source path: {source_path}")
    print(f"Using destination path: {destination_path}")

    if not os.path.exists(source_path):
        print("Error: Source path does not exist.")
        os.system("pause")
        exit(2)

    

    wgs_path = os.path.join(source_path, "SystemAppData", "wgs")
    container_regex = re.compile(r"[0-9A-F]{16}_[0-9A-F]{32}$")
    container_path = None
    for d in os.listdir(wgs_path):
        if container_regex.match(d):
            container_path = os.path.join(wgs_path, d)
            break
    if container_path is None:
        print("Error: Could not find the container path. Please try to run the game once to create it.")
        os.system("pause")
        exit(2)
    print(f"Found container path: {container_path}")

    container_index_path = os.path.join(container_path, "containers.index")
    container_index_file = open(container_index_path, "rb")
    try:
        container_index = ContainerIndex.from_stream(container_index_file)
    except NotSupportedError as e:
        print(f"Error: Detected unsupported container format, please report this issue: {e}")
        os.system("pause")
        exit(3)
    container_index_file.close()

    print("Listing save files:")
    print("0. Cancel")
    for i, container in enumerate(container_index.containers):
        modified_time = datetime.datetime.fromtimestamp(container.mtime.to_timestamp()).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i + 1}. {container.container_name} | Modified Time: {modified_time} | Size: {container.size} bytes")
    choice = input("Select a save by entering its number: ")
    if choice == "0":
        print("Operation cancelled.")
        os.system("pause")
        exit(0)
    try:
        choice = int(choice) - 1
        if choice < 0 or choice >= len(container_index.containers):
            raise ValueError
    except ValueError:
        print("Invalid choice. Operation cancelled.")
        os.system("pause")
        exit(1)

    selected_container = container_index.containers[choice]
    container_uuid_path = os.path.join(container_path, selected_container.container_uuid.bytes_le.hex().upper())

    no_extension_file = None
    for file_name in os.listdir(container_uuid_path):
        if '.' not in file_name:
            no_extension_file = file_name
            break

    if no_extension_file is None:
        print(f"Error: No file without an extension found in {container_uuid_path}.")
        os.system("pause")
        exit(4)

    source_file_path = os.path.join(container_uuid_path, no_extension_file)
    export_path = os.path.join(destination_path, f"{selected_container.container_name}.sav")

    os.makedirs(destination_path, exist_ok=True)
    shutil.copyfile(source_file_path, export_path)
    print(f"Exported {selected_container.container_name} to {export_path}.")

if __name__ == '__main__':
    main()