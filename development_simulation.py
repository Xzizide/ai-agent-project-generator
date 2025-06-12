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

    def project_creation(self, prompt):
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

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 5: QA tests the website ===")
        self.conversation_manager.run_conversation_round(
            "Test the website functionality, verify the page displays properly, and ensure it works as expected."
        )

        self.conversation_manager.show_project_status()

        print(
            "\n=== SCENARIO 6: Developer updates website after QA feedback ==="
        )
        self.conversation_manager.run_conversation_round(
            "Update the website based on QA feedback. Make sure all functionality works correctly and the website is visually appealing."
        )

        self.conversation_manager.show_project_status()
        self.conversation_manager.reset_all_agents()

    def add_new_page(self, page_request):
        print(f"=== ADDING NEW PAGE TO PROJECT: {self.project_name} ===")
        print("=== SCENARIO 1: Client specifies new page requirements ===")
        self.conversation_manager.run_conversation_round(page_request)

        self.conversation_manager.show_project_status()

        print(
            "\n=== SCENARIO 2: Designer creates layout and visual design for new page ==="
        )
        self.conversation_manager.run_conversation_round(
            "Design the layout and visual elements for this new page. Consider how it fits with the existing website design and create any necessary images or graphics."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 3: Developer creates the new page ===")
        self.conversation_manager.run_conversation_round(
            "Create the new page with proper HTML structure, CSS styling, and any necessary JavaScript functionality. Make sure it matches the existing website's design and structure."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 4: Developer updates navigation and links ===")
        self.conversation_manager.run_conversation_round(
            "Update all existing pages to include navigation links to the new page. Add appropriate <a> tags, update navigation menus, and ensure the new page is properly integrated into the website structure."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 5: QA tests the new page and navigation ===")
        self.conversation_manager.run_conversation_round(
            "Test the new page functionality, check that all navigation links work correctly, verify the page displays properly, and ensure it integrates well with the existing website."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 6: Developer updates page after QA feedback ===")
        self.conversation_manager.run_conversation_round(
            "Update the new page based on QA feedback. Make sure all functionality works correctly and the page is visually appealing."
        )

        self.conversation_manager.show_project_status()
        self.conversation_manager.reset_all_agents()

    def improve_existing_page(self, improvement_request):
        print(
            f"=== IMPROVING EXISTING PAGE IN PROJECT: {self.project_name} ==="
        )
        print(
            "=== SCENARIO 1: Client specifies page improvement requirements ==="
        )
        self.conversation_manager.run_conversation_round(improvement_request)

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 2: Designer reviews and updates page design ===")
        self.conversation_manager.run_conversation_round(
            "Review the existing page and create an improved design. Update the visual elements, layout, and styling. Generate any new images or graphics if needed to enhance the page."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 3: Developer implements page improvements ===")
        self.conversation_manager.run_conversation_round(
            "Implement the page improvements. Update the HTML structure, CSS styling, and JavaScript functionality as needed. Ensure the improvements enhance user experience while maintaining consistency with the overall website design."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 4: QA tests the improved page ===")
        self.conversation_manager.run_conversation_round(
            "Test the improved page thoroughly. Verify all functionality works correctly, check that the improvements meet the requirements, and ensure the page still integrates well with the rest of the website."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 5: Developer makes final adjustments ===")
        self.conversation_manager.run_conversation_round(
            "Make final adjustments to the improved page based on QA feedback. Polish any remaining issues and ensure the page meets all quality standards."
        )

        self.conversation_manager.show_project_status()
        self.conversation_manager.reset_all_agents()
