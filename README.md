# Write Proofread Software - Web Interface

This is a web interface for the Write Proofread Software that allows users to:

1. Select from available modules
2. Edit text in a contenteditable panel
3. Run selected modules on the text
4. View highlighted results with different colors for different modules
5. Click on highlighted text to see detailed results

## Features

- Three-panel layout with module selection, text editor, and results
- Bootstrap styling for a modern look
- Dynamic module discovery
- Text highlighting with different colors for different modules
- Overlapping highlight detection with combination colors
- Click on highlights to see detailed results
- Text editing capabilities that preserve highlights

## Available Modules

### Isolated Pronouns Module
Identifies isolated pronouns that don't carry specific meaning by themselves

### Transition Module
Identifies missing transition words between consecutive sentences within the same paragraph. Uses LLMs to analyze sentence pairs and suggest appropriate transition words when needed.

## File Structure

- `run_web_interface.py` - Simple script to run the web interface
- `web_interface.py` - Flask server with API endpoints
- `templates/index.html` - HTML structure
- `static/css/style.css` - Styling with Bootstrap
- `static/js/main.js` - All JavaScript functionality
- `modules/` - Directory containing module implementations
- `settings.json` - Configuration for LLM services
- `.env` - Environment variables for API keys

## How to Run

1. Install required packages:
   ```
   pip install flask requests python-dotenv nltk
   ```

2. Run the web interface:
   ```
   python run_web_interface.py
   ```

3. Access the interface at http://localhost:5000

## API Endpoints

- `GET /api/modules` - Get list of available modules
- `POST /api/process` - Process text with specified modules

## How to Use

1. Select one or more modules from the "Available Modules" panel
2. Edit the text in the "Text Editor" panel
3. Click "Run Selected Modules" to process the text
4. View highlighted results in the text editor
5. Click on any highlighted text to see detailed results in the "Results" panel