"""A tiny app so the GitHub Actions demo has something to run and test."""


def add(a, b):
    """Return the sum of a & b."""
    return a + b


def multiply(a, b):
    """Return the product of a and b."""
    return a * b


def is_even(number):
    """Return True if number is even, otherwise False."""
    return number % 2 == 0


def main():
    """Print a few results so `python -m src.app` shows output."""
    print("add(2, 3)      =", add(2, 3))
    print("multiply(2, 3) =", multiply(2, 3))
    print("is_even(4)     =", is_even(4))
    print("is_even(7)     =", is_even(7))


if __name__ == "__main__":
    main()
