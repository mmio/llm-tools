# import os
# import pathlib
#
# cwd = os.getcwd()
# path = pathlib.Path(cwd)
#
# print(path)

from agents.instructiongenerator import InstructionGenerator

def main() -> None:
    """
    Create InstructionGenerator instance and call it if possible.
    """
    try:
        igen = InstructionGenerator()
        if hasattr(igen, 'generate') and callable(getattr(igen, 'generate')):
            igen.generate()
        elif hasattr(igen, 'run') and callable(getattr(igen, 'run')):
            igen.run()
    except Exception:
        raise

if __name__ == '__main__':
    main()
