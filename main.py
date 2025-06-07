from development_simulation import DevelopmentSimulation


def show_menu():
    print("\n" + "=" * 50)
    print("🏢 DEVELOPMENT OFFICE SIMULATION")
    print("=" * 50)
    print("1. Run first runthrough")
    print("2. Exit")
    print("=" * 50)


def main():
    office = DevelopmentSimulation()

    while True:
        show_menu()
        choice = input("Enter your choice (1-2): ").strip()

        if choice == "1":
            prompt = input("\nEnter your project request: ")
            if prompt.strip():
                office.first_runthrough(prompt)
            else:
                print("❌ Please enter a valid project request.")

        elif choice == "2":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
