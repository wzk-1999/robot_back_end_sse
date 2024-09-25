from daphne.cli import CommandLineInterface

if __name__ == "__main__":
    CommandLineInterface().run([
        "-b", "0.0.0.0",
        "-p", "8000",
        "back_end_sse.asgi:application"
    ])