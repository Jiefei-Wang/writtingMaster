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
    
    # Check if modules directory exists
    if not os.path.exists(modules_dir):
        print("Error: modules directory not found")
        return modules
    
    # Iterate through all Python files in the modules directory
    for filename in os.listdir(modules_dir):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "base_module.py":
            module_name = filename[:-3]  # Remove .py extension
            module_path = os.path.join(modules_dir, filename)
            
            # Load the module dynamically
            try:
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
            except Exception as e:
                print(f"Warning: Failed to load module {module_name}: {e}")
    
    return modules

def list_modules():
    """List all available modules with their names and descriptions"""
    modules = discover_modules()
    if not modules:
        print("No modules found")
        return
    
    print("Available modules:")
    for name, module in modules.items():
        print(f"  {name}: {module.description()}")

def process_text(text_file, module_names):
    """Process text file with specified modules"""
    # Check if text file exists
    if not os.path.exists(text_file):
        print(f"Error: Text file '{text_file}' not found")
        sys.exit(1)
    
    # Read the text file
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading text file: {e}")
        sys.exit(1)
    
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
        module_names = [name.strip() for name in args.modules.split(",")]
        process_text(args.text_file, module_names)
        return
    
    # If no arguments provided, show help
    parser.print_help()

if __name__ == "__main__":
    main()