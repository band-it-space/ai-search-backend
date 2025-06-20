import openai
import json
import threading
from threading import Thread
from typing import List, Dict, Optional
from time import sleep
from utils.logging import setup_logger

logger = setup_logger("debug")


class Task:
    def __init__(
        self,
        task_id: str,
        assistant_id: str,
        openai_api_key: str,
        lines: List[str],
        function_name: str,
    ):
        self.id = task_id
        self.assistant_id = assistant_id
        self.api_key = openai_api_key
        self.lines = lines
        self.function_name = function_name
        self.response: Optional[List[Dict]] = None
        self.error: Optional[str] = None
        self.thread: Optional[Thread] = None
        self._lock = threading.Lock()

    def run(self):
        def target():
            try:
                client = openai.OpenAI(api_key=self.api_key)
                logger.info(f"Running Task {self.id}")
                message = {
                    "role": "user",
                    "content": "\n".join(f"{i+1}. {line}" for i, line in enumerate(self.lines))
                }

                run = client.beta.threads.create_and_run(
                    assistant_id=self.assistant_id,
                    thread={"messages": [message]},
                    tool_choice={"type": "function", "function": {"name": self.function_name}}
                )

                thread_id = run.thread_id
                run_id = run.id

                while True:
                    status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                    logger.info(f"Task {self.id} status: {status.status}")

                    if status.status == "requires_action":
                        tool_calls = status.required_action.submit_tool_outputs.tool_calls
                        parsed_results = []

                        for call in tool_calls:
                            logger.info(f"Assistant called function: {call.function.name}")
                            logger.info(f"Function arguments:\n{call.function.arguments}")
                            try:
                                args = json.loads(call.function.arguments)
                                parsed_results.append(args)
                            except Exception as e:
                                logger.warning(f"Failed to parse function arguments: {e}")

                        with self._lock:
                            self.response = parsed_results

                        client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run_id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call.id,
                                    "output": json.dumps({"ack": True})
                                }
                                for call in tool_calls
                            ]
                        )

                    if status.status in ("completed", "failed", "expired"):
                        break

                    sleep(1)

            except Exception as e:
                with self._lock:
                    self.error = str(e)

        self.thread = Thread(target=target)
        self.thread.start()

    def join(self):
        if self.thread:
            self.thread.join()

    def get_result(self) -> Dict:
        with self._lock:
            return {
                "id": self.id,
                "function": self.function_name,
                "response": self.response,
                "error": self.error
            }

class AssistantManager:
    def __init__(self, assistant_id: str, openai_api_key: str):
        self.assistant_id = assistant_id
        self.api_key = openai_api_key
        self._queue: List[Task] = []
        self.tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()
        self._runner_thread = Thread(target=self._run_queue_loop, daemon=True)
        self._runner_thread.start()

    def add_task(self, task_id: str, lines: List[str], function_name: str):
        task = Task(
            task_id=task_id,
            assistant_id=self.assistant_id,
            openai_api_key=self.api_key,
            lines=lines,
            function_name=function_name,
        )
        with self._lock:
            self._queue.append(task)
            self.tasks[task_id] = task
        return task.id

    def _run_queue_loop(self):
        while True:
            task = None
            with self._lock:
                if self._queue:
                    task = self._queue.pop(0)

            if task:
                task.run()
                task.join()
                logger.info(f"Task {task.id} completed")
            else:
                sleep(1)

    def get_task_result(self, task_id: str) -> Optional[Dict]:
        task = self.tasks.get(task_id)
        if task:
            return task.get_result()
        return None

    def clear_tasks(self):
        with self._lock:
            self._queue.clear()
            self.tasks.clear()
