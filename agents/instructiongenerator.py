import os
import pathlib

import litellm
import dotenv

import json
from typing import List, Dict, Any

import warnings

warnings.filterwarnings('ignore')

dotenv.load_dotenv('.env')

class InstructionGenerator:
    def __init__(self):
        self.instructions_history_file = 'instructions_history.json'
        self.system_instructions = ""

        with open(pathlib.Path('instructions', 'generator.txt'), 'rt', encoding='utf-8') as instr_file:
            self.system_instructions = instr_file.read()
            print(self.system_instructions)

        if InstructionGenerator.file_exists(self.instructions_history_file):
            self.messages = InstructionGenerator.load_messages_from_file(self.instructions_history_file)
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

    def add_file_context(self, filename: str) -> 'InstructionGenerator':
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

    def ask(self, prompt: str) -> 'InstructionGenerator':
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
            model = "gpt-4.1-nano",
            #model='ollama/gemma3',
            messages=msgs,
        )

        if choice := response.get('choices').pop():
            if message := choice.get('message'):
                if content := message.get('content'):
                    # print(content)

                    self.messages.append({
                        "role": "user",
                        "content": prompt,
                    })
                    
                    self.messages.append({
                        "role": message.get('role'),
                        "content": message.get('content'),
                    })

                    self.last_response = message.get('content')

        InstructionGenerator.save_messages_to_file(self.messages, filename=self.instructions_history_file)
                    
        return self

if __name__ == '__main__':
    ignr = InstructionGenerator()
