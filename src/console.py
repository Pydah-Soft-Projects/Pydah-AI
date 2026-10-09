import sys
from typing import List, Dict, Optional
from src.config import Config, ConfigError
from src.llm_client import LLMClient, LLMError

DEFAULT_SYSTEM_PROMPT = (
    "You are Pydah AI, a helpful, respectful, and intelligent AI assistant. "
    "Provide clear, accurate, and concise answers to user queries."
)


class ConsoleApp:
    """Console application for interacting with Pydah AI."""

    def __init__(self, config: Config, llm_client: Optional[LLMClient] = None, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self.config = config
        self.llm_client = llm_client or LLMClient(config)
        self.system_prompt = system_prompt
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _truncate_history(self) -> List[Dict[str, str]]:
        """
        Maintain conversation context within configured maximum size limit.
        Always retains system message at index 0 and latest max_history_messages.
        """
        system_msg = self.messages[0]
        conversation = self.messages[1:]
        
        if len(conversation) > self.config.max_history_messages:
            conversation = conversation[-self.config.max_history_messages:]
        
        return [system_msg] + conversation

    def run(self) -> None:
        """Start the interactive console chat loop."""
        print("=" * 60)
        print(" Welcome to Pydah AI Assistant Console")
        print(f" Configured Model: {self.config.model}")
        print(" Type 'exit' or 'quit' to close the session.")
        print("=" * 60)
        print()

        while True:
            try:
                user_input = input("User > ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\nExiting Pydah AI Console. Goodbye!")
                break

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                print("\nExiting Pydah AI Console. Goodbye!")
                break

            # Append user message to history
            self.messages.append({"role": "user", "content": user_input})
            payload_messages = self._truncate_history()

            print("\nPydah AI > Thinking...", end="\r", flush=True)

            try:
                answer = self.llm_client.generate_response(payload_messages)
                print(" " * 30, end="\r")  # Clear "Thinking..." line
                print(f"Pydah AI > {answer}\n")
                
                # Append assistant response to history
                self.messages.append({"role": "assistant", "content": answer})

            except LLMError as e:
                print(" " * 30, end="\r")
                print(f"\n[Error] {e}\n")
                # Remove the failed user message so history isn't corrupted
                if self.messages and self.messages[-1]["role"] == "user":
                    self.messages.pop()
            except Exception as e:
                print(" " * 30, end="\r")
                print(f"\n[Unexpected Error] {str(e)}\n")
                if self.messages and self.messages[-1]["role"] == "user":
                    self.messages.pop()


def start_console() -> None:
    """Entry point function to initialize configuration and launch console."""
    try:
        config = Config.load()
    except ConfigError as e:
        print(f"\n[Configuration Error] {e}\n", file=sys.stderr)
        sys.exit(1)

    app = ConsoleApp(config)
    app.run()
