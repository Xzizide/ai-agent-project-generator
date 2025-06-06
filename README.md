# ai-agent-project-generator
Using multiple LLM-agents to simulate a development studio to develop projects from given initial prompt.

## Setup

### Prerequisites
1. **LM Studio**: Download and install LM Studio from [https://lmstudio.ai/](https://lmstudio.ai/)
2. **Python 3.8+**: Make sure you have Python installed

### Installation
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### LM Studio Configuration
1. Open LM Studio
2. Download a language model (recommended: any 7B or 13B parameter model that fits your hardware)
3. Start the local server:
   - In LM Studio, go to "Local Server" tab
   - Select your model
   - Start the server (default: `http://localhost:1234`)
4. The application will automatically connect to LM Studio at `http://localhost:1234/v1`

### Optional: Image Generation
The system also supports local image generation APIs:
- **ComfyUI**: For advanced Stable Diffusion workflows
- **Automatic1111**: For standard Stable Diffusion WebUI

If none are available, the system will generate placeholder images with text descriptions.

## Usage
Run the main script:
```bash
python main.py
```

The system simulates a development team with multiple agents:
- **Developer**: Creates and modifies code files
- **Client**: Provides requirements and feedback
- **Designer**: Creates visual designs and generates images
- **Boss**: Provides oversight and deadline pressure
- **QA**: Tests functionality and finds bugs
- **Manager**: Coordinates team activities
- **Rubber Duck**: Helps with problem-solving when stuck

## Configuration
You can modify the LM Studio connection in `main.py`:
```python
lm_studio = LMStudioClient(
    base_url="http://localhost:1234/v1",  # Change if using different port
    model="local-model"  # This is automatically detected by LM Studio
)
```