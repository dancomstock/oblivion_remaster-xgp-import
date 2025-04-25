import os
import re
import shutil
import datetime
from sys import exit

from container_types import ContainerIndex, NotSupportedError

def main():
    print("========== Oblivion Remaster Save File Deleter v1.0.0 based on Starfield Save File Importer v0.0.7 ==========")
    print("WARNING: This tool is experimental. Always manually back up your existing saves!")
    print()

    # Locate the container path
    package_path = os.path.expandvars(r"%LOCALAPPDATA%\Packages\BethesdaSoftworks.ProjectAltar_3275kfvn8vcwc")
    if not os.path.exists(package_path):
        print("Error: Could not find the package path. Make sure you have Xbox Oblivion installed.")
        os.system("pause")
        exit(2)

    wgs_path = os.path.join(package_path, "SystemAppData", "wgs")
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

    # Read the container index file
    container_index_path = os.path.join(container_path, "containers.index")
    container_index_file = open(container_index_path, "rb")
    try:
        container_index = ContainerIndex.from_stream(container_index_file)
    except NotSupportedError as e:
        print(f"Error: Detected unsupported container format, please report this issue: {e}")
        os.system("pause")
        exit(3)
    container_index_file.close()

    # List save files
    print("Listing save files:")
    print("0. Cancel")
    for i, container in enumerate(container_index.containers):
        modified_time = datetime.datetime.fromtimestamp(container.mtime.to_timestamp()).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i + 1}. {container.container_name} | Modified Time: {modified_time} | Size: {container.size} bytes")
    choice = input("Select a save to delete by entering its number: ")
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

    # Cowardly creating a backup of the container
    container_backup_path = os.path.join(container_path, f"{container_path}.backup.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    shutil.copytree(container_path, container_backup_path)
    print(f"Created backup of container: {container_backup_path}")

    # Delete the selected save
    print(f"Deleting save: {selected_container.container_name}")
    # container_index.containers.remove(selected_container)
    if os.path.exists(container_uuid_path):
        shutil.rmtree(container_uuid_path)
        print(f"Deleted save directory: {container_uuid_path}")

    saves_meta_uuid_path = None
    for container in container_index.containers:
        if container.container_name == "saves_meta":
            saves_meta_uuid_path = os.path.join(container_path, container.container_uuid.bytes_le.hex().upper())
            break

    if saves_meta_uuid_path and os.path.exists(saves_meta_uuid_path):
        shutil.rmtree(saves_meta_uuid_path)
        print(f"Deleted 'saves_meta' directory: {saves_meta_uuid_path}")
    else:
        print("'saves_meta' directory not found or already removed.")


    # Remove the 'saves_meta' container if it exists
    container_index.containers = [
        container for container in container_index.containers
        if container.container_name not in ["saves_meta", selected_container.container_name]
    ]
    print("Removed save container and 'saves_meta' container if it existed.")


    # Write the updated container index
    container_index.write_file(container_path)
    print("Updated container index.")

    print("Save deletion complete!")
    os.system("pause")

if __name__ == '__main__':
    main()