import os
from pathlib import Path
from image_generator import ImageGenerator


class FileManager:
    def __init__(self, project_name):
        # Create the main website_project directory
        main_project_dir = Path("website_project")
        main_project_dir.mkdir(exist_ok=True)

        # Create a subdirectory for this specific project
        self.project_dir = main_project_dir / project_name
        self.project_dir.mkdir(exist_ok=True)
        self.project_files = {}
        self.image_generator = ImageGenerator()

        # Create images directory within the project folder
        images_dir = self.project_dir / "images"
        images_dir.mkdir(exist_ok=True)

    def process_agent_response(self, response):
        """Process agent response for file operations and image generation"""
        actions_performed = []

        # Handle file operations
        if "FILE_ACTION:" in response:
            actions_performed.extend(self._process_file_actions(response))

        # Handle image generation
        if "IMAGE_ACTION:" in response:
            actions_performed.extend(self._process_image_actions(response))

        return actions_performed

    def _process_file_actions(self, response):
        """Process FILE_ACTION commands"""
        actions_performed = []
        lines = response.split("\n")
        current_action = None
        current_filename = None
        current_content = []
        in_content = False
        in_code_block = False

        for line in lines:
            original_line = line
            line = line.strip()

            # Handle markdown code blocks for content
            if line.startswith("```") and in_content:
                if len(current_content) > 0:  # End of content block
                    content = "\n".join(current_content)
                    if current_action == "CREATE":
                        self.create_file(current_filename, content)
                        actions_performed.append(
                            f"Created file: {current_filename}"
                        )
                    elif current_action == "MODIFY":
                        self.modify_file(current_filename, content)
                        actions_performed.append(
                            f"Modified file: {current_filename}"
                        )
                    in_content = False
                    current_content = []
                else:  # Start of content block
                    continue
            elif in_content and not line.startswith("```"):
                current_content.append(
                    original_line
                )  # Keep original formatting for content
                continue

            # Strip markdown for command parsing
            clean_line = self._strip_markdown(line)

            if (
                "FILE_ACTION:" in clean_line.upper()
                or "FILE ACTION:" in clean_line.upper()
            ):
                action = self._extract_value_after_colon(clean_line).upper()
                current_action = action
            elif "FILENAME:" in clean_line.upper():
                current_filename = self._extract_value_after_colon(
                    clean_line
                ).strip("\"'`")

                # Handle READ action immediately when filename is provided
                if current_action == "READ" and current_filename:
                    content = self.read_file(current_filename)
                    if content is not None:
                        print(f"📖 Reading file: {current_filename}")
                        print("=" * 50)
                        print(content)
                        print("=" * 50)
                        # Return the read content as part of the action result
                        actions_performed.append(
                            {
                                "type": "read",
                                "filename": current_filename,
                                "content": content,
                                "message": f"Read file: {current_filename}",
                            }
                        )
                    else:
                        print(f"❌ File not found: {current_filename}")
                        actions_performed.append(
                            {
                                "type": "read_error",
                                "filename": current_filename,
                                "message": f"File not found: {current_filename}",
                            }
                        )
                    # Reset action state
                    current_action = None
                    current_filename = None

            elif "CONTENT:" in clean_line.upper():
                in_content = True
                current_content = []

        return actions_performed

    def _process_image_actions(self, response):
        """Process IMAGE_ACTION commands"""
        actions_performed = []
        lines = response.split("\n")

        # Collect all image requests first
        image_requests = []
        current_filename = None
        current_prompt = None
        current_style = ""
        in_image_action = False
        in_code_block = False

        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()

            # Handle markdown code blocks
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip processing if we're inside a code block (unless it's our special format)
            if in_code_block and not any(
                keyword in line
                for keyword in [
                    "IMAGE_ACTION:",
                    "FILENAME:",
                    "PROMPT:",
                    "STYLE:",
                ]
            ):
                continue

            # Strip markdown formatting from the line
            line = self._strip_markdown(line)

            if (
                "IMAGE_ACTION" in line.upper()
                or "IMAGE ACTION" in line.upper()
            ) and "GENERATE" in line.upper():
                # Reset for new image generation
                current_filename = None
                current_prompt = None
                current_style = ""
                in_image_action = True
                continue

            if in_image_action:
                if "FILENAME:" in line.upper():
                    current_filename = self._extract_value_after_colon(line)
                elif "PROMPT:" in line.upper():
                    current_prompt = self._extract_value_after_colon(line)
                elif "STYLE:" in line.upper():
                    current_style = self._extract_value_after_colon(line)

                # Check if this is the end of the image action block
                is_end_of_block = (
                    line == ""  # Empty line
                    or (i + 1 >= len(lines))  # End of response
                    or (
                        i + 1 < len(lines)
                        and any(
                            keyword in lines[i + 1].upper()
                            for keyword in [
                                "IMAGE_ACTION:",
                                "IMAGE ACTION:",
                                "FILE_ACTION:",
                                "FILE ACTION:",
                            ]
                        )
                    )  # Next action
                    or (
                        "STYLE:" in line.upper()
                        and (
                            i + 1 >= len(lines)
                            or not any(
                                keyword in lines[i + 1].upper()
                                for keyword in [
                                    "FILENAME:",
                                    "PROMPT:",
                                    "STYLE:",
                                ]
                            )
                        )
                    )  # End after STYLE
                )

                if is_end_of_block:
                    # End of this image action block - collect the request
                    if current_filename and current_prompt:
                        # Clean up the filename and prompt
                        current_filename = current_filename.strip("\"'`")
                        current_prompt = current_prompt.strip("\"'`")

                        output_path = self.project_dir / current_filename
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        image_requests.append(
                            {
                                "filename": current_filename,
                                "prompt": current_prompt,
                                "style": current_style.strip("\"'`")
                                if current_style
                                else "",
                                "output_path": str(output_path),
                            }
                        )

                    # Reset for next action
                    current_filename = None
                    current_prompt = None
                    current_style = ""
                    in_image_action = False

        # Process all images one by one
        for request in image_requests:
            print(f"🎨 Generating image: {request['filename']}")
            print(f"📝 Prompt: {request['prompt']}")
            print(f"🎭 Style: {request['style']}")

            success = (
                self.image_generator.generate_image_with_stable_diffusion(
                    request["prompt"], request["style"], request["output_path"]
                )
            )

            if success:
                self.project_files[request["filename"]] = "image_file"
                actions_performed.append(
                    f"✅ Generated image: {request['filename']}"
                )
            else:
                actions_performed.append(
                    f"❌ Failed to generate image: {request['filename']}"
                )

        return actions_performed

    def _strip_markdown(self, text):
        """Strip common markdown formatting from text"""
        import re

        # Remove bold/italic formatting
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # **bold**
        text = re.sub(r"\*(.*?)\*", r"\1", text)  # *italic*
        text = re.sub(r"__(.*?)__", r"\1", text)  # __bold__
        text = re.sub(r"_(.*?)_", r"\1", text)  # _italic_

        # Remove inline code formatting
        text = re.sub(r"`(.*?)`", r"\1", text)  # `code`

        # Remove list markers
        text = re.sub(r"^[-*+]\s+", "", text)  # - * + list items
        text = re.sub(r"^\d+\.\s+", "", text)  # 1. numbered lists

        return text.strip()

    def _extract_value_after_colon(self, line):
        """Extract the value after a colon, handling various formatting"""
        if ":" in line:
            value = line.split(":", 1)[1].strip()
            # Remove common markdown formatting
            value = value.strip("*_`\"'")
            return value
        return ""

    def create_file(self, filename, content):
        # Clean up the filename to prevent path issues
        filename = filename.strip()
        if filename.startswith("/"):
            filename = filename[1:]  # Remove leading slash
        if filename.startswith("\\"):
            filename = filename[1:]  # Remove leading backslash

        file_path = self.project_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.project_files[filename] = content
        print(f"✅ Created file: {filename}")

    def modify_file(self, filename, content):
        # Clean up the filename to prevent path issues
        filename = filename.strip()
        if filename.startswith("/"):
            filename = filename[1:]  # Remove leading slash
        if filename.startswith("\\"):
            filename = filename[1:]  # Remove leading backslash

        file_path = self.project_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.project_files[filename] = content
        print(f"✅ Modified file: {filename}")

    def read_file(self, filename):
        file_path = self.project_dir / filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.project_files[filename] = content
                return content
        return None

    def get_project_structure(self):
        """Get a summary of all project files"""
        structure = {}
        for root, dirs, files in os.walk(self.project_dir):
            for file in files:
                rel_path = os.path.relpath(
                    os.path.join(root, file), self.project_dir
                )
                structure[rel_path] = os.path.getsize(os.path.join(root, file))
        return structure

    def debug_action_detection(self, response):
        """Debug helper to show what actions are detected in a response"""
        print("\n🔍 DEBUG: Action Detection")
        print("=" * 40)
        lines = response.split("\n")

        for i, line in enumerate(lines):
            clean_line = self._strip_markdown(line.strip())

            detected_actions = []
            if (
                "FILE_ACTION:" in clean_line.upper()
                or "FILE ACTION:" in clean_line.upper()
            ):
                detected_actions.append("FILE_ACTION")
            if (
                "IMAGE_ACTION:" in clean_line.upper()
                or "IMAGE ACTION:" in clean_line.upper()
            ):
                detected_actions.append("IMAGE_ACTION")
            if "FILENAME:" in clean_line.upper():
                detected_actions.append("FILENAME")
            if "PROMPT:" in clean_line.upper():
                detected_actions.append("PROMPT")
            if "STYLE:" in clean_line.upper():
                detected_actions.append("STYLE")
            if "CONTENT:" in clean_line.upper():
                detected_actions.append("CONTENT")

            if detected_actions or line.strip().startswith("```"):
                print(
                    f"Line {i + 1:3d}: {detected_actions if detected_actions else ['CODE_BLOCK']} | {line[:80]}"
                )

        print("=" * 40)
