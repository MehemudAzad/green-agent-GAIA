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

"""Purple Advanced Agent: Hierarchical multi-agent system for GAIA benchmark.

This package implements a sophisticated purple agent with specialized sub-agents:
- Web Search Agent: Finds information online
- Deep Analyzer Agent: Analyzes complex multi-step problems
- Calculator Agent: Performs mathematical computations

The architecture follows the DeepResearchAgent pattern with a coordinator
that orchestrates specialized sub-agents.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from . import agent
from .agent import root_agent, gaia_coordinator

__all__ = ["agent", "root_agent", "gaia_coordinator"]
