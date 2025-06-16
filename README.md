# ai-agent-project-generator
Using multiple LLM-agents to simulate a development studio to develop websites from given initial prompt.

## Recent Updates ✨

### 🤖 **Google AI Studio Integration**
- Replaced LMStudio with Google AI Studio (Gemini 2.0 Flash)
- Added environment variable support for secure API key management
- Improved response processing and error handling

### 📖 **Enhanced File Reading Capabilities**
- Developer and QA agents can now read existing files using `FILE_ACTION: READ`
- File contents are automatically included in agent conversation context
- Agents can analyze existing code before making improvements

### 🔍 **Automatic Project Directory Scanning**
- Conversation manager automatically scans entire project directory
- All existing files are loaded into agent context at conversation start
- Supports external file detection (files added outside the agent system)
- Smart filtering skips irrelevant files (hidden, cache, binary images)

## Setup

### Prerequisites
1. **Google AI Studio API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Python 3.8+**: Make sure you have Python installed

### Installation
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Google AI Studio Configuration
1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the project root:
   ```env
   # Google AI Studio API Configuration
   GOOGLE_API_KEY=your_google_ai_studio_api_key_here
   ```
3. Replace `your_google_ai_studio_api_key_here` with your actual API key
4. The application will automatically use the API key from the environment

### Optional: Image Generation
The system also supports local image generation APIs:
- **ComfyUI**: For advanced Stable Diffusion workflows

If none are available, the system will generate placeholder images with text descriptions.

## Usage
Run the main script:
```bash
python main.py
```

The system simulates a development team with multiple agents:
- **Developer**: Creates and modifies code files, **can read existing files** for analysis
- **Client**: Provides requirements and feedback
- **Designer**: Creates visual designs and generates images
- **QA**: Tests functionality and finds bugs, **can read files for code quality analysis**
- **Manager**: Coordinates team activities

## Enhanced Agent Capabilities

### 📝 **File Operations**
Agents with file capabilities can now:

#### **Writing Files** (Developer, Designer, QA)
```
FILE_ACTION: CREATE
FILENAME: index.html
CONTENT:
```html
<!DOCTYPE html>
<html>...
```

#### **Reading Files** (Developer, QA) ✨ **NEW**
```
FILE_ACTION: READ
FILENAME: index.html
```
- File content is displayed and added to agent conversation context
- Enables informed decision-making when modifying existing code
- Supports analysis of current project structure

#### **Image Generation** (Designer)
```
IMAGE_ACTION: GENERATE
FILENAME: images/hero.png
PROMPT: Professional website hero image
STYLE: modern, clean
```

## Features

### 🎯 **Intelligent Development Workflow**
- Agents automatically read existing files before making changes
- Complete project context awareness
- Smart file filtering and loading
- Seamless collaboration between different agent roles

### 🔧 **Advanced File Management**
- Automatic project directory scanning
- Support for external file detection
- Binary file handling
- Error handling for encoding and permission issues

### 🌐 **Modern API Integration**
- Google AI Studio (Gemini 2.0 Flash)
- Environment variable security
- Robust error handling and retry logic
- Efficient conversation context management

### 🎨 **Creative Capabilities**
- Professional image generation
- Responsive web design
- Modern UI/UX patterns
- Cross-platform compatibility