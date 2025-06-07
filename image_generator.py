import random
import requests
from PIL import Image, ImageDraw, ImageFont


class ImageGenerator:
    def __init__(self):
        self.comfyui_available = self._check_comfyui()

    def _check_comfyui(self):
        """Check if ComfyUI is running"""
        try:
            response = requests.get("http://127.0.0.1:8188/", timeout=2)
            if response.status_code == 200:
                print("✅ ComfyUI detected and ready")
                return True
        except Exception:
            print("⚠️ ComfyUI not detected, will use placeholder images")
        return False

    def generate_image_with_stable_diffusion(
        self, prompt, style="", output_path=""
    ):
        """Generate image using ComfyUI or fallback to placeholder"""
        try:
            if self.comfyui_available:
                success = self._comfyui_generate(prompt, style, output_path)
                if success:
                    return True

            # Fallback to placeholder images
            return self._generate_placeholder_image(prompt, style, output_path)

        except Exception as e:
            print(f"Image generation failed: {e}")
            return self._generate_placeholder_image(prompt, style, output_path)

    def _comfyui_generate(self, prompt, style, output_path):
        """Generate image using ComfyUI API"""
        try:
            full_prompt = f"{prompt}, {style}" if style else prompt

            # Get available models
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
                        "sampler_name": "dpmpp_sde_gpu",
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
                    "inputs": {"ckpt_name": model_name},
                    "class_type": "CheckpointLoaderSimple",
                },
                "5": {
                    "inputs": {"width": 800, "height": 600, "batch_size": 1},
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

                    for _ in range(180):  # Wait up to 180 seconds
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

    def _generate_placeholder_image(self, prompt, style, output_path):
        """Generate a placeholder image with the prompt as text"""
        try:
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
