import os
import subprocess
from pathlib import Path
from image_generator import ImageGenerator


class FileManager:
    def __init__(self, project_dir="website_project"):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(exist_ok=True)
        self.project_files = {}
        self.image_generator = ImageGenerator()

        # Create images directory
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

        for line in lines:
            if line.startswith("FILE_ACTION:"):
                action = line.split(":", 1)[1].strip()
                current_action = action
            elif line.startswith("FILENAME:"):
                current_filename = line.split(":", 1)[1].strip()
            elif line.startswith("COMMAND:"):
                command = line.split(":", 1)[1].strip()
                if current_action == "RUN":
                    result = self.run_command(command)
                    actions_performed.append(
                        f"Ran command: {command}\nResult: {result}"
                    )
            elif line.startswith("CONTENT:"):
                in_content = True
                current_content = []
            elif line.startswith("```") and in_content:
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
                else:  # Start of content block
                    continue
            elif in_content and not line.startswith("```"):
                current_content.append(line)

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

        for i, line in enumerate(lines):
            line = line.strip()

            if line.startswith("IMAGE_ACTION:") and "GENERATE" in line:
                # Reset for new image generation
                current_filename = None
                current_prompt = None
                current_style = ""
                in_image_action = True
                continue

            if in_image_action:
                if line.startswith("FILENAME:"):
                    current_filename = line.split(":", 1)[1].strip()
                elif line.startswith("PROMPT:"):
                    current_prompt = line.split(":", 1)[1].strip()
                elif line.startswith("STYLE:"):
                    current_style = line.split(":", 1)[1].strip()

                # Check if this is the end of the image action block
                is_end_of_block = (
                    line == ""  # Empty line
                    or (i + 1 >= len(lines))  # End of response
                    or (
                        i + 1 < len(lines)
                        and lines[i + 1]
                        .strip()
                        .startswith(("IMAGE_ACTION:", "FILE_ACTION:"))
                    )  # Next action
                    or (
                        line.startswith("STYLE:")
                        and (
                            i + 1 >= len(lines)
                            or not lines[i + 1]
                            .strip()
                            .startswith(("FILENAME:", "PROMPT:", "STYLE:"))
                        )
                    )  # End after STYLE
                )

                if is_end_of_block:
                    # End of this image action block - collect the request
                    if current_filename and current_prompt:
                        output_path = self.project_dir / current_filename
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        image_requests.append(
                            {
                                "filename": current_filename,
                                "prompt": current_prompt,
                                "style": current_style,
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

    def run_command(self, command):
        try:
            # Change to project directory for commands
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return f"Exit code: {result.returncode}\nOutput: {result.stdout}\nError: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error running command: {str(e)}"

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
