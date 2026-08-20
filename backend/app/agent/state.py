from pydantic import BaseModel
from typing import Optional, Tuple

class LoanApplicationState(BaseModel):
    name: Optional[str] = None
    business_type: Optional[str] = None
    years_operating: Optional[int] = None
    monthly_revenue: Optional[float] = None
    requested_amount: Optional[float] = None
    has_unresolved_default: Optional[bool] = None
    loan_purpose: Optional[str] = None
    human_escalation_requested: bool = False

    # Synchronized Policy Thresholds
    MIN_YEARS_OPERATING: int = 2
    MIN_MONTHLY_REVENUE: float = 50000.0

    def get_missing_field(self) -> Optional[str]:
        required_fields = [
            "name", 
            "business_type", 
            "years_operating", 
            "monthly_revenue", 
            "requested_amount", 
            "has_unresolved_default", 
            "loan_purpose"
        ]
        for field in required_fields:
            if getattr(self, field) is None:
                return field
        return None

    def evaluate_eligibility(self) -> Tuple[str, Optional[str]]:
        if self.has_unresolved_default is True:
            return "DISQUALIFIED", "Unresolved default on credit history."
        if self.years_operating is not None and self.years_operating < self.MIN_YEARS_OPERATING:
            return "DISQUALIFIED", f"Business must operate for at least {self.MIN_YEARS_OPERATING} years."
        if self.monthly_revenue is not None and self.monthly_revenue < self.MIN_MONTHLY_REVENUE:
            return "DISQUALIFIED", f"Monthly revenue must be at least ₹{self.MIN_MONTHLY_REVENUE:,.0f}."
        
        if self.get_missing_field() is None:
            return "QUALIFIED", None
        return "INCOMPLETE", None