from models import MyAction, MyObservation
from typing import Tuple
from tasks.base import BaseTask

class HardTask(BaseTask):
    """
    Hard task: Optimize resource allocation with constraints
    Grader: Based on how close to optimal allocation
    """

    def __init__(self):
        super().__init__(max_steps=30, difficulty="hard")
        self.resources = None
        self.projects = None
        self.current_allocation = None
        self._cached_optimal_value = None

    async def reset(self) -> MyObservation:
        # Initialize hard task state
        self.resources = self._generate_resources()
        self.projects = self._generate_projects()
        self.current_allocation = self._init_allocation()
        self.step_count = 0
        self._cached_optimal_value = None
        return MyObservation(
            current_state={
                "resources": self.resources,
                "projects": self.projects,
                "allocation": self.current_allocation
            },
            available_actions=self._get_available_actions(),
            task_description=f"Hard task: Allocate resources to maximize project value"
        )

    async def step(self, action: MyAction) -> Tuple[MyObservation, float, bool]:
        self.current_allocation = self._apply_action(action)
        return await super().step(action)

    def _generate_resources(self):
        """Generate available resources"""
        return {
            "developers": 10,
            "designers": 5,
            "budget": 100000
        }

    def _generate_projects(self):
        """Generate projects with resource requirements and values"""
        return [
            {"id": "project_a", "developers": 3, "designers": 2, "budget": 30000, "value": 50000},
            {"id": "project_b", "developers": 5, "designers": 1, "budget": 40000, "value": 70000},
            {"id": "project_c", "developers": 2, "designers": 3, "budget": 20000, "value": 30000},
            {"id": "project_d", "developers": 4, "designers": 2, "budget": 35000, "value": 60000},
            {"id": "project_e", "developers": 1, "designers": 1, "budget": 10000, "value": 15000}
        ]

    def _init_allocation(self):
        """Initialize the allocation state"""
        return {project["id"]: False for project in self.projects}

    def _get_available_actions(self):
        """Get list of available actions"""
        return ["allocate_project", "deallocate_project", "optimize_allocation", "check_feasibility"]

    def _apply_action(self, action: MyAction):
        """Apply the action to the current allocation"""
        allocation = self.current_allocation.copy()

        if action.action_type == "allocate_project":
            project_id = action.parameters.get("project_id")
            if project_id in allocation:
                allocation[project_id] = True

        elif action.action_type == "deallocate_project":
            project_id = action.parameters.get("project_id")
            if project_id in allocation:
                allocation[project_id] = False

        elif action.action_type == "optimize_allocation":
            # Simple greedy optimization
            allocation = self._greedy_optimization()

        elif action.action_type == "check_feasibility":
            # This action doesn't change state but might provide info
            pass

        return allocation

    def _greedy_optimization(self):
        """Perform a simple greedy optimization"""
        # Reset allocation
        allocation = {project["id"]: False for project in self.projects}

        # Sort projects by value-to-cost ratio
        projects_sorted = sorted(
            self.projects,
            key=lambda p: p["value"] / p["budget"] if p["budget"] > 0 else 0,
            reverse=True
        )

        # Allocate resources greedily
        remaining_resources = self.resources.copy()

        for project in projects_sorted:
            # Check if we can allocate this project
            if (remaining_resources["developers"] >= project["developers"] and
                remaining_resources["designers"] >= project["designers"] and
                remaining_resources["budget"] >= project["budget"]):

                # Allocate the project
                allocation[project["id"]] = True
                remaining_resources["developers"] -= project["developers"]
                remaining_resources["designers"] -= project["designers"]
                remaining_resources["budget"] -= project["budget"]

        return allocation

    def _grade(self) -> float:
        """
        Grade the current allocation based on total value and resource constraints
        Returns a value between 0.0 and 1.0
        """
        # Calculate total value of allocated projects
        total_value = 0
        total_developers = 0
        total_designers = 0
        total_budget = 0

        for project in self.projects:
            if self.current_allocation.get(project["id"], False):
                total_value += project["value"]
                total_developers += project["developers"]
                total_designers += project["designers"]
                total_budget += project["budget"]

        # Check if constraints are violated
        if (total_developers > self.resources["developers"] or
            total_designers > self.resources["designers"] or
            total_budget > self.resources["budget"]):
            # Invalid allocation gets minimal reward
            return 0.1

        # Calculate maximum possible value (optimal solution) - cached
        if self._cached_optimal_value is None:
            self._cached_optimal_value = self._calculate_optimal_value(self.projects, self.resources)
        max_value = self._cached_optimal_value

        # Return normalized reward
        if max_value == 0:
            return 0.0

        return min(1.0, total_value / max_value)

    def _calculate_optimal_value(self, projects, resources):
        """
        Calculate the optimal value using dynamic programming approach
        For simplicity, we'll use a greedy approximation here
        """
        # Simple greedy approach for estimating maximum value
        temp_resources = resources.copy()
        max_value = 0
        projects_sorted = sorted(
            projects,
            key=lambda p: p["value"] / p["budget"] if p["budget"] > 0 else 0,
            reverse=True
        )

        for project in projects_sorted:
            if (temp_resources["developers"] >= project["developers"] and
                temp_resources["designers"] >= project["designers"] and
                temp_resources["budget"] >= project["budget"]):

                max_value += project["value"]
                temp_resources["developers"] -= project["developers"]
                temp_resources["designers"] -= project["designers"]
                temp_resources["budget"] -= project["budget"]

        return max_value if max_value > 0 else 1.0

    def _get_hint(self, reward: float) -> str:
        """Provide a hint based on the current reward"""
        if reward >= 0.9:
            return "Your allocation is nearly optimal!"
        elif reward >= 0.7:
            return "Your allocation is quite good."
        elif reward >= 0.5:
            return "Your allocation is reasonable but could be improved."
        elif reward >= 0.3:
            return "Your allocation needs significant improvement."
        else:
            return "Your allocation is inefficient. Try reallocating resources."

