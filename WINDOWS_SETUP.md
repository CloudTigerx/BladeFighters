# 🎮 BladeFighters - Windows Setup Guide

## 🚀 **Quick Start (Easiest)**

1. **Double-click** `setup_and_run.bat`
   - This will automatically install Python dependencies and run the game
   - If you don't have Python, it will tell you where to get it

## 🛠️ **Manual Setup**

### **Step 1: Install Python**
- Download Python 3.8+ from [python.org](https://python.org)
- ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

### **Step 2: Install Dependencies**
Open Command Prompt and run:
```bash
pip install -r requirements.txt
```

### **Step 3: Run the Game**
- Double-click `run_bladefighters.bat`, OR
- In Command Prompt: `python main.py`

## 🎯 **Game Controls**

- **Arrow Keys**: Move puzzle pieces
- **Z/X Keys**: Rotate pieces
- **Space**: Drop pieces quickly
- **ESC**: Return to menu

## 🏗️ **Architecture Status**

This version showcases **90% Modular Architecture**:
- ✅ 6 extracted modules (Audio, Menu, Settings, Screen, Story, TestMode)
- ✅ Clean file organization (`contracts/`, `modules/`, `core/`)
- ✅ 45% code reduction (1,815 → 987 lines in main client)
- 🔄 Final 10%: PuzzleEngine & PuzzleRenderer extraction

## 🎊 **Features**

- **Puzzle Fighting**: Tetris-style puzzle combat
- **Beautiful UI**: Particle effects and smooth animations  
- **Audio System**: Music and sound effects
- **Story Mode**: Scrolling story content
- **Test Mode**: AI vs Player battles
- **Settings**: Customizable resolution and UI

## 🆘 **Troubleshooting**

### **"Python not found"**
- Reinstall Python and check "Add to PATH"
- Or download from Microsoft Store

### **"Import Error"**
- Run: `pip install pygame`
- Or use `setup_and_run.bat`

### **Game won't start**
- Check Python version: `python --version` (need 3.8+)
- Try: `python3 main.py` instead

## 🎯 **Coming Soon**

- **.exe distribution** (after 100% modular architecture)
- **Multiplayer support**
- **More game modes**

---

**Enjoy the modular puzzle fighting experience!** 🚀 