# Oblivion Remaster XGP Save Importer

Forked from [Starfield XGP Save Importer by HarukaMa](https://github.com/HarukaMa/starfield-xgp-import)

An experimental tool to import .sav savefiles into XGP savefile container.

## Usage

```
$ python3 main.py <path to .sav file>
```

Or just drop the .sav file onto the executable from releases.

**NOTE**: The cloud sync feature of Xbox app might interfere with outside modifications to the savefile container. After shutting down the game, please wait a minute or two before trying to import savefiles to give Xbox app some time to do the sync. 

## Path references

Steam version: `Documents\My Games\Oblivion Remastered\Saves`

Xbox version: `%LOCALAPPDATA%\Packages\BethesdaSoftworks.ProjectAltar_3275kfvn8vcwc\SystemAppData\wgs`