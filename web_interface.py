from flask import Flask, jsonify, request, render_template
from modules.logger import module_logger
import os
import sys
import importlib.util
from modules.base_module import BaseModule

app = Flask(__name__)

# Serve sample text from text/sample.txt
@app.route('/api/sample-text', methods=['GET'])
def get_sample_text():
    """Serve the sample text from text/example.txt"""
    try:
        with open('text/example.txt', 'r', encoding='utf-8') as f:
            sample_text = f.read()
        return sample_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f"Error loading sample text: {e}", 500

def discover_modules():
    """Discover and load all modules from the modules directory"""
    modules = {}
    modules_dir = "modules"
    
    # Check if modules directory exists
    if not os.path.exists(modules_dir):
        print("Error: modules directory not found")
        return modules
    
    # Iterate through all subdirectories in the modules directory
    for subfolder in os.listdir(modules_dir):
        subfolder_path = os.path.join(modules_dir, subfolder)
        if os.path.isdir(subfolder_path):
            module_file = f"module.py"
            module_path = os.path.join(subfolder_path, module_file)
            if os.path.isfile(module_path):
                module_name = f"{subfolder}.module_file"
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec is None or spec.loader is None:
                        print(f"Warning: Failed to load module spec or loader for {module_name}")
                        continue
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

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template('index.html')

@app.route('/api/modules', methods=['GET'])
def get_modules():
    """Get list of all available modules"""
    try:
        modules = discover_modules()
        module_list = []
        for name, module in modules.items():
            module_list.append({
                'name': name,
                'description': module.description()
            })
        return jsonify(module_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_text():
    """Process text with specified modules"""
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '')
        module_names = data.get('modules', [])
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not module_names:
            return jsonify({'error': 'No modules specified'}), 400
        
        # Discover modules
        available_modules = discover_modules()
        
        # Process with specified modules
        results = {}
        for module_name in module_names:
            if module_name in available_modules:
                module = available_modules[module_name]
                results[module_name] = module.process(text)
            else:
                return jsonify({'error': f'Module \'{module_name}\' not found'}), 400
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Write Proofread Software Web Interface...")
    print("Access the interface at http://localhost:5000")
    app.run(debug=True, port=5000)