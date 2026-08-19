class LoanQualificationState:
    def __init__(self):
        self.name = None
        self.business_type = None
        self.years_operating = None
        self.monthly_revenue = None
        self.loan_amount = None
        self.loan_purpose = None
        self.has_unresolved_default = None
        self.human_escalation_requested = False

    def get_missing_field(self):
        """Returns the next field needed from the applicant."""
        if not self.name:
            return "name"
        if not self.business_type:
            return "business_type"
        if self.years_operating is None:
            return "years_operating"
        if self.monthly_revenue is None:
            return "monthly_revenue"
        if self.loan_amount is None:
            return "loan_amount"
        if not self.loan_purpose:
            return "loan_purpose"
        if self.has_unresolved_default is None:
            return "has_unresolved_default"
        return None

    def evaluate_eligibility(self):
        """Evaluates gathered data against loan policies."""
        if self.has_unresolved_default is True:
            return "DISQUALIFIED", "Unresolved default on existing loan."
        
        if self.years_operating is not None and self.years_operating < 2:
            return "DISQUALIFIED", "Business operating period under 2 years."
            
        if self.monthly_revenue is not None and self.monthly_revenue < 50000:
            return "DISQUALIFIED", "Monthly revenue under INR 50,000."
            
        missing = self.get_missing_field()
        if missing:
            return "INCOMPLETE", f"Missing field: {missing}"
            
        return "QUALIFIED", "Meets basic qualification criteria."

if __name__ == "__main__":
    # Test state machine logic
    applicant = LoanQualificationState()
    applicant.name = "Rahul"
    applicant.business_type = "Retail"
    applicant.years_operating = 3
    applicant.monthly_revenue = 60000
    applicant.loan_amount = 200000
    applicant.loan_purpose = "Inventory"
    applicant.has_unresolved_default = False

    status, reason = applicant.evaluate_eligibility()
    print(f"Status: {status}")
    print(f"Reason: {reason}")