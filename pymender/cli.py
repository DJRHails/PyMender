import argparse
import inspect
import os
import pkgutil
import sys
from pathlib import Path
from libcst.codemod import (
    CodemodCommand,
    VisitorBasedCodemodCommand,
    CodemodContext,
    gather_files,
    parallel_exec_transform_with_prettyprint,
)
from gitignore_parser import parse_gitignore
from pymender import commands

def run_command(Command: type[CodemodCommand], repo_root: str = ".") -> int:
    os.environ["LIBCST_PARSER_TYPE"] = "native"
    parser = argparse.ArgumentParser(
        description=Command.DESCRIPTION,
    )
    parser.add_argument(
        "path",
        metavar="PATH",
        nargs="+",
        help=(
            "Path to codemod. Can be a directory, file, or multiple of either. To "
            + 'instead read from stdin and write to stdout, use "-"'
        ),
    )
    parser.add_argument(
        "--gitignore",
        default=".gitignore",
        action="store",
        metavar="GITIGNORE",
        help=(
            "Path to a gitignore file. Files that match the gitignore will not be "
            + "codemodded."
        ),   
    )
    args = parser.parse_args()

    context = CodemodContext()
    command_instance = Command(context)
    files = gather_files(args.path)
    
    gitignore_path = Path(args.gitignore) if args.gitignore else Path(repo_root) / ".gitignore"
    if gitignore_path.exists() and (validator := parse_gitignore(gitignore_path)):
        files = [file for file in files if not validator(file)]
    
    if not files:
        print("No files to modify! Check if you need to adjust the .gitignore", file=sys.stderr)
        return 1
    
    try:
        result = parallel_exec_transform_with_prettyprint(
            command_instance, files, repo_root=repo_root,
        )
    except KeyboardInterrupt:
        print("Interrupted!", file=sys.stderr)
        return 2

    # Print a fancy summary at the end.
    print(
        f"Finished codemodding {result.successes + result.skips + result.failures} files!",
        file=sys.stderr,
    )
    print(f" - Transformed {result.successes} files successfully.", file=sys.stderr)
    print(f" - Skipped {result.skips} files.", file=sys.stderr)
    print(f" - Failed to codemod {result.failures} files.", file=sys.stderr)
    print(f" - {result.warnings} warnings were generated.", file=sys.stderr)
    if result.failures > 0:
        return 1
    return 0



def discover_commands() -> list[type[CodemodCommand]]:
    codemod_command_classes = set()
    for loader, name, _ in pkgutil.walk_packages(commands.__path__, commands.__name__ + '.'):
        module = loader.find_module(name).load_module(name)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, CodemodCommand) and not inspect.isabstract(obj):
                codemod_command_classes.add(obj)
    codemod_command_classes -= {VisitorBasedCodemodCommand}
    return codemod_command_classes

def main() -> int:
    commands = discover_commands()
    command_lookup = {cmd.__name__: cmd for cmd in commands}
    
    parser = argparse.ArgumentParser(
        description="Mends Python code to be more idiomatic."
    )
    parser.add_argument(
        "command",
        metavar="COMMAND",
        choices=command_lookup.keys(),
        help=f"The codemod to run, choose from: {', '.join(command_lookup.keys())}",
    )
    args, _ = parser.parse_known_args()
    
    Command = command_lookup.get(args.command)
    if not Command:
        print(f"Unknown command {args.command}", file=sys.stderr)
        return 1
    return run_command(Command)
    