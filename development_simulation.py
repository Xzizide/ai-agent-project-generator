from agents import Agent
from conversation_manager import ConversationManager


class DevelopmentSimulation:
    def __init__(self, project_name):
        self.project_name = project_name
        self.developer = Agent(
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
        self.client = Agent(
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
        self.designer = Agent(
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
        self.qa = Agent(
            "QA",
            "You are the QA of the company that the developer works for. You test the website and give the developer feedback on the website. You can run commands to test functionality.",
            activation_triggers=["testing", "qa", "bug", "quality", "test"],
            can_write_files=True,
        )
        self.manager = Agent(
            "Manager",
            "You are the manager of the company that the developer works for. You manage the other agents and the developer.",
            activation_triggers=[
                "planning",
                "coordination",
                "meeting",
                "organize",
            ],
        )

        self.agents = [
            self.developer,
            self.client,
            self.designer,
            self.qa,
            self.manager,
        ]
        self.conversation_manager = ConversationManager(
            self.agents, project_name
        )

    def first_runthrough(self, prompt):
        print(f"=== STARTING PROJECT: {self.project_name} ===")
        print("=== SCENARIO 1: Client wants to discuss requirements ===")
        self.conversation_manager.run_conversation_round(prompt)

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 2: Developer implements the basic structure ===")
        self.conversation_manager.run_conversation_round(
            "Let's start implementing the website. Create the basic HTML structure with a homepage."
        )

        self.conversation_manager.show_project_status()

        print(
            "\n=== SCENARIO 3: Designer creates images and improves visuals ==="
        )
        self.conversation_manager.run_conversation_round(
            "We need actual images for the website. Generate hero images and product photos that look professional."
        )

        self.conversation_manager.show_project_status()

        print(
            "\n=== SCENARIO 4: Developer implements the newly made images ==="
        )
        self.conversation_manager.run_conversation_round(
            "Additional images have been made. I need to them to be implemented into the website with additional css, javascript and functionality."
        )
