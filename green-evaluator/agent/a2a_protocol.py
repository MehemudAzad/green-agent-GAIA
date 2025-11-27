# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A2A Protocol: Agent-to-Agent communication interface."""

import logging
import time
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .schemas import A2ATask, A2AResponse

logger = logging.getLogger(__name__)


class A2AProtocol:
    """HTTP-based A2A protocol for communicating with purple agents."""
    
    def __init__(
        self, 
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5
    ):
        """Initialize the A2A protocol client.
        
        Args:
            base_url: Base URL of the purple agent (e.g., "http://localhost:8080")
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retries
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def send_task(self, task: A2ATask) -> bool:
        """Send a task to the purple agent.
        
        Args:
            task: A2ATask object containing the task details
            
        Returns:
            True if task was successfully sent, False otherwise
        """
        url = f"{self.base_url}/a2a/task"
        
        try:
            response = self.session.post(
                url,
                json=task.model_dump(),
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Successfully sent task {task.task_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send task {task.task_id}: {e}")
            return False
    
    def receive_response(
        self, 
        task_id: str,
        max_wait_time: int = 60,
        poll_interval: float = 1.0
    ) -> Optional[A2AResponse]:
        """Poll for a response from the purple agent.
        
        Args:
            task_id: Task identifier to poll for
            max_wait_time: Maximum time to wait for response in seconds
            poll_interval: Time between polls in seconds
            
        Returns:
            A2AResponse object if received, None if timeout or error
        """
        url = f"{self.base_url}/a2a/response/{task_id}"
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = self.session.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    a2a_response = A2AResponse(**data)
                    logger.info(f"Successfully received response for task {task_id}")
                    return a2a_response
                elif response.status_code == 404:
                    # Response not ready yet, continue polling
                    logger.debug(f"Response not ready for task {task_id}, polling...")
                    time.sleep(poll_interval)
                else:
                    logger.error(f"Unexpected status code {response.status_code} for task {task_id}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error polling for response {task_id}: {e}")
                return None
        
        logger.warning(f"Timeout waiting for response to task {task_id}")
        return None
    
    def send_and_receive(
        self, 
        task: A2ATask,
        max_wait_time: int = 60
    ) -> Optional[A2AResponse]:
        """Send a task and wait for the response.
        
        Args:
            task: A2ATask object containing the task details
            max_wait_time: Maximum time to wait for response in seconds
            
        Returns:
            A2AResponse object if successful, None otherwise
        """
        if not self.send_task(task):
            return None
        
        return self.receive_response(task.task_id, max_wait_time=max_wait_time)
    
    def health_check(self) -> bool:
        """Check if the purple agent is healthy and responsive.
        
        Returns:
            True if agent is healthy, False otherwise
        """
        url = f"{self.base_url}/health"
        
        try:
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def close(self) -> None:
        """Close the session and cleanup resources."""
        self.session.close()
