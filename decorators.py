import time
import functools

def time_logger(func):
    @functools.wraps(func)  # This preserves the original function's name and docstring
    def wrapper(*args, **kwargs):
        start = time.time()
        
        # Run the actual function
        result = func(*args, **kwargs)
        
        elapsed = time.time() - start
        print(f"[TIMER] {func.__name__} took {elapsed:.4f} seconds")
        
        return result
    return wrapper
