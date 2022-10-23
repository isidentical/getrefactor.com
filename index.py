import ast
import refactor
import traceback

import panel as pn

pn.config.sizing_mode = "stretch_both"
pn.extension()


def _format_with_refactor(rule_code: str, source_code: str) -> str:
    ast.parse(source_code)

    namespace = {}
    exec(rule_code, namespace)

    rules = [
        maybe_rule
        for maybe_rule in namespace.values()
        if isinstance(maybe_rule, type)
        if issubclass(maybe_rule, refactor.Rule)
        if maybe_rule is not refactor.Rule
    ]

    lines = []

    if rules:
        lines.append("# Active rules: " + ", ".join(rule.__name__ for rule in rules))
        lines.append("")
        lines.append("")
        session = refactor.Session(rules=rules)
        lines.append(session.run(source_code))
    else:
        lines.append("# No rules found.")
        lines.append(
            "# Consider writing some rules (a class that inherits from refactor.Rule)"
        )

    return "\n".join(lines)


def run_refactor(
    rule_code: str,
    source_code: str,
) -> pn.widgets.Ace:
    try:
        refactored_source = _format_with_refactor(rule_code, source_code)
        language = "python"
    except Exception:
        refactored_source = traceback.format_exc()
        language = "text"

    return pn.widgets.Ace(
        value=refactored_source,
        language=language,
        readonly=True,
    )


refactor_template = """\
import ast
from refactor import Rule, Replace
from refactor.context import Scope

class FoldMyConstants(Rule):
    def match(self, node: ast.AST) -> Replace:
        # Look for an arithmetic addition or subtraction
        assert isinstance(node, ast.BinOp)
        assert isinstance(op := node.op, (ast.Add, ast.Sub))

        # Where both left and right are constants
        assert isinstance(left := node.left, ast.Constant)
        assert isinstance(right := node.right, ast.Constant)

        # And then replace it with the result of the computation
        if isinstance(op, ast.Add):
            result = ast.Constant(left.value + right.value)
        else:
            result = ast.Constant(left.value - right.value)
        return Replace(node, result)

class PropagateMyConstants(Rule):
    context_providers = (Scope,)

    def match(self, node: ast.AST) -> Replace:
        # Look for a variable
        assert isinstance(node, ast.Name)
        assert isinstance(node.ctx, ast.Load)

        # Try to see if we can find its definition
        scope = self.context.scope.resolve(node)
        definitions = scope.get_definitions(node.id)
        assert len(definitions) == 1

        # The definition might be anything, it might be coming
        # from an import or it might be function. So we'll only
        # allow assignments.
        [definition] = definitions
        assert isinstance(definition, ast.Assign)

        # Replace the definition with its value, if the definition
        # itself is a constant.
        assert isinstance(defined_value := definition.value, ast.Constant)
        return Replace(node, defined_value)
"""

source_code = """\
PI = 3.14
TAU = PI + PI

# This is a very interesting constant that can
# solve world's all problems.
WEIRD_MATH_CONSTANT = PI + TAU

def make_computation(x: int, y: int, z: int) -> float:
    result = (
        WEIRD_MATH_CONSTANT * 2 + (5 + 3) # A very complex math equation
    ) + 8 # Don't forget the 8 here

    # This would help us find the point of origin
    result += 2 + 1

    return 3.14 - 6.28 + result + z * 2
"""

rule_editor = pn.widgets.Ace(
    value=refactor_template,
    language="python",
)
source_editor = pn.widgets.Ace(
    value=source_code,
    language="python",
)

result_editor = pn.bind(run_refactor, rule_editor, source_editor)


docs_button = pn.widgets.Button(name="Go to docs", button_type="primary", width=100)
docs_button.js_on_click(code="window.open('https://refactor.readthedocs.io')")
follow_tutorial_button = pn.widgets.Button(
    name="Introduction Tutorial", button_type="primary", width=150
)
follow_tutorial_button.js_on_click(
    code="window.open('https://refactor.readthedocs.io/en/latest/tutorials/exploring-rules.html')"
)
github_button = pn.widgets.Button(name="GitHub", button_type="primary", width=100)
github_button.js_on_click(code="window.open('https://github.com/isidentical/refactor')")

app_row = pn.Row(rule_editor, source_editor, result_editor)


bootstrap = pn.template.MaterialTemplate(title="Try Refactor")
bootstrap.header.append(pn.Row(docs_button, follow_tutorial_button, github_button))
bootstrap.main.append(app_row)
bootstrap.servable()
