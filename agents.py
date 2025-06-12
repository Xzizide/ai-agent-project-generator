import requests
import re


class Agent:
    def __init__(
        self,
        name,
        personality,
        activation_triggers=None,
        can_write_files=False,
        can_generate_images=False,
        model_name="qwen3:8b",
    ):
        self.name = name
        self.personality = personality
        self.activation_triggers = activation_triggers or []
        self.can_write_files = can_write_files
        self.can_generate_images = can_generate_images
        self.model_name = model_name
        self.messages = [
            {
                "role": "user",
                "content": f"Your name is {self.name} and your personality is {self.personality}. {self.get_file_instructions()}",
            }
        ]

    def _filter_thinking_sections(self, text):
        """Remove thinking sections between <think> and </think> tags"""
        # Use regex to remove everything between <think> and </think> tags (case insensitive)
        filtered_text = re.sub(
            r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE
        )
        # Clean up any extra whitespace that might be left
        filtered_text = re.sub(r"\n\s*\n\s*\n", "\n\n", filtered_text)
        return filtered_text.strip()

    def get_file_instructions(self):
        instructions = ""
        if self.can_write_files:
            instructions += """When you need to create or modify files, use this format:
            
FILE_ACTION: CREATE
FILENAME: file.ext
CONTENT:
```
[file content here]
```

FILE_ACTION: MODIFY
FILENAME: file.ext
CHANGES: [describe what you're changing]
CONTENT:
```
[new file content here]
```

Always use this exact format when working with files."""

        if self.can_generate_images:
            instructions += """

When you need to generate images, use this format:

IMAGE_ACTION: GENERATE
FILENAME: images/image.png
PROMPT: [detailed description of the image you want to generate]
STYLE: [optional style guidance like "photorealistic", "illustration", "minimalist", etc.]

Always be very descriptive in your prompts for better image generation."""

        return instructions

    def update_messages(self, name, message):
        self.messages.append(
            {"role": "user", "content": name + ": " + message}
        )

    def get_response(self, name, prompt, project_files=None):
        # Add context about existing files
        context_prompt = prompt
        if project_files and (
            self.can_write_files or self.can_generate_images
        ):
            files_info = "\n\nCurrent project files:\n"
            for file_path, content in project_files.items():
                if isinstance(content, str):
                    files_info += f"- {file_path}: {len(content)} characters\n"
                else:
                    files_info += f"- {file_path}: image file\n"
            context_prompt = prompt + files_info

        # LMStudio API call
        try:
            response = requests.post(
                "http://localhost:1234/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model_name,
                    "messages": self.messages
                    + [
                        {
                            "role": "user",
                            "content": name + ": " + context_prompt,
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "stream": False,
                },
                timeout=60,
            )

            if response.status_code == 200:
                response_data = response.json()
                message_content = response_data["choices"][0]["message"][
                    "content"
                ]
                # Filter out thinking sections
                message_content = self._filter_thinking_sections(
                    message_content
                )
            else:
                print(f"LMStudio API error: {response.status_code}")
                message_content = f"Error: Failed to get response from LMStudio (status: {response.status_code})"

        except requests.exceptions.RequestException as e:
            print(f"LMStudio connection error: {e}")
            message_content = "Error: Could not connect to LMStudio. Make sure LMStudio is running on localhost:1234"
        except Exception as e:
            print(f"Unexpected error: {e}")
            message_content = f"Error: {str(e)}"

        self.update_messages(name, prompt)
        self.update_messages(self.name, message_content)

        return message_content

    def should_activate(self, context):
        """Check if this agent should respond based on current context"""
        return any(
            trigger in context.get("phase", "")
            or trigger in context.get("keywords", [])
            or trigger in context.get("last_message", "")
            for trigger in self.activation_triggers
        )

    def reset_messages(self):
        """Reset agent messages to only the initial system prompt"""
        self.messages = [
            {
                "role": "user",
                "content": f"Your name is {self.name} and your personality is {self.personality}. {self.get_file_instructions()}",
            }
        ]
