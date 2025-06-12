from file_manager import FileManager


class ConversationManager:
    def __init__(self, agents, project_name):
        self.agents = agents
        self.project_name = project_name
        self.conversation_history = []
        self.current_phase = "planning"
        self.project_context = {
            "satisfaction_level": 0.7,
            "deadline_pressure": 0.3,
            "bugs_found": 0,
            "stuck_count": 0,
        }
        self.file_manager = FileManager(project_name)

    def determine_active_agents(self, context):
        """Determine which agents should participate based on context"""
        active_agents = []

        for agent in self.agents:
            if agent.should_activate(context):
                active_agents.append(agent)

        # Always include manager if multiple agents are active (to facilitate)
        if (
            len(active_agents) > 2 and self.agents[4] not in active_agents
        ):  # manager
            active_agents.append(self.agents[4])

        return active_agents[:3]  # Limit to 3 agents max per round

    def run_conversation_round(
        self, initial_prompt, max_exchanges=3, debug=False
    ):
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

                # Debug action detection if requested
                if debug and (
                    agent.can_write_files or agent.can_generate_images
                ):
                    self.file_manager.debug_action_detection(response)

                # Process any file operations
                if agent.can_write_files or agent.can_generate_images:
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
