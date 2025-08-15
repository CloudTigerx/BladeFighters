# Unified Input Management System
# This module now uses the new unified input system with backward compatibility

from modules.input_module.compatibility_layer import InputHandlerCompat

# Re-export the compatibility class as InputHandler for backward compatibility
InputHandler = InputHandlerCompat