# 🎯 Draggable Menu System Guide

## **How to Use:**

### **1. Enable Draggable Mode**
- Press **F2** to toggle draggable mode on/off
- When active, you'll see green outlines around all elements
- Instructions appear on screen

### **2. Drag Elements**
- **Hold E key + Mouse** to drag any element
- Elements turn **yellow** while being dragged
- Elements stay within screen bounds automatically

### **3. Save Your Layout**
- **F3**: Save positions manually
- **F2** (toggle off): Automatically saves when exiting draggable mode
- Positions are saved to `puzzleassets/menus/saved_positions.json`

### **4. Reset if Needed**
- **F4**: Reset all elements to original positions

## **Controls:**
- **F2**: Toggle draggable mode
- **F3**: Save positions
- **F4**: Reset positions
- **E + Mouse**: Drag elements

## **Integration:**

### **Option 1: Replace Existing Menu System**
```python
# In your main game file, replace:
# from modules.menu_module.scaled_menu_system import ScaledMenuSystem
# menu_system = ScaledMenuSystem(screen, font, audio)

# With:
from modules.menu_module.draggable_menu_system import DraggableMenuSystem
menu_system = DraggableMenuSystem(screen, font, audio)
```

### **Option 2: Quick Test**
```python
# Just change the import and class name:
menu_system = DraggableMenuSystem(screen, font, audio)
```

## **Features:**
- ✅ **Zero overhead** when draggable mode is off
- ✅ **Persistent positioning** - saves to JSON file
- ✅ **Visual feedback** - outlines and instructions
- ✅ **Screen bounds** - elements can't be dragged off-screen
- ✅ **Automatic saving** - positions saved when exiting mode

## **Perfect Positioning Workflow:**
1. Start game with draggable system
2. Press **F2** to enable draggable mode
3. Hold **E + Mouse** to drag elements to perfect positions
4. Press **F2** again to save and exit
5. Your layout is now saved and will load automatically!

## **File Structure:**
```
puzzleassets/menus/
├── saved_positions.json  # Your saved layout
├── button_normal.png
├── button_hover.png
└── button_pressed.png
```

## **Performance:**
- **Normal mode**: Zero overhead (same as regular menu)
- **Draggable mode**: Minimal overhead (just outlines and event processing)
- **Saving**: Only happens when you press F2 or exit draggable mode
