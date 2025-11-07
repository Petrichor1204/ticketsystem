# Event Ticketing System - Documentation

## Project Overview
This is a Python-based Event Ticketing System that manages ticket purchases with priority queue handling. VIP tickets are processed before Regular tickets, and all transactions are logged to a CSV file.

## Code Structure

### Files
1. **app.py** - Main application file containing the user interface and menu system
2. **ticket_manager.py** - Core ticketing logic with TicketManager class
3. **transactions.csv** - Auto-generated log file for all transactions

### Data Structures Used

#### 1. **Deque (Double-ended Queue)**
- **Purpose**: Managing VIP and Regular ticket queues
- **Location**: `self.vip_queue` and `self.regular_queue` in TicketManager class
- **Why**: Provides O(1) time complexity for both append and popleft operations, making it efficient for FIFO queue operations

#### 2. **Dictionary**
- **Purpose**: Storing and returning ticket availability, sales summaries, and queue status
- **Location**: Return values of `get_availability()`, `get_sales_summary()`, and `get_queue_status()`
- **Why**: Provides clear key-value mapping for organized data access

#### 3. **List (Implicit in Processing)**
- **Purpose**: Storing processed ticket information temporarily
- **Location**: `processed` list in `process_tickets()` method
- **Why**: Simple sequential storage for displaying results

#### 4. **Tuple**
- **Purpose**: Storing user registration data (name, ticket_type, timestamp)
- **Location**: Queue elements stored as tuples
- **Why**: Immutable data structure that groups related information together

### Class Structure

#### TicketManager Class
The core class that manages all ticketing operations.

**Attributes:**
- `vip_tickets`: Current available VIP tickets
- `regular_tickets`: Current available Regular tickets
- `initial_vip_tickets`: Initial VIP ticket count (for sales summary)
- `initial_regular_tickets`: Initial Regular ticket count (for sales summary)
- `vip_queue`: Deque for VIP ticket requests
- `regular_queue`: Deque for Regular ticket requests
- `log_file`: Path to CSV transaction log file

**Methods:**

1. **`__init__(vip_tickets, regular_tickets, log_file)`**
   - Initializes the ticket manager with specified ticket counts
   - Creates CSV log file if it doesn't exist

2. **`register_user(name, ticket_type)`**
   - Adds user to appropriate queue based on ticket type
   - Validates input for empty names and invalid ticket types
   - Stores timestamp with registration

3. **`process_tickets()`**
   - Processes all pending requests (VIP first, then Regular)
   - Updates ticket availability
   - Logs all transactions
   - Returns list of processed requests for user feedback

4. **`cancel_ticket(name, ticket_type)`**
   - Cancels a ticket and frees up availability
   - Validates that tickets were actually sold before cancelling
   - Logs cancellation transaction

5. **`get_sales_summary()`**
   - Returns detailed breakdown of tickets sold and remaining
   - Calculates sold tickets from initial and current counts

6. **`get_queue_status()`**
   - Returns number of pending requests in each queue

7. **`get_availability()`**
   - Returns current ticket availability for both types

8. **`_log_transaction(name, ticket_type, status)`**
   - Private method to log transactions to CSV file
   - Records name, ticket type, timestamp, and status

## How to Run the Program

### Prerequisites
- Python 3.6 or higher
- No external libraries required (uses only standard library)

### Running the Application

1. **Ensure all files are in the same directory:**
   ```
   project_folder/
   ├── app.py
   ├── ticket_manager.py
   └── transactions.csv (auto-generated)
   ```

2. **Run from command line:**
   ```bash
   python app.py
   ```

3. **Or run from IDE:**
   - Open `app.py` in your Python IDE
   - Click Run/Execute

### Using the System

#### Menu Options:

**1. Register for Ticket**
- Enter your name when prompted
- Enter ticket type: VIP or Regular
- System adds you to the appropriate queue

**2. Process Tickets**
- Processes all pending ticket requests
- VIP requests are processed first
- Shows confirmation or sold-out status for each request
- Updates ticket availability automatically

**3. View Availability**
- Shows current available tickets for VIP and Regular
- Shows pending requests in each queue

**4. Cancel Ticket**
- Enter your name
- Enter ticket type to cancel
- Frees up one ticket of that type
- Only works if tickets were actually sold

**5. View Sales Summary**
- Shows detailed breakdown of tickets sold and remaining
- Displays totals for each ticket type
- Shows overall sales statistics

**6. View Queue Status**
- Shows number of pending requests in VIP and Regular queues

**7. Exit**
- Exits the program
- All transactions remain logged in transactions.csv

## Features Implemented

### Required Features ✓
- [x] User Registration & Ticket Purchase
- [x] Ticket Queue Management (VIP priority)
- [x] Ticket Processing & Confirmation
- [x] Real-Time Ticket Availability
- [x] Transaction Logging to CSV
- [x] Priority Queue Implementation
- [x] User-Friendly Text-Based Interface
- [x] Efficient Data Structures

### Optional Extensions ✓
- [x] Auto-Cancellation (allows ticket cancellation)
- [x] Ticket Sales Summary
- [x] Error Handling (comprehensive input validation)

## Error Handling

The system handles the following errors gracefully:

1. **Empty Name Input**: Validates that name is not empty or whitespace-only
2. **Invalid Ticket Type**: Only accepts "VIP" or "Regular" (case-insensitive)
3. **Invalid Menu Choice**: Prompts user to enter valid option
4. **Keyboard Interrupt**: Handles Ctrl+C gracefully
5. **File Operations**: Handles potential file I/O errors
6. **Invalid Cancellation**: Prevents cancelling tickets that weren't sold

## Transaction Log Format

The `transactions.csv` file contains the following columns:

| Column | Description |
|--------|-------------|
| Name | Customer name |
| Ticket Type | VIP or Regular |
| Time | Timestamp (YYYY-MM-DD HH:MM:SS) |
| Status | Confirmed, Sold Out, or Cancelled |

Example:
```csv
Name,Ticket Type,Time,Status
John Doe,VIP,2025-11-06 14:30:15,Confirmed
Jane Smith,Regular,2025-11-06 14:31:22,Confirmed
Bob Johnson,VIP,2025-11-06 14:32:05,Sold Out
```

## Design Decisions

### Priority Queue Implementation
- Used two separate deques instead of a single priority queue
- Simpler to implement and understand
- Equally efficient for this use case (VIP always processed first)
- Maintains FIFO order within each priority level

### CSV Logging
- Append mode preserves transaction history across program runs
- Human-readable format for easy verification
- Can be imported into Excel or other tools for analysis

### Input Validation
- All user inputs are validated before processing
- Clear error messages guide users to correct input
- System remains stable even with invalid input

### User Feedback
- Clear visual indicators (✓ for success, ✗ for errors)
- Detailed processing results shown to user
- Real-time updates on ticket availability

## Testing Recommendations

### Test Cases to Verify:

1. **Basic Flow**
   - Register VIP user → Process → Verify confirmation
   - Register Regular user → Process → Verify confirmation

2. **Priority Testing**
   - Register Regular user, then VIP user
   - Process tickets
   - Verify VIP processed first

3. **Sold Out Scenario**
   - Register more users than available tickets
   - Process all
   - Verify sold-out messages for excess requests

4. **Cancellation**
   - Purchase tickets
   - Cancel a ticket
   - Verify availability increases

5. **Error Handling**
   - Try empty name
   - Try invalid ticket type
   - Try invalid menu option

6. **CSV Logging**
   - Perform various operations
   - Check transactions.csv for correct entries

## Future Enhancements (Not Implemented)

- GUI interface
- Multiple events support
- Persistent user accounts
- Email confirmation
- Payment processing
- Seat selection
- Event scheduling

