import datetime
import os
import re
import shutil
import sys
import uuid
from sys import exit

import crccheck.crc

from container_types import ContainerIndex, NotSupportedError, ContainerFile, ContainerFileList, FILETIME, Container


def main():
    print("========== Oblivion Remastered Save File Importer v1.0.0 based on Starfield Save File Importer v0.0.7 ==========")
    print("WARNING: This tool is experimental. Always manually back up your existing saves!")
    print()
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <save_file>")
        # print("No save file provided. Please select a source file or directory.")
        default_path = os.path.expandvars(r"%UserProfile%\Documents\My Games\Oblivion Remastered\Saved\SaveGames")
        source_path = input(f"Enter the path to a save file or directory. Leave blank for default (default: {default_path}): ").strip() or default_path

        if not os.path.exists(source_path):
            print("Error: The provided path does not exist.")
            os.system("pause")
            exit(1)

        if os.path.isdir(source_path):
            print("Listing files in the directory:")
            # save_files = [f for f in os.listdir(source_path) if f.endswith(".sav")]
            save_files = os.listdir(source_path)
            if not save_files:
                print("No save files found in the directory.")
                os.system("pause")
                exit(1)

            for i, file_name in enumerate(save_files, start=1):
                file_size = os.path.getsize(os.path.join(source_path, file_name))
                modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(source_path, file_name))).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{i}. {file_name} | Modified Time: {modified_time} | Size: {file_size} bytes")
            try:
                choice = int(input("Select a file by entering its number: ")) - 1
                if choice < 0 or choice >= len(save_files):
                    raise ValueError
            except ValueError:
                print("Invalid choice. Operation cancelled.")
                os.system("pause")
                exit(1)

            source_save_path = os.path.join(source_path, save_files[choice])
        else:
            source_save_path = source_path
    else:
        source_save_path = sys.argv[1]

    if not os.path.exists(source_save_path):
        print(f"Error: Source save file does not exist: {source_save_path}")
        os.system("pause")
        exit(4)

    # 1. find the container
    package_path = os.path.expandvars(r"%LOCALAPPDATA%\Packages\BethesdaSoftworks.ProjectAltar_3275kfvn8vcwc")
    if not os.path.exists(package_path):
        print("Error: Could not find the package path. Make sure you have Xbox Starfield installed.")
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
        # not actually sure when this will not exist though
        print("Error: Could not find the container path. Please try to run the game once to create it.")
        os.system("pause")
        exit(2)
    print(f"Found container path: {container_path}")

    # 2. read the container index file
    container_index_path = os.path.join(container_path, "containers.index")
    container_index_file = open(container_index_path, "rb")
    try:
        container_index = ContainerIndex.from_stream(container_index_file)
    except NotSupportedError as e:
        print(f"Error: Detected unsupported container format, please report this issue: {e}")
        os.system("pause")
        exit(3)
    container_index_file.close()
    # print("Parsed container index:")
    # print(f"  Package name: {container_index.package_name}")
    # print(f"  {len(container_index.containers)} containers:")
    # for container in container_index.containers:
    #     print("Container Details:")
    #     print(f"  Name: {container.container_name}")
    #     # print(f"  Cloud ID: {container.cloud_id}")
    #     # print(f"  Sequence: {container.seq}")
    #     # print(f"  Flag: {container.flag}")
    #     # print(f"  UUID: {container.container_uuid}")
    #     print(f"  Modified Time: {container.mtime.to_timestamp()}")
    #     print(f"  Size: {container.size} bytes")
    #     print(f"  UUID to bytes: {container.container_uuid.bytes_le.hex().upper()}")
    #     print()
    # print()
    

    # 4.6 write container index
    container_index.write_file(container_path)

    # 3. read the source save file
    source_save_file = open(source_save_path, "rb")
    save_file_name = os.path.basename(source_save_path).removesuffix(".sav").replace(" ", "").replace(",","").replace(".","")
    print(f"Cleaned save file name: {save_file_name}")
    save_file_size = os.path.getsize(source_save_path)

    # 3.2 check if the save file already exists
    for container in container_index.containers:
        if container.container_name == f"{save_file_name}":
            print(f"Error: Save file already exists: {container.container_name}")
            os.system("pause")
            exit(5)

    # 4. create a new container
    # 4.1 create container file list
    print("Creating new container")
    toc = "version:1;blobSize:16777216;"
    files = []
    total_blobs = (save_file_size + 0xFFFFFF) // 0x1000000
    for blob_index in range(total_blobs):
        blob_data = source_save_file.read(0x1000000)
        blob_crc = crccheck.crc.Crc32Jamcrc.calc(blob_data, 0)
        files.append(ContainerFile(f"Data", uuid.uuid4(), blob_data))
    #     toc += f"BlobData{blob_index}:{blob_crc};"
    # files.append(ContainerFile("toc", uuid.uuid4(), toc.encode()))
    container_file_list = ContainerFileList(seq=1, files=files)

    # 4.2 create container index entry
    container_name = f"{save_file_name}"
    container_uuid = uuid.uuid4()
    mtime = FILETIME.from_timestamp(os.path.getmtime(source_save_path))
    size = save_file_size + len(toc)
    container = Container(
        container_name=container_name,
        cloud_id="",
        seq=1,
        flag=5,
        container_uuid=container_uuid,
        mtime=mtime,
        size=size,
    )

    # 4.3 add new container to container index
    container_index.containers.append(container)
    container_index.mtime = FILETIME.from_timestamp(datetime.datetime.now().timestamp())

    # 4.4 cowardly creating a backup of the container
    container_backup_path = os.path.join(container_path, f"{container_path}.backup.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    shutil.copytree(container_path, container_backup_path)
    print(f"Created backup of container: {container_backup_path}")

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

    # Remove the 'saves_meta' container if it exists to force it to regenerate
    container_index.containers = [
        container for container in container_index.containers
        if container.container_name != "saves_meta"
    ]
    print("Removed 'saves_meta' container if it existed.")


    # 4.5 write container file list
    container_content_path = os.path.join(container_path, container_uuid.bytes_le.hex().upper())
    os.makedirs(container_content_path, exist_ok=True)
    container_file_list.write_container(container_content_path)
    print(f"Wrote new container to {container_content_path}")

    # 4.6 write container index
    container_index.write_file(container_path)
    print("Updated container index")

    print("Done!")
    os.system("pause")


if __name__ == '__main__':
    main()