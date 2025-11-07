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
        status = t.get("status", "").lower()
        ticket_type = t.get("ticket_type", "").lower()

        if status == "confirmed":
            if ticket_type == "vip":
                vip_left -= 1
            elif ticket_type == "regular":
                reg_left -= 1

    return {"VIP": max(vip_left, 0), "Regular": max(reg_left, 0)}



def get_queue_position(first_name, last_name, ticket_type):
    """Get user's position in their respective queue."""
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
    """Process a specific user's ticket request."""
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    
    queue = read_csv_as_dicts(paths.queue_csv)
    vip_queue, regular_queue = separate_queues(queue)

    availability = get_availability()
    vip_left = availability["VIP"]
    reg_left = availability["Regular"]

    # Find the user in queues
    user_found = None
    ticket_type = None
    
    # Check VIP queue first
    for user in vip_queue:
        if user["first_name"] == first_name and user["last_name"] == last_name:
            user_found = user
            ticket_type = ticket_type
            break
    
    # If not in VIP, check Regular queue
    if not user_found:
        for user in regular_queue:
            if user["first_name"] == first_name and user["last_name"] == last_name:
                user_found = user
                ticket_type = "Regular"
                break
    
    if not user_found:
        return jsonify({"error": "User not found in queue"}), 404

    # Determine status based on availability
    if ticket_type == "VIP":
        status = "Confirmed" if vip_left > 0 else "Sold Out"
    else:
        status = "Confirmed" if reg_left > 0 else "Sold Out"

    # Log transaction
    append_transaction(paths.transactions_csv, {
        "first_name": first_name,
        "last_name": last_name,
        "ticket_type": ticket_type,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status
    })

    # Remove user from queue
    updated_queue = [u for u in queue if not (u["first_name"] == first_name and u["last_name"] == last_name)]
    write_queue(paths.queue_csv, updated_queue)

    return jsonify({
        "processed": f"{first_name} {last_name}",
        "ticket_type": ticket_type,
        "status": status,
        "remaining_tickets": get_availability()
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