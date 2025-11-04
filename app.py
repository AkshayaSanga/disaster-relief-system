from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# -----------------------------
# Global variables
# -----------------------------
total_resources = {}
remaining_resources = {}
allocations = []


# -----------------------------
# Step 1 – Enter Total Stock
# -----------------------------
@app.route('/')
def home():
    """Initial resource input page."""
    return render_template('index.html', total=None)


@app.route('/save_totals', methods=['POST'])
def save_totals():
    """Save total available stock and start allocation."""
    global total_resources, remaining_resources, allocations

    total_resources = {
        "Food": int(request.form['food']),
        "Water": int(request.form['water']),
        "Clothes": int(request.form['clothes']),
        "Medicine": int(request.form['medicine'])
    }

    remaining_resources = total_resources.copy()
    allocations = []

    # Redirect immediately to allocation step
    return redirect(url_for('allocate'))


# -----------------------------
# Step 2 – Resource Allocation
# -----------------------------
@app.route('/allocate', methods=['GET', 'POST'])
def allocate():
    """Handle each new location request."""
    global remaining_resources, allocations

    if request.method == 'POST':
        # Generate a simple location label
        location_name = f"Location {len(allocations) + 1}"

        # Get requested quantities
        requests_data = {
            "Food": int(request.form['food']),
            "Water": int(request.form['water']),
            "Clothes": int(request.form['clothes']),
            "Medicine": int(request.form['medicine'])
        }

        allocation_result = {}
        total_priority = 0

        # Allocation logic
        for resource, req_qty in requests_data.items():
            avail = remaining_resources.get(resource, 0)
            if req_qty <= avail:
                allocated = req_qty
                status = "Full"
            elif avail > 0:
                allocated = avail
                status = "Partial"
            else:
                allocated = 0
                status = "None"

            remaining_resources[resource] = max(avail - allocated, 0)
            priority = allocated * 10
            total_priority += priority

            allocation_result[resource] = {
                "Requested": req_qty,
                "Allocated": allocated,
                "Type": status,
                "Priority": priority
            }

        # Save this location’s allocation
        allocations.append({
            "location": location_name,
            "resources": allocation_result,
            "total_priority": total_priority
        })

        # If stock exhausted or user clicks Exit, go to report
        if all(v == 0 for v in remaining_resources.values()) or 'exit' in request.form:
            return redirect(url_for('result'))

    return render_template('request.html', remaining=remaining_resources)


# -----------------------------
# Step 3 – Final Report
# -----------------------------
@app.route('/result')
def result():
    """Display final summary report."""
    return render_template('result.html', allocations=allocations, remaining=remaining_resources)


# -----------------------------
# Run the app
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
