from models import (
    ContractClauseAction,
    ContractClauseObservation,
    ActionType,
    ClauseType,
)
from typing import Tuple, List, Dict, Any
from tasks.base import BaseTask
import random


EASY_CONTRACTS: List[Dict[str, Any]] = [
    {
        "text": """
SOFTWARE LICENSE AGREEMENT

This Software License Agreement (the "Agreement") is entered into between:
Licensor: ABC Software Corp
Licensee: XYZ Company

1. LICENSE GRANT
ABC Software Corp grants XYZ Company a non-exclusive license to use the software.

2. INTELLECTUAL PROPERTY
All intellectual property rights remain with ABC Software Corp.

3. CONFIDENTIALITY
Both parties agree to maintain confidentiality of proprietary information.

Signed: ________________
Date: ________________
""",
        "contract_type": "software_license",
        "missing": [
            ClauseType.TERMINATION,
            ClauseType.PAYMENT,
            ClauseType.GOVERNING_LAW,
        ],
        "present": ["license_grant", "intellectual_property", "confidentiality"],
    },
    {
        "text": """
NON-DISCLOSURE AGREEMENT

This NDA is between DataTech Inc ("Disclosing Party") and AnalytiCo ("Receiving Party").

1. DEFINITION
Confidential Information includes all technical and business information shared.

2. OBLIGATIONS
Receiving Party shall not disclose Confidential Information to third parties.

3. TERM
This agreement remains in effect for 2 years from the date of signing.

Signed: ________________
""",
        "contract_type": "nda",
        "missing": [
            ClauseType.DISPUTE_RESOLUTION,
            ClauseType.LIMITATION_LIABILITY,
            ClauseType.INDEMNIFICATION,
        ],
        "present": ["confidentiality", "term"],
    },
    {
        "text": """
EMPLOYMENT CONTRACT

Between InnovateTech ("Employer") and Jane Doe ("Employee").

1. POSITION
Employee shall serve as Senior Software Engineer.

2. COMPENSATION
Annual salary of $120,000, paid bi-weekly.

3. BENEFITS
Employee receives health insurance, 401k matching, and 20 days PTO.

4. CONFIDENTIALITY
Employee agrees to keep all company information confidential.

Signed: ________________
Date: ________________
""",
        "contract_type": "employment",
        "missing": [
            ClauseType.TERMINATION,
            ClauseType.DISPUTE_RESOLUTION,
            ClauseType.GOVERNING_LAW,
            ClauseType.FORCE_MAJEURE,
        ],
        "present": ["compensation", "confidentiality"],
    },
    {
        "text": """VENDOR AGREEMENT

Between SupplyMax Inc ("Vendor") and RetailCo ("Buyer").

1. PRODUCTS
Vendor shall supply goods as ordered by Buyer from time to time.

2. PRICING
Prices are as agreed in purchase orders issued by Buyer.

3. DELIVERY
Vendor shall deliver within 14 days of order confirmation.

4. PAYMENT
Buyer shall pay within 30 days of delivery and invoice receipt.
""",
        "contract_type": "vendor_agreement",
        "missing": [
            ClauseType.TERMINATION,
            ClauseType.LIMITATION_LIABILITY,
            ClauseType.INDEMNIFICATION,
            ClauseType.DISPUTE_RESOLUTION,
            ClauseType.GOVERNING_LAW,
            ClauseType.FORCE_MAJEURE,
        ],
        "present": ["payment_terms"],
    },
    {
        "text": """
CONSULTING SERVICES AGREEMENT

Between TechConsult LLC ("Consultant") and GlobalCorp ("Client").

1. SERVICES
Consultant shall provide IT strategy consulting services.

2. FEES
Client shall pay Consultant $200/hour, invoiced monthly.

3. INTELLECTUAL PROPERTY
All work product shall be owned by Client upon payment.

4. TERM
This agreement commences on the date signed and continues for 6 months.

Signed: ________________
Date: ________________
""",
        "contract_type": "consulting",
        "missing": [
            ClauseType.TERMINATION,
            ClauseType.LIMITATION_LIABILITY,
            ClauseType.INDEMNIFICATION,
            ClauseType.DISPUTE_RESOLUTION,
        ],
        "present": ["fees", "intellectual_property", "term"],
    },
]


class EasyTask(BaseTask):
    """
    Easy task: Identify missing clauses in a simple contract.
    Grader: Based on correctly identifying missing critical clauses.
    """

    def __init__(self):
        super().__init__(max_steps=20, difficulty="easy")
        self.found_clauses = set()
        self.contract = None
        self.clause_values = [c.value for c in ClauseType]

    async def reset(self) -> ContractClauseObservation:
        self.found_clauses = set()
        self.step_count = 0
        self.current_state = {"identified_clauses": []}
        self.contract = random.choice(EASY_CONTRACTS)
        return ContractClauseObservation(
            contract_text=self.contract["text"],
            task_description="Identify the missing critical clauses in this contract.",
            current_score=0.0,
            step_count=0,
            max_steps=self.max_steps,
            available_actions=[
                ActionType.FLAG_MISSING,
                ActionType.REQUEST_CLARIFICATION,
            ],
            progress_hint="Look for standard contract clauses that are missing.",
        )

    async def step(
        self, action: ContractClauseAction
    ) -> Tuple[ContractClauseObservation, float, bool]:
        return await super().step(action)

    def _apply_action(self, action: ContractClauseAction) -> dict:
        state = self.current_state.copy()

        if action.action_type == ActionType.FLAG_MISSING and action.missing_clauses:
            for clause in action.missing_clauses:
                if isinstance(clause, ClauseType):
                    self.found_clauses.add(clause.value)
                elif isinstance(clause, str) and clause in self.clause_values:
                    self.found_clauses.add(clause)
            state["identified_clauses"] = list(self.found_clauses)
        elif action.action_type == ActionType.REQUEST_CLARIFICATION:
            pass

        return state

    def _get_available_actions(self):
        return [ActionType.FLAG_MISSING, ActionType.REQUEST_CLARIFICATION]

    def _get_contract_text(self) -> str:
        return self.contract["text"] if self.contract else ""

    def _get_task_description(self) -> str:
        return "Identify the missing critical clauses in this contract."

    def _grade(self, action: ContractClauseAction) -> float:
        if action.action_type != ActionType.FLAG_MISSING or not action.missing_clauses:
            return 0.05

        required = set(self.contract["missing"])
        identified = set(action.missing_clauses)
        correct = required & identified

        score = min(len(correct) * 0.25, 0.95)

        present_values = set(self.contract["present"])
        false_positives = sum(1 for c in identified if c.value in present_values)
        score = max(0.05, score - false_positives * 0.05)

        return round(score, 4)

    def _get_hint(self, reward: float) -> str:
        if reward >= 0.9:
            return "Excellent! You've found most missing clauses."
        elif reward >= 0.7:
            return "Good progress. Check for termination and payment terms."
        elif reward >= 0.5:
            return "Keep looking. Think about what happens when the agreement ends."
        elif reward >= 0.3:
            return "Consider standard business contract elements."
        else:
            return "Look for: What governs the agreement? How does it end? How is payment handled?"
