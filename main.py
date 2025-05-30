from ollama import chat, ChatResponse
import random
import os
import subprocess
import json
import base64
import requests
from pathlib import Path


class Agent:
    def __init__(
        self,
        name,
        personality,
        activation_triggers=None,
        can_write_files=False,
        can_generate_images=False,
    ):
        self.name = name
        self.personality = personality
        self.activation_triggers = activation_triggers or []
        self.can_write_files = can_write_files
        self.can_generate_images = can_generate_images
        self.messages = [
            {
                "role": "user",
                "content": f"Your name is {self.name} and your personality is {self.personality}. {self.get_file_instructions()}",
            }
        ]

    def get_file_instructions(self):
        instructions = ""
        if self.can_write_files:
            instructions += """When you need to create or modify files, use this format:
            
FILE_ACTION: CREATE
FILENAME: path/to/file.ext
CONTENT:
```
[file content here]
```

FILE_ACTION: MODIFY
FILENAME: path/to/file.ext
CHANGES: [describe what you're changing]
CONTENT:
```
[new file content here]
```

FILE_ACTION: RUN
COMMAND: [command to run]

Always use this exact format when working with files."""

        if self.can_generate_images:
            instructions += """

When you need to generate images, use this format:

IMAGE_ACTION: GENERATE
FILENAME: path/to/image.png
PROMPT: [detailed description of the image you want to generate]
STYLE: [optional style guidance like "photorealistic", "illustration", "minimalist", etc.]

Always be very descriptive in your prompts for better image generation."""

        return instructions

    def update_messages(self, name, message):
        self.messages.append({"role": name, "content": message})

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

        response: ChatResponse = chat(
            model="qwen3:8b",
            messages=self.messages
            + [{"role": name, "content": context_prompt}],
        )
        self.update_messages(name, prompt)
        self.update_messages(self.name, response.message.content)

        return response.message.content

    def should_activate(self, context):
        """Check if this agent should respond based on current context"""
        return any(
            trigger in context.get("phase", "")
            or trigger in context.get("keywords", [])
            or trigger in context.get("last_message", "")
            for trigger in self.activation_triggers
        )


class ImageGenerator:
    def __init__(self):
        # Try different local API endpoints - ComfyUI first
        self.api_endpoints = {
            "comfyui": "http://127.0.0.1:8188/api/v1/generate",
            "automatic1111": "http://127.0.0.1:7860/api/v1/txt2img",
            "ollama": "http://127.0.0.1:11434/api/generate",
        }
        self.active_endpoint = None
        self.model_loaded = False
        self._detect_available_api()

    def _detect_available_api(self):
        """Detect which local SD API is running"""
        for name, url in self.api_endpoints.items():
            try:
                if name == "comfyui":
                    # ComfyUI health check endpoint
                    response = requests.get(
                        "http://127.0.0.1:8188/", timeout=2
                    )
                elif name == "automatic1111":
                    response = requests.get(
                        "http://127.0.0.1:7860/", timeout=2
                    )
                else:
                    response = requests.get(
                        url.replace("/api/generate", "/"), timeout=2
                    )

                if response.status_code == 200:
                    self.active_endpoint = name
                    print(f"✅ Detected {name} running at {url}")
                    return
            except:
                continue
        print("🔍 No local SD API detected, using placeholder generation")

    def _load_comfyui_model(self):
        """Load model into VRAM for ComfyUI"""
        try:
            if self.active_endpoint == "comfyui" and not self.model_loaded:
                print("🔄 Loading ComfyUI model into VRAM...")

                # Get VRAM usage before loading
                vram_before = self._get_vram_usage()
                if vram_before:
                    print(
                        f"📊 VRAM before: {vram_before['vram_free_gb']:.1f}GB free / {vram_before['vram_total_gb']:.1f}GB total"
                    )

                # Check if ComfyUI is ready and has models available
                try:
                    # Get available checkpoints
                    response = requests.get(
                        "http://127.0.0.1:8188/object_info/CheckpointLoaderSimple",
                        timeout=10,
                    )

                    if response.status_code == 200:
                        object_info = response.json()
                        if (
                            "input" in object_info
                            and "required" in object_info["input"]
                        ):
                            available_models = object_info["input"][
                                "required"
                            ].get("ckpt_name", [])
                            if (
                                isinstance(available_models, list)
                                and len(available_models) > 0
                            ):
                                # Use the first available model
                                model_name = (
                                    available_models[0][0]
                                    if available_models[0]
                                    else "sd_xl_base_1.0.safetensors"
                                )
                                print(f"📦 Using model: {model_name}")

                                # Model will be loaded during first generation
                                self.model_loaded = True
                                print("✅ Model ready for generation")
                                return True
                            else:
                                print("⚠️ No models found in ComfyUI")
                                return False
                    else:
                        print(
                            f"⚠️ ComfyUI object_info failed: {response.status_code}"
                        )
                        # Assume model is available and continue
                        self.model_loaded = True
                        return True

                except Exception as e:
                    print(f"⚠️ Model check error: {e}")
                    # Assume model is available and continue
                    self.model_loaded = True
                    return True

        except Exception as e:
            print(f"⚠️ Model loading error: {e}")
            return False
        return True

    def _unload_comfyui_model(self):
        """Unload model from VRAM for ComfyUI"""
        try:
            if self.active_endpoint == "comfyui" and self.model_loaded:
                print("🔄 Unloading ComfyUI model from VRAM...")

                # Get VRAM usage before unloading
                vram_before = self._get_vram_usage()

                # Send free memory request to ComfyUI
                try:
                    response = requests.post(
                        "http://127.0.0.1:8188/free",
                        json={"unload_models": True, "free_memory": True},
                        timeout=10,
                    )

                    if response.status_code == 200:
                        # Wait a moment for the unloading to complete
                        import time

                        time.sleep(1)

                        # Check VRAM usage after unloading
                        vram_after = self._get_vram_usage()

                        self.model_loaded = False

                        if vram_before and vram_after:
                            freed_mb = (
                                vram_after["vram_free"]
                                - vram_before["vram_free"]
                            ) / (1024 * 1024)
                            print(
                                f"✅ Model unloaded, freed {freed_mb:.0f}MB VRAM"
                            )
                            print(
                                f"📊 VRAM: {vram_after['vram_free_gb']:.1f}GB free / {vram_after['vram_total_gb']:.1f}GB total"
                            )
                        else:
                            print("✅ Model unloaded successfully")
                        return True
                    else:
                        # Even if the API call fails, mark as unloaded
                        self.model_loaded = False
                        print("✅ Model marked as unloaded")
                        return True

                except Exception as e:
                    print(f"⚠️ Unload API error: {e}")
                    # Mark as unloaded anyway
                    self.model_loaded = False
                    print("✅ Model marked as unloaded")
                    return True

        except Exception as e:
            print(f"⚠️ Model unloading error: {e}")
            return False
        return True

    def _get_vram_usage(self):
        """Get current VRAM usage from ComfyUI"""
        try:
            response = requests.get(
                "http://127.0.0.1:8188/system_stats", timeout=5
            )
            if response.status_code == 200:
                stats = response.json()
                if "devices" in stats and len(stats["devices"]) > 0:
                    device = stats["devices"][0]  # First GPU
                    return {
                        "vram_total": device["vram_total"],
                        "vram_free": device["vram_free"],
                        "vram_total_gb": device["vram_total"]
                        / (1024 * 1024 * 1024),
                        "vram_free_gb": device["vram_free"]
                        / (1024 * 1024 * 1024),
                        "vram_used_gb": (
                            device["vram_total"] - device["vram_free"]
                        )
                        / (1024 * 1024 * 1024),
                    }
        except:
            pass
        return None

    def generate_image_with_stable_diffusion(
        self, prompt, style="", output_path=""
    ):
        """Generate image using Stable Diffusion via local API or fallback methods"""
        try:
            # Try local SD APIs first
            if self.active_endpoint:
                # Load model if needed (for ComfyUI)
                if self.active_endpoint == "comfyui":
                    if not self._load_comfyui_model():
                        print("⚠️ Failed to load model, using fallback")
                        return self._generate_placeholder_image(
                            prompt, style, output_path
                        )

                success = self._try_local_sd_api(prompt, style, output_path)

                # Unload model after generation (for ComfyUI)
                if self.active_endpoint == "comfyui":
                    self._unload_comfyui_model()

                if success:
                    return True

            # Fallback to placeholder images
            return self._generate_placeholder_image(prompt, style, output_path)

        except Exception as e:
            print(f"Image generation failed: {e}")
            # Make sure to unload model even if there's an error
            if self.active_endpoint == "comfyui":
                self._unload_comfyui_model()
            return self._generate_placeholder_image(prompt, style, output_path)

    def _try_local_sd_api(self, prompt, style, output_path):
        """Try to connect to local Stable Diffusion API"""
        try:
            if self.active_endpoint == "comfyui":
                return self._comfyui_generate(prompt, style, output_path)
            elif self.active_endpoint == "automatic1111":
                return self._a1111_generate(prompt, style, output_path)
            elif self.active_endpoint == "ollama":
                return self._ollama_generate(prompt, style, output_path)
        except Exception as e:
            print(f"Local API failed: {e}")
            return False

    def _comfyui_generate(self, prompt, style, output_path):
        """Generate image using ComfyUI API"""
        try:
            full_prompt = f"{prompt}, {style}" if style else prompt

            # Get available models first
            model_name = "sd_xl_base_1.0.safetensors"  # Default
            try:
                response = requests.get(
                    "http://127.0.0.1:8188/object_info/CheckpointLoaderSimple",
                    timeout=5,
                )
                if response.status_code == 200:
                    object_info = response.json()
                    if (
                        "input" in object_info
                        and "required" in object_info["input"]
                    ):
                        available_models = object_info["input"][
                            "required"
                        ].get("ckpt_name", [])
                        if (
                            isinstance(available_models, list)
                            and len(available_models) > 0
                        ):
                            model_name = (
                                available_models[0][0]
                                if available_models[0]
                                else model_name
                            )
                            print(f"📦 Using model: {model_name}")
            except:
                print(f"📦 Using default model: {model_name}")

            # ComfyUI workflow for text-to-image generation
            workflow = {
                "3": {
                    "inputs": {
                        "seed": random.randint(1, 1000000),
                        "steps": 25,
                        "cfg": 7.0,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": 1.0,
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0],
                    },
                    "class_type": "KSampler",
                },
                "4": {
                    "inputs": {
                        "ckpt_name": model_name  # Use detected model
                    },
                    "class_type": "CheckpointLoaderSimple",
                },
                "5": {
                    "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
                    "class_type": "EmptyLatentImage",
                },
                "6": {
                    "inputs": {"text": full_prompt, "clip": ["4", 1]},
                    "class_type": "CLIPTextEncode",
                },
                "7": {
                    "inputs": {
                        "text": "low quality, blurry, distorted, ugly, bad anatomy",
                        "clip": ["4", 1],
                    },
                    "class_type": "CLIPTextEncode",
                },
                "8": {
                    "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
                    "class_type": "VAEDecode",
                },
                "9": {
                    "inputs": {
                        "filename_prefix": "ComfyUI",
                        "images": ["8", 0],
                    },
                    "class_type": "SaveImage",
                },
            }

            # Submit the workflow
            response = requests.post(
                "http://127.0.0.1:8188/prompt",
                json={"prompt": workflow},
                timeout=120,
            )

            if response.status_code == 200:
                result = response.json()
                prompt_id = result.get("prompt_id")

                if prompt_id:
                    # Poll for completion
                    import time

                    for _ in range(60):  # Wait up to 60 seconds
                        time.sleep(1)

                        # Check if generation is complete
                        history_response = requests.get(
                            f"http://127.0.0.1:8188/history/{prompt_id}",
                            timeout=5,
                        )

                        if history_response.status_code == 200:
                            history = history_response.json()
                            if (
                                prompt_id in history
                                and "outputs" in history[prompt_id]
                            ):
                                outputs = history[prompt_id]["outputs"]
                                if "9" in outputs and "images" in outputs["9"]:
                                    # Get the generated image
                                    image_info = outputs["9"]["images"][0]
                                    filename = image_info["filename"]

                                    # Download the image from ComfyUI
                                    image_response = requests.get(
                                        f"http://127.0.0.1:8188/view?filename={filename}",
                                        timeout=30,
                                    )

                                    if image_response.status_code == 200:
                                        with open(output_path, "wb") as f:
                                            f.write(image_response.content)
                                        print(
                                            "✅ ComfyUI generated image successfully"
                                        )
                                        return True

                    print("⚠️ ComfyUI generation timed out")
                    return False
                else:
                    print("❌ ComfyUI didn't return a prompt ID")
                    return False
            else:
                print(f"❌ ComfyUI API error: {response.status_code}")
                return False

        except Exception as e:
            print(f"ComfyUI generation failed: {e}")
            return False

    def _a1111_generate(self, prompt, style, output_path):
        """Generate image using Automatic1111 API"""
        try:
            full_prompt = f"{prompt}, {style}" if style else prompt

            payload = {
                "prompt": full_prompt,
                "negative_prompt": "low quality, blurry, distorted",
                "width": 1024,
                "height": 1024,
                "steps": 30,
                "cfg_scale": 7.0,
                "sampler_name": "Euler a",
            }

            response = requests.post(
                "http://127.0.0.1:7860/api/v1/txt2img",
                json=payload,
                timeout=120,
            )

            if response.status_code == 200:
                result = response.json()
                if "images" in result and result["images"]:
                    # Decode base64 image and save
                    import base64
                    from PIL import Image
                    import io

                    image_data = base64.b64decode(result["images"][0])
                    image = Image.open(io.BytesIO(image_data))
                    image.save(output_path)
                    print("✅ Automatic1111 generated image successfully")
                    return True

        except Exception as e:
            print(f"Automatic1111 generation failed: {e}")
            return False

    def _ollama_generate(self, prompt, style, output_path):
        """Generate image description using Ollama (text-based)"""
        try:
            # Ollama doesn't generate images directly, but we can use it for enhanced descriptions
            full_prompt = f"Create a detailed visual description for an AI image generator: {prompt}"
            if style:
                full_prompt += f" in {style} style"

            response = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "llava",
                    "prompt": full_prompt,
                    "stream": False,
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                enhanced_description = result.get("response", prompt)
                # Use enhanced description for placeholder generation
                return self._generate_placeholder_image(
                    enhanced_description, style, output_path
                )

        except Exception as e:
            print(f"Ollama enhancement failed: {e}")
            return False

    def _generate_placeholder_image(self, prompt, style, output_path):
        """Generate a placeholder image with the prompt as text"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            # Create a 800x600 image with a nice gradient background
            width, height = 800, 600
            image = Image.new("RGB", (width, height), "#f0f0f0")
            draw = ImageDraw.Draw(image)

            # Create gradient background
            for y in range(height):
                color_value = int(
                    240 - (y / height) * 40
                )  # Gradient from light to slightly darker
                color = (color_value, color_value + 10, color_value + 20)
                draw.line([(0, y), (width, y)], fill=color)

            # Add text
            try:
                # Try to use a nice font
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 16)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Wrap text
            lines = self._wrap_text(prompt, 50)

            # Calculate text positioning
            total_text_height = len(lines) * 30 + 60
            start_y = (height - total_text_height) // 2

            # Draw main prompt
            y_offset = start_y
            for line in lines:
                text_width = draw.textlength(line, font=font_large)
                x = (width - text_width) // 2
                draw.text((x, y_offset), line, fill="#333333", font=font_large)
                y_offset += 30

            # Add style info if provided
            if style:
                style_text = f"Style: {style}"
                text_width = draw.textlength(style_text, font=font_small)
                x = (width - text_width) // 2
                draw.text(
                    (x, y_offset + 20),
                    style_text,
                    fill="#666666",
                    font=font_small,
                )

            # Add a decorative border
            draw.rectangle(
                [10, 10, width - 10, height - 10], outline="#cccccc", width=2
            )

            # Save the image
            image.save(output_path)
            return True

        except Exception as e:
            print(f"Placeholder generation failed: {e}")
            # Create a simple colored rectangle as absolute fallback
            try:
                from PIL import Image

                img = Image.new("RGB", (800, 600), "#e0e0e0")
                img.save(output_path)
                return True
            except:
                return False

    def _wrap_text(self, text, width):
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def generate_batch_images(self, image_requests):
        """Generate multiple images efficiently by keeping model loaded"""
        if not image_requests:
            return []

        results = []
        model_was_loaded = False

        try:
            # Load model once for batch processing
            if self.active_endpoint == "comfyui":
                model_was_loaded = self._load_comfyui_model()
                if not model_was_loaded:
                    print("⚠️ Failed to load model for batch processing")

            # Generate all images
            for request in image_requests:
                prompt = request.get("prompt", "")
                style = request.get("style", "")
                output_path = request.get("output_path", "")

                if self.active_endpoint and model_was_loaded:
                    success = self._try_local_sd_api(
                        prompt, style, output_path
                    )
                else:
                    success = self._generate_placeholder_image(
                        prompt, style, output_path
                    )

                results.append(
                    {
                        "output_path": output_path,
                        "success": success,
                        "prompt": prompt,
                    }
                )

        except Exception as e:
            print(f"Batch generation error: {e}")
        finally:
            # Unload model after batch processing
            if self.active_endpoint == "comfyui" and model_was_loaded:
                self._unload_comfyui_model()

        return results

    def load_model_manually(self):
        """Manually load model into VRAM (useful for multiple generations)"""
        if self.active_endpoint == "comfyui":
            return self._load_comfyui_model()
        return True

    def unload_model_manually(self):
        """Manually unload model from VRAM to free memory"""
        if self.active_endpoint == "comfyui":
            return self._unload_comfyui_model()
        return True

    def get_model_status(self):
        """Check if model is currently loaded"""
        vram_info = self._get_vram_usage()
        status = {
            "active_endpoint": self.active_endpoint,
            "model_loaded": self.model_loaded,
            "vram_usage": "loaded" if self.model_loaded else "free",
        }

        if vram_info:
            status.update(
                {
                    "vram_total_gb": vram_info["vram_total_gb"],
                    "vram_free_gb": vram_info["vram_free_gb"],
                    "vram_used_gb": vram_info["vram_used_gb"],
                    "vram_usage_percent": (
                        vram_info["vram_used_gb"] / vram_info["vram_total_gb"]
                    )
                    * 100,
                }
            )

        return status

    def model_context(self):
        """Context manager for automatic model loading/unloading"""
        return ModelContext(self)

    def force_unload_all_models(self):
        """Force unload all models from VRAM, regardless of tracking state"""
        if self.active_endpoint == "comfyui":
            print("🔄 Force unloading ALL models from VRAM...")

            # Get VRAM usage before unloading
            vram_before = self._get_vram_usage()
            if vram_before:
                print(
                    f"📊 VRAM before: {vram_before['vram_free_gb']:.1f}GB free / {vram_before['vram_total_gb']:.1f}GB total"
                )

            try:
                response = requests.post(
                    "http://127.0.0.1:8188/free",
                    json={"unload_models": True, "free_memory": True},
                    timeout=10,
                )

                if response.status_code == 200:
                    # Wait for unloading to complete
                    import time

                    time.sleep(2)

                    # Check VRAM usage after unloading
                    vram_after = self._get_vram_usage()

                    self.model_loaded = False

                    if vram_before and vram_after:
                        freed_mb = (
                            vram_after["vram_free"] - vram_before["vram_free"]
                        ) / (1024 * 1024)
                        print(
                            f"✅ ALL models unloaded, freed {freed_mb:.0f}MB VRAM"
                        )
                        print(
                            f"📊 VRAM after: {vram_after['vram_free_gb']:.1f}GB free / {vram_after['vram_total_gb']:.1f}GB total"
                        )
                    else:
                        print("✅ ALL models unloaded successfully")
                    return True
                else:
                    print(f"❌ Force unload failed: {response.status_code}")
                    return False

            except Exception as e:
                print(f"❌ Force unload error: {e}")
                return False
        else:
            print("⚠️ ComfyUI not detected, cannot force unload")
            return False


class ModelContext:
    """Context manager for automatic model management"""

    def __init__(self, image_generator):
        self.image_generator = image_generator
        self.was_loaded = False

    def __enter__(self):
        if self.image_generator.active_endpoint == "comfyui":
            self.was_loaded = self.image_generator.model_loaded
            if not self.was_loaded:
                self.image_generator._load_comfyui_model()
        return self.image_generator

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (
            self.image_generator.active_endpoint == "comfyui"
            and not self.was_loaded
            and self.image_generator.model_loaded
        ):
            self.image_generator._unload_comfyui_model()


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

        # Process images - use batch if multiple, single if just one
        if len(image_requests) > 1:
            print(f"🎨 Batch generating {len(image_requests)} images...")
            results = self.image_generator.generate_batch_images(
                image_requests
            )

            for result in results:
                filename = next(
                    req["filename"]
                    for req in image_requests
                    if req["output_path"] == result["output_path"]
                )
                if result["success"]:
                    self.project_files[filename] = "image_file"
                    actions_performed.append(f"✅ Generated image: {filename}")
                else:
                    actions_performed.append(
                        f"❌ Failed to generate image: {filename}"
                    )

        elif len(image_requests) == 1:
            # Single image generation
            request = image_requests[0]
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


class ConversationManager:
    def __init__(self, agents):
        self.agents = agents
        self.conversation_history = []
        self.current_phase = "planning"
        self.project_context = {
            "satisfaction_level": 0.7,
            "deadline_pressure": 0.3,
            "bugs_found": 0,
            "stuck_count": 0,
        }
        self.file_manager = FileManager()

    def determine_active_agents(self, context):
        """Determine which agents should participate based on context"""
        active_agents = []

        for agent in self.agents:
            if agent.should_activate(context):
                active_agents.append(agent)

        # Always include manager if multiple agents are active (to facilitate)
        if (
            len(active_agents) > 2 and self.agents[5] not in active_agents
        ):  # manager
            active_agents.append(self.agents[5])

        # Special conditions
        if self.project_context["stuck_count"] > 2:
            # Bring in rubber duck for problem solving
            if self.agents[6] not in active_agents:  # rubber duck
                active_agents.append(self.agents[6])

        if self.project_context["satisfaction_level"] < 0.4:
            # Crisis mode - bring in boss
            if self.agents[1] not in active_agents:  # boss
                active_agents.append(self.agents[1])

        return active_agents[:3]  # Limit to 3 agents max per round

    def run_conversation_round(self, initial_prompt, max_exchanges=3):
        """Run one round of conversation with relevant agents"""

        # Determine context from the prompt
        context = self.analyze_context(initial_prompt)
        active_agents = self.determine_active_agents(context)

        print(f"\n--- {context['phase'].upper()} PHASE ---")
        print(f"Active agents: {[agent.name for agent in active_agents]}")
        print(f"Project files: {list(self.file_manager.project_files.keys())}")
        print("-" * 50)

        current_message = initial_prompt

        for round_num in range(max_exchanges):
            for agent in active_agents:
                print(f"\n{agent.name}: ", end="")
                response = agent.get_response(
                    "user", current_message, self.file_manager.project_files
                )
                print(response)

                # Process any file operations
                if agent.can_write_files:
                    actions = self.file_manager.process_agent_response(
                        response
                    )
                    for action in actions:
                        print(f"🔧 {action}")

                # Update context based on response
                self.update_context_from_response(agent.name, response)
                current_message = response

                # Check if we need to change active agents mid-conversation
                if self.should_change_agents(response):
                    break

            # Check if conversation should continue
            if self.should_end_round(current_message):
                break

    def analyze_context(self, message):
        """Analyze the message to determine context and phase"""
        message_lower = message.lower()

        # Determine phase
        if any(
            word in message_lower
            for word in ["design", "mockup", "ui", "layout"]
        ):
            phase = "design"
        elif any(
            word in message_lower
            for word in ["code", "develop", "implement", "feature"]
        ):
            phase = "development"
        elif any(
            word in message_lower for word in ["test", "bug", "qa", "quality"]
        ):
            phase = "testing"
        elif any(
            word in message_lower
            for word in ["requirements", "spec", "need", "want"]
        ):
            phase = "planning"
        elif any(
            word in message_lower for word in ["review", "feedback", "check"]
        ):
            phase = "review"
        else:
            phase = self.current_phase

        # Extract keywords
        keywords = [
            word
            for word in message_lower.split()
            if word
            in ["urgent", "deadline", "stuck", "help", "problem", "bug"]
        ]

        return {
            "phase": phase,
            "keywords": keywords,
            "last_message": message,
            "project_context": self.project_context,
        }

    def update_context_from_response(self, agent_name, response):
        """Update project context based on agent responses"""
        response_lower = response.lower()

        if "stuck" in response_lower or "problem" in response_lower:
            self.project_context["stuck_count"] += 1
        elif "solved" in response_lower or "fixed" in response_lower:
            self.project_context["stuck_count"] = max(
                0, self.project_context["stuck_count"] - 1
            )

        if agent_name == "Client":
            if any(
                word in response_lower
                for word in ["good", "great", "perfect", "love"]
            ):
                self.project_context["satisfaction_level"] = min(
                    1.0, self.project_context["satisfaction_level"] + 0.1
                )
            elif any(
                word in response_lower
                for word in ["bad", "terrible", "hate", "wrong"]
            ):
                self.project_context["satisfaction_level"] = max(
                    0.0, self.project_context["satisfaction_level"] - 0.2
                )

    def should_change_agents(self, response):
        """Check if we need different agents based on the response"""
        return (
            "need designer" in response.lower()
            or "call the manager" in response.lower()
            or "get qa" in response.lower()
        )

    def should_end_round(self, message):
        """Determine if this conversation round should end"""
        return any(
            phrase in message.lower()
            for phrase in [
                "that sounds good",
                "agreed",
                "let's move forward",
                "next step",
            ]
        )

    def show_project_status(self):
        """Show current project files and structure"""
        print("\n=== PROJECT STATUS ===")
        structure = self.file_manager.get_project_structure()
        for file_path, size in structure.items():
            print(f"📄 {file_path} ({size} bytes)")
        print("=" * 23)


# Create agents with specific activation triggers
agent1 = Agent(
    "Developer",
    "You develop a website for a company. When you need to create or modify files, use the FILE_ACTION format exactly as instructed. Create actual HTML, CSS, and JavaScript files that work together to build the website.",
    activation_triggers=[
        "development",
        "code",
        "implement",
        "feature",
        "stuck",
        "technical",
    ],
    can_write_files=True,
)

agent2 = Agent(
    "Boss",
    "You are the boss of the company that the developer works for. You watch over the developer and give them feedback on the website.",
    activation_triggers=["deadline", "budget", "urgent", "crisis", "review"],
)

agent3 = Agent(
    "Client",
    "You are the client of the company that wants a website for their business. You decide the overall design of the website and the features that the website will have.",
    activation_triggers=[
        "planning",
        "requirements",
        "design",
        "review",
        "feedback",
    ],
)

agent4 = Agent(
    "Designer",
    "You are the designer of the company that the developer works for. You design the website and give the developer the design. When giving design specifications, be specific about colors, layouts, and styling. You can also generate images for the website using the IMAGE_ACTION format. Create beautiful, professional images that match the website's theme. ALWAYS use IMAGE_ACTION: GENERATE when the client or other agents request actual images to be created. Use the exact format: IMAGE_ACTION: GENERATE, FILENAME: path/to/image.png, PROMPT: detailed description, STYLE: style description.",
    activation_triggers=[
        "design",
        "ui",
        "mockup",
        "layout",
        "visual",
        "images",
        "graphics",
        "generate",
        "create images",
        "actual images",
        "professional images",
    ],
    can_write_files=True,
    can_generate_images=True,
)

agent5 = Agent(
    "QA",
    "You are the QA of the company that the developer works for. You test the website and give the developer feedback on the website. You can run commands to test functionality.",
    activation_triggers=["testing", "qa", "bug", "quality", "test"],
    can_write_files=True,
)

agent6 = Agent(
    "Manager",
    "You are the manager of the company that the developer works for. You manage the other agents and the developer.",
    activation_triggers=["planning", "coordination", "meeting", "organize"],
)

agent7 = Agent(
    "Rubber duck",
    "When the client is unhappy you get bonked on the head and say quack quack.",
    activation_triggers=["stuck", "problem", "help", "frustrated"],
)

# Create conversation manager
agents = [agent1, agent2, agent3, agent4, agent5, agent6, agent7]
conversation_manager = ConversationManager(agents)

# Example usage:
if __name__ == "__main__":
    # Different scenarios that would activate different agents

    print("=== SCENARIO 1: Client wants to discuss requirements ===")
    conversation_manager.run_conversation_round(
        "I need a website for my bakery business. I want customers to be able to order cakes online and I want the style to be based of italian brainrot."
    )

    conversation_manager.show_project_status()

    print("\n=== SCENARIO 2: Developer implements the basic structure ===")
    conversation_manager.run_conversation_round(
        "Let's start implementing the bakery website. Create the basic HTML structure with a homepage."
    )

    conversation_manager.show_project_status()

    print("\n=== SCENARIO 3: Designer creates images and improves visuals ===")
    conversation_manager.run_conversation_round(
        "We need actual images for the bakery website. Generate hero images and product photos that look professional."
    )
