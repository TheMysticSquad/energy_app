import time, functools

def retry(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        delay = 1
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Retry {attempt+1} failed: {e}")
                time.sleep(delay)
                delay *= 2
        raise Exception("Max retries exceeded")
    return wrapper
