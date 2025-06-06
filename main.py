from agents import Agent
from conversation_manager import ConversationManager


# Create agents with specific activation triggers
developer = Agent(
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

boss = Agent(
    "Boss",
    "You are the boss of the company that the developer works for. You watch over the developer and give them feedback on the website.",
    activation_triggers=["deadline", "budget", "urgent", "crisis", "review"],
)

client = Agent(
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

designer = Agent(
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

qa = Agent(
    "QA",
    "You are the QA of the company that the developer works for. You test the website and give the developer feedback on the website. You can run commands to test functionality.",
    activation_triggers=["testing", "qa", "bug", "quality", "test"],
    can_write_files=True,
)

manager = Agent(
    "Manager",
    "You are the manager of the company that the developer works for. You manage the other agents and the developer.",
    activation_triggers=["planning", "coordination", "meeting", "organize"],
)

rubber_duck = Agent(
    "Rubber duck",
    "When the client is unhappy you get bonked on the head and say quack quack.",
    activation_triggers=["stuck", "problem", "help", "frustrated"],
)

# Create conversation manager
agents = [developer, boss, client, designer, qa, manager, rubber_duck]
conversation_manager = ConversationManager(agents)

# Example usage:
if __name__ == "__main__":
    # Different scenarios that would activate different agents

    print("=== SCENARIO 1: Client wants to discuss requirements ===")
    conversation_manager.run_conversation_round(
        "I need a website for my bakery business. I want customers to be able to order cakes online and I want a lot of images of the cakes."
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
