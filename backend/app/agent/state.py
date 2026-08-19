from pydantic import BaseModel
from typing import Optional, Tuple

class LoanApplicationState(BaseModel):
    name: Optional[str] = None
    business_type: Optional[str] = None
    years_operating: Optional[int] = None
    monthly_revenue: Optional[float] = None
    requested_amount: Optional[float] = None
    has_unresolved_default: Optional[bool] = None

    def get_missing_field(self) -> Optional[str]:
        for field_name, value in self.model_dump().items():
            if value is None:
                return field_name
        return None

    def evaluate_eligibility(self) -> Tuple[str, str]:
        missing = self.get_missing_field()
        if missing:
            return "INCOMPLETE", f"Missing field: {missing}"
        
        if self.has_unresolved_default:
            return "REJECTED", "Unresolved loan default on file."
        if self.years_operating is not None and self.years_operating < 1:
            return "REJECTED", "Business must be operating for at least 1 year."
        if self.monthly_revenue is not None and self.monthly_revenue < 10000:
            return "REJECTED", "Monthly revenue below minimum eligibility threshold."
        
        return "QUALIFIED", "Application meets all preliminary qualification criteria."