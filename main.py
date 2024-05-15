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


# Function to fetch data from an external API
def fetch_data_one(task_id):
    print(f'Fucntion 1. task id : {task_id}')
    url = "https://www.google.com"
    response = requests.get(url)
    print(response.status_code)
    

def fetch_data_two(task_id):
    print(f'Fucntion 2. task id : {task_id}')
    url = "https://www.google.com"
    response = requests.get(url)
    print(response.status_code)
    

def fetch_data_three(task_id):
    print(f'Fucntion 3. task id : {task_id}')
    url = "https://www.google.com"
    response = requests.get(url)
    print(response.status_code)
   

def fetch_data_four(task_id):
    print(f'Fucntion 4. task id : {task_id}')
    url = "https://www.google.com"
    response = requests.get(url)
    print(response.status_code)
   
   


# Function to simulate a task
def task(task_id):
    print(f"Task {task_id} started")
    stop_flag = stop_flags.get(task_id, False)
    pause_flag = pause_flags.get(task_id, False)
    pause_lock = pause_locks[task_id]

    while not stop_flag:
        print(f"Task {task_id} running...")
        
        with pause_lock:
            while pause_flag:
                print(f"Task {task_id} paused...")
                time.sleep(1)
                pause_flag = pause_flags.get(task_id, False)
                if pause_flag:
                    print(f"Task {task_id} still paused...")

            fetch_data_one(task_id)
            time.sleep(5)
            fetch_data_two(task_id)
            time.sleep(5)
            fetch_data_three(task_id)
            time.sleep(5)
            fetch_data_four(task_id)
            time.sleep(1)

            
            stop_flags[task_id] = True

        stop_flag = stop_flags.get(task_id, False)
        pause_flag = pause_flags.get(task_id, False)

    print(f"Task {task_id} stopped")
    return f"Task {task_id} result"


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
    future = executor.submit(task, task_id)
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
