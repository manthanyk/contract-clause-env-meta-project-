from models import MyAction, MyObservation
from typing import Tuple
from tasks.base import BaseTask

class EasyTask(BaseTask):
    """
    Easy task: Find a specific item in a small collection
    Grader: Based on proximity to target item
    """

    def __init__(self):
        super().__init__(max_steps=10, difficulty="easy")
        self.target = None

    async def reset(self) -> MyObservation:
        # Initialize easy task state
        self.target = self._generate_easy_target()
        self.current_state = self._init_state()
        self.step_count = 0
        return MyObservation(
            current_state=self.current_state,
            available_actions=self._get_available_actions(),
            task_description=f"Easy task: Find the item '{self.target}' among 5 items"
        )

    async def step(self, action: MyAction) -> Tuple[MyObservation, float, bool]:
        return await super().step(action)

    def _generate_easy_target(self):
        """Generate a simple target for the easy task"""
        return "item_3"

    def _init_state(self):
        """Initialize the environment state"""
        return {
            "items": ["item_1", "item_2", "item_3", "item_4", "item_5"],
            "current_position": 0,
            "found_item": None
        }

    def _get_available_actions(self):
        """Get list of available actions"""
        return ["move_left", "move_right", "select_current", "check_item"]

    def _apply_action(self, action: MyAction):
        """Apply the action to the current state"""
        state = self.current_state.copy()

        if action.action_type == "move_left":
            state["current_position"] = max(0, state["current_position"] - 1)
        elif action.action_type == "move_right":
            state["current_position"] = min(len(state["items"]) - 1, state["current_position"] + 1)
        elif action.action_type == "select_current":
            current_item = state["items"][state["current_position"]]
            state["found_item"] = current_item
        elif action.action_type == "check_item":
            # This action doesn't change state but might provide info
            pass

        return state

    def _grade(self) -> float:
        state = self.current_state
        target = self.target
        """
        Grade the current state based on proximity to target
        Returns a value between 0.0 and 1.0
        """
        if state["found_item"] == target:
            return 1.0
        elif state["found_item"] is not None:
            # Wrong item selected
            return 0.1

        # Calculate proximity based on distance to target
        items = state["items"]
        try:
            target_index = items.index(target)
            current_index = state["current_position"]
            max_distance = len(items) - 1
            distance = abs(target_index - current_index)

            # Convert distance to reward (closer = higher reward)
            if max_distance == 0:
                return 1.0
            return 1.0 - (distance / max_distance)
        except ValueError:
            # Target not in items
            return 0.0

    def _get_hint(self, reward: float) -> str:
        """Provide a hint based on the current reward"""
        if reward >= 0.9:
            return "You're very close to the target!"
        elif reward >= 0.7:
            return "You're getting closer to the target."
        elif reward >= 0.5:
            return "You're halfway there."
        elif reward >= 0.3:
            return "You're making some progress."
        else:
            return "Keep searching for the target."

