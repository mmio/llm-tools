# TODO: Ctrl O insert line above
# TODO: indent with tab
# TODO: line numbers on off
# TODO: start with empty buffer
# TODO: Buffer search fucntionality Control S
# TODO: Modline with info
# TODO: Buffer switcing with ControlXB
# TODO: Plugin architecture?
# TODO: Integrate langchain
# TODO: copy paste
# TODO: extend selection to function
# TODO: MVC 


import os
import pathlib

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.shortcuts import input_dialog
from components.fileselect import radiolist_dialog
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import PythonLexer

from pythoncodegenerator import PythonCodeGenerator


def is_empty(line: str) -> bool:
    return line.strip() == ""


def run_python_on_text(text: str, prompt: str = '', whole: str = '') -> str:
    """
    Example: run external Python script that reads stdin
    """
    result = (
        PythonCodeGenerator()
        .ask(f"""
        Whole file text : {whole}.
        Here is selected code to change: {text}.
        Here is the user prompt: {prompt}.
        Only return the selection changed if provided otherwise the whole file changed.
        """)
        .last_response
    )

    return result

FILE_PATH = 'tmp.txt'

if __name__ == '__main__':
    text_area = TextArea(
        text="This is a temporary file buffer",
        multiline=True,
        scrollbar=True,
        lexer=PygmentsLexer(PythonLexer),
    )

    kb = KeyBindings()


    @kb.add(Keys.Tab)
    def insert_tab(event):
        buffer = event.current_buffer
        position = buffer.cursor_position

        def __insert_tab():
            buffer.text = buffer.text[:position] + '    ' + buffer.text[position:]
            buffer.cursor_position = position + len('    ')

        __insert_tab()


    @kb.add('escape', '{')   # Alt+{
    def previous_empty_line(event):
        buffer = event.current_buffer
        text = buffer.text
        pos = buffer.cursor_position

        lines = text.splitlines(keepends=True)

        # Find current line index
        index = 0
        char_count = 0
        for i, line in enumerate(lines):
            char_count += len(line)
            if char_count >= pos:
                index = i
                break

        # Search backwards
        for i in range(index - 1, -1, -1):
            if is_empty(lines[i]):
                buffer.cursor_position = sum(len(l) for l in lines[:i + 1])
                return


    @kb.add('escape', '}')   # Alt+}
    def next_empty_line(event):
        buffer = event.current_buffer
        text = buffer.text
        pos = buffer.cursor_position

        lines = text.splitlines(keepends=True)

        # Find current line index
        index = 0
        char_count = 0
        for i, line in enumerate(lines):
            char_count += len(line)
            if char_count >= pos:
                index = i
                break

        # Search forwards
        for i in range(index + 1, len(lines)):
            if is_empty(lines[i]):
                buffer.cursor_position = sum(len(l) for l in lines[:i + 1])
                return

    @kb.add(Keys.Escape, '<')
    def _(event):
        event.current_buffer.cursor_position = 0

    @kb.add(Keys.ControlX, Keys.ControlC)
    def _(event):
        event.app.exit()

    @kb.add(Keys.ControlX, Keys.ControlS)
    def _(event):
        with open(FILE_PATH, "w") as f:
            buffer = event.app.current_buffer
            f.write(buffer.text)

    @kb.add(Keys.ControlX, Keys.ControlF)
    def open_different_file(event):
        # Prompt for new filename
        async def prompt_filename():
            # filename = await input_dialog(
            #     title="Switch File",
            #     text="Enter filename:",
            # ).run_async()

            cwd = os.getcwd()
            print(pathlib.Path(cwd).name)
            filename = ".."

            while filename == '..':
                dir_list = ['..', *os.listdir(cwd)]
                filename = await radiolist_dialog(
                    title="Select File",
                    text=cwd,
                    values=[
                        (item, item)
                        for item in dir_list
                    ],
                ).run_async()

                # Going one level up
                if filename == '..':
                    cwd = str(pathlib.Path(cwd).parent)
                # Entering directory
                elif pathlib.Path(cwd, filename).is_dir():
                    cwd = str(pathlib.Path(cwd, filename))
                    filename = '..'
                # Opening File
                else:
                    filename = str(pathlib.Path(cwd, filename))

            return filename

        async def run():
            filename = await prompt_filename()
            if filename:
                try:
                    with open(filename, "r") as next_file_to_open:
                        new_text = next_file_to_open.read()
                    # Update text_area with new content
                    text_area.text = new_text
                    global FILE_PATH
                    FILE_PATH = filename
                except Exception as e:
                    # Optionally, handle errors here (e.g., show message)
                    pass

        event.app.create_background_task(run())

    @kb.add("c-t")
    def _(event):
        buffer = event.app.current_buffer
        # Prompt user for input
        async def prompt_input():
            user_input = await input_dialog(
                title="Prompt",
                text="Enter value:",
            ).run_async()
            return user_input

        async def run():
            user_input = await prompt_input()
            if user_input is None:
                return
            # Generate code based on entire buffer or other context
            output = run_python_on_text('', user_input, buffer.text)
            # Insert generated text at cursor position
            buffer.insert_text(output)

        event.app.create_background_task(run())
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
            output = run_python_on_text(selected_text, user_input, buffer.text)

            # Replace selection with output
            if buffer.cursor_position > start:
                buffer.delete_before_cursor(count=buffer.cursor_position - start)
            else:
                pass
                # how do we delete stuff here???
                # buffer.delete_after_cursor(count=end - buffer.cursor_position)

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
