# Niva Console Custom Commands Documentation

## Introduction
Custom commands in Niva Console allow you to extend the functionality of the console by adding your own commands. This documentation provides a guide on how to create and use custom commands.

## Command Template
```python
class Command:
    name = "command_name"
    description = "Command description"
    usage = "command [options]"
    hidden = False
    
    async def execute(self, console, args):
        """
        Execute command logic
        Args:
            console: NivaConsole instance
            args: List of command arguments
        """
        # Your command logic here
        return True # Return True to continue, False to exit the console
```

## Creating Custom Commands
To create a custom command, follow these steps:

1. 📁 **Create a new Python file** in the `CLI/Commands` directory.
2. 📝 **Define a class** named `Command` in the new file.
3. 🏷️ **Set the `name` and `description` attributes** for the command.
4. 🛠️ **Implement the `execute` method** to define the command's behavior.
5. 💾 **Save the file** and restart the console to load the new command.

## Command Attributes
Here is a detailed explanation of the attributes used in the command template:

- **name**: The name of the command. This is the string that users will type to execute the command.
- **description**: A brief description of what the command does. This is used in the help text.
- **usage**: A string that describes how to use the command, including any options or arguments.
- **hidden**: A boolean value that indicates whether the command should be hidden from the help text. Set this to `True` if you want to hide the command.
- **args**: A list of arguments that the command accepts. This is optional and can be used to define specific arguments for the command.
