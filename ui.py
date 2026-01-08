from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout import Layout
from prompt_toolkit.buffer import SelectionState
import subprocess

from prompt_toolkit.shortcuts import input_dialog

# ---- Load file ----
FILE_PATH = "example.py"

with open(FILE_PATH, "r") as f:
    initial_text = f.read()

text_area = TextArea(
    text=initial_text,
    multiline=True,
    scrollbar=True,
)

kb = KeyBindings()

from pythoncodegenerator import PythonCodeGenerator

# ---- Function that processes selected text ----
def run_python_on_text(text: str, prompt: str = '') -> str:
    """
    Example: run external Python script that reads stdin
    """
    result = (
        PythonCodeGenerator()
        .ask(f"here is the code: {text}, and here is the user prompt: {prompt}")
        .last_response
    )

    return result

@kb.add("c-q")
def _(event):
    event.app.exit()

@kb.add("c-s")
def _(event):
    with open(FILE_PATH, "w") as f:
        buffer = event.app.current_buffer
        f.write(buffer.text)
    
# ---- Keybinding: Ctrl-R ----
@kb.add("c-r")
def _(event):
    buffer = text_area.buffer
    sel = buffer.selection_state

    if not sel:
        return

    # Get selection range
    start, end = buffer.document.selection_range()
    selected_text = buffer.text[start:end]

    async def run():
        user_input = await input_dialog(
            title="Prompt",
            text="Enter value:",
        ).run_async()

        if user_input is None:
            return

        # Run script
        output = run_python_on_text(selected_text, user_input)

        # Replace selection with output
        buffer.delete_before_cursor(count=buffer.cursor_position - start)
        buffer.insert_text(output)

        # Clear selection
        buffer.selection_state = None

        # print("User input:", result)

    event.app.create_background_task(run())

    # user_input = input_dialog(
    #     title="Prompt",
    #     text="Enter value:"
    # ).run()

    # if not user_input:
    #     return

    # Run script
    # output = run_python_on_text(selected_text, user_input)

    # # Replace selection with output
    # buffer.delete_before_cursor(count=buffer.cursor_position - start)
    # buffer.insert_text(output)

    # # Clear selection
    # buffer.selection_state = None

# ---- App ----
app = Application(
    layout=Layout(text_area),
    key_bindings=kb,
    full_screen=True,
)

app.run()
