import concurrent.futures
import threading
import time
import requests
from fastapi import FastAPI

app = FastAPI()

# Global variables
task_executor = None
task_id_counter = 0
task_futures = {}
stop_flags = {}
pause_flags = {}
pause_locks = {}


# Custom thread pool executor with pause, resume, and stop functionality
class CustomThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    def __init__(self, max_workers=None):
        super().__init__(max_workers=max_workers)
        self._paused = threading.Event()
        self._stop = threading.Event()

    def pause(self):
        self._paused.set()

    def resume(self):
        self._paused.clear()

    def stop_all_tasks(self):
        for future in task_futures.values():
            future.cancel()
        task_futures.clear()

# Decorator function to handle task stop, pause, and resume functionality
def task_control_decorator(func):
    def wrapper(task_id, *args, **kwargs):
        print(f"Task {task_id} started")
        stop_flag = stop_flags.get(task_id, False)
        pause_flag = pause_flags.get(task_id, False)
        pause_lock = pause_locks.get(task_id, threading.Lock())

        while not stop_flag:
            print(f"Task {task_id} running...")
            
            with pause_lock:
                while pause_flag:
                    print(f"Task {task_id} paused...")
                    time.sleep(1)
                    pause_flag = pause_flags.get(task_id, False)

                # Call the original function
                func(task_id, *args, **kwargs)
                time.sleep(5)  # Simulating some work

            stop_flag = stop_flags.get(task_id, False)
            pause_flag = pause_flags.get(task_id, False)

        print(f"Task {task_id} stopped")
        return f"Task {task_id} result"
    return wrapper

# Function to fetch data from an external API
@task_control_decorator
def fetch_data(task_id):
    while True:
        print(f"Task {task_id} running...")
        time.sleep(5)
        break
    url = "https://www.google.com"
    response = requests.get(url)
    print(f"Task {task_id}. Response status code: {response.status_code}")
    stop_flags[task_id] = True

# Endpoint to start a task
@app.post("/start_task/")
def start_task():
    global task_id_counter, task_executor
    task_id_counter += 1
    task_id = task_id_counter
    executor = task_executor
    if executor is None:
        executor = CustomThreadPoolExecutor(max_workers=3)
        task_executor = executor
    future = executor.submit(fetch_data, task_id)
    task_futures[task_id] = future
    stop_flags[task_id] = False
    pause_flags[task_id] = False
    pause_locks[task_id] = threading.Lock()
    return {"task_id": task_id}

# Endpoint to stop a task
@app.put("/stop_task/{task_id}")
def stop_task(task_id: int):
    global stop_flags
    stop_flags[task_id] = True
    return {"message": f"Task {task_id} stop flag set"}

# Endpoint to pause a task
@app.put("/pause_task/{task_id}")
def pause_task(task_id: int):
    global pause_flags
    pause_flags[task_id] = True
    return {"message": f"Task {task_id} pause flag set"}

# Endpoint to resume a task
@app.put("/resume_task/{task_id}")
def resume_task(task_id: int):
    global pause_flags
    pause_flags[task_id] = False
    return {"message": f"Task {task_id} resume flag set"}