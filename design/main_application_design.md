# Main Application Design

## File: main.py

```python
import argparse
import os
import sys
import json
import importlib.util
from modules.base_module import BaseModule

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

def list_modules():
    """List all available modules with their names and descriptions"""
    modules = discover_modules()
    print("Available modules:")
    for name, module in modules.items():
        print(f"  {name}: {module.description()}")

def process_text(text_file, module_names):
    """Process text file with specified modules"""
    # Read the text file
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Discover modules
    available_modules = discover_modules()
    
    # Process with specified modules
    results = {}
    for module_name in module_names:
        if module_name in available_modules:
            module = available_modules[module_name]
            results[module_name] = module.process(text)
        else:
            print(f"Warning: Module '{module_name}' not found")
    
    # Output results in JSON format
    print(json.dumps(results, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Write Proofread Software")
    parser.add_argument("--list-modules", action="store_true", help="List all available modules")
    parser.add_argument("--text-file", type=str, help="Path to the text file to proofread")
    parser.add_argument("--modules", type=str, help="Comma-separated list of module names to use")
    
    args = parser.parse_args()
    
    if args.list_modules:
        list_modules()
        return
    
    if args.text_file and args.modules:
        if not os.path.exists(args.text_file):
            print(f"Error: Text file '{args.text_file}' not found")
            sys.exit(1)
        
        module_names = [name.strip() for name in args.modules.split(",")]
        process_text(args.text_file, module_names)
        return
    
    # If no arguments provided, show help
    parser.print_help()

if __name__ == "__main__":
    main()
```

## Application Functionality

### Module Discovery
The application automatically discovers modules by:
1. Scanning the `modules/` directory for Python files
2. Dynamically loading each module
3. Instantiating classes that inherit from `BaseModule`
4. Registering them by their `name()` method

### Command-Line Interface
The application supports these commands:
1. `python main.py --list-modules` - Lists all available modules with descriptions
2. `python main.py --text-file path/to/text.txt --modules isolated_pronouns` - Processes text with specified modules
3. `python main.py --text-file path/to/text.txt --modules isolated_pronouns,other_module` - Processes text with multiple modules

### Text Processing
The application:
1. Reads the specified text file
2. Loads the specified modules
3. Processes the text with each module
4. Returns results in JSON format, separated by modules

### Error Handling
The application includes basic error handling for:
- Missing text files
- Non-existent modules
- Invalid command-line arguments