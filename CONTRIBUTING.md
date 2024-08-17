# Contributing to DocsBot

First off, thank you for considering contributing to DocsBot! It's people like you that make DocsBot such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct (to be developed).

## Understanding Our Constraints

We want to be transparent about the constraints we faced during the initial development:

- Limited infrastructure
- Resource availability challenges
- Tight timeframes

Despite these constraints, we've strived to adhere to coding standards as much as possible. However, we acknowledge that there's significant room for improvement, and we welcome your suggestions and contributions.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for DocsBot. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

- Use a clear and descriptive title for the issue to identify the problem.
- Describe the exact steps which reproduce the problem in as many details as possible.
- Provide specific examples to demonstrate the steps.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for DocsBot, including completely new features and minor improvements to existing functionality.

- Use a clear and descriptive title for the issue to identify the suggestion.
- Provide a step-by-step description of the suggested enhancement in as many details as possible.
- Provide specific examples to demonstrate the steps or point out the part of DocsBot where the enhancement could be implemented.
- Explain why this enhancement would be useful to most DocsBot users.

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible.
- Follow the JavaScript and Python styleguides.
- End all files with a newline

## Styleguides and Coding Standards

While we had to make some exceptions in our initial release due to constraints, we are now focusing on maintaining high coding standards. Please adhere to the following guidelines:

### General Rules

- Create packages for dedicated functionalities
- Use snake_case for all names (variables, functions, etc.) except Class names, which should use PascalCase
- Use TODO comments for future implementation ideas
- Ensure function signatures clearly indicate return types and parameter types
- Use descriptive names for functions and parameters that reflect their purpose
- Include a brief docstring for each function explaining its purpose, inputs, and outputs
- Use Union types (e.g., `Union[int, float]` or `int | float`) when a variable can be of multiple types
- Use Optional types (e.g., `Optional[int]`) when a variable can be None
- Prefer the `|` syntax for Union types where possible (e.g., `int | float` instead of `Union[int, float]`)
- Avoid deeply nested logic; prefer flat, readable code structures
- Add high-level comments to functions explaining:
  - The purpose of input parameters
  - The overall function behavior
  - Expected return values
- Keep functions focused and concise; aim for single responsibility
- Use type hints in Python to improve code readability and catch potential type-related errors early
- Write self-documenting code where possible, using clear variable and function names

Example of a well-documented function:

```python
def calculate_total_price(item_prices: List[float], discount_percentage: float = 0.0) -> float:
    """
    Calculate the total price of items after applying a discount.

    Args:
    item_prices (List[float]): A list of individual item prices
    discount_percentage (float): The discount to apply, expressed as a percentage (default: 0.0)

    Returns:
    float: The total price after applying the discount

    Raises:
    ValueError: If discount_percentage is not between 0 and 100
    """
    if not 0 <= discount_percentage <= 100:
        raise ValueError("Discount percentage must be between 0 and 100")

    total = sum(item_prices)
    discounted_total = total * (1 - discount_percentage / 100)
    return round(discounted_total, 2)
```

Example of a function with optional parameter

```python
def greet(name: Optional[str] = None) -> str:
    if name is None:
        return "Hello, stranger!"
    return f"Hello, {name}!"
```

Example Union

```python
numeric_value: Union[int, float] = 5  # Can also be written as `numeric_value: int | float = 5`
optional_greeting: Optional[str] = 'hello'  # This is equivalent to `Union[str, None]`
```

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### JavaScript Styleguide

All JavaScript must adhere to [JavaScript Standard Style](https://standardjs.com/).

### Python Styleguide

All Python must adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/).

### Code Quality Expectations

While we understand that the initial codebase may not be perfect due to our constraints, we expect all new contributions to maintain a high standard of code quality. This includes:

- Following the established coding conventions
- Writing clear, self-documenting code
- Providing appropriate comments and documentation
- Follow the guidance provided in general rules
- Writing unit tests for new functionality

Remember, the goal is to make the codebase easy for others to follow and contribute to. We're committed to improving the overall quality of the project, and your contributions play a crucial role in this effort.

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

* `bug` - Issues that are bugs.
* `enhancement` - Issues that are feature requests.
* `documentation` - Issues or pull requests related to documentation.
* `good first issue` - Good for newcomers.

## Getting Started

For information on how to set up the project locally, please refer to the README.md file.

Thank you for contributing to DocsBot! Your efforts to maintain and improve our code standards are greatly appreciated.