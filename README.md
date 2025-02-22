# Canvas Course Outline Generator

A Chrome extension that extracts and organizes course content from Canvas LMS into a structured JSON format. The extension uses AI to dynamically generate a schema that adapts to different course structures, making it flexible for various instructor organization styles.

## Features

### 1. Canvas LMS Integration
- Seamlessly extracts course content including modules, assignments, quizzes, and files
- Automatically detects course ID and interfaces with Canvas API endpoints

### 2. AI-Powered Schema Generation
- Leverages OpenAI's GPT models for intelligent content processing (can change to Deepseek easily)
- Implements prompt chaining for enhanced schema generation:
  1. Initial prompt analyzes raw Canvas data to understand course structure
  2. Secondary prompt generates optimal JSON schema based on structure analysis
  3. Final prompt transforms and organizes course content into the generated schema
- Handles edge cases and varying instructor organization patterns
- Maintains semantic relationships between course components
- Generates consistent, well-structured output regardless of input variation

### 3. Dynamic Data Processing
- Smart content categorization based on context and relationships
- Intelligent mapping of course materials to appropriate schema sections
- Preservation of hierarchical relationships in course structure
- Automatic handling of cross-referenced content

## Setup and Installation

### 1. Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/pvelleleth/CanvasCourseOutline.git
   cd CanvasCourseOutline/backend
   ```

2. Set up Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Create `.env` file in backend directory
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

4. Start the FastAPI server:
   ```bash
   fastapi dev main.py
   ```

### 2. Chrome Extension Setup
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked"
4. Select the root directory of the cloned repository
5. The extension icon should appear in your Chrome toolbar

## Technical Implementation

### AI Implementation Details
- **Data Processing Pipeline**:
  1. Raw Canvas API data collection
  2. Initial content analysis using GPT for structure understanding
  3. Schema generation based on analyzed patterns
  4. Content transformation using generated schema
  
- **Prompt Engineering**:
  - Custom-designed prompt chain for optimal results
  - Context-aware prompts that maintain course relationships
  - Robust error handling and edge case management
  - Intelligent content categorization and organization

### Architecture
- Chrome Extension components:
  - Manifest V3 configuration
  - Background service worker (not used)
  - Content script for data extraction
  - Popup interface for user interaction

### Key Components
1. **Content Script (`content.js`)**
   - Extracts course ID from URL
   - Makes API calls to Canvas endpoints
   - Sends data to backend for processing
   - Handles file download

2. **Popup Interface (`popup.js`, `popup.html`)**
   - Provides user interface
   - Manages loading states
   - Triggers content script execution
   - Handles error states

3. **Backend Integration**
   - Processes raw Canvas data
   - Generates AI-powered schema
   - Creates structured JSON output
   - Handles data transformation

## Usage

1. Navigate to any Canvas course page
2. Click the extension icon
3. Click "Generate Outline"
4. Wait for processing
5. JSON file will automatically download

## Technical Requirements

- Chrome browser
- Active Canvas LMS account
- Access to course content
- Internet connection for API calls

## Security and Permissions

The extension requires:
- Access to Canvas domains (*.instructure.com)
- Active tab permissions
- Storage access
- Download capabilities

## Development Notes

- Utilizes OpenAI API for intelligent content processing
- Implements prompt chaining for enhanced results
- Built with vanilla JavaScript and FastAPI
- Uses Chrome Extension Manifest V3