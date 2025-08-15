# BladeFighters Settings Guide

## ⚙️ **Settings System Overview**

The BladeFighters settings system provides comprehensive customization options for graphics, audio, input, and gameplay. All settings are automatically saved and persist between game sessions.

## 🎮 **Accessing Settings**

### **From Main Menu**
- Navigate to **Settings** option
- Use arrow keys to select
- Press **Enter** to open settings

### **During Gameplay**
- Press **Escape** to pause
- Select **Settings** from pause menu
- Or use the dedicated settings key

### **Settings Interface**
- **Tabbed Interface**: Graphics, Audio, Controls tabs
- **Real-time Preview**: See changes immediately
- **Auto-save**: Settings save automatically
- **Reset Options**: Restore defaults if needed

## 🖥️ **Graphics Settings**

### **Display Options**

#### **Resolution**
- **Automatic Detection**: Game detects optimal resolution for your display
- **Custom Selection**: Choose from available resolutions
- **High-DPI Support**: Native support for Retina and 4K displays
- **Aspect Ratio**: Maintains proper proportions

**Available Resolutions**:
- 1920x1080 (Full HD)
- 2560x1440 (2K)
- 3840x2160 (4K)
- Custom resolutions based on your display

#### **Window Mode**
- **Fullscreen**: Immersive gaming experience
- **Borderless**: Windowed mode without borders
- **Windowed**: Traditional windowed mode
- **Native Fullscreen**: Use native resolution for high-DPI displays

#### **V-Sync**
- **Enabled**: Synchronizes frame rate with monitor refresh rate
- **Disabled**: Unlocked frame rate (may cause screen tearing)
- **Recommendation**: Enable for smooth gameplay

### **Visual Quality**

#### **UI Scale**
- **Range**: 0.8x to 1.5x
- **Default**: 1.0x (100%)
- **Purpose**: Adjust interface size for different displays
- **Accessibility**: Larger UI for better visibility

#### **Brightness**
- **Range**: 0.3 to 1.0
- **Default**: 1.0 (100%)
- **Purpose**: Adjust game brightness
- **Usage**: Compensate for different lighting conditions

#### **Particle Effects**
- **Enabled**: Full visual effects
- **Disabled**: Reduced visual effects for performance
- **Impact**: Affects performance on lower-end systems

#### **Show FPS**
- **Enabled**: Display frames per second counter
- **Disabled**: Hide FPS counter
- **Usage**: Monitor performance during gameplay

## 🔊 **Audio Settings**

### **Volume Controls**

#### **Master Volume**
- **Range**: 0.0 to 1.0 (0% to 100%)
- **Default**: 0.7 (70%)
- **Purpose**: Overall game volume control
- **Affects**: All audio in the game

#### **Music Volume**
- **Range**: 0.0 to 1.0 (0% to 100%)
- **Default**: 0.63 (63%)
- **Purpose**: Background music volume
- **Independent**: Separate from sound effects

#### **Sound Effects Volume**
- **Range**: 0.0 to 1.0 (0% to 100%)
- **Default**: Based on master volume
- **Purpose**: Game sound effects volume
- **Examples**: Piece placement, line clears, notifications

### **Audio Features**

#### **MP3 Player Integration**
- **Built-in Player**: Access from audio settings
- **Custom Music**: Load your own music files
- **Playlist Support**: Create custom playlists
- **Volume Control**: Independent music volume

#### **Audio State Management**
- **Persistent Settings**: Audio preferences saved between sessions
- **State Validation**: Ensures audio settings are valid
- **Change Tracking**: Monitors audio setting changes
- **Snapshot System**: Backup and restore audio configurations

## 🎮 **Input Settings**

### **Input Feel Tuner**

#### **Access**
- **In-Game**: Press **F9** during gameplay
- **Overlay**: Real-time adjustment interface
- **Live Testing**: Changes apply immediately
- **Persistent**: Settings save automatically

#### **Adjustable Parameters**

##### **Repeat Initial Delay (ms)**
- **Range**: 50-500 milliseconds
- **Default**: 120ms
- **Purpose**: Time before key repeat starts
- **Usage**: Adjust for your typing speed

##### **Generic Repeat Interval (ms)**
- **Range**: 20-200 milliseconds
- **Default**: 80ms
- **Purpose**: Standard key repeat rate
- **Usage**: General input responsiveness

##### **Move Repeat Interval (ms)**
- **Range**: 20-200 milliseconds
- **Default**: 50ms
- **Purpose**: Arrow key repeat rate
- **Usage**: Piece movement speed

##### **Rotate Repeat Interval (ms)**
- **Range**: 100-1000 milliseconds
- **Default**: 600ms
- **Purpose**: Rotation key repeat rate
- **Usage**: Piece rotation speed

#### **Tuner Controls**
- **I/K**: Navigate between parameters
- **J/L**: Adjust values (small steps)
- **Shift + J/L**: Adjust values (large steps)
- **Enter**: Apply changes
- **Escape**: Close tuner

### **Control Rebinding**

#### **Available Actions**
- **Move Left**: Move piece left
- **Move Right**: Move piece right
- **Rotate**: Rotate piece
- **Soft Drop**: Accelerate falling
- **Hard Drop**: Instant placement
- **Pause**: Pause game
- **Settings**: Open settings
- **Input Tuner**: Toggle input tuner

#### **Rebinding Process**
1. **Navigate to Controls tab**
2. **Click on action to rebind**
3. **Press new key** to assign
4. **Settings save automatically**
5. **Test new binding** immediately

#### **Default Bindings**
- **Arrow Keys**: Movement and rotation
- **Space**: Hard drop
- **Escape**: Pause/Settings
- **F9**: Input Feel Tuner

## 🔧 **Advanced Settings**

### **Performance Options**

#### **Frame Rate**
- **Unlimited**: Maximum frame rate
- **60 FPS**: Standard frame rate
- **30 FPS**: Lower frame rate for performance
- **V-Sync**: Synchronized with monitor

#### **Memory Management**
- **State Caching**: Intelligent caching for performance
- **State Batching**: Batch operations for efficiency
- **Memory Monitoring**: Track memory usage
- **Cleanup**: Automatic memory cleanup

### **Debug Options**

#### **Performance Overlay**
- **FPS Display**: Show frame rate
- **Memory Usage**: Display memory consumption
- **CPU Usage**: Show processor usage
- **Render Stats**: Rendering performance metrics

#### **Logging**
- **Error Logging**: Track errors and issues
- **Performance Logging**: Monitor performance
- **Debug Output**: Detailed debug information
- **Log Levels**: Adjust logging detail

## 🎯 **Settings Profiles**

### **Profile Management**
- **Default Profile**: Standard settings
- **Performance Profile**: Optimized for performance
- **Quality Profile**: Optimized for visual quality
- **Custom Profiles**: User-created profiles

### **Profile Features**
- **Save Profile**: Save current settings as profile
- **Load Profile**: Load saved profile
- **Delete Profile**: Remove unwanted profiles
- **Export/Import**: Share profiles between systems

## 🔄 **Settings Synchronization**

### **Cross-Platform**
- **Cloud Sync**: Settings sync across devices
- **Local Storage**: Settings stored locally
- **Backup**: Automatic settings backup
- **Restore**: Restore from backup

### **Version Compatibility**
- **Backward Compatibility**: Old settings work with new versions
- **Migration**: Automatic settings migration
- **Validation**: Settings validation on load
- **Fallback**: Default settings if validation fails

## 🐛 **Troubleshooting Settings**

### **Common Issues**

#### **Settings Not Saving**
- **Check Permissions**: Ensure write permissions
- **Verify Path**: Check settings file path
- **Restart Game**: Restart to apply changes
- **Reset Settings**: Use default settings

#### **Settings Reset**
- **Corrupted File**: Settings file may be corrupted
- **Version Mismatch**: Settings from different version
- **Manual Reset**: Delete settings file
- **Automatic Recovery**: Game creates new settings

#### **Performance Issues**
- **Lower Settings**: Reduce quality settings
- **Update Drivers**: Update graphics drivers
- **Close Background Apps**: Free up system resources
- **Monitor Performance**: Use performance overlay

### **Getting Help**
- **Check Documentation**: Review this guide
- **Community Support**: Ask community for help
- **Bug Reports**: Report settings issues
- **Developer Logs**: Check logs for errors

## 📊 **Settings Reference**

### **Default Values**
```json
{
  "master_volume": 0.7,
  "music_volume": 0.63,
  "brightness": 1.0,
  "ui_scale": 0.9,
  "vsync": true,
  "fullscreen": false,
  "native_fullscreen": false,
  "borderless": true,
  "show_fps": true,
  "particle_effects": true,
  "repeat_initial_delay_ms": 120,
  "repeat_interval_ms": 80,
  "repeat_move_interval_ms": 50,
  "repeat_rotate_interval_ms": 600
}
```

### **Settings File Location**
- **Windows**: `%APPDATA%/BladeFighters/settings.json`
- **macOS**: `~/Library/Application Support/BladeFighters/settings.json`
- **Linux**: `~/.config/BladeFighters/settings.json`

### **Backup Settings**
- **Automatic**: Settings backed up automatically
- **Manual**: Copy settings file to safe location
- **Cloud**: Use cloud sync for backup
- **Version Control**: Track settings changes

---

**Settings Guide**: ✅ **COMPLETE**  
**User Documentation**: 📚 **READY**  
**Troubleshooting**: 🔧 **COVERED**  
**Advanced Features**: 🚀 **DOCUMENTED**

*This settings guide is maintained by the Documentation Specialist. For technical details, refer to the module documentation.*

