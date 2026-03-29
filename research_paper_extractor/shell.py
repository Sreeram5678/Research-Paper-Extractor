import click
from .utils import themed_print, themed_header

class InteractiveShell:
    """An interactive shell mode for the CLI."""

    def __init__(self, cli_group):
        self.cli_group = cli_group

    def start(self):
        """Starts the interactive shell loop."""
        themed_header("Research Paper Extractor — Interactive Shell")
        themed_print("Type 'help' for commands, 'exit' or 'quit' to leave.\n", "info")

        while True:
            try:
                cmd_line = input("paper-extractor> ").strip()
                if not cmd_line:
                    continue
                
                if cmd_line.lower() in ("exit", "quit"):
                    themed_print("Goodbye!", "info")
                    break
                
                # Simple argument splitting
                import shlex
                args = shlex.split(cmd_line)
                
                # Execute command via Click
                try:
                    self.cli_group.main(args=args, standalone_mode=False)
                except click.exceptions.UsageError as e:
                    themed_print(f"Usage Error: {e}", "warning")
                except click.exceptions.ClickException as e:
                    themed_print(f"Error: {e}", "error")
                except SystemExit:
                    pass # Click often calls sys.exit()
                except Exception as e:
                    themed_print(f"Unexpected error: {e}", "error")
                    
            except KeyboardInterrupt:
                themed_print("\nUse 'exit' to quit.", "info")
            except EOFError:
                themed_print("\nGoodbye!", "info")
                break
