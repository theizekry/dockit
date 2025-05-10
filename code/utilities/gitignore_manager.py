import os
from utilities.messenger import Messenger

class GitignoreManager:
    def __init__(self):
        self.messenger = Messenger()


    def add_pattern(self, pattern: str, comment: str = None) -> bool:
        """
        Add a pattern to .gitignore if it doesn't exist
        
        Args:
            pattern (str): The pattern to add to .gitignore
            comment (str, optional): A comment to add above the pattern. If None, no comment will be added.
            
        Returns:
            bool: True if pattern was added or already exists, False if there was an error
        """
        gitignore_path = '.gitignore'
        if not os.path.exists(gitignore_path):
            return False

        try:
            with open(gitignore_path, 'r') as f:
                content = f.read()

            # Check if the pattern already exists
            if pattern not in content:
                with open(gitignore_path, 'a') as f:
                    if comment is not None:
                        f.write(f'\n# {comment}\n')
                    f.write(f'{pattern}\n')
                self.messenger.info(f"Updated .gitignore to exclude {pattern}")
            return True
        except Exception as e:
            self.messenger.warning(f"Failed to update .gitignore: {str(e)}")
            return False 