# Reset history
# RAG
# input file to refactor
# different name not OpenAIAgent, create hierarchi?
# code validator, code tester, commit reviewer, ?, code navigator, bug_finder, requirement generator analyzer
# tools: websearch (for documentation), git differ?, edit_file, calculator
# switch to project/directory
# start test watch mode

import os 
import pprint

import litellm
import dotenv

import json
from typing import List, Dict, Any

import warnings

warnings.filterwarnings('ignore')

dotenv.load_dotenv('.env')

class PythonCodeGenerator:
    def __init__(self):
        self.system_instructions = """
        TITLE
        Python Code Generator

        VERSION
        0.0.1

        DESCRIPTION
        This agent serves for python code generation

        CONTENXT
        None

        INPUT
        The user provides a prompt asking for a piece of python code or
        a codebase that needs to be changed.

        OUTPUT
        Working python code. This code will be piped into a file most of the time.

        RULES
        -MUSTN'T
        Never include markdown for code like ```python. 
        Do not introduce bugs.
        Do not introduce side efects if possible. Except for IO.
        
        -MUST
        Only generate python code nothing else.
        Include doctest for every function written.
        Write functions.
        Prefer functional programming over OOP.
        Make the code testable.
        Use python 3.
        As short as possible. Do not be verbose.
        Write performant code.
        Include type annotations.
        Include error handling and error throwing.
        
        -CAN
        You can use: pandas, litellm, numpy, and any build-in libraries

        EXAMPLES
        -EXAMPLE 1
        user> create hello world program
        ai>
        def hello_world() -> None:
            print('Hello World')

        if __name__ == '__main__':
            hello_world()
        
        """

        if PythonCodeGenerator.file_exists('history.json'):
            self.messages = PythonCodeGenerator.load_messages_from_file('history.json')
            # print('Loaded history file from history.json')
        else:
            self.messages = [{
                "role": "system", "content": self.system_instructions
            }]

        self.last_response = ''
        self.file_context = ''

    def write_last_response(self, filename: str) -> None:
        with open(filename, 'wt', encoding='utf-8') as output_file:
            output_file.write(self.last_response)

    @staticmethod
    def file_exists(filename: str) -> bool:
        """
        Check if a file exists.

        Args:
            filename: Path to the file.

        Returns:
            True if the file exists, False otherwise.
        """
        return os.path.isfile(filename)

    @staticmethod
    def save_messages_to_file(messages: List[Dict[str, Any]], filename: str = 'history.json') -> None:
        """
        Save a list of message dictionaries to a JSON file.

        Args:
            messages: List of message dictionaries.
            filename: Path to the file where messages will be saved.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(messages, f)
        except IOError as e:
            raise RuntimeError(f"Failed to save messages to {filename}: {e}")

    @staticmethod
    def load_messages_from_file(filename: str = 'history.json') -> List[Dict[str, Any]]:
        """
        Load a list of message dictionaries from a JSON file.

        Args:
            filename: Path to the file from which messages will be loaded.

        Returns:
            A list of message dictionaries.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load messages from {filename}: {e}")

    def add_file_context(self, filename: str) -> 'PythonCodeGenerator':
        """
        Read the content of a file and store it as the file context.
        Args:
            filename: Path to the file to be added as context.
        Returns:
            self: The instance with updated file context.
        """
        try:
            with open(filename, 'rt', encoding='utf-8') as f:
                self.file_context = f.read()
        except IOError as e:
            raise RuntimeError(f"Failed to read file {filename}: {e}")
        return self

    def ask(self, prompt: str) -> 'PythonCodeGenerator':
        context = self.file_context
        msgs = [
                *self.messages,
                {
                    "role": "user",
                    "content": (context + ' ' + prompt).strip(),
                }
            ]

        response = litellm.completion(
            #model = "gpt-5-nano",
            model = "gpt-4.1",
            #model='ollama/gemma3',
            messages=msgs,
        )

        choices = response.get('choices')
        if not choices:
            raise Exception(f'LLM response missing "choices" key or it is empty. Response received: {response}')

        choice = choices.pop()
        message = choice.get('message')
        if not message:
            raise Exception(f'LLM response "choice" missing "message" key. Choice received: {choice}')

        content = message.get('content')
        if not content:
            raise Exception(f'LLM response "message" missing "content" key. Message received: {message}')

        self.messages.append({
            "role": "user",
            "content": prompt,
        })

        self.messages.append({
            "role": message.get('role'),
            "content": content,
        })

        self.last_response = content

        # if choice := response.get('choices').pop():
        #     if message := choice.get('message'):
        #         if content := message.get('content'):
        #             self.messages.append({
        #                 "role": "user",
        #                 "content": prompt,
        #             })
        #
        #             self.messages.append({
        #                 "role": message.get('role'),
        #                 "content": content,
        #             })
        #
        #             self.last_response = content

        PythonCodeGenerator.save_messages_to_file(self.messages)
                    
        return self

if __name__ == '__main__':
    pcg = PythonCodeGenerator()
