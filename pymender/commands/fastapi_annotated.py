import logging
import sys

import libcst as cst
from libcst.codemod import VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor

logger = logging.getLogger(__name__)


def wrap_subscript_elements_with_annotated(
    param: cst.Param,
    elements: list[cst.BaseExpression | None],
    default: cst.BaseExpression | None,
) -> cst.Param:
    annotated = cst.Annotation(
        cst.Subscript(
            value=cst.Name("Annotated"),
            slice=tuple(
                [
                    cst.SubscriptElement(cst.Index(elem))
                    for elem in elements
                    if elem is not None
                ]
            ),
        )
    )
    return param.with_changes(
        annotation=annotated, equal=cst.MaybeSentinel.DEFAULT, default=default
    )


def adapt_param(param: cst.Param) -> cst.Param | None:
    match param.default:
        case cst.Call(func=cst.Name("Depends")):
            logger.info(f"Found Depends annotation")
            elements: list[cst.BaseExpression | None] = [
                param.annotation.annotation if param.annotation is not None else None,
                param.default,
            ]
            return wrap_subscript_elements_with_annotated(param, elements, None)
        case cst.Call(func=cst.Name("Body")) | cst.Call(func=cst.Name("Query")):
            logger.info(f"Found Body annotation")

            call = param.default

            # Find the default value (either first unnamed argument or default=)
            # breakpoint()

            # First unnamed argument, that is not Ellipsis
            first_unnamed_arg = next(
                (arg for arg in call.args if arg.keyword is None),
                None,
            )
            default_keyword = next(
                (
                    arg
                    for arg in call.args
                    if arg.keyword and arg.keyword.value == "default"
                ),
                None,
            )
            default = default_keyword or first_unnamed_arg

            if default is not None:
                call = call.with_changes(
                    args=[arg for arg in call.args if arg != default]
                )

            elements = [
                param.annotation.annotation if param.annotation is not None else None,
                call,
            ]
            return wrap_subscript_elements_with_annotated(
                param,
                elements,
                default.value
                if default and not isinstance(default.value, cst.Ellipsis)
                else None,
            )

        case _:
            return None


def sort_params_preserving_spacing(params: list[cst.Param]) -> list[cst.Param]:
    return [
        param.with_changes(comma=params[idx].comma)
        for idx, param in enumerate(
            sorted(params, key=lambda param: param.default is None, reverse=True)
        )
    ]


class FastAPIAnnotated(VisitorBasedCodemodCommand):
    DESCRIPTION = "Converts FastAPI annotations to use Annotated."

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        new_parameters: list[cst.Param] = []
        new_kwonlyparams: list[cst.Param] = []
        has_changes = False

        for param in node.params.params:
            adapted_param = adapt_param(param)
            if adapted_param is not None:
                new_parameters.append(adapted_param)
                has_changes = True
            else:
                new_parameters.append(param)

        for param in node.params.kwonly_params:
            adapted_param = adapt_param(param)
            if adapted_param is not None:
                new_kwonlyparams.append(adapted_param)
                has_changes = True
            else:
                new_kwonlyparams.append(param)

        if not has_changes:
            return

        # Sort the parameters to make sure default parameters are at the end
        # Preserve the original comma formats
        new_parameters = sort_params_preserving_spacing(new_parameters)
        new_kwonlyparams = sort_params_preserving_spacing(new_kwonlyparams)

        logger.debug(
            f"Converted {node.name.value} parameters: {new_parameters} * {new_kwonlyparams}"
        )

        self.context.scratch[node] = node.with_changes(
            params=node.params.with_changes(
                params=new_parameters, kwonly_params=new_kwonlyparams
            )
        )

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        new_node = self.context.scratch.get(original_node, updated_node)
        if original_node in self.context.scratch:
            AddImportsVisitor.add_needed_import(self.context, "typing", "Annotated")
        return new_node

