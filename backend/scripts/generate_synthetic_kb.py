import os
import csv
from pathlib import Path

# Set output path to project data directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "data" / "synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

files_content = {
    "01_product_overview.txt": """---
market_code: default
doc_type: product_overview
---
# Salita Business Capital Loan - Overview
Salita Financial Services provides unsecured business capital loans designed to support working capital, inventory purchases, and business expansion.
Features:
- Loan amounts ranging from ₹100,000 to ₹5,000,000.
- Flexible repayment terms from 12 to 36 months.
- No collateral required for qualified business owners.
- Fast digital processing within 24 to 48 hours.""",

    "02_loan_eligibility_current.txt": """---
market_code: default
doc_type: eligibility_policy
version: 2.0 (Active)
---
# Current Business Loan Eligibility Criteria (Updated 2026)
To qualify for a Salita Business Loan, applicants must meet ALL of the following criteria:
1. Business Operating History: Minimum 2 years of continuous operational history.
2. Revenue Threshold: Minimum monthly revenue of ₹50,000 (₹600,000 annually).
3. Credit History: Zero unresolved defaults on any personal or business credit lines.
4. Business Registration: Registered entity with valid GSTIN and active business bank account.
5. Entity Types: Sole proprietorships, partnerships, LLPs, and Private Limited companies.""",

    "03_loan_eligibility_v1_stale.txt": """---
market_code: default
doc_type: eligibility_policy
version: 1.0 (SUPERSEDED)
---
# Archive: Business Loan Policy (Deprecated 2024)
Requirements for business financing:
- Minimum business operating history of 1 year.
- Minimum monthly turnover of ₹10,000.
- Unresolved defaults permitted if under ₹25,000.""",

    "05_required_documents.txt": """---
market_code: default
doc_type: Operations
---
# Required Document Checklist
To process a loan application, the customer must submit:
1. Identity & Address Proof: Aadhaar Card, PAN Card, or Passport.
2. Business Proof: GST Registration Certificate or Shops & Establishment License.
3. Financial Records: Last 6 months bank statements for the main operating account.
4. Income Verification: Latest GST returns (GSTR-3B) and ITR for the last financial year.""",

    "06_frequently_asked_questions.txt": """---
market_code: default
doc_type: FAQ
---
# Business Loan FAQs
Q: What is the interest rate?
A: Rates range from 14% to 22% per annum depending on credit profile and monthly turnover.

Q: Is there a pre-payment penalty?
A: No foreclosure fees after completing 6 timely monthly installments.

Q: How long does approval take?
A: Preliminary qualification takes less than 5 minutes. Full disbursement takes 24-48 hours.""",

    "07_objection_handling.txt": """---
market_code: default
doc_type: Sales
---
# Agent Objection Handling Guide
Objection: "Your interest rate is too high."
Response: "I understand your concern. Our loans are completely collateral-free with no hidden processing costs, allowing you to access working capital immediately without locking up assets."

Objection: "I do not want to share 6 months bank statements."
Response: "We use bank statements solely to calculate your cash flow and ensure we offer a comfortable monthly installment plan that will not strain your business." """,

    "08_application_process.txt": """---
market_code: default
doc_type: Process
---
# End-to-End Application Workflow
1. Initial Screening: Agent verifies basic business details (Name, Revenue, Tenure, Default history).
2. Qualification Status: State evaluates to QUALIFIED or DISQUALIFIED.
3. Document Upload: Applicant submits 6-month bank statement link.
4. Automated Underwriting: System checks FOIR and revenue consistency.
5. Final Disbursement: Funds credited directly to business bank account.""",

    "09_business_restrictions.txt": """---
market_code: default
doc_type: Risk
---
# Prohibited Business Sectors
Salita does NOT provide loans to businesses engaged in:
- Cryptocurrencies or speculative digital asset trading.
- Gambling, casinos, or betting operations.
- Firearms, defense manufacturing, or ammunition.
- Real estate land speculation.
- Multi-level marketing (MLM) or pyramid schemes.""",

    "10_revenue_verification_rules.txt": """---
market_code: default
doc_type: Underwriting
---
# Revenue Verification Policy
1. Monthly Revenue Calculation: Calculated using the 6-month average cash credit/current account deposits.
2. Intra-account transfers and self-transfers are excluded from monthly revenue calculations.
3. Revenue Variance: If GST returns show a variance >30% compared to bank credits, the lower figure is used.""",

    "11_existing_debt_obligations.txt": """---
market_code: default
doc_type: Underwriting
---
# Debt Obligation and FOIR Policy
1. Maximum Fixed Obligation to Income Ratio (FOIR): Total monthly EMI obligations (including proposed loan) cannot exceed 50% of verified average monthly revenue.
2. Existing Default Rule: Any active or unresolved payment default on CIBIL/Equifax instantly disqualifies the applicant.""",

    "12_compliance_disclosures.txt": """---
market_code: default
doc_type: Legal
---
# Regulatory Compliance and Fair Practices
1. Salita operates in compliance with RBI Digital Lending Guidelines.
2. Key Fact Statement (KFS) containing APR, processing fees, and repayment schedules will be issued prior to loan agreement signing.
3. Customer data is encrypted and never sold to third parties.""",

    "13_escalation_policy.txt": """---
market_code: default
doc_type: Escalation
---
# Call Escalation Protocol
An AI agent MUST immediately offer human supervisor escalation when:
1. The customer explicitly asks to speak to a human or manager.
2. The customer raises a formal legal or regulatory compliance dispute.
3. The customer poses a complex question outside the knowledge base context twice consecutively.""",

    "14_callback_policy.txt": """---
market_code: default
doc_type: Operations
---
# Customer Callback Scheduling Policy
1. Callbacks can be scheduled between 9:00 AM and 7:00 PM local time, Monday to Saturday.
2. Callback SLA: A human relationship manager will reach out within 2 operational hours of request creation.""",

    "15_philippines_bancassurance_policy.txt": """---
market_code: PH
doc_type: Insurance
---
# Philippines Market: Bancassurance and Life Protection Policy
Para sa customer sa Philippines:
1. Eligibility: Ages 18 to 65 years old with valid government ID (SSS, UMID, Drivers License).
2. Premium / Hulog: Starts at PHP 500 per month for basic coverage.
3. Coverage / Proteksyon: Up to PHP 1,000,000 for natural death or total disability.
4. Beneficiary / Tagapag-mana: Direct family members (spouse, children, parents).
5. Monthly revenue requirements for financing: Minimum 30,000 PHP per month.""",

    "16_indonesia_multifinance_policy.txt": """---
market_code: ID
doc_type: Multifinance
---
# Indonesia Market: Multifinance and Consumer Credit Rules
Untuk nasabah di Indonesia:
1. Persyaratan Usia: Minimal 21 tahun atau sudah menikah, maksimal 60 tahun saat tenor berakhir.
2. Cicilan / Angsuran: Maksimal 40% dari pendapatan bulanan terverifikasi.
3. Tenor / Jangka Waktu: Pilihan 6, 12, 18, atau 24 bulan.
4. DP / Uang Muka: Minimal 10% untuk pembiayaan barang atau kendaraan.
5. Denda Keterlambatan: 0.5% per hari dari nilai angsuran yang tertunggak.""",

    "17_near_duplicate_eligibility.txt": """---
market_code: default
doc_type: Vector_Test
---
# Commercial Loan Standard Requirements
Criteria for securing a corporate business credit facility:
- Business operational tenure must be a minimum of two full years (24 months).
- Verified monthly income must be at least ₹50,000.
- No historical credit defaults that remain outstanding.""",

    "18_garbled_table_sample.txt": """---
market_code: default
doc_type: Clean_Test
---
# Fee Structure Breakdown
[CORRUPT TABLE START]
Fee_Type | Amount || Status
ProcessingFee | 2% || Mandatory
Late Penalty | ₹500/day || If_Overdue
Prepayment | Nil || After_6_m
[CORRUPT TABLE END]"""
}

def create_csv_file():
    csv_path = OUTPUT_DIR / "04_pricing_and_limits.csv"
    data = [
        ["Credit_Score_Band", "Min_Monthly_Revenue", "Max_Loan_Amount", "Annual_Interest_Rate"],
        ["750+", "50000", "5000000", "14%"],
        ["700-749", "50000", "3000000", "16.5%"],
        ["650-699", "75000", "1500000", "19%"],
        ["Below 650", "100000", "500000", "22%"]
    ]
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print(f"Created: {csv_path.name}")

def generate_all():
    print(f"Generating synthetic knowledge base in: {OUTPUT_DIR}\n")
    for filename, content in files_content.items():
        file_path = OUTPUT_DIR / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {filename}")
    
    create_csv_file()
    print("\n✅ Knowledge base generation complete! Total 18 files created.")

if __name__ == "__main__":
    generate_all()