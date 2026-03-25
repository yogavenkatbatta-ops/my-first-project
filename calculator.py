# Simple Calculator in Python
# Supports: + - * / % ** // √ ^ sin cos tan log log10 π e ( ) and numbers

import math

def show_help():
    print("\nSupported operations and symbols:")
    print("  +   -   *   /   %   **   //")
    print("  ^      (means power, same as **)")
    print("  √ or sqrt     (square root)")
    print("  sin cos tan   (angles in radians)")
    print("  log     (natural log = ln)")
    print("  log10         (base-10 logarithm)")
    print("  pi  or  π     (3.14159...)")
    print("  e             (2.71828...)")
    print("  ( )           (parentheses for order)")
    print("  q or quit     → exit program\n")


def safe_eval_expression(expr):
    # Replace friendly symbols with Python-understandable ones
    expr = expr.replace('^', '**')
    expr = expr.replace('√', 'math.sqrt')
    expr = expr.replace('π', 'math.pi')
    expr = expr.replace('pi', 'math.pi')
    expr = expr.replace('e', 'math.e')  # careful - 'e' also appears in numbers

    # We create safe environment with only math functions
    safe_dict = {
        "__builtins__": {},     # block dangerous built-ins
        "math": math
    }

    try:
        result = eval(expr, safe_dict)
        return result
    except NameError:
        return "Error: Unknown function or variable"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {str(e)}"


print("┌──────────────────────────────┐")
print("│      Simple Calculator       │")
print("└──────────────────────────────┘")
print("   Type 'help' to see commands")
print("   Type 'q' or 'quit' to exit\n")

while True:
    user_input = input("➤ ").strip()

    if user_input.lower() in ['q', 'quit', 'exit']:
        print("Goodbye! 👋")
        break

    if user_input.lower() == 'help':
        show_help()
        continue

    if user_input == '':
        continue

    result = safe_eval_expression(user_input)

    # Format nice output
    if isinstance(result, (int, float)):
        if result == int(result):  # clean integer display
            print(f"  = {int(result)}")
        else:
            print(f"  = {result:.8g}")   # nice float, no too many decimals
    else:
        print(" ", result)