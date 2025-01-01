import multiprocessing
import math

def get_optimal_workers():
    cores = multiprocessing.cpu_count()
    # Using common formula: (2 * cores) + 1
    optimal = (2 * cores) + 1
    
    # Cap at reasonable maximum
    return min(optimal, 8)

if __name__ == "__main__":
    workers = get_optimal_workers()
    print(f"Number of CPU cores: {multiprocessing.cpu_count()}")
    print(f"Recommended number of workers: {workers}")