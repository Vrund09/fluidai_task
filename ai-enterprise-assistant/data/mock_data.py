EMPLOYEES = [
    {"id": "E001", "name": "Priya Sharma", "department": "Engineering", "role": "Senior Developer", "email": "priya.sharma@company.com"},
    {"id": "E002", "name": "Rahul Sharma", "department": "Marketing", "role": "Marketing Lead", "email": "rahul.sharma@company.com"},
    {"id": "E003", "name": "Alice Chen", "department": "Engineering", "role": "DevOps Engineer", "email": "alice.chen@company.com"},
    {"id": "E004", "name": "Bob Martinez", "department": "Sales", "role": "Account Executive", "email": "bob.martinez@company.com"},
    {"id": "E005", "name": "Diana Okonkwo", "department": "HR", "role": "HR Manager", "email": "diana.okonkwo@company.com"},
]

_ticket_counter = 1000
_tickets = []


def get_next_ticket_id() -> str:
    global _ticket_counter
    _ticket_counter += 1
    return f"TKT-{_ticket_counter}"


def add_ticket(title: str, description: str, priority: str) -> dict:
    ticket = {
        "ticket_id": get_next_ticket_id(),
        "title": title,
        "description": description,
        "priority": priority,
        "status": "open",
    }
    _tickets.append(ticket)
    return ticket


def get_tickets() -> list[dict]:
    return list(_tickets)


REPORTS = {
    "open_tickets": {
        "total_open": 12,
        "by_priority": {"high": 3, "medium": 5, "low": 4},
        "avg_resolution_hours": 28.5,
    },
    "headcount": {
        "total_employees": len(EMPLOYEES),
        "by_department": {
            "Engineering": 2,
            "Marketing": 1,
            "Sales": 1,
            "HR": 1,
        },
    },
}
