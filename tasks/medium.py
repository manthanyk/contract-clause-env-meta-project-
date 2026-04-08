from models import (
    ContractClauseAction,
    ContractClauseObservation,
    ActionType,
    RiskLevel,
)
from typing import Tuple, List, Dict, Any
from tasks.base import BaseTask
import random


MEDIUM_CONTRACTS: List[Dict[str, Any]] = [
    {
        "text": """
SERVICE AGREEMENT

This Service Agreement (the "Agreement") is effective as of January 1, 2024.

1. SERVICES
Provider agrees to deliver services as specified in Exhibit A. Provider may
substitute materials of equivalent quality without prior notice.

2. PAYMENT
Client shall pay all fees within 30 days of invoice. Late payments subject to
2% monthly penalty. Client waives right to dispute charges after 10 days.

3. LIMITATION OF LIABILITY
Provider's liability is limited to fees paid in the preceding 3 months.
Provider is not liable for indirect, consequential, or incidental damages.

4. INDEMNIFICATION
Client agrees to indemnify Provider for all claims arising from Client's use
of services, including Provider's negligence, except for gross negligence.

5. TERMINATION
Either party may terminate with 30 days notice. Upon termination, Client must
immediately cease use and destroy all materials. No refunds for prepaid services.

6. INTELLECTUAL PROPERTY
All deliverables become Client's property upon full payment. Provider retains
rights to pre-existing materials and may use Client's name in marketing.

7. GOVERNING LAW
This Agreement is governed by the laws of Provider's state of incorporation.

Signed: ___________________
""",
        "clauses": [
            {
                "text": """PAYMENT
Client shall pay all fees within 30 days of invoice. Late payments subject to
2% monthly penalty. Client waives right to dispute charges after 10 days.""",
                "risk_level": RiskLevel.HIGH,
                "reason_keywords": [
                    "penalty",
                    "waive",
                    "dispute",
                    "one-sided",
                    "unfair",
                ],
                "explanation": "2% monthly penalty is excessive and waiver of dispute rights heavily favors provider.",
            },
            {
                "text": """LIMITATION OF LIABILITY
Provider's liability is limited to fees paid in the preceding 3 months.
Provider is not liable for indirect, consequential, or incidental damages.""",
                "risk_level": RiskLevel.HIGH,
                "reason_keywords": [
                    "limited",
                    "liability",
                    "cap",
                    "unfair",
                    "one-sided",
                ],
                "explanation": "Very narrow liability cap that leaves client exposed to significant losses.",
            },
            {
                "text": """INDEMNIFICATION
Client agrees to indemnify Provider for all claims arising from Client's use
of services, including Provider's negligence, except for gross negligence.""",
                "risk_level": RiskLevel.MEDIUM,
                "reason_keywords": ["indemnify", "broad", "negligence", "one-sided"],
                "explanation": "Broad indemnification that includes provider's own negligence is problematic.",
            },
        ],
    },
    {
        "text": """
CONSULTING MASTER SERVICES AGREEMENT

1. SCOPE OF WORK
Consultant will provide advisory services as defined in individual Statements of Work.
Consultant reserves the right to decline any engagement without penalty.

2. COMPENSATION
Fees are due within 15 days of invoice. Consultant may suspend services for any
outstanding balance exceeding 5 days past due. Interest accrues at 3% per month.

3. OWNERSHIP
All work product, including pre-existing IP incorporated into deliverables,
becomes the sole property of Client upon payment.

4. NON-SOLICITATION
Client may not hire any Consultant employee for 24 months following engagement.
Penalty: $50,000 per violation.

5. TERMINATION
Consultant may terminate immediately for any reason. Client must provide 60 days
written notice and pay all fees through the termination date plus a 15% early
termination fee.
""",
        "clauses": [
            {
                "text": """COMPENSATION
Fees are due within 15 days of invoice. Consultant may suspend services for any
outstanding balance exceeding 5 days past due. Interest accrues at 3% per month.""",
                "risk_level": RiskLevel.HIGH,
                "reason_keywords": [
                    "suspend",
                    "interest",
                    "penalty",
                    "unfair",
                    "one-sided",
                ],
                "explanation": "3% monthly interest is usurious and 5-day suspension window is extremely aggressive.",
            },
            {
                "text": """NON-SOLICITATION
Client may not hire any Consultant employee for 24 months following engagement.
Penalty: $50,000 per violation.""",
                "risk_level": RiskLevel.MEDIUM,
                "reason_keywords": [
                    "non-solicitation",
                    "penalty",
                    "restrictive",
                    "unfair",
                ],
                "explanation": "24-month non-solicitation with fixed $50k penalty is overly restrictive on client.",
            },
            {
                "text": """TERMINATION
Consultant may terminate immediately for any reason. Client must provide 60 days
written notice and pay all fees through the termination date plus a 15% early
termination fee.""",
                "risk_level": RiskLevel.HIGH,
                "reason_keywords": [
                    "asymmetric",
                    "termination",
                    "unfair",
                    "one-sided",
                    "penalty",
                ],
                "explanation": "Completely asymmetric termination rights with early termination penalty on client only.",
            },
        ],
    },
    {
        "text": """ASSIGNMENT
Provider may assign this agreement and all obligations hereunder
to any third party without Client's consent. Client may not
assign any rights without Provider's prior written approval.""",
        "risk_level": RiskLevel.HIGH,
        "reason_keywords": [
            "unilateral",
            "assign",
            "no consent",
            "one-sided",
            "third party",
        ],
        "explanation": "Provider can assign freely while client cannot — creates asymmetric control and risk of unknown parties taking over the contract.",
    },
]


class MediumTask(BaseTask):
    """
    Medium task: Assess risk levels of contract clauses.
    Grader: Based on accuracy of risk assessments.
    """

    def __init__(self):
        super().__init__(max_steps=30, difficulty="medium")
        self.risk_assessments = {}
        self.clause = None
        self.contract = None

    async def reset(self) -> ContractClauseObservation:
        self.risk_assessments = {}
        self.step_count = 0
        self.current_state = {"assessments": {}}
        self.contract = random.choice(MEDIUM_CONTRACTS)
        if "clauses" in self.contract:
            self.clause = random.choice(self.contract["clauses"])
        else:
            self.clause = self.contract
        return ContractClauseObservation(
            contract_text=self.contract["text"],
            task_description="Assess the risk level (none/low/medium/high/critical) of the highlighted contract clause and explain your reasoning.",
            current_score=0.05,
            step_count=0,
            max_steps=self.max_steps,
            available_actions=[
                ActionType.RISK_ASSESS,
                ActionType.REQUEST_CLARIFICATION,
            ],
            progress_hint="Focus on payment terms, liability limits, and indemnification clauses.",
        )

    async def step(
        self, action: ContractClauseAction
    ) -> Tuple[ContractClauseObservation, float, bool]:
        return await super().step(action)

    def _apply_action(self, action: ContractClauseAction) -> dict:
        state = self.current_state.copy()

        if action.action_type == ActionType.RISK_ASSESS and action.risk_explanation:
            explanation = action.risk_explanation.lower()
            for clause_key in self.contract.get("clauses", []):
                if clause_key.get("text", "").lower()[:20] in explanation:
                    self.risk_assessments[clause_key["text"][:30]] = action.risk_level
            state["assessments"] = self.risk_assessments

        return state

    def _get_available_actions(self):
        return [ActionType.RISK_ASSESS, ActionType.REQUEST_CLARIFICATION]

    def _get_contract_text(self) -> str:
        return self.contract["text"] if self.contract else ""

    def _get_task_description(self) -> str:
        return "Assess the risk level (none/low/medium/high/critical) of the highlighted contract clause and explain your reasoning."

    def _grade(self, action: ContractClauseAction) -> float:
        score = 0.05
        explanation = (action.risk_explanation or "").lower()

        if action.risk_level is None:
            pass
        elif action.risk_level == self.clause["risk_level"]:
            score += 0.35
        else:
            risk_order = [
                RiskLevel.LOW,
                RiskLevel.MEDIUM,
                RiskLevel.HIGH,
                RiskLevel.CRITICAL,
            ]
            if (
                action.risk_level in risk_order
                and self.clause["risk_level"] in risk_order
            ):
                diff = abs(
                    risk_order.index(action.risk_level)
                    - risk_order.index(self.clause["risk_level"])
                )
                if diff == 1:
                    score += 0.20

        if len(explanation) > 20:
            score += 0.30

        disadvantaged_keywords = [
            "provider",
            "consultant",
            "freelancer",
            "vendor",
            "seller",
            "client",
            "company",
            "buyer",
            "one-sided",
            "unfair",
            "favours",
            "favor",
            "risk",
            "penalty",
            "liability",
            "indemnify",
        ]
        if any(kw in explanation for kw in disadvantaged_keywords):
            score += 0.25

        if any(kw in explanation for kw in self.clause.get("reason_keywords", [])):
            score += 0.20

        return round(max(0.05, min(0.95, score)), 4)

    def _get_hint(self, reward: float) -> str:
        if reward >= 0.9:
            return "Excellent risk assessment!"
        elif reward >= 0.7:
            return "Good progress. Re-examine the liability and payment clauses."
        elif reward >= 0.5:
            return "Focus on clauses that heavily favor one party."
        elif reward >= 0.3:
            return "Look for unlimited liability or penalties."
        else:
            return "Hint: Payment penalties, liability caps, and broad indemnification are typically high-risk."
