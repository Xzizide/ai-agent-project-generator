from development_simulation import DevelopmentSimulation


def show_menu():
    print("\n" + "=" * 50)
    print("🏢 DEVELOPMENT OFFICE SIMULATION")
    print("=" * 50)
    print("1. Run first runthrough")
    print("2. Exit")
    print("=" * 50)


def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1-2): ").strip()

        if choice == "1":
            project_name = input("\nEnter your project name: ").strip()
            if not project_name:
                print("❌ Please enter a valid project name.")
                continue

            prompt = input("Enter your project request: ").strip()
            if not prompt:
                print("❌ Please enter a valid project request.")
                continue

            office = DevelopmentSimulation(project_name)
            office.first_runthrough(prompt)

        elif choice == "2":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
