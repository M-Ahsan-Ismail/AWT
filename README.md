# AWT


Developed Income Tax Slabs module
Added Income Tax Slabs configuration under Payroll → Configuration.

Each slab record contains:
Year/Name of the slab.
Multiple slab lines defining salary brackets with:
Start & end limits (annual income range).
Tax rate (%).
Fixed amount.

Extended the HR Contract form to display the Monthly Income Tax field.

Added an "Compute Income Tax" action on contracts:
Select one or more employee contracts.
Choose the applicable Tax Slab Year in the wizard.
System calculates each employee’s monthly tax based on their annual salary and selected slab rules.
Result is stored in the Monthly Income Tax field on the contract.




Developed a CRM Admin Dashboard to provide an overview of all leads and opportunities.

Displays key metrics: total leads, opportunities, expected revenue, and deals currently in view.
Supports filtering by salesperson, date range, and type (lead or opportunity) for precise analysis.
Allows quick access to detailed lead data, including customer information, stage, and revenue potential.
