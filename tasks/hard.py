from models import ContractClauseAction, ContractClauseObservation, ActionType
from typing import Tuple, List, Dict, Any
from tasks.base import BaseTask
import random


HARD_CONTRACTS: List[Dict[str, Any]] = [
    {
        "text": """
SOFTWARE DEVELOPMENT AGREEMENT

This Agreement is entered into between Client and Developer.

1. DEVELOPMENT SERVICES
Developer shall create custom software per Client's specifications.
All specifications are subject to unilateral modification by Client.

2. PAYMENT TERMS
Client shall pay $50,000 upon completion. Payment due within 90 days.
Late fees of 5% per month apply. Client may withhold payment for any reason.

3. INTELLECTUAL PROPERTY
Developer assigns all rights, including derivative works, to Client.
Developer waives moral rights and agrees to perpetual non-compete.
Developer may not use any similar code in future projects.

4. WARRANTY AND LIABILITY
Developer warrants code will be error-free for 30 days only.
Developer's maximum liability is limited to $100 total.
Client has no obligation to mitigate damages.

5. INDEMNIFICATION
Developer indemnifies Client for ALL claims, including:
- Third-party intellectual property claims
- Data breaches, even if caused by Client
- Client's own negligence
- Acts of third parties

6. TERMINATION
Client may terminate at any time for convenience with 7 days notice.
Developer must refund all payments upon termination.
All work product remains Client's property.

7. DISPUTE RESOLUTION
Any disputes resolved in [Client's City] courts under Client's state law.
Developer waives right to jury trial and class action.
Loser pays all attorney fees, expert costs, and expenses.

8. NON-COMPETE
Developer may not compete with Client for 5 years post-termination,
worldwide, in any business similar to Client's actual or planned activities.

9. FORCE MAJEURE
Only Client may invoke force majeure. Developer must still deliver
regardless of circumstances.

Signed: ___________________
""",
        "issues": [
            "unilateral modification of specifications",
            "withhold payment for any reason",
            "perpetual non-compete",
            "grossly inadequate liability cap of $100",
            "overly broad indemnification",
            "refund all payments upon termination",
            "waiver of jury trial",
            "excessive 5-year non-compete",
            "worldwide geographic scope",
            "one-sided force majeure",
        ],
        "unfair_keywords": [
            "unilateral",
            "withhold",
            "any reason",
            "perpetual",
            "non-compete",
            "$100",
            "indemnifies",
            "ALL claims",
            "refund all",
            "waives",
            "jury trial",
            "5 years",
            "worldwide",
            "only client",
        ],
    },
    {
        "text": """
EMPLOYMENT AGREEMENT

Between MegaCorp Inc. ("Employer") and Employee.

1. POSITION AND DUTIES
Employee shall serve as Senior Developer and perform duties as assigned.
Employee may be reassigned to any role at Employer's sole discretion.

2. COMPENSATION
Base salary of $80,000 per year. Bonus is entirely at Employer's discretion
and may be withheld without cause or explanation.

3. INTELLECTUAL PROPERTY
All inventions, works, and ideas created by Employee during employment,
including those created on personal time using personal resources, are
the sole property of Employer.

4. NON-COMPETE
Employee may not work for any competitor for 2 years after leaving.
This applies worldwide and to any similar business.

5. NON-DISPARAGEMENT
Employee shall not make any negative statements about Employer,
its products, services, or personnel, during or after employment.
Violation results in forfeiture of all severance benefits.

6. ARBITRATION
All disputes shall be resolved by binding arbitration selected by Employer.
Employee waives right to jury trial, class action, and discovery.
""",
        "issues": [
            "unilateral reassignment at sole discretion",
            "bonus entirely discretionary with no criteria",
            "IP assignment covers personal time and resources",
            "2-year worldwide non-compete is excessive",
            "broad non-disparagement with severe penalty",
            "employer-selected arbitration with waived rights",
        ],
        "unfair_keywords": [
            "sole discretion",
            "withheld",
            "without cause",
            "personal time",
            "personal resources",
            "non-compete",
            "worldwide",
            "non-disparagement",
            "forfeiture",
            "binding arbitration",
            "waives",
            "jury trial",
        ],
    },
    {
        "text": """
SaaS SERVICE LEVEL AGREEMENT

1. AVAILABILITY
Provider guarantees 99.0% uptime measured monthly. Downtime excludes
scheduled maintenance, which Provider may perform at any time without notice.

2. REMEDIES
If uptime falls below 99.0%, Client receives service credits equal to
5% of monthly fee for each 0.5% below target. Maximum credit is 25%
of monthly fee. Credits are Client's sole and exclusive remedy.

3. DATA
Provider is not responsible for data loss. Client must maintain backups.
Provider may delete data 30 days after account termination without notice.

4. LIABILITY
Provider's total liability shall not exceed fees paid in the prior 3 months.
Provider is not liable for any indirect, special, incidental, or consequential
damages, including lost profits, data, or business interruption.

5. TERMINATION
Provider may terminate for any reason with 30 days notice.
Client may only terminate for material breach with 90 days written notice
and must pay all fees through the remainder of the annual term.

6. CHANGES
Provider may modify terms, features, or pricing with 15 days email notice.
Continued use constitutes acceptance of all changes.
""",
        "issues": [
            "99.0% uptime guarantee is below industry standard",
            "scheduled maintenance without notice is abusive",
            "credits capped at 25% with no other remedy",
            "no responsibility for data loss",
            "data deletion 30 days after termination without notice",
            "asymmetric termination rights",
            "unilateral changes to terms with only 15 days notice",
        ],
        "unfair_keywords": [
            "without notice",
            "sole and exclusive",
            "not responsible",
            "data loss",
            "delete data",
            "any reason",
            "material breach",
            "90 days",
            "modify terms",
            "15 days",
            "constitutes acceptance",
        ],
    },
    {
        "text": """DATA AND PRIVACY
Client grants Provider an irrevocable, worldwide license to use,
sell, and share all data generated by Client during use of the
services, including personally identifiable information, for any
commercial purpose. Provider may retain all data indefinitely
after contract termination.""",
        "issues": [
            "irrevocable data license survives contract termination",
            "selling PII without consent likely violates GDPR/CCPA",
            "no limitation on data use — any commercial purpose",
            "indefinite retention with no deletion right",
        ],
        "unfair_keywords": [
            "irrevocable",
            "sell",
            "pii",
            "personally identifiable",
            "any commercial purpose",
            "indefinitely",
            "gdpr",
            "ccpa",
            "retention",
        ],
    },
    {
        "text": """INDEPENDENT CONTRACTOR AGREEMENT

1. STATUS
Contractor is an independent contractor, not an employee. Contractor is
responsible for all taxes, insurance, and benefits.

2. EXCLUSIVITY
Contractor shall not provide similar services to any other client during
the term of this agreement without prior written consent from Company.

3. INTELLECTUAL PROPERTY
All work product, including tools, frameworks, and methodologies developed
by Contractor independently and used in connection with services, becomes
the exclusive property of Company.

4. NON-SOLICITATION
Contractor may not solicit or hire any Company employee, contractor, or
client for 3 years following termination. Penalty of $100,000 per violation.

5. INDEMNIFICATION
Contractor shall indemnify Company for all claims, damages, and losses
arising from Contractor's services, including Company's own negligence.
""",
        "issues": [
            "exclusivity clause prevents contractor from working with others",
            "IP assignment covers contractor's pre-existing tools and methods",
            "3-year non-solicitation with $100k penalty is excessive",
            "indemnification includes company's own negligence",
        ],
        "unfair_keywords": [
            "exclusivity",
            "shall not",
            "without consent",
            "independently",
            "exclusive property",
            "non-solicitation",
            "3 years",
            "$100,000",
            "indemnify",
            "own negligence",
        ],
    },
]


class HardTask(BaseTask):
    """
    Hard task: Detect unfair or unconscionable contract clauses.
    Grader: Based on correctly identifying unfair clauses and explaining why.
    """

    def __init__(self):
        super().__init__(max_steps=50, difficulty="hard")
        self.found_unfair = set()
        self.explanations = {}
        self.contract = None

    async def reset(self) -> ContractClauseObservation:
        self.found_unfair = set()
        self.explanations = {}
        self.step_count = 0
        self.current_state = {"found_unfair": [], "explanations": {}}
        self.contract = random.choice(HARD_CONTRACTS)
        return ContractClauseObservation(
            contract_text=self.contract["text"],
            task_description="Identify unfair or unconscionable clauses in this contract. For each, explain why it's unfair and suggest a revision.",
            current_score=0.0,
            step_count=0,
            max_steps=self.max_steps,
            available_actions=[
                ActionType.FLAG_UNFAIR,
                ActionType.PROPOSE_REVISION,
                ActionType.REQUEST_CLARIFICATION,
            ],
            progress_hint="Look for one-sided terms, excessive limitations, and waivers of rights.",
        )

    async def step(
        self, action: ContractClauseAction
    ) -> Tuple[ContractClauseObservation, float, bool]:
        return await super().step(action)

    def _apply_action(self, action: ContractClauseAction) -> dict:
        state = self.current_state.copy()

        if action.action_type == ActionType.FLAG_UNFAIR and action.unfair_clause:
            clause_text = action.unfair_clause.lower()
            for unfair_key in self.contract.get("issues", []):
                if unfair_key.lower() in clause_text or any(
                    word in clause_text for word in unfair_key.lower().split()
                ):
                    self.found_unfair.add(unfair_key)
                    if action.unfair_reason:
                        self.explanations[unfair_key] = action.unfair_reason
            state["found_unfair"] = list(self.found_unfair)
            state["explanations"] = self.explanations

        return state

    def _get_available_actions(self):
        return [
            ActionType.FLAG_UNFAIR,
            ActionType.PROPOSE_REVISION,
            ActionType.REQUEST_CLARIFICATION,
        ]

    def _get_contract_text(self) -> str:
        return self.contract["text"] if self.contract else ""

    def _get_task_description(self) -> str:
        return "Identify unfair or unconscionable clauses in this contract. For each, explain why it's unfair and suggest a revision."

    def _get_review_comments(self) -> list:
        comments = []
        for clause, explanation in self.explanations.items():
            comments.append(
                {"clause": clause, "issue": clause, "explanation": explanation}
            )
        return comments

    def _grade(self, action: ContractClauseAction) -> float:
        score = 0.0
        parts = []
        if action.unfair_reason:
            parts.append(action.unfair_reason)
        if action.risk_explanation:
            parts.append(action.risk_explanation)
        if action.clarification_request:
            parts.append(action.clarification_request)
        full_text = " ".join(parts).lower()

        unfair_signals = [
            "unfair",
            "problematic",
            "one-sided",
            "unreasonable",
            "ambiguous",
            "void",
            "unenforceable",
            "abusive",
            "exploitative",
            "risk",
            "liability",
            "penalty",
        ]
        if any(kw in full_text for kw in unfair_signals):
            score += 0.30

        issues_found = sum(
            1 for kw in self.contract.get("unfair_keywords", []) if kw in full_text
        )

        if issues_found >= 1:
            score += 0.25
        if issues_found >= 2:
            score += 0.25

        alt_signals = [
            "instead",
            "should read",
            "replace",
            "fairer",
            "alternative",
            "suggest",
            "recommend",
            "amend",
            "propose",
            "asymmetric",
            "unilateral",
            "excessive",
        ]
        if any(kw in full_text for kw in alt_signals) or issues_found >= 3:
            score += 0.25

        if len(full_text) > 100:
            score += 0.15

        return round(max(0.05, min(0.95, score)), 4)

    def _get_hint(self, reward: float) -> str:
        if reward >= 0.9:
            return "Excellent! You've identified most unfair clauses."
        elif reward >= 0.7:
            return "Good progress. Check the indemnification and non-compete clauses."
        elif reward >= 0.5:
            return "Look for clauses that give one party unlimited power."
        elif reward >= 0.3:
            return "Focus on termination and payment terms."
        else:
            return "Hint: Look for: unilateral changes, excessive liability caps, broad indemnification, and long non-competes."
