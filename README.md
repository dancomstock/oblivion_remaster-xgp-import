# Oblivion Remastered Game Pass Save Manager

Forked from [Starfield XGP Save Importer by HarukaMa](https://github.com/HarukaMa/starfield-xgp-import)

An experimental tool to manage .sav savefiles in XGP savefile containers. This tool allows importing, exporting, and deleting save files.

## Usage

### Import Save Files
To import a save file into the XGP savefile container (Game Pass):

```
$ python import_to_game_pass.py <path to .sav file>
```

Or just drop the `.sav` file onto the executable from releases.

A backup of the container will be created before importing.

**NOTE**: The cloud sync feature of the Xbox app might interfere with outside modifications to the savefile container. After shutting down the game, please wait a minute or two before trying to import savefiles to give the Xbox app some time to sync.

### Export Save Files
To export save files from the XGP savefile container to a Steam-compatible format:

For interactive mode:
```
python export_to_steam.py
```

Or:
```
$ python export_to_steam.py [--source <source path>] [--destination <destination path>]
```

- `--source`: Path to the Xbox Game Pass save files (default: `%LOCALAPPDATA%\Packages\BethesdaSoftworks.ProjectAltar_3275kfvn8vcwc`).
- `--destination`: Path to save the exported files (default: `%UserProfile%\Documents\My Games\Oblivion Remastered\Saved\SaveGames`).

### Delete Save Files
To delete save files from the XGP savefile container:

```
$ python delete.py
```

Follow the prompts to select and delete a save file. A backup of the container will be created before deletion.

## Path References

- **Steam version**: `%UserProfile%\Documents\My Games\Oblivion Remastered\Saved\SaveGames`
- **Xbox version**: `%LOCALAPPDATA%\Packages\BethesdaSoftworks.ProjectAltar_3275kfvn8vcwc\SystemAppData\wgs`
```