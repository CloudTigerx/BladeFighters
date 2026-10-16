# Build a Windows `.exe`

This project is Python + Pygame. On Windows, the recommended packaging path is **PyInstaller**.

## Prereqs

- Windows 10/11
- Python (this repo already uses `.venv/`)

## One-command build

From the repo root:

```powershell
./tools/build_exe.ps1
```

Outputs:
- `./Blade Fighters.exe` (when `--OneFile` is enabled; default)

## Options

Build as a folder (faster start, easier debugging):

```powershell
./tools/build_exe.ps1 -OneFile:$false
```

Change EXE name:

```powershell
./tools/build_exe.ps1 -Name "Blade Fighters 1.5"
```

Choose where the EXE is written:

```powershell
./tools/build_exe.ps1 -DistPath ".\dist"
```

## Icon / logo

The EXE icon is generated from:
- `assets/menus/title_wordmark.png`

The build script converts it into:
- `build/icon.ico`

## Notes

- Assets are bundled via PyInstaller `--add-data "assets;assets"` and resolved at runtime via `swordfighting_new.util.resources.assets_dir()`.
- Save files default to `./saves/save.json` next to wherever you run the EXE. You can override with `BF_SAVE_DIR`.
