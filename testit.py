#!/usr/bin/env python3

def fibonacci(n):
    """Generate Fibonacci sequence up to n terms"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        next_num = fib_sequence[-1] + fib_sequence[-2]
        fib_sequence.append(next_num)
    
    return fib_sequence

def fibonacci_recursive(n):
    """Calculate nth Fibonacci number recursively"""
    if n <= 0:
        return None
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

def main():
    # Demonstrate iterative approach
    print("Fibonacci Sequence (Iterative):")
    print("First 10 numbers:", fibonacci(10))
    print("First 20 numbers:", fibonacci(20))
    
    print("\nFibonacci Numbers (Recursive):")
    for i in range(1, 11):
        print(f"F({i}) = {fibonacci_recursive(i)}")
    
    # Generate sequence until a limit
    print("\nFibonacci numbers less than 1000:")
    fib_list = []
    a, b = 0, 1
    while a < 1000:
        fib_list.append(a)
        a, b = b, a + b
    print(fib_list)

if __name__ == "__main__":
    main()