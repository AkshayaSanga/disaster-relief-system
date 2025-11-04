from flask import Flask, render_template, request, redirect, url_for
import json, os

app = Flask(__name__)

# Resource Priority Information
RESOURCE_INFO = {
    "food": {"priority": 9},
    "water": {"priority": 8},
    "clothes": {"priority": 5},
    "medicine": {"priority": 10}
}

# ------------------------------
# Allocation Logic
# ------------------------------
def distribute_resources(requests_list, available_stock):
    allocations = []
    total_priority = 0

    items = []
    for idx, req in enumerate(requests_list):
        for res, info in RESOURCE_INFO.items():
            qty_requested = req.get(res, 0)
            if qty_requested > 0:
                items.append({
                    "location": idx + 1,
                    "resource": res.capitalize(),
                    "requested_qty": qty_requested,
                    "priority": info["priority"]
                })

    items.sort(key=lambda x: x["priority"], reverse=True)
    remaining_stock = available_stock.copy()

    for item in items:
        res = item["resource"].lower()
        if remaining_stock[res] <= 0:
            continue

        qty_to_allocate = min(item["requested_qty"], remaining_stock[res])
        remaining_stock[res] -= qty_to_allocate

        allocations.append({
            "location": item["location"],
            "resource": item["resource"],
            "requested_qty": item["requested_qty"],
            "allocated_qty": qty_to_allocate,
            "allocation_type": "Full" if qty_to_allocate == item["requested_qty"] else "Partial",
            "priority_value": item["priority"] * qty_to_allocate
        })
        total_priority += item["priority"] * qty_to_allocate

    distributed_stock = {
        res: available_stock[res] - remaining_stock[res]
        for res in available_stock
    }

    return allocations, total_priority, remaining_stock, distributed_stock


# ------------------------------
# Routes
# ------------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit_request', methods=['POST'])
def submit_request():
    data = {
        "latitude": request.form.get('latitude'),
        "longitude": request.form.get('longitude'),
        "food": int(request.form.get('food', 0)),
        "water": int(request.form.get('water', 0)),
        "clothes": int(request.form.get('clothes', 0)),
        "medicine": int(request.form.get('medicine', 0))
    }

    if not os.path.exists('requests.json'):
        with open('requests.json', 'w') as f:
            json.dump([], f)

    with open('requests.json', 'r') as f:
        requests_list = json.load(f)

    requests_list.append(data)

    with open('requests.json', 'w') as f:
        json.dump(requests_list, f, indent=4)

    return redirect(url_for('admin_dashboard'))


@app.route('/admin')
def admin_dashboard():
    if os.path.exists('requests.json'):
        with open('requests.json', 'r') as f:
            requests_list = json.load(f)
    else:
        requests_list = []
    return render_template('admin.html', requests=requests_list)


@app.route('/allocate', methods=['POST'])
def allocate_resources():
    available_stock = {
        "food": int(request.form.get('food_stock')),
        "water": int(request.form.get('water_stock')),
        "clothes": int(request.form.get('clothes_stock')),
        "medicine": int(request.form.get('medicine_stock'))
    }

    with open('requests.json', 'r') as f:
        requests_list = json.load(f)

    allocations, total_priority, remaining_stock, distributed_stock = distribute_resources(
        requests_list, available_stock
    )

    return render_template(
        'result.html',
        allocations=allocations,
        total_priority=round(total_priority, 2),
        remaining_stock=remaining_stock,
        distributed_stock=distributed_stock,
        available_stock=available_stock
    )


if __name__ == "__main__":
    app.run(debug=True)
