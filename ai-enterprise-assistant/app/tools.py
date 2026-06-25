from data.mock_data import EMPLOYEES, add_ticket, REPORTS, get_tickets


# ── Business actions (used directly as Gemini tool functions) ──────────────

def create_ticket(title: str, description: str, priority: str = "medium") -> dict:
    """Create a new support ticket with the given title, description, and priority.

    Args:
        title: A short summary of the issue (e.g. "VPN not connecting").
        description: Detailed description of the problem.
        priority: Priority level — "high", "medium", or "low". Defaults to "medium".

    Returns:
        A dict with ticket_id, title, description, priority, and status.
    """
    ticket = add_ticket(title, description, priority)
    return {
        "ticket_id": ticket["ticket_id"],
        "title": ticket["title"],
        "description": ticket["description"],
        "priority": ticket["priority"],
        "status": ticket["status"],
    }


def get_employee_info(name_or_id: str) -> dict:
    """Look up an employee by name or employee ID.

    Searches by full name, partial name, or employee ID (e.g. "E001").
    If multiple employees match, returns a disambiguation list instead of guessing.

    Args:
        name_or_id: Employee name (full or partial) or employee ID.

    Returns:
        A dict with either a single employee record or a disambiguation list.
    """
    query = name_or_id.strip().lower()

    results = []
    for emp in EMPLOYEES:
        if query == emp["id"].lower():
            return {"match": "single", "employee": dict(emp)}
        if query in emp["name"].lower():
            results.append(dict(emp))

    if len(results) == 0:
        return {"match": "none", "message": f"No employee found matching '{name_or_id}'."}
    if len(results) == 1:
        return {"match": "single", "employee": results[0]}
    return {
        "match": "multiple",
        "message": f"Multiple employees match '{name_or_id}'. Please specify which one.",
        "candidates": results,
    }


def generate_report(report_type: str) -> dict:
    """Generate a pre-computed business report.

    Args:
        report_type: The type of report — "open_tickets" or "headcount".

    Returns:
        A dict with the report data, or an error if the report type is unknown.
    """
    if report_type not in REPORTS:
        return {
            "error": f"Unknown report type '{report_type}'. Available: {', '.join(REPORTS.keys())}.",
        }
    return {"report_type": report_type, "data": dict(REPORTS[report_type])}


# ── Dispatch ──────────────────────────────────────────────────────────────

TOOL_FUNCTIONS = {
    "create_ticket": create_ticket,
    "get_employee_info": get_employee_info,
    "generate_report": generate_report,
}


def dispatch(name: str, args: dict) -> dict:
    """Execute a tool by name with the given arguments.

    Args:
        name: Tool name (key in TOOL_FUNCTIONS).
        args: Keyword arguments to pass to the tool function.

    Returns:
        The tool's result dict.
    """
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    return fn(**args)


# ── Rule-based fallback (deterministic keyword router) ────────────────────
# This is the "before" baseline AND the safety net when the LLM is unavailable.

def rule_based_fallback(question: str) -> dict:
    """Fallback that routes by keyword when the LLM call fails."""
    q = question.lower()

    # Ticket creation
    if "ticket" in q:
        result = create_ticket(
            title="Issue reported",
            description=question,
            priority="high" if any(w in q for w in ["high", "critical", "urgent"]) else "medium",
        )
        return {
            "answer": f"I created a ticket for you: {result['ticket_id']} ({result['priority']} priority). A human will follow up.",
            "action_taken": "create_ticket",
            "action_result": result,
        }

    # Report generation
    if "report" in q:
        if "headcount" in q or "employee" in q:
            rtype = "headcount"
        else:
            rtype = "open_tickets"
        result = generate_report(rtype)
        return {
            "answer": f"Here is the {rtype} report: {result['data']}",
            "action_taken": "generate_report",
            "action_result": result,
        }

    # Employee lookup
    for emp in EMPLOYEES:
        if emp["name"].lower() in q:
            result = get_employee_info(emp["name"])
            return {
                "answer": f"Found {emp['name']}: {emp['role']} in {emp['department']}.",
                "action_taken": "get_employee_info",
                "action_result": result,
            }

    return {
        "answer": "I'm not sure how to help with that. Try asking me to create a ticket, look up an employee, or generate a report.",
        "action_taken": None,
        "action_result": None,
    }
