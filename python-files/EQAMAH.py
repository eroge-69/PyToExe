from dataclasses import dataclass, field
from typing import Dict
from uuid import uuid4
from decimal import Decimal, ROUND_HALF_UP

def D(x):
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@dataclass
class SPV:
    id: str
    project_id: str
    assets_value: Decimal = D("0.00")
    liabilities_value: Decimal = D("0.00")
    def net_capital(self) -> Decimal:
        return (self.assets_value - self.liabilities_value).quantize(Decimal("0.01"))

@dataclass
class Project:
    id: str
    name: str
    description: str
    spv: SPV
    share_price: Decimal = D("1000.00")
    total_shares: int = 0
    shares_sold: int = 0
    management_fee_pct: Decimal = D("0.05")
    investors: Dict[str, int] = field(default_factory=dict)

    def struct_shares(self):
        capital = self.spv.net_capital()
        total_shares = int(capital // self.share_price)
        if total_shares == 0:
            raise ValueError("Capital too small relative to share price.")
        self.total_shares = total_shares
        return total_shares

    def available_shares(self):
        return self.total_shares - self.shares_sold

    def sell_shares(self, investor_id: str, num_shares: int):
        if num_shares > self.available_shares():
            raise ValueError("Not enough available shares")
        self.shares_sold += num_shares
        self.investors[investor_id] = self.investors.get(investor_id, 0) + num_shares

@dataclass
class Investor:
    id: str
    name: str
    wallet: Decimal = D("0.00")
    holdings: Dict[str, int] = field(default_factory=dict)

    def deposit(self, amount: Decimal):
        self.wallet += D(amount)

    def buy_shares(self, project: Project, num_shares: int):
        cost = (project.share_price * D(num_shares)).quantize(Decimal("0.01"))
        if self.wallet < cost:
            raise ValueError("Insufficient funds")
        project.sell_shares(self.id, num_shares)
        self.wallet -= cost
        self.holdings[project.id] = self.holdings.get(project.id, 0) + num_shares
        return cost

@dataclass
class Platform:
    projects: Dict[str, Project] = field(default_factory=dict)
    investors: Dict[str, Investor] = field(default_factory=dict)

    def register_project(self, name: str, description: str, assets: Decimal, liabilities: Decimal, share_price: Decimal):
        spv = SPV(id=str(uuid4()), project_id="")
        proj_id = str(uuid4())
        spv.project_id = proj_id
        spv.assets_value = D(assets)
        spv.liabilities_value = D(liabilities)
        project = Project(id=proj_id, name=name, description=description, spv=spv, share_price=D(share_price))
        project.struct_shares()
        self.projects[proj_id] = project
        return project

    def onboard_investor(self, name: str, deposit_amount: Decimal):
        investor = Investor(id=str(uuid4()), name=name)
        investor.deposit(D(deposit_amount))
        self.investors[investor.id] = investor
        return investor

    def distribute_profit(self, project: Project, revenue: Decimal, expenses: Decimal):
        profit = D(revenue) - D(expenses)
        distribution = {}
        if profit <= 0:
            loss = -profit
            for inv_id, shares in project.investors.items():
                share_frac = D(shares) / D(project.total_shares)
                distribution[inv_id] = - (loss * share_frac).quantize(Decimal("0.01"))
            project.spv.assets_value -= D(loss)
            return distribution
        fee = (profit * project.management_fee_pct).quantize(Decimal("0.01"))
        distributable = profit - fee
        for inv_id, shares in project.investors.items():
            share_frac = D(shares) / D(project.total_shares)
            distribution[inv_id] = (distributable * share_frac).quantize(Decimal("0.01"))
        project.spv.assets_value += distributable
        return distribution

if __name__ == "__main__":
    platform = Platform()

    # Step 1: Register project
    print("=== Register a new project ===")
    name = input("Project name: ")
    description = input("Project description: ")
    assets = input("Total assets value (BDT): ")
    liabilities = input("Total liabilities value (BDT): ")
    share_price = input("Share price (BDT): ")
    project = platform.register_project(name, description, assets, liabilities, share_price)
    print(f"Project '{project.name}' registered with {project.total_shares} shares at {project.share_price} BDT each.\n")

    # Step 2: Onboard investors
    num_investors = int(input("How many investors to onboard? "))
    for _ in range(num_investors):
        inv_name = input("Investor name: ")
        deposit = input("Initial deposit (BDT): ")
        investor = platform.onboard_investor(inv_name, deposit)
        print(f"Investor '{investor.name}' onboarded with wallet {investor.wallet} BDT")

    # Step 3: Investors buy shares
    print("\n=== Investors buying shares ===")
    for inv_id, investor in platform.investors.items():
        print(f"\nInvestor: {investor.name}, Wallet: {investor.wallet}")
        buy_qty = int(input("Number of shares to buy: "))
        try:
            cost = investor.buy_shares(project, buy_qty)
            print(f"{investor.name} bought {buy_qty} shares for {cost} BDT")
        except Exception as e:
            print("Error:", e)

    # Step 4: Profit distribution
    print("\n=== Profit/Loss Distribution ===")
    revenue = input("Enter project revenue for the period (BDT): ")
    expenses = input("Enter project expenses for the period (BDT): ")
    distribution = platform.distribute_profit(project, revenue, expenses)
    for inv_id, amount in distribution.items():
        investor = platform.investors[inv_id]
        print(f"{investor.name} receives: {amount} BDT")
