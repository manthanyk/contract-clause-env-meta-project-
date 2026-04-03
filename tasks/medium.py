from models import MyAction, MyObservation
from typing import Tuple
from tasks.base import BaseTask

class MediumTask(BaseTask):
    """
    Medium task: Sort a collection of items with multiple attributes
    Grader: Based on how well sorted the items are
    """

    def __init__(self):
        super().__init__(max_steps=20, difficulty="medium")
        self.target_order = None

    async def reset(self) -> MyObservation:
        # Initialize medium task state
        self.target_order = self._generate_target_order()
        self.current_state = self._init_state()
        self.step_count = 0
        return MyObservation(
            current_state=self.current_state,
            available_actions=self._get_available_actions(),
            task_description=f"Medium task: Sort items by priority (1=highest, 5=lowest)"
        )

    async def step(self, action: MyAction) -> Tuple[MyObservation, float, bool]:
        return await super().step(action)

    def _generate_target_order(self):
        """Generate the target order for the medium task"""
        return [
            {"id": "item_a", "priority": 1},
            {"id": "item_b", "priority": 2},
            {"id": "item_c", "priority": 3},
            {"id": "item_d", "priority": 4},
            {"id": "item_e", "priority": 5}
        ]

    def _init_state(self):
        """Initialize the environment state"""
        # Start with shuffled order
        return {
            "items": [
                {"id": "item_c", "priority": 3},
                {"id": "item_a", "priority": 1},
                {"id": "item_e", "priority": 5},
                {"id": "item_b", "priority": 2},
                {"id": "item_d", "priority": 4}
            ],
            "selected_items": [],
            "swap_buffer": None
        }

    def _get_available_actions(self):
        """Get list of available actions"""
        return ["select_item", "swap_items", "sort_section", "check_order"]

    def _apply_action(self, action: MyAction):
        """Apply the action to the current state"""
        state = self.current_state.copy()

        if action.action_type == "select_item":
            item_index = action.parameters.get("index", 0)
            if 0 <= item_index < len(state["items"]):
                if state["swap_buffer"] is None:
                    state["swap_buffer"] = item_index
                else:
                    # Swap the items
                    buf_idx = state["swap_buffer"]
                    state["items"][buf_idx], state["items"][item_index] = \
                        state["items"][item_index], state["items"][buf_idx]
                    state["swap_buffer"] = None

        elif action.action_type == "swap_items":
            idx1 = action.parameters.get("index1", 0)
            idx2 = action.parameters.get("index2", 1)
            if 0 <= idx1 < len(state["items"]) and 0 <= idx2 < len(state["items"]):
                state["items"][idx1], state["items"][idx2] = \
                    state["items"][idx2], state["items"][idx1]

        elif action.action_type == "sort_section":
            start = action.parameters.get("start", 0)
            end = action.parameters.get("end", len(state["items"]))
            if 0 <= start < end <= len(state["items"]):
                state["items"][start:end] = sorted(
                    state["items"][start:end],
                    key=lambda x: x["priority"]
                )

        elif action.action_type == "check_order":
            # This action doesn't change state but might provide info
            pass

        return state

    def _grade(self) -> float:
        state = self.current_state
        target_order = self.target_order
        """
        Grade the current state based on how well sorted the items are
        Returns a value between 0.0 and 1.0
        """
        items = state["items"]

        # Count how many items are in the correct position
        correct_positions = 0
        for i, (current, target) in enumerate(zip(items, target_order)):
            if current["id"] == target["id"]:
                correct_positions += 1

        # Calculate the reward based on correct positions
        if len(items) == 0:
            return 0.0

        return correct_positions / len(items)

    def _get_hint(self, reward: float) -> str:
        """Provide a hint based on the current reward"""
        if reward >= 0.9:
            return "The items are almost perfectly sorted!"
        elif reward >= 0.7:
            return "Most items are in the correct order."
        elif reward >= 0.5:
            return "About half the items are sorted correctly."
        elif reward >= 0.3:
            return "Some items are in the right position."
        else:
            return "The items need more sorting."

