import json
from flask import Flask, request, jsonify, render_template
from utils.storage import (
    DataPaths, ensure_files, read_csv_as_dicts,
    append_transaction, write_queue
)
import time
import os

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/register")
def register_page():
    return render_template('register.html')

@app.route("/summary")
def summary_page():
    return render_template('summary.html')

# File setup
paths = DataPaths(
    transactions_csv="data/transactions.csv",
    queue_csv="data/queue.csv"
)
ensure_files(paths)

# Set starting ticket availability
VIP_TICKETS = 3
REGULAR_TICKETS = 5


def separate_queues(queue_rows):
    vip = [row for row in queue_rows if row["ticket_type"].lower() == "vip"]
    regular = [row for row in queue_rows if row["ticket_type"].lower() == "regular"]
    return vip, regular


def get_availability():    
    path = 'data/availability.json'
    try:
        with open(path, 'r') as f:
            current = json.load(f)
    except FileNotFoundError:
        current = {"VIP": VIP_TICKETS, "Regular": REGULAR_TICKETS}
        with open(path, 'w') as f:
            json.dump(current, f)
    return current


def update_availability(ticket_type):
    """Update availability after processing a ticket."""
    try:
        with open('data/availability.json', 'r') as f:
            current = json.load(f)
        
        if ticket_type.upper() == "VIP":
            current["VIP"] = max(current["VIP"] - 1, 0)
        elif ticket_type.upper() == "REGULAR":
            current["Regular"] = max(current["Regular"] - 1, 0)
            
        with open('data/availability.json', 'w') as f:
            json.dump(current, f)
            
    except FileNotFoundError:
        get_availability()  # Create initial file if it doesn't exist

def get_queue_position(first_name, last_name, ticket_type):
    queue = read_csv_as_dicts(paths.queue_csv)
    vip_queue, regular_queue = separate_queues(queue)
    
    target_queue = vip_queue if ticket_type.lower() == "vip" else regular_queue
    
    for idx, user in enumerate(target_queue):
        if user["first_name"] == first_name and user["last_name"] == last_name:
            # Add 1 because position is 1-indexed for users
            return idx + 1
    return None


@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.json
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    ticket_type = data.get("ticket_type", "").strip()

    if not first_name or not last_name:
        return jsonify({"error": "First name and last name are required"}), 400

    if ticket_type not in ["VIP", "Regular"]:
        return jsonify({"error": "Invalid ticket type"}), 400


    # Normalize to VIP/Regular
    ticket_type = "VIP" if ticket_type == "VIP" else "Regular"

    new_entry = {
        "first_name": first_name,
        "last_name": last_name,
        "ticket_type": ticket_type,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    queue = read_csv_as_dicts(paths.queue_csv)
    queue.append(new_entry)
    write_queue(paths.queue_csv, queue)

    # Get position in queue
    position = get_queue_position(first_name, last_name, ticket_type)

    return jsonify({
        "message": f"{first_name} {last_name} added to {ticket_type} queue.",
        "first_name": first_name,
        "last_name": last_name,
        "ticket_type": ticket_type,
        "queue_position": position,
        "current_queue_length": len(queue)
    })




@app.route("/api/process_user", methods=["POST"])
def process_user():

    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    ticket_type = data.get("ticket_type")

    # Load current queues and availability
    queue = read_csv_as_dicts(paths.queue_csv)
    vip_queue, regular_queue = separate_queues(queue)
    availability = get_availability()
    vip_left, reg_left = availability["VIP"], availability["Regular"]

    # Order is priority-based: VIP queue first, then Regular
    serving_order = vip_queue + regular_queue

    updates = []
    processed_user = None

    for idx, user in enumerate(serving_order):
        current_type = user["ticket_type"].upper()
        current_name = f"{user['first_name']} {user['last_name']}"
        updates.append({
            "name": current_name,
            "ticket_type": current_type,
            "status": "Processing",
            "remaining": {"VIP": vip_left, "Regular": reg_left}
        })

        time.sleep(1)  # simulate processing delay

        # Serve based on separate inventories
        if current_type == "VIP":
            if vip_left > 0:
                vip_left -= 1
                status = "Confirmed"
            else:
                status = "Sold Out"
        elif current_type == "REGULAR":
            if reg_left > 0:
                reg_left -= 1
                status = "Confirmed"
            else:
                status = "Sold Out"
        else:
            status = "Invalid Type"

        # Persist new availability after each user
        with open('data/availability.json', 'w') as f:
            json.dump({"VIP": vip_left, "Regular": reg_left}, f)

        # Log transaction
        append_transaction(paths.transactions_csv, {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "ticket_type": current_type,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status
        })

        updates[-1]["status"] = status
        updates[-1]["remaining"] = {"VIP": vip_left, "Regular": reg_left}


        if user["first_name"] == first_name and user["last_name"] == last_name:
            processed_user = user
            break

    # Remove everyone processed so far (up to this user)
    updated_queue = [
        u for u in queue
        if not any(
            (u["first_name"] == p["first_name"] and u["last_name"] == p["last_name"])
            for p in serving_order[: len(updates)]
        )
    ]
    write_queue(paths.queue_csv, updated_queue)

    final_status = updates[-1]["status"] if updates else "Unknown"

    return jsonify({
        "updates": updates,
        "final_status": final_status,
        "remaining_tickets": {"VIP": vip_left, "Regular": reg_left}
    })




@app.route("/process_next", methods=["POST"])
def process_next():
    queue = read_csv_as_dicts(paths.queue_csv)
    vip_queue, regular_queue = separate_queues(queue)

    availability = get_availability()
    vip_left = availability["VIP"]
    reg_left = availability["Regular"]

    # Pick next user (VIP first)
    if vip_queue:
        next_user = vip_queue.pop(0)
        ticket_type = "VIP"
        if vip_left > 0:
            status = "Confirmed"
        else:
            status = "Sold Out"
    elif regular_queue:
        next_user = regular_queue.pop(0)
        ticket_type = "Regular"
        if reg_left > 0:
            status = "Confirmed"
        else:
            status = "Sold Out"
    else:
        return jsonify({"message": "No users in queue."})

    # Log transaction
    append_transaction(paths.transactions_csv, {
        "first_name": next_user["first_name"],
        "last_name": next_user["last_name"],
        "ticket_type": ticket_type,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status
    })

    # Rebuild queue (remove processed user)
    updated_queue = vip_queue + regular_queue
    write_queue(paths.queue_csv, updated_queue)

    return jsonify({
        "processed": f"{next_user['first_name']} {next_user['last_name']}",
        "ticket_type": ticket_type,
        "status": status,
        "remaining_tickets": get_availability()
    })


@app.route("/availability", methods=["GET"])
def view_availability():
    return jsonify(get_availability())


@app.route("/queue", methods=["GET"])
def view_queue():
    queue = read_csv_as_dicts(paths.queue_csv)
    vip, regular = separate_queues(queue)
    return jsonify({
        "VIP Queue": vip,
        "Regular Queue": regular
    })

@app.route("/summary_data", methods=["GET"])
def summary_data():
    """Return summary of tickets sold and remaining availability."""
    try:
        # --- Read availability ---
        with open('data/availability.json', 'r') as f:
            availability = json.load(f)
        vip_remaining = availability.get("VIP", 0)
        regular_remaining = availability.get("Regular", 0)
    except FileNotFoundError:
        vip_remaining = VIP_TICKETS
        regular_remaining = REGULAR_TICKETS

    # --- Count tickets sold from transactions.csv ---
    transactions = read_csv_as_dicts(paths.transactions_csv)
    vip_sold = sum(1 for t in transactions if t.get("ticket_type", "").lower() == "vip" and t.get("status", "").lower() == "confirmed")
    regular_sold = sum(1 for t in transactions if t.get("ticket_type", "").lower() == "regular" and t.get("status", "").lower() == "confirmed")

    # --- Totals ---
    total_sold = vip_sold + regular_sold
    total_remaining = vip_remaining + regular_remaining

    return jsonify({
        "vip_sold": vip_sold,
        "regular_sold": regular_sold,
        "vip_remaining": vip_remaining,
        "regular_remaining": regular_remaining,
        "total_sold": total_sold,
        "total_remaining": total_remaining
    })


@app.route("/api/cancel_ticket", methods=["DELETE"])
def cancel_ticket():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    ticket_type = data.get("ticket_type")

    if not first_name or not last_name or not ticket_type:
        return jsonify({"error": "Missing required information"}), 400

    # Read current queue
    queue = read_csv_as_dicts(paths.queue_csv)

    # Filter out the matching ticket
    updated_queue = [
        q for q in queue
        if not (
            q["first_name"].strip().lower() == first_name.strip().lower()
            and q["last_name"].strip().lower() == last_name.strip().lower()
            and q["ticket_type"].strip().lower() == ticket_type.strip().lower()
        )
    ]

    if len(updated_queue) == len(queue):
        return jsonify({"error": "Ticket not found"}), 404

    # Write the updated queue back
    write_queue(paths.queue_csv, updated_queue)

    

    return jsonify({
        "message": f"{first_name} {last_name}'s {ticket_type} ticket was cancelled successfully.",

    }), 200


if __name__ == "__main__":
    # Make sure the server doesn't break if files aren't created yet
    os.makedirs(os.path.dirname(paths.transactions_csv) or ".", exist_ok=True)
    app.run(debug=True)