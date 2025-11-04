from flask import Flask, render_template, request, redirect, url_for, session
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "disaster_relief_secret_key"

# --- Helper Functions ---

def calculate_allocation(request_data, total_stock):
    allocation_results = []
    total_priority = 0

    for resource, requested in request_data.items():
        available = total_stock.get(resource, 0)
        if requested <= available:
            allocated = requested
            alloc_type = "Full"
        elif available > 0:
            allocated = available
            alloc_type = "Partial"
        else:
            allocated = 0
            alloc_type = "None"

        # Update remaining stock
        total_stock[resource] = max(available - allocated, 0)

        # Calculate priority (arbitrary but consistent weight)
        priority = allocated * {"food": 9, "water": 8, "medicine": 10, "clothes": 5}.get(resource, 1)
        total_priority += priority

        allocation_results.append({
            "resource": resource.capitalize(),
            "available": available,
            "requested": requested,
            "allocated": allocated,
            "type": alloc_type,
            "priority": priority
        })

    return allocation_results, total_priority


# --- Routes ---

@app.route("/")
def index():
    remaining = session.get("remaining_stock", None)
    return render_template("index.html", remaining=remaining)


@app.route("/set_stock", methods=["POST"])
def set_stock():
    session["total_stock"] = {
        "food": int(request.form["food"]),
        "water": int(request.form["water"]),
        "medicine": int(request.form["medicine"]),
        "clothes": int(request.form["clothes"])
    }
    session["remaining_stock"] = session["total_stock"].copy()
    session["report"] = []
    return redirect(url_for("index"))


@app.route("/allocate", methods=["POST"])
def allocate():
    if "remaining_stock" not in session:
        return redirect(url_for("index"))

    location = request.form["location"]

    request_data = {
        "food": int(request.form["food"]),
        "water": int(request.form["water"]),
        "medicine": int(request.form["medicine"]),
        "clothes": int(request.form["clothes"])
    }

    remaining_stock = session["remaining_stock"]
    results, total_priority = calculate_allocation(request_data, remaining_stock)

    # Append to report
    report = session.get("report", [])
    for entry in results:
        entry["location"] = location
        report.append(entry)

    session["remaining_stock"] = remaining_stock
    session["report"] = report

    return redirect(url_for("report"))


@app.route("/report")
def report():
    report = session.get("report", [])
    remaining = session.get("remaining_stock", {"food": 0, "water": 0, "medicine": 0, "clothes": 0})
    total_priority = sum(item["priority"] for item in report)
    return render_template("report.html", report=report, remaining=remaining, total_priority=total_priority)


# --- Main Entry Point ---
if __name__ == "__main__":
    app.run(debug=True)
