import gradio as gr

from .agent import generate_command
from .safety import check_command


def process_request(user_request, service=None):
    """Process a user's request and validate the generated command."""

    if not user_request or not user_request.strip():
        return "", "Please enter a request."

    try:
        command = generate_command(
            user_request,
            service=service
        )

        if command == "BLOCKED":
            return "", "Request blocked for security reasons."

        if command == "UNSUPPORTED":
            return "", "This request is not supported."

        if command == "NEED_CLARIFICATION":
            return "", "More information is required."

        is_safe, message = check_command(command)

        if not is_safe:
            return "", f"Command rejected: {message}"

        return command, "Command approved. Not executed."

    except Exception as error:
        return "", f"Error: {type(error).__name__}: {error}"


def create_demo(service=None):

    with gr.Blocks(
        title="Natural Language to CMD Agent"
    ) as demo:

        gr.Markdown(
            """
            # Natural Language to CMD Agent

            Write an instruction in natural language
            and receive a Windows CMD command.

            Commands are checked for safety
            and are never executed automatically.
            """
        )

        user_input = gr.Textbox(
            label="Your instruction",
            placeholder="What is my computer's IP address?",
            lines=3
        )

        submit_button = gr.Button(
            "Generate CMD Command"
        )

        command_output = gr.Textbox(
            label="Generated CMD Command",
            interactive=False
        )

        status_output = gr.Textbox(
            label="Status",
            interactive=False
        )

        submit_button.click(
            fn=lambda request: process_request(request, service),
            inputs=user_input,
            outputs=[command_output, status_output]
        )

        user_input.submit(
            fn=lambda request: process_request(request, service),
            inputs=user_input,
            outputs=[command_output, status_output]
        )

    return demo


def main() -> None:
    """Launch the Gradio app."""

    demo = create_demo()

    demo.launch(
        server_name="127.0.0.1",
        share=False,
        inbrowser=True
    )


if __name__ == "__main__":
    main()
