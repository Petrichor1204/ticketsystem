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
    """Split all users into VIP and Regular queues based on ticket type."""
    vip = [row for row in queue_rows if row["ticket_type"].lower() == "vip"]
    regular = [row for row in queue_rows if row["ticket_type"].lower() == "regular"]
    return vip, regular


def get_availability():
    """Compute remaining tickets based on transactions."""
    vip_left = VIP_TICKETS
    reg_left = REGULAR_TICKETS
    transactions = read_csv_as_dicts(paths.transactions_csv)
    for t in transactions:
        if t["status"].lower() == "confirmed":
            if t["ticket_type"].lower() == "vip":
                vip_left -= 1
            elif t["ticket_type"].lower() == "regular":
                reg_left -= 1
    return {"VIP": max(vip_left, 0), "Regular": max(reg_left, 0)}


@app.route("/register", methods=["POST"])
def register_user():
    """Add a new user to the correct queue (VIP or Regular)."""
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    ticket_type = data.get("ticket_type", "").title()

    if ticket_type not in ["VIP", "Regular"]:
        return jsonify({"error": "Invalid ticket type"}), 400

    new_entry = {
        "first_name": first_name,
        "last_name": last_name,
        "ticket_type": ticket_type,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    queue = read_csv_as_dicts(paths.queue_csv)
    queue.append(new_entry)
    write_queue(paths.queue_csv, queue)

    return jsonify({
        "message": f"{first_name} added to {ticket_type} queue.",
        "current_queue_length": len(queue)
    })


@app.route("/process_next", methods=["POST"])
def process_next():
    """Process one person at a time, with VIP priority."""
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
    """Return how many tickets remain."""
    return jsonify(get_availability())


@app.route("/queue", methods=["GET"])
def view_queue():
    """View everyone still waiting in line (both queues)."""
    queue = read_csv_as_dicts(paths.queue_csv)
    vip, regular = separate_queues(queue)
    return jsonify({
        "VIP Queue": vip,
        "Regular Queue": regular
    })


if __name__ == "__main__":
    # Make sure the server doesn't break if files aren't created yet
    os.makedirs(os.path.dirname(paths.transactions_csv) or ".", exist_ok=True)
    app.run(debug=True)
