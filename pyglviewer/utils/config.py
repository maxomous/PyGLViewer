import json
from pathlib import Path
from typing import Any, Dict

class Config:
    """Global configuration management system with file persistence.
    
    Handles registration, loading, saving and access of application configuration.
    Configuration is stored in JSON format and can be loaded/saved at runtime.
    """
    
    def __init__(self, config_file: str = "config.json"):
        self._config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._descriptions: Dict[str, str] = {}
        self.load()

    def add(self, name: str, default_value: Any, description: str = "") -> None:
        """Register a new configuration value with default.
        
        Args:
            name: Configuration identifier
            default_value: Initial/default value
            description: Optional configuration description
        """
        self._defaults[name] = default_value
        self._descriptions[name] = description
        self._config[name] = self._get_stored_value(name, default_value)

    def load(self) -> None:
        """Load configuration from JSON file."""
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r') as f:
                    self._stored_data = json.load(f)
                    # Update registered configuration with stored values
                    for name in self._config:
                        if name in self._stored_data:
                            self._config[name] = self._stored_data[name]
            except json.JSONDecodeError:
                print(f"Warning: Could not load configuration from {self._config_file}")

    def save(self) -> None:
        """Save current configuration values to JSON file."""
        with open(self._config_file, 'w') as f:
            json.dump(self._config, f, indent=2)

    def reset_to_defaults(self) -> None:
        """Reset all configuration to their default values."""
        for name, default in self._defaults.items():
            self._config[name] = default

    def _get_stored_value(self, name: str, default_value: Any) -> Any:
        """Get stored value if it exists, otherwise return default."""
        if hasattr(self, '_stored_data') and name in self._stored_data:
            return self._stored_data[name]
        return default_value

    def __getitem__(self, key: str) -> Any:
        return self._config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if key not in self._config:
            raise KeyError(f"Configuration key '{key}' not registered")
        self._config[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._config


if __name__ == '__main__':
    # Example usage
    config = Config()
    # Register configuration with defaults, if config already exists, use value from file
    config.add("variable_1", 0.001, "Description of variable 1")
    config.add("variable_2", [1, 2, 3], "Description of variable 2")
    # Save, modify and load and reset configuration
    config["variable_1"] = 0.002  
    config.save()
    config.load() 
    print(config["variable_1"])
    config.reset_to_defaults() # reset to defaults