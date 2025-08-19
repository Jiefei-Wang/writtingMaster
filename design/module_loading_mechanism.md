# Module Loading Mechanism

## How Modules Are Discovered and Loaded

The write proofread software uses a dynamic module loading mechanism that allows users to simply drop new modules into the `modules/` directory without modifying the main application code.

## Discovery Process

1. **Directory Scanning**: The appliscation scans the `modules/` directory for Python files
2. **File Filtering**: Files are filtered to exclude:
   - `__init__.py` (package initializer)
   - `base_module.py` (abstract base class)
   - Non-Python files
3. **Dynamic Import**: Each module file is dynamically imported using `importlib`
4. **Class Discovery**: The application searches for classes that inherit from `BaseModule`
5. **Instantiation**: Valid module classes are instantiated
6. **Registration**: Modules are registered using their `name()` method as the key

## Implementation Details

```python
def discover_modules():
    """Discover and load all modules from the modules directory"""
    modules = {}
    modules_dir = "modules"
    
    # Iterate through all Python files in the modules directory
    for filename in os.listdir(modules_dir):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "base_module.py":
            module_name = filename[:-3]  # Remove .py extension
            module_path = os.path.join(modules_dir, filename)
            
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the module class (assuming it's the only class that inherits from BaseModule)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseModule) and attr != BaseModule:
                    module_instance = attr()
                    modules[module_instance.name()] = module_instance
                    break
    
    return modules
```

## Requirements for Custom Modules

To ensure a module is properly discovered and loaded, it must:

1. **Be a Python file** in the `modules/` directory
2. **Contain a class** that inherits from `BaseModule`
3. **Implement all abstract methods** (`name()`, `description()`, `process()`)
4. **Return a unique name** from the `name()` method

## Example Module Structure

```python
# modules/example_module.py
from modules.base_module import BaseModule

class ExampleModule(BaseModule):
    def name(self) -> str:
        return "example_module"
    
    def description(self) -> str:
        return "An example module that demonstrates the interface"
    
    def process(self, text: str) -> dict:
        # Implementation here
        return {
            "module_name": self.name(),
            "module_description": self.description(),
            "results": []
        }
```

## Module Registration

When the above module is discovered, it will be registered as:
```python
modules["example_module"] = ExampleModule()
```

This allows users to reference the module by its name in command-line arguments:
```bash
python main.py --text-file text/sample.txt --modules example_module
```

## Error Handling

The discovery mechanism includes basic error handling:
- Skips non-Python files
- Skips special files (`__init__.py`, `base_module.py`)
- Only instantiates classes that properly inherit from `BaseModule`
- Warns when a specified module is not found during processing

## Benefits of This Approach

1. **Extensibility**: New modules can be added without modifying existing code
2. **Isolation**: Modules are self-contained and don't affect each other
3. **Simplicity**: Users only need to follow the interface contract
4. **Automatic Discovery**: No manual registration required
5. **Dynamic Loading**: Only the modules needed are loaded