import logging
from typing import Any

logger = logging.getLogger(__name__)

import libcst as cst
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand

def rename_node(old_name_node: Any, from_name: str, to_name: str) -> cst.Name | None:
    if not isinstance(old_name_node, cst.Name):
        return None
    
    if from_name not in old_name_node.value:
        return None

    new_name = old_name_node.value.replace(from_name, to_name, 1)
    return old_name_node.with_changes(value=new_name)

class MovePackage(VisitorBasedCodemodCommand):
    DESCRIPTION = """
    Moves a package/module from a specified folder to another and updates all imports that reference that.
    """
    package_old: str
    package_new: str

    def __init__(self, context: CodemodContext, old: str, new: str) -> None:
        super().__init__(context)
        self.package_new = new
        self.package_old = old
        

    @staticmethod
    def add_args(arg_parser):
        arg_parser.add_argument("--old", required=True, help="Module to move from.")
        arg_parser.add_argument("--new", required=True, help="Module to move to.")

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        new_imports = []
        for import_alias in updated_node.names:
            if replacement_name := rename_node(import_alias.name, self.package_old, self.package_new):
                new_imports.append(import_alias.with_changes(name=replacement_name))
                logger.debug(f"Updated import from {self.package_old} to {self.package_new}")
            else:
                new_imports.append(import_alias)
        return updated_node.with_changes(names=new_imports)

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        if replacement_name := rename_node(updated_node.module, self.package_old, self.package_new):
            logger.debug(f"Updated import from {self.package_old} to {self.package_new}")
            updated_node = updated_node.with_changes(module=replacement_name)
        return updated_node

    def transform_module(self, tree: cst.Module) -> cst.Module:
        logger.debug(f"Transforming module with from={self.package_old}, to={self.package_new}")
        return super().transform_module(tree)
