from libcst.codemod import CodemodTest
from pymender.commands.move_package import MovePackage

from ..fastapi_annotated import FastAPIAnnotated

OLD_FILE = """
from typing import Annotated
import typing as te
"""

NEW_FILE = """
from typing_extension import Annotated
import typing_extension as te
"""


class TestTypingRename(CodemodTest):
    # The codemod that will be instantiated for us in assertCodemod.
    TRANSFORM = MovePackage

    def test_swap(self) -> None:
        self.maxDiff = None
        self.assertCodemod(OLD_FILE, NEW_FILE, old="typing", new="typing_extension")
        
    def test_no_swap(self) -> None:
        self.maxDiff = None
        self.assertCodemod(NEW_FILE, NEW_FILE, old="typing2", new="typing_extension")