import time
import functools
import inspect

def time_logger(func):
    """
    A smart decorator that measures execution time for BOTH 
    synchronous and asynchronous (async def) functions!
    """
    
    if inspect.iscoroutinefunction(func):
        # 1. Traffic Cop sees an ASYNC function (like the AI Worker)
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs) # We must AWAIT it!
            elapsed = time.time() - start
            print(f"[TIMER] {func.__name__} took {elapsed:.4f} seconds")
            return result
        return async_wrapper
        
    else:
        # 2. Traffic Cop sees a NORMAL function (like the API routes)
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs) # Normal execution
            elapsed = time.time() - start
            print(f"[TIMER] {func.__name__} took {elapsed:.4f} seconds")
            return result
        return sync_wrapper
