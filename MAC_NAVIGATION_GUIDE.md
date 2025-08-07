# 🍎 Mac Navigation Guide for BladeFighters

## 📁 Current Location
Your game is located at:
```
/Users/justinearp/Downloads/BladeFighters-cluster-fix-working
```

## 🔧 Mac vs Windows Commands

| Windows | Mac | Description |
|---------|-----|-------------|
| `dir` | `ls` | List files and folders |
| `cd folder` | `cd folder` | Change directory |
| `cd ..` | `cd ..` | Go up one folder |
| `cd \` | `cd /` | Go to root |
| `copy file1 file2` | `cp file1 file2` | Copy files |
| `move file1 file2` | `mv file1 file2` | Move/rename files |
| `del file` | `rm file` | Delete file |
| `rmdir folder` | `rmdir folder` | Remove empty folder |
| `mkdir folder` | `mkdir folder` | Create folder |
| `type file` | `cat file` | View file contents |
| `echo text` | `echo text` | Print text |

## 🚀 Running Your Game

### Option 1: Using the Mac script (Recommended)
```bash
./run_mac.sh
```

### Option 2: Direct Python command
```bash
python3 main.py
```

### Option 3: Using the setup script
```bash
./setup_mac.sh
```

## 📂 Important Folders

- `main.py` - The main game file
- `game_client.py` - Core game logic
- `puzzleassets/` - Game images and assets
- `sounds/` - Audio files
- `modules/` - Game modules
- `core/` - Core game systems

## 🛠️ Useful Mac Commands

### Navigate to your game folder:
```bash
cd ~/Downloads/BladeFighters-cluster-fix-working
```

### List files with details:
```bash
ls -la
```

### View a file:
```bash
cat filename.txt
```

### Edit a file (opens in TextEdit):
```bash
open filename.txt
```

### Open current folder in Finder:
```bash
open .
```

### Check Python version:
```bash
python3 --version
```

### Check if pygame is installed:
```bash
python3 -c "import pygame; print('pygame installed')"
```

## 🔍 Finding Your Way Around

### Current directory:
```bash
pwd
```

### Go to Downloads:
```bash
cd ~/Downloads
```

### Go to your game:
```bash
cd ~/Downloads/BladeFighters-cluster-fix-working
```

### Go home:
```bash
cd ~
```

## 📝 Creating Your Own Scripts

Create a new script:
```bash
nano my_script.sh
```

Make it executable:
```bash
chmod +x my_script.sh
```

Run it:
```bash
./my_script.sh
```

## 🎮 Game Development Commands

### Run the game:
```bash
./run_mac.sh
```

### Install dependencies:
```bash
./setup_mac.sh
```

### Test Python:
```bash
python3 -c "print('Python is working!')"
```

### Check pygame:
```bash
python3 -c "import pygame; print(f'pygame {pygame.version.ver}')"
``` 