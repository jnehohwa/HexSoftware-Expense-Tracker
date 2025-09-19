"""Configuration management for LedgerLite."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Simple configuration manager using JSON files."""
    
    def __init__(self, config_name: str = "ledgerlite_config.json") -> None:
        """Initialize configuration manager.
        
        Args:
            config_name: Name of the configuration file.
        """
        # Use macOS Application Support directory
        self.config_dir = Path.home() / "Library" / "Application Support" / "LedgerLite"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / config_name
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}
        else:
            self._config = {}
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key.
            value: Configuration value.
        """
        self._config[key] = value
        self.save()
    
    def get_last_month(self) -> Optional[str]:
        """Get the last selected month.
        
        Returns:
            Last selected month in YYYY-MM format, or None.
        """
        return self.get("last_month")
    
    def set_last_month(self, month: str) -> None:
        """Set the last selected month.
        
        Args:
            month: Month in YYYY-MM format.
        """
        self.set("last_month", month)
    
    def get_window_geometry(self) -> Optional[Dict[str, int]]:
        """Get the last window geometry.
        
        Returns:
            Dictionary with window geometry, or None.
        """
        return self.get("window_geometry")
    
    def set_window_geometry(self, geometry: Dict[str, int]) -> None:
        """Set the window geometry.
        
        Args:
            geometry: Dictionary with window geometry.
        """
        self.set("window_geometry", geometry)
    
    def get_theme(self) -> str:
        """Get the current theme.
        
        Returns:
            Current theme name.
        """
        return self.get("theme", "light")
    
    def set_theme(self, theme: str) -> None:
        """Set the current theme.
        
        Args:
            theme: Theme name.
        """
        self.set("theme", theme)


# Global config instance
config = Config()


