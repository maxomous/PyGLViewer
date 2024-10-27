import json
import numpy as np
from pathlib import Path
from typing import Any, Dict, Union

class Parameters:
    def __init__(self, param_file: str = "parameters.json"):
        self._param_file = Path(param_file)
        self._params: Dict[str, Parameter] = {}
        self.load()

    def register(self, name: str, default_value: Any, description: str = "") -> None:
        """Register a new parameter with a default value"""
        self._params[name] = Parameter(
            name=name,
            default_value=default_value,
            current_value=self._get_stored_value(name, default_value),
            description=description
        )

    def _get_stored_value(self, name: str, default_value: Any) -> Any:
        """Get stored value from file if it exists, otherwise return default"""
        if hasattr(self, '_stored_data') and name in self._stored_data:
            return self._decode_value(self._stored_data[name])
        return default_value

    def load(self) -> None:
        """Load parameters from file and update all parameter values"""
        self._stored_data = {}
        if self._param_file.exists():
            try:
                with open(self._param_file, 'r') as f:
                    self._stored_data = json.load(f)
                    # Update all registered parameters with loaded values
                    for name, param in self._params.items():
                        if name in self._stored_data:
                            param.value = self._decode_value(self._stored_data[name])
            except json.JSONDecodeError:
                print(f"Warning: Could not load parameters from {self._param_file}")

    def save(self) -> None:
        """Explicitly save parameters to file"""
        data = {name: self._encode_value(param.value) 
                for name, param in self._params.items()}
        with open(self._param_file, 'w') as f:
            json.dump(data, f, indent=2)

    def reset_to_defaults(self) -> None:
        """Reset all parameters to their default values"""
        for param in self._params.values():
            param.reset_to_default()

    def _encode_value(self, value: Any) -> Any:
        """Encode special types (like numpy arrays) for JSON serialization"""
        if isinstance(value, np.ndarray):
            return {'__type__': 'ndarray', 'data': value.tolist()}
        return value

    def _decode_value(self, value: Any) -> Any:
        """Decode special types from JSON"""
        if isinstance(value, dict) and '__type__' in value:
            if value['__type__'] == 'ndarray':
                return np.array(value['data'])
        return value

    def __getitem__(self, key: str) -> Any:
        return self._params[key].value

    def __setitem__(self, key: str, value: Any) -> None:
        if key not in self._params:
            raise KeyError(f"Parameter '{key}' not registered")
        self._params[key].value = value

    def __contains__(self, key: str) -> bool:
        return key in self._params

class Parameter:
    def __init__(self, name: str, default_value: Any, current_value: Any, description: str = ""):
        self.name = name
        self._default_value = default_value
        self._value = current_value
        self.description = description

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        self._value = new_value

    def reset_to_default(self) -> None:
        self._value = self._default_value

# Global instance
parameters = Parameters()

if __name__ == '__main__':
    from parameters import parameters

    # Register parameters with defaults
    parameters.register("learning_rate", 0.001, "Learning rate for training")
    parameters.register("batch_size", 32, "Batch size for training")
    parameters.register("model_weights", np.zeros(10), "Initial model weights")

    print(parameters["batch_size"])  # 0.001
    # Access parameters dictionary-style
    print(parameters["learning_rate"])  # 0.001
    parameters["batch_size"] = 64
    print(parameters["batch_size"])  # 0.001

    # Save explicitly when needed
    parameters.save()

    # Reset to defaults when needed
    parameters.reset_to_defaults()
