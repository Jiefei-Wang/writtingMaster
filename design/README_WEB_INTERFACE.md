# Write Proofread Software - Web Interface

This web interface provides a user-friendly way to interact with the Write Proofread Software modules.

## Features

1. **Module Selection Panel**: Lists all available modules with checkboxes to enable/disable them
2. **Text Editor Panel**: Allows users to write or paste text and run selected modules on it
3. **Results Panel**: Shows detailed results when highlighted text is clicked

## How to Use

1. **Start the API Server**:
   - Run `python api.py` to start the Flask API server
   - The server will start on http://localhost:5000

2. **Open the Web Interface**:
   - Open `web_interface.html` in a web browser

3. **Select Modules**:
   - Check the boxes next to the modules you want to use

4. **Edit Text**:
   - Modify the text in the text editor panel as needed

5. **Run Modules**:
   - Click the "Run Selected Modules" button to process the text

6. **View Results**:
   - Matched text spans will be highlighted in different colors
   - Click on any highlighted text to see detailed results in the results panel

## Highlighting System

- Each module uses a different color for highlighting
- When multiple modules match the same text span, a combination color is used
- Highlights have 0.9 transparency so the underlying text is still visible

## Text Editing

- You can modify the text even after obtaining results
- If you add text within a highlighted span, it will remain highlighted
- If you delete text, the highlights will be cleared and you'll need to re-run the modules

## Requirements

- Python 3.x
- Flask (`pip install flask`)
- The modules must be properly implemented according to the BaseModule interface

## API Endpoints

- `GET /api/modules`: Returns a list of all available modules
- `POST /api/process`: Processes text with specified modules

## File Structure

- `web_interface.html`: The main web interface
- `api.py`: Flask API server
- `modules/`: Directory containing module implementations