from agents import Agent
from conversation_manager import ConversationManager


class DevelopmentSimulation:
    def __init__(self, project_name):
        self.project_name = project_name
        self.developer = Agent(
            "Developer",
            "You develop a website for a company. When you need to create or modify files, use the FILE_ACTION format exactly as instructed. Create actual HTML, CSS, and JavaScript files that work together to build the website. IMPORTANT: When implementing images in HTML, always use relative paths like 'images/filename.png' since HTML files are in the root directory and images are in the 'images' subdirectory. Always read existing files first to understand the current structure before making improvements.",
            activation_triggers=[
                "development",
                "code",
                "implement",
                "feature",
                "stuck",
                "technical",
            ],
            can_write_files=True,
            can_read_files=True,
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
            "You are the QA of the company that the developer works for. You test the website and give the developer feedback on the website. You can run commands to test functionality. Read existing files to analyze code quality, find potential bugs, and suggest improvements.",
            activation_triggers=["testing", "qa", "bug", "quality", "test"],
            can_write_files=True,
            can_read_files=True,
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
            "Let's start implementing the website. Create the basic HTML structure with a homepage. Include proper DOCTYPE, head section with meta tags, title, and body structure. Also create a CSS file for styling and link it to the HTML. Make sure to create a solid foundation for the website."
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
            "IMPORTANT: Look at the images that have been generated and implement them into the existing HTML files. Review all HTML files in the project and update them to include the new images using proper <img> tags with relative paths (e.g., src='images/filename.png'). Update the CSS files to style the images appropriately and add any necessary JavaScript functionality. Make sure to modify the existing files to properly display and integrate the new images."
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
            "Look at the existing project files and create the new page with proper HTML structure, CSS styling, and any necessary JavaScript functionality. Make sure it matches the existing website's design and structure. Review all existing HTML files to understand the current design patterns, CSS classes, and layout structure before creating the new page."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 4: Developer updates navigation and links ===")
        self.conversation_manager.run_conversation_round(
            "IMPORTANT: Review ALL existing HTML files in the project and update each one to include navigation links to the new page. Look at the current navigation structure in each HTML file, then add appropriate <a> tags and update navigation menus consistently across all pages. Ensure the new page is properly integrated into the website structure by modifying every HTML file that contains navigation."
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
            "IMPORTANT: Look at all existing project files to understand the current structure, then implement the page improvements. Identify which specific HTML file needs to be improved and modify that file with updated HTML structure, CSS styling, and JavaScript functionality as needed. Also update any related CSS files and ensure the improvements enhance user experience while maintaining consistency with the overall website design. Review the existing files first, then make the specific modifications."
        )

        self.conversation_manager.show_project_status()
        self.conversation_manager.reset_all_agents()

    def add_images_to_website(self, image_request):
        print(f"=== ADDING IMAGES TO PROJECT: {self.project_name} ===")
        print("=== SCENARIO 1: Client specifies image requirements ===")
        self.conversation_manager.run_conversation_round(image_request)

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 2: Designer creates and generates images ===")
        self.conversation_manager.run_conversation_round(
            "Create and generate the requested images for the website. Use the IMAGE_ACTION format to generate professional, high-quality images that match the website's theme and purpose. Consider different image types like hero images, banners, icons, product photos, or background images as needed."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 3: Developer implements images into website ===")
        self.conversation_manager.run_conversation_round(
            "IMPORTANT: Review all existing HTML files and implement the newly generated images into the appropriate pages. For each image generated, determine which HTML file(s) should display it, then update those files to include the images with proper <img> tags using relative paths (e.g., src='images/filename.png'), add appropriate alt text, and ensure responsive design. Update CSS files to style the images appropriately and ensure they integrate well with the existing layout. Modify every relevant HTML file to include the new images."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 4: Developer optimizes image integration ===")
        self.conversation_manager.run_conversation_round(
            "Optimize the image integration by adding proper styling, responsive design features, and any necessary JavaScript functionality. Ensure images load efficiently and enhance the overall user experience."
        )

        self.conversation_manager.show_project_status()
        self.conversation_manager.reset_all_agents()

    def add_custom_feature(self, feature_request):
        print(f"=== ADDING CUSTOM FEATURE TO PROJECT: {self.project_name} ===")
        print(
            "=== SCENARIO 1: Client specifies custom feature requirements ==="
        )
        self.conversation_manager.run_conversation_round(feature_request)

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 2: Designer creates UI/UX for the feature ===")
        self.conversation_manager.run_conversation_round(
            "Design the user interface and user experience for the custom feature. Create mockups, determine the visual design, layout, and any necessary graphics or icons. Ensure the feature integrates well with the existing website design."
        )

        self.conversation_manager.show_project_status()

        print(
            "\n=== SCENARIO 3: Developer implements the feature functionality ==="
        )
        self.conversation_manager.run_conversation_round(
            "IMPORTANT: Review all existing project files to understand the current website structure, then implement the custom feature functionality. Determine which HTML file(s) should contain the feature and modify those files to add the necessary HTML structure. Update or create CSS files to style the feature, and add JavaScript code to make the feature work. Ensure the feature is responsive, accessible, and integrates properly with the existing website by examining and modifying the appropriate existing files."
        )

        self.conversation_manager.show_project_status()

        print("\n=== SCENARIO 4: Developer adds feature integration ===")
        self.conversation_manager.run_conversation_round(
            "IMPORTANT: Review ALL existing HTML files and integrate the custom feature with the rest of the website. Update navigation menus in each HTML file if needed, add links to the feature from relevant pages, and ensure the feature can be easily accessed by users. Look at each existing HTML file and make any necessary modifications to properly link to and integrate with the new feature."
        )

        self.conversation_manager.show_project_status()
        self.conversation_manager.reset_all_agents()
