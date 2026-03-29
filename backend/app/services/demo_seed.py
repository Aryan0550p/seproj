from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import or_
from sqlmodel import Session, delete, select

from app.core.security import hash_password
from app.models import (
    ApprovalFlow,
    ApprovalLog,
    ApprovalStep,
    Company,
    EmployeeManagerMap,
    Expense,
    ExpenseStatus,
    Receipt,
    Role,
    SessionToken,
    User,
)


def _to_int_ids(values: list[int | None]) -> list[int]:
    return [v for v in values if v is not None]


def reset_company_data(session: Session, company_id: int, keep_admin_user_id: int | None = None) -> dict:
    user_ids = _to_int_ids(session.exec(select(User.id).where(User.company_id == company_id)).all())
    expense_ids = _to_int_ids(session.exec(select(Expense.id).where(Expense.company_id == company_id)).all())

    if expense_ids:
        session.exec(delete(ApprovalStep).where(ApprovalStep.expense_id.in_(expense_ids)))
        session.exec(delete(ApprovalLog).where(ApprovalLog.expense_id.in_(expense_ids)))
        session.exec(delete(Receipt).where(Receipt.expense_id.in_(expense_ids)))

    if user_ids:
        session.exec(
            delete(EmployeeManagerMap).where(
                or_(
                    EmployeeManagerMap.employee_id.in_(user_ids),
                    EmployeeManagerMap.manager_id.in_(user_ids),
                )
            )
        )
        session.exec(delete(SessionToken).where(SessionToken.user_id.in_(user_ids)))

    session.exec(delete(ApprovalFlow).where(ApprovalFlow.company_id == company_id))
    session.exec(delete(Expense).where(Expense.company_id == company_id))

    if keep_admin_user_id is not None:
        session.exec(
            delete(User).where(
                User.company_id == company_id,
                User.id != keep_admin_user_id,
            )
        )
    else:
        session.exec(delete(User).where(User.company_id == company_id))

    session.commit()

    remaining_users = session.exec(select(User.id).where(User.company_id == company_id)).all()
    remaining_expenses = session.exec(select(Expense.id).where(Expense.company_id == company_id)).all()

    return {
        "message": "Company data reset complete",
        "company_id": company_id,
        "remaining_users": len(remaining_users),
        "remaining_expenses": len(remaining_expenses),
    }


def seed_company_demo_data(session: Session, admin_user: User) -> dict:
    reset_company_data(session, admin_user.company_id, keep_admin_user_id=admin_user.id)

    company = session.get(Company, admin_user.company_id)
    if company:
        company.name = "Acme Demo Corp"
        company.country = "India"
        company.default_currency = "INR"
        session.add(company)
        session.commit()

    suffix = f"c{admin_user.company_id}"

    mgr1 = User(
        name="Sarah Manager",
        email=f"sarah.{suffix}@acme-demo.com",
        password_hash=hash_password("manager123"),
        role=Role.manager,
        company_id=admin_user.company_id,
    )
    mgr2 = User(
        name="John Director",
        email=f"john.{suffix}@acme-demo.com",
        password_hash=hash_password("manager123"),
        role=Role.manager,
        company_id=admin_user.company_id,
    )
    emp1 = User(
        name="Marc Employee",
        email=f"marc.{suffix}@acme-demo.com",
        password_hash=hash_password("employee123"),
        role=Role.employee,
        company_id=admin_user.company_id,
    )
    emp2 = User(
        name="Alice Engineer",
        email=f"alice.{suffix}@acme-demo.com",
        password_hash=hash_password("employee123"),
        role=Role.employee,
        company_id=admin_user.company_id,
    )
    emp3 = User(
        name="Raj Developer",
        email=f"raj.{suffix}@acme-demo.com",
        password_hash=hash_password("employee123"),
        role=Role.employee,
        company_id=admin_user.company_id,
    )

    session.add_all([mgr1, mgr2, emp1, emp2, emp3])
    session.commit()
    for user in [mgr1, mgr2, emp1, emp2, emp3]:
        session.refresh(user)

    session.add_all(
        [
            EmployeeManagerMap(employee_id=emp1.id, manager_id=mgr1.id),
            EmployeeManagerMap(employee_id=emp2.id, manager_id=mgr1.id),
            EmployeeManagerMap(employee_id=emp3.id, manager_id=mgr2.id),
        ]
    )
    session.commit()

    for emp, manager_id in [(emp1, mgr1.id), (emp2, mgr1.id), (emp3, mgr2.id)]:
        session.add(
            ApprovalFlow(
                company_id=admin_user.company_id,
                user_id=emp.id,
                description=f"Standard approval for {emp.name}",
                manager_first=True,
                sequential=True,
                min_approval_percentage=60,
                approvers=[manager_id, mgr2.id if manager_id != mgr2.id else mgr1.id],
                required_approvers=[manager_id],
            )
        )
    session.commit()

    now = datetime.utcnow()

    expenses = [
        Expense(
            user_id=emp1.id,
            company_id=admin_user.company_id,
            amount=567,
            currency="USD",
            converted_amount=47250,
            base_currency="INR",
            category="Food",
            description="Client dinner at Nobu",
            paid_by="Self",
            expense_date=now - timedelta(days=1),
            remarks="Business dinner with Globex prospect",
            status=ExpenseStatus.draft,
        ),
        Expense(
            user_id=emp1.id,
            company_id=admin_user.company_id,
            amount=1200,
            currency="INR",
            converted_amount=1200,
            base_currency="INR",
            category="Travel",
            description="Train ticket - Mumbai to Pune",
            paid_by="Self",
            expense_date=now - timedelta(days=5),
            remarks="Quarterly review meeting",
            status=ExpenseStatus.pending,
        ),
        Expense(
            user_id=emp1.id,
            company_id=admin_user.company_id,
            amount=2500,
            currency="INR",
            converted_amount=2500,
            base_currency="INR",
            category="Food",
            description="Team lunch - sprint celebration",
            paid_by="Self",
            expense_date=now - timedelta(days=15),
            remarks="End of Q4 sprint",
            status=ExpenseStatus.approved,
        ),
        Expense(
            user_id=emp1.id,
            company_id=admin_user.company_id,
            amount=4500,
            currency="USD",
            converted_amount=375000,
            base_currency="INR",
            category="Lodging",
            description="Luxury resort offsite",
            paid_by="Self",
            expense_date=now - timedelta(days=30),
            remarks="Team offsite retreat",
            status=ExpenseStatus.rejected,
        ),
        Expense(
            user_id=emp2.id,
            company_id=admin_user.company_id,
            amount=250,
            currency="EUR",
            converted_amount=22500,
            base_currency="INR",
            category="Lodging",
            description="Hotel - annual conference",
            paid_by="Company Card",
            expense_date=now - timedelta(days=3),
            remarks="Tech conference in Amsterdam",
            status=ExpenseStatus.pending,
        ),
        Expense(
            user_id=emp2.id,
            company_id=admin_user.company_id,
            amount=180,
            currency="USD",
            converted_amount=15000,
            base_currency="INR",
            category="Food",
            description="Client dinner - SaaS onboarding",
            paid_by="Self",
            expense_date=now - timedelta(days=12),
            remarks="",
            status=ExpenseStatus.approved,
        ),
        Expense(
            user_id=emp2.id,
            company_id=admin_user.company_id,
            amount=45,
            currency="USD",
            converted_amount=3750,
            base_currency="INR",
            category="Miscellaneous",
            description="Office supplies - keyboard",
            paid_by="Self",
            expense_date=now - timedelta(days=1),
            remarks="Ergonomic keyboard",
            status=ExpenseStatus.draft,
        ),
        Expense(
            user_id=emp3.id,
            company_id=admin_user.company_id,
            amount=950,
            currency="INR",
            converted_amount=950,
            base_currency="INR",
            category="Travel",
            description="Metro card recharge - monthly",
            paid_by="Self",
            expense_date=now - timedelta(days=2),
            remarks="Monthly commute",
            status=ExpenseStatus.pending,
        ),
        Expense(
            user_id=emp3.id,
            company_id=admin_user.company_id,
            amount=3200,
            currency="INR",
            converted_amount=3200,
            base_currency="INR",
            category="Food",
            description="Team snacks - hackathon",
            paid_by="Self",
            expense_date=now - timedelta(days=10),
            remarks="Hackathon day supplies",
            status=ExpenseStatus.approved,
        ),
    ]

    session.add_all(expenses)
    session.commit()
    for expense in expenses:
        session.refresh(expense)

    pending_expenses = [e for e in expenses if e.status == ExpenseStatus.pending]
    approved_expenses = [e for e in expenses if e.status == ExpenseStatus.approved]
    rejected_expenses = [e for e in expenses if e.status == ExpenseStatus.rejected]

    for expense in pending_expenses:
        primary_manager = mgr1.id if expense.user_id in (emp1.id, emp2.id) else mgr2.id
        session.add(
            ApprovalStep(
                expense_id=expense.id,
                approver_id=primary_manager,
                sequence_order=1,
                required=True,
                status="pending",
            )
        )

    for expense in approved_expenses:
        approver_id = mgr1.id if expense.user_id in (emp1.id, emp2.id) else mgr2.id
        session.add(
            ApprovalLog(
                expense_id=expense.id,
                approver_id=approver_id,
                decision="approved",
                comment="Approved for demo workflow.",
                timestamp=expense.expense_date + timedelta(days=1),
            )
        )

    for expense in rejected_expenses:
        session.add(
            ApprovalLog(
                expense_id=expense.id,
                approver_id=mgr1.id,
                decision="rejected",
                comment="Rejected for budget threshold demo.",
                timestamp=expense.expense_date + timedelta(days=1),
            )
        )

    session.commit()

    role_counts = {"admin": 1, "manager": 2, "employee": 3}
    status_counts = {
        "draft": len([e for e in expenses if e.status == ExpenseStatus.draft]),
        "pending": len([e for e in expenses if e.status == ExpenseStatus.pending]),
        "approved": len([e for e in expenses if e.status == ExpenseStatus.approved]),
        "rejected": len([e for e in expenses if e.status == ExpenseStatus.rejected]),
    }

    return {
        "message": "Demo data loaded successfully",
        "company": {
            "id": admin_user.company_id,
            "name": company.name if company else "",
            "country": company.country if company else "",
            "base_currency": company.default_currency if company else "",
        },
        "users": role_counts,
        "expenses": status_counts,
        "credentials": [
            {"role": "manager", "email": mgr1.email, "password": "manager123"},
            {"role": "manager", "email": mgr2.email, "password": "manager123"},
            {"role": "employee", "email": emp1.email, "password": "employee123"},
            {"role": "employee", "email": emp2.email, "password": "employee123"},
            {"role": "employee", "email": emp3.email, "password": "employee123"},
        ],
    }
