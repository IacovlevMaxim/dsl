from typing import Union
from eyed3 import AudioFile
import eyed3
import exiftool

from src.utils.image_metadata import metadata_prefix
from src.utils.variable_type import VariableType
from src.interpreter.exceptions.break_exception import BreakException
from src.interpreter.exceptions.infinte_loop_exception import InfiniteLoopException

variables = {}


class Variable:
    def __init__(self, name: str, var_type: VariableType, value: Union[int, float, str, AudioFile] = None):
        self.name = name
        self.type = var_type
        self.value = value


class ASTNode:
    """Base class for all AST nodes"""

    def eval(self):
        raise NotImplementedError("Subclasses must implement eval()")


class Program(ASTNode):
    """Represents a program (sequence of statements)"""

    def __init__(self, statements):
        self.statements = statements

    def eval(self):
        for stmt in self.statements:
            stmt.eval()


class VariableDeclaration(ASTNode):
    """Represents variable declaration"""

    def __init__(self, var_type, name, value_expr):
        self.var_type = var_type
        if var_type == VariableType.UNKNOWN:
            raise SyntaxError(f"Unknown variable type for variable '{name}'. Invalid or unsupported extension?")

        self.name = name
        self.value_expr = value_expr

    def eval(self):
        value = self.value_expr.eval()
        variables[self.name] = Variable(self.name, self.var_type, value)
        return variables[self.name]


class Assignment(ASTNode):
    """Represents variable assignment"""

    def __init__(self, name, value_expr, expr_type):
        self.name = name
        self.value_expr = value_expr
        self.expr_type = expr_type

    def eval(self):
        if self.name not in variables:
            raise NameError(f"Cannot assign to '{self.name}' (not defined)")

        value = self.value_expr.eval()
        if variables[self.name].type != self.expr_type:
            raise TypeError(f"Value '{value}' is not of variable type '{self.name}'")

        variables[self.name].value = value
        return value


class BinaryOperation(ASTNode):
    """Represents binary operations like +, ==, >, etc."""

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def eval(self):
        left_val = self.left.eval()
        right_val = self.right.eval()

        if self.op == '+':
            return left_val + right_val
        elif self.op == '-':
            return left_val - right_val
        elif self.op == '*':
            return left_val * right_val
        elif self.op == '/':
            if right_val == 0:
                raise ZeroDivisionError("Division by zero")
            return left_val / right_val
        elif self.op == '==':
            return left_val == right_val
        elif self.op == '>':
            return left_val > right_val
        elif self.op == '<':
            return left_val < right_val


class UnaryOperation(ASTNode):
    """Represents unary operations like NOT"""

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def eval(self):
        val = self.expr.eval()
        if self.op == 'NOT':
            return not val
        elif self.op == '-':  # Handle negative numbers
            return -val
        # Add more unary operations as needed


class Literal(ASTNode):
    """Represents literal values (numbers, strings, booleans)"""

    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value


class Identifier(ASTNode):
    """Represents variable references"""

    def __init__(self, name):
        self.name = name

    def eval(self):
        if self.name not in variables:
            raise NameError(f"Variable '{self.name}' not defined")
        return variables[self.name].value


class IfStatement(ASTNode):
    """Represents if conditional statements"""

    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def eval(self):
        if self.condition.eval():
            return self.then_branch.eval()
        elif self.else_branch:
            return self.else_branch.eval()
        return None


class WhileLoop(ASTNode):
    """Represents while loop statements"""

    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        self.max_iterations = 10000

    def eval(self):
        if not self.condition.eval():
            return None
        iterations = 0
        initial_vars = {}
        for var_name, var_obj in variables.items():
            if isinstance(var_obj.value, (int, float, bool, str)):
                initial_vars[var_name] = var_obj.value
        try:
            while self.condition.eval():
                try:
                    self.body.eval()
                except BreakException:
                    break
                iterations += 1
                if iterations >= self.max_iterations:
                    changed = False
                    for var_name, initial_value in initial_vars.items():
                        if var_name in variables and variables[var_name].value != initial_value:
                            changed = True
                            break
                    if not changed:
                        raise InfiniteLoopException("Potential infinite loop detected")
                    print(f"Warning: Loop has run {self.max_iterations} iterations")

        except InfiniteLoopException as e:
            raise InfiniteLoopException(f"Infinite loop detected: {str(e)}")
        return None


class BreakStatement(ASTNode):
    """Represents a break statement"""
    def eval(self):
        raise BreakException()


class FunctionCall(ASTNode):
    """Represents function calls like print, set_author, etc."""

    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

    def eval(self):
        args = [arg.eval() for arg in self.args]

        if self.func_name == 'print':
            for arg in self.args:
                value = arg.eval()
                # Print metadata if AUDIO_FILE
                if isinstance(arg, Identifier) and arg.name in variables:
                    var = variables[arg.name]
                    if var.type == VariableType.AUDIO_FILE:
                        tag = var.value.tag
                        print(f"title: {tag.title or 'None'}")
                        print(f"artist: {tag.artist or 'None'}")
                        print(f"album: {tag.album or 'None'}")
                        print(f"album artist: {tag.album_artist or 'None'}")
                        print(f"track: {tag.track_num[0] if tag.track_num else 'None'}")
                    elif var.type == VariableType.IMAGE_FILE:
                        metadata = var.value
                        for key, value in metadata.items():
                            print(f"{key}: {value}")
                    else:
                        print(value)
                else:
                    print(value)
        elif self.func_name == 'set':
            var_name = self.args[0].name
            var_type = variables[var_name].type

            if var_type == VariableType.AUDIO_FILE:
                setattr(variables[var_name].value.tag, args[1], args[2])
            elif var_type == VariableType.IMAGE_FILE:
                metadata = variables[var_name].value
                file_path = metadata["SourceFile"] if metadata["File:Directory"] in metadata["SourceFile"] \
                    else metadata["File:Directory"] + "/" + metadata["SourceFile"]
                key = args[1] if ":" in args[1] else f"{metadata_prefix(args[1])}:{args[1]}"
                print("key", key)
                print("file_path", file_path)
                value = args[2]
                with exiftool.ExifTool() as et:
                    try:
                        et.execute(f"-{key}={value}", file_path)
                    except exiftool.exceptions.ExifToolNotRunning:
                        print("Exiftool not running")

                variables[var_name].value[key] = value

        elif self.func_name == 'save_file':
            var_name = self.args[0].name
            if variables[var_name].type == VariableType.AUDIO_FILE:
                variables[var_name].value.tag.save()
        elif self.func_name == 'loadfile':
            path = args[0]
            if len(path.split('.')) < 2:
                raise SyntaxError(f"No file extension provided for path '{path}'")
            file_extension = path.split('.')[1]
            if file_extension == "mp3":
                file = eyed3.load(path)
            elif file_extension == "png" or file_extension == "jpg":
                with exiftool.ExifToolHelper() as et:
                    file = et.get_metadata(path)[0]
            else:
                raise SyntaxError(f"Unsupported file extension '{file_extension}'")
            return file

        elif self.func_name == 'length':
            if not isinstance(args[0], str):
                raise TypeError(f"Argument to 'length' must be a string, got {type(args[0])}")
            return len(args[0])

        elif self.func_name == 'slice':
            if not isinstance(args[0], str):
                raise TypeError(f"First argument to 'slice' must be a string, got {type(args[0])}")
            start = args[1]
            if len(args) == 3:
                length = args[2]
                return args[0][start:start + length]
            return args[0][start:]  # Slice until the end if length is not provided

        elif self.func_name == 'includes':
            if not isinstance(args[0], str) or not isinstance(args[1], str):
                raise TypeError(f"Arguments to 'includes' must be strings")
            return args[1] in args[0]

        elif self.func_name == 'startsWith':
            if not isinstance(args[0], str) or not isinstance(args[1], str):
                raise TypeError(f"Arguments to 'startsWith' must be strings")
            return args[0].startswith(args[1])

        elif self.func_name == 'endsWith':
            if not isinstance(args[0], str) or not isinstance(args[1], str):
                raise TypeError(f"Arguments to 'endsWith' must be strings")
            return args[0].endswith(args[1])
