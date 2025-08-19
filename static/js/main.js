// Module colors for highlighting
const moduleColors = {
    'isolated_pronouns': '#FF5733'  // Example color
};

// Store for highlight information
let highlights = [];
let moduleResults = {};
let isProcessingText = false;
let originalText = '';

// Function to discover modules
async function discoverModules() {
    try {
        const response = await fetch('/api/modules');
        const modules = await response.json();

        const moduleList = document.getElementById('moduleList');
        const moduleLoading = document.getElementById('moduleLoading');

        moduleList.innerHTML = '';

        if (modules.length === 0) {
            moduleList.innerHTML = '<li class="list-group-item">No modules found</li>';
        } else {
            modules.forEach(module => {
                const li = document.createElement('li');
                li.className = 'list-group-item module-item';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'form-check-input me-2';
                checkbox.id = `module-${module.name}`;
                checkbox.value = module.name;
                checkbox.addEventListener('change', updateRunButtonState);

                const label = document.createElement('label');
                label.className = 'form-check-label';
                label.htmlFor = `module-${module.name}`;
                label.innerHTML = `<strong>${module.name}</strong>: ${module.description}`;

                li.appendChild(checkbox);
                li.appendChild(label);
                moduleList.appendChild(li);
            });
        }

        // Show the module list and hide loading message
        moduleLoading.style.display = 'none';
        moduleList.style.display = 'block';
    } catch (error) {
        console.error('Error loading modules:', error);
        document.getElementById('moduleLoading').textContent = 'Error loading modules';
    }
}

// Update run button state based on selections
function updateRunButtonState() {
    const selectedModules = document.querySelectorAll('.module-item input[type="checkbox"]:checked');
    const runButton = document.getElementById('runButton');
    runButton.disabled = selectedModules.length === 0;
}

// Function to process text with selected modules
async function processText() {
    const text = getTextFromEditor();
    originalText = text; // Store original text for reference
    const selectedModules = [];

    // Get selected modules
    document.querySelectorAll('.module-item input[type="checkbox"]:checked').forEach(checkbox => {
        selectedModules.push(checkbox.value);
    });

    if (selectedModules.length === 0) {
        alert('Please select at least one module');
        return;
    }

    // Show loading state
    const runButton = document.getElementById('runButton');
    runButton.disabled = true;
    runButton.textContent = 'Processing...';
    isProcessingText = true;

    try {
        // Send request to API
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                modules: selectedModules
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        moduleResults = await response.json();

        // Process results and apply highlights
        processResults(text, moduleResults);
    } catch (error) {
        console.error('Error processing text:', error);
        alert('Error processing text: ' + error.message);
    } finally {
        // Restore button state
        runButton.disabled = false;
        runButton.textContent = 'Run Selected Modules';
        isProcessingText = false;
    }
}

// Process results and apply highlights
function processResults(text, results) {
    // Clear previous highlights
    highlights = [];

    // Collect all highlights from all modules
    for (const moduleName in results) {
        const moduleResult = results[moduleName];
        if (moduleResult.results) {
            highlights.push(...moduleResult.results.map(result => ({
                ...result,
                module_name: moduleName
            })));
        }
    }

    // Apply highlights to text
    applyHighlights(text);
}

// Get text content from the editor
function getTextFromEditor() {
    const editor = document.getElementById('textEditor');
    // Get text content without HTML tags
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = editor.innerHTML;
    return tempDiv.textContent || tempDiv.innerText || '';
}

// Apply highlights to text
function applyHighlights(text) {
    // Sort highlights by position (descending order to preserve positions when inserting)
    highlights.sort((a, b) => b.position - a.position);

    // Create a map to track which positions are highlighted by which modules
    const highlightMap = new Map();

    // Populate highlight map
    highlights.forEach(highlight => {
        const key = `${highlight.position}-${highlight.text_span.length}`;
        if (!highlightMap.has(key)) {
            highlightMap.set(key, []);
        }
        highlightMap.get(key).push(highlight);
    });

    // Create highlighted text
    let highlightedText = text;

    // Process each unique highlight position
    for (const [key, highlightItems] of highlightMap.entries()) {
        const [position, length] = key.split('-').map(Number);

        // Get the text span to highlight
        const textSpan = highlightedText.substring(position, position + length);

        // Determine highlight color based on modules
        const moduleNames = highlightItems.map(item => item.module_name);
        const color = determineHighlightColor(moduleNames);

        // Create data attribute with module information
        const modulesData = moduleNames.join(',');
        const explanationsData = highlightItems.map(item => item.explanation).join('|');

        // Create highlighted span
        const highlightSpan = `<span class="highlight" style="background-color: ${color}" data-modules="${modulesData}" data-explanations="${explanationsData}">${textSpan}</span>`;

        // Replace text with highlighted span
        highlightedText = highlightedText.substring(0, position) +
                          highlightSpan +
                          highlightedText.substring(position + length);
    }

    // Set the highlighted text in the editor
    document.getElementById('textEditor').innerHTML = highlightedText;
}

// Determine highlight color based on modules
function determineHighlightColor(moduleNames) {
    if (moduleNames.length === 1) {
        // Single module highlight
        return moduleColors[moduleNames[0]] || '#FFFF00';  // Default yellow
    } else {
        // Multiple modules - combine colors (simplified approach)
        // In a real implementation, you might want to blend colors or use a pattern
        return '#9B59B6';  // Purple for overlapping highlights
    }
}

// Show results for clicked highlight
function showResultsForHighlight(event) {
    const modules = event.target.dataset.modules.split(',');
    const explanations = event.target.dataset.explanations.split('|');
    const textSpan = event.target.textContent;

    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = '<h3>Module Results</h3>';

    modules.forEach((moduleName, index) => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';

        const resultHeader = document.createElement('div');
        resultHeader.className = 'result-header';
        resultHeader.innerHTML = `<strong>${moduleName}</strong>`;

        const resultExplanation = document.createElement('div');
        resultExplanation.className = 'result-explanation mt-2';
        resultExplanation.textContent = `Matched text: "${textSpan}" - Explanation: ${explanations[index]}`;

        resultItem.appendChild(resultHeader);
        resultItem.appendChild(resultExplanation);
        resultsContainer.appendChild(resultItem);
    });
}

// Handle text changes in the editor while preserving highlights
function handleTextChange() {
    // Skip handling if we're processing text (to avoid interference)
    if (isProcessingText) {
        return;
    }

    // Clear results when text changes
    document.getElementById('resultsContainer').innerHTML = '';
}

// Handle paste events to preserve text content without HTML
function handlePaste(event) {
    // Prevent default paste behavior
    event.preventDefault();

    // Get plain text from clipboard
    const text = (event.clipboardData || window.clipboardData).getData('text/plain');

    // Insert text at cursor position
    const selection = window.getSelection();
    if (!selection.rangeCount) return;

    const range = selection.getRangeAt(0);
    range.deleteContents();

    const textNode = document.createTextNode(text);
    range.insertNode(textNode);

    // Move cursor to end of inserted text
    range.setStartAfter(textNode);
    range.setEndAfter(textNode);
    selection.removeAllRanges();
    selection.addRange(range);
}

// Handle keydown events for special handling
function handleKeyDown(event) {
    // Skip handling if we're processing text
    if (isProcessingText) {
        return;
    }

    // Handle special keys that might affect highlights
    if (event.key === 'Enter' || event.key === 'Backspace' || event.key === 'Delete') {
        // These keys might affect highlight positions
        // In a more advanced implementation, you would track these changes
        // For now, we'll just clear results when these keys are pressed
        setTimeout(() => {
            document.getElementById('resultsContainer').innerHTML = '';
        }, 10);
    }
}

// Initialize the interface
function init() {
    // Load sample text
    document.getElementById('textEditor').textContent = `This is a sample text file that we can use to test our proofreading software. It contains several instances of isolated pronouns that our module should identify.

This sentence starts with an isolated pronoun. That sentence also starts with one. These sentences are examples. Those examples are useful for testing.

In the middle of a sentence, we might find this kind of construction. Or that kind of pattern. These kinds of examples are helpful. Those types of sentences work too.

Some pronouns should not be matched, like "this" when it's part of a larger word like "thisexample" or "anotherthis". Similarly, "that" in "thatexample" should not be matched.

But standalone pronouns like this one should be identified. That one too. These are clear cases. Those are also obvious.

This.
That.
These.
Those.

The end of the text.`;

    // Discover modules
    discoverModules();

    // Add event listeners
    document.getElementById('runButton').addEventListener('click', processText);

    // Add event listener for highlights
    document.getElementById('textEditor').addEventListener('click', function(event) {
        if (event.target.classList.contains('highlight')) {
            showResultsForHighlight(event);
        }
    });

    // Add event listener for text changes
    document.getElementById('textEditor').addEventListener('input', handleTextChange);

    // Add event listener for paste events
    document.getElementById('textEditor').addEventListener('paste', handlePaste);

    // Add event listener for keydown events
    document.getElementById('textEditor').addEventListener('keydown', handleKeyDown);
}

// Run initialization when page loads
window.addEventListener('load', init);