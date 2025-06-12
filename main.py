import os
from pathlib import Path
from development_simulation import DevelopmentSimulation


def show_main_menu():
    print("\n" + "=" * 50)
    print("🏢 DEVELOPMENT OFFICE SIMULATION")
    print("=" * 50)
    print("0. Exit")
    print("1. Create new project")
    print("2. Select existing project")
    print("=" * 50)


def show_project_menu(project_name):
    print("\n" + "=" * 50)
    print(f"📁 PROJECT: {project_name}")
    print("=" * 50)
    print("0. Exit")
    print("1. Continue development")
    print("2. Add new page")
    print("3. Improve existing page")
    print("=" * 50)


def get_existing_projects():
    """Get list of existing project folders"""
    website_project_dir = Path("website_project")
    if not website_project_dir.exists():
        return []

    projects = []
    for item in website_project_dir.iterdir():
        if item.is_dir():
            projects.append(item.name)

    return sorted(projects)


def select_existing_project():
    """Let user select from existing projects"""
    projects = get_existing_projects()

    if not projects:
        print("❌ No existing projects found.")
        return None

    print("\n📁 EXISTING PROJECTS:")
    print("-" * 30)
    print("0. Exit")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project}")
    print("-" * 30)

    try:
        choice = int(input("Select project number: ").strip())
        if choice == 0:
            return None
        if 1 <= choice <= len(projects):
            return projects[choice - 1]
        else:
            print("❌ Invalid project number.")
            return None
    except ValueError:
        print("❌ Please enter a valid number.")
        return None


def create_new_project():
    """Handle new project creation"""
    project_name = input("\nEnter your project name: ").strip()
    if not project_name:
        print("❌ Please enter a valid project name.")
        return False

    prompt = input("Enter your project request: ").strip()
    if not prompt:
        print("❌ Please enter a valid project request.")
        return False

    office = DevelopmentSimulation(project_name)
    office.project_creation(prompt)
    return True


def handle_existing_project(project_name):
    """Handle actions for existing project"""
    while True:
        show_project_menu(project_name)
        choice = input("Enter your choice (0-3): ").strip()

        if choice == "0":
            break

        elif choice == "1":
            prompt = input("\nEnter your development request: ").strip()
            if not prompt:
                print("❌ Please enter a valid request.")
                continue

            office = DevelopmentSimulation(project_name)
            office.project_creation(prompt)

        elif choice == "2":
            page_request = input(
                "\nEnter your new page request (what page to add): "
            ).strip()
            if not page_request:
                print("❌ Please enter a valid page request.")
                continue

            office = DevelopmentSimulation(project_name)
            office.add_new_page(page_request)

        elif choice == "3":
            improvement_request = input(
                "\nEnter your page improvement request (which page to improve and how): "
            ).strip()
            if not improvement_request:
                print("❌ Please enter a valid improvement request.")
                continue

            office = DevelopmentSimulation(project_name)
            office.improve_existing_page(improvement_request)

        else:
            print("❌ Invalid choice. Please enter 0, 1, 2, or 3.")


def main():
    while True:
        show_main_menu()
        choice = input("Enter your choice (0-2): ").strip()

        if choice == "1":
            create_new_project()

        elif choice == "2":
            project_name = select_existing_project()
            if project_name:
                handle_existing_project(project_name)

        elif choice == "0":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 0, 1, or 2.")


if __name__ == "__main__":
    main()
