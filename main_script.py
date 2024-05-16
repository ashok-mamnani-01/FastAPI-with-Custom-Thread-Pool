import concurrent.futures
import threading
import time

class CustomThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    def __init__(self, max_workers=None):
        super().__init__(max_workers=max_workers)
        self._paused = threading.Event()
        self._pause_lock = threading.Lock()

    def pause(self):
        with self._pause_lock:
            self._paused.set()

    def resume(self):
        with self._pause_lock:
            self._paused.clear()

    def submit_paused(self, func, *args, **kwargs):
        self._paused.wait()
        return self.submit(func, *args, **kwargs)

# Function to simulate a task
def task(n):
    print(f"Task {n} started")
    time.sleep(2)  # Simulate some work
    print(f"Task {n} finished")
    return f"Task {n} result"

def main():
    # Create a CustomThreadPoolExecutor with 3 worker threads
    with CustomThreadPoolExecutor(max_workers=3) as executor:
        # Submit tasks to the thread pool
        futures = [executor.submit(task, i) for i in range(5)]

        # Pause the thread pool
        print("Pausing thread pool...")
        executor.pause()

        # Wait for 5 seconds to simulate pausing
        time.sleep(5)

        # Resume the thread pool
        print("Resuming thread pool...")
        executor.resume()

        # Wait for all tasks to complete
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # Print results
    print("All tasks completed:")
    for result in results:
        print(result)

if __name__ == "__main__":
    main()
