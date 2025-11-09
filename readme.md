Event Ticketing System

A lightweight Flask + JavaScript web app that manages event ticket purchases with VIP-priority queueing, real-time updates, and persistent CSV logging.
Users can register, purchase, cancel tickets, and view a live sales summary—all in one interface.

🚀 Features

✅ Priority-Based Queues – VIP tickets always processed before Regular
✅ Auto-Cancellation – Frees up ticket spots immediately after a user cancels
✅ Sales Summary – Shows tickets sold and remaining availability per type
✅ Persistent Storage – All data saved in simple CSV/JSON files
✅ Error Handling – Graceful responses for invalid or missing input

🧠 How It Works
🎫 Ticket Flow

Register: Users enter name and ticket type (VIP / Regular).

Queue: Requests are stored in queue.csv.

Processing: VIPs are served first, then Regulars.

Logging: All results (Confirmed, Sold Out, Cancelled) are saved in transactions.csv.

Availability: Tracked persistently in availability.json.

Summary: /summary page shows tickets sold and remaining in real time.

🗂 File Overview
File	Purpose
app.py	Main Flask backend with all routes
utils/storage.py	CSV helpers for reading/writing queue and transactions
static/js/main.js	Handles registration, processing, and cancellation
static/js/summary.js	Loads sales/availability summary
static/css/style.css	Page styling
data/queue.csv	Live user queue
data/transactions.csv	Transaction history
data/availability.json	Persistent ticket counts
🧩 Key Endpoints
Route	Method	Description
/api/register	POST	Add user to the queue
/api/process_user	POST	Process ticket purchase for current user
/api/cancel_ticket	DELETE	Cancel a queued ticket and free up availability
/availability	GET	Get current VIP/Regular availability
/summary_data	GET	Get total sold and remaining tickets
🖥 Running the App
Prerequisites

Python 3.8+

Flask (install via pip install flask)

Steps
python app.py


Then open http://127.0.0.1:5000
 in your browser.

📊 Example Output
Type	Sold	Remaining
VIP	2	1
Regular	3	2

Cancelled users instantly free up new slots in the correct queue.

⚡ Error Handling

Missing fields → 400 Bad Request

Invalid ticket type → 400 Invalid Input

Ticket not found → 404 Not Found

Unexpected file errors → Graceful fallback with user-friendly message

🧾 Data Files

All files auto-generate when you run the app.
You can open them directly for inspection in Excel or any text editor.

transactions.csv: Logs all actions

queue.csv: Current waiting list

availability.json: Persistent availability counts