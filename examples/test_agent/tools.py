"""Tool definitions and execution for the test agent."""

from __future__ import annotations

import ast
import operator
from typing import Any

from examples.test_agent.llm import ChatClient, Message

# Tool definitions in OpenAI function calling format
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information. Returns search results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression. Supports +, -, *, /, **, (), and common math functions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate (e.g., '2 + 3 * 4')",
                    },
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Explicitly store a fact in memory for later recall. Use this when the user asks you to remember something specific.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "The fact to remember",
                    },
                },
                "required": ["fact"],
            },
        },
    },
]


class ToolExecutor:
    """Executes tools for the agent."""

    def __init__(self, llm_client: ChatClient) -> None:
        self._llm_client = llm_client
        self._remembered_facts: list[str] = []

    async def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool and return the result.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result as string
        """
        if name == "web_search":
            return await self._web_search(arguments.get("query", ""))
        elif name == "calculator":
            return self._calculator(arguments.get("expression", ""))
        elif name == "remember":
            return self._remember(arguments.get("fact", ""))
        else:
            return f"Error: Unknown tool '{name}'"

    async def _web_search(self, query: str) -> str:
        """Stub web search using LLM to generate plausible results."""
        if not query:
            return "Error: No query provided"

        prompt = f"""You are simulating a web search. Generate 3 plausible search results for the query: "{query}"

Format each result as:
1. [Title] - Brief description/snippet

Be realistic and helpful. The results should be relevant to the query."""

        response = await self._llm_client.chat([Message(role="user", content=prompt)])

        return f"Search results for '{query}':\n\n{response.content}"

    def _calculator(self, expression: str) -> str:
        """Safely evaluate a mathematical expression."""
        if not expression:
            return "Error: No expression provided"

        # Allowed operators
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def _eval(node: ast.AST) -> float:
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return float(node.value)
                raise ValueError(f"Unsupported constant: {node.value}")
            elif isinstance(node, ast.BinOp):
                op_type = type(node.op)
                if op_type not in allowed_operators:
                    raise ValueError(f"Unsupported operator: {op_type.__name__}")
                left = _eval(node.left)
                right = _eval(node.right)
                return allowed_operators[op_type](left, right)
            elif isinstance(node, ast.UnaryOp):
                op_type = type(node.op)
                if op_type not in allowed_operators:
                    raise ValueError(f"Unsupported operator: {op_type.__name__}")
                operand = _eval(node.operand)
                return allowed_operators[op_type](operand)
            elif isinstance(node, ast.Expression):
                return _eval(node.body)
            else:
                raise ValueError(f"Unsupported expression: {type(node).__name__}")

        try:
            tree = ast.parse(expression, mode="eval")
            result = _eval(tree)
            return f"{expression} = {result}"
        except (ValueError, SyntaxError, ZeroDivisionError) as e:
            return f"Error evaluating '{expression}': {e}"

    def _remember(self, fact: str) -> str:
        """Remember a fact (will be ingested with special marker)."""
        if not fact:
            return "Error: No fact provided"

        self._remembered_facts.append(fact)
        return f"Remembered: {fact}"

    def get_pending_facts(self) -> list[str]:
        """Get and clear pending facts to be ingested."""
        facts = self._remembered_facts.copy()
        self._remembered_facts.clear()
        return facts
