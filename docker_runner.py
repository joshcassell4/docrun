#!/usr/bin/env python3
"""Run Docker containers in parallel using threads and subprocess."""

import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from typing import List, Tuple, Optional
import os

def run_docker_container(command: str) -> Tuple[int, Optional[str], Optional[str]]:
    """
    Run a single Docker container with echo command.
    
    Args:
        index: The string to prompt the container with
        
    Returns:
        Tuple of (index, stdout, stderr)
    """
    cmd = [
        "docker", "run",
        "-u", "coder",
        "-v", f"{os.getcwd()}:/home/coder/project",
        "-w", "/home/coder/project",
        "--rm", 
        "py-cl-7",
        "sh", "-c", f"echo '{command}'"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return (index, result.stdout.strip(), None)
    except subprocess.CalledProcessError as e:
        return (index, None, f"Error: {e.stderr.strip()}")
    except Exception as e:
        return (index, None, f"Error: {str(e)}")


def run_containers_parallel(num_containers: int, commands: List[str]) -> List[Tuple[int, Optional[str], Optional[str]]]:
    """
    Run multiple Docker containers in parallel.
    
    Args:
        num_containers: Number of containers to run
        
    Returns:
        List of results (index, stdout, stderr) for each container
    """
    results = []
    
    # Use ThreadPoolExecutor to run containers in parallel
    with ThreadPoolExecutor(max_workers=num_containers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(run_docker_container, i): i 
            for i in commands
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_index):
            result = future.result()
            results.append(result)
    
    # Sort results by index for consistent output
    results.sort(key=lambda x: x[0])
    return results


def aggregate_and_display_results(results: List[Tuple[int, Optional[str], Optional[str]]]) -> None:
    """
    Aggregate and display results from all containers.
    
    Args:
        results: List of (index, stdout, stderr) tuples
    """
    print("\n" + "="*50)
    print("DOCKER CONTAINER RESULTS")
    print("="*50 + "\n")
    
    successful_runs = 0
    failed_runs = 0
    
    for index, stdout, stderr in results:
        if stdout:
            print(f"Container {index}: SUCCESS")
            print(f"  Output: {stdout}")
            successful_runs += 1
        else:
            print(f"Container {index}: FAILED")
            print(f"  Error: {stderr}")
            failed_runs += 1
        print()
    
    print("="*50)
    print(f"SUMMARY: {successful_runs} successful, {failed_runs} failed")
    print("="*50)


def main():
    """Main entry point for the application."""
    # Default number of containers
    num_containers = 5
    
    # Check if a number was provided as command line argument
    if len(sys.argv) > 1:
        try:
            num_containers = int(sys.argv[1])
            if num_containers < 1:
                raise ValueError("Number must be positive")
        except ValueError as e:
            print(f"Invalid argument: {e}")
            print(f"Usage: {sys.argv[0]} [number_of_containers]")
            sys.exit(1)
    
    print(f"Running {num_containers} Docker containers in parallel...")
    
    commands = ["test 1",
                "test 2",
                "test 3"]
    
    # Run containers in parallel
    results = run_containers_parallel(num_containers, commands)
    
    # Display aggregated results
    aggregate_and_display_results(results)


if __name__ == "__main__":
    main()