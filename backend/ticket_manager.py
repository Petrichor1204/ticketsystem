import csv
import time
import os
from collections import deque

class TicketManager:
    def __init__(self, vip_tickets, regular_tickets, log_file="transactions.csv"):
        self.vip_tickets = vip_tickets
        self.regular_tickets = regular_tickets
        self.initial_vip_tickets = vip_tickets
        self.initial_regular_tickets = regular_tickets
        self.vip_queue = deque()      # FIFO queue for VIP users
        self.regular_queue = deque()  # FIFO queue for Regular users
        self.log_file = log_file

        # Create the CSV file with headers if it doesn't exist (append mode preserves history)
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Ticket Type", "Time", "Status"])

    def register_user(self, name, ticket_type):
        """Add a user to the appropriate queue based on ticket type."""
        # Input validation
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        
        ticket_type_lower = ticket_type.lower()
        if ticket_type_lower not in ["vip", "regular"]:
            raise ValueError("Invalid ticket type. Must be 'VIP' or 'Regular'")
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if ticket_type_lower == "vip":
            self.vip_queue.append((name.strip(), "VIP", timestamp))
        else:
            self.regular_queue.append((name.strip(), "Regular", timestamp))

    def process_tickets(self):
        """Process VIP queue first, then Regular queue."""
        processed = []
        
        # Process VIP requests
        while self.vip_queue:
            name, ticket_type, reg_time = self.vip_queue.popleft()
            if self.vip_tickets > 0:
                self.vip_tickets -= 1
                self._log_transaction(name, ticket_type, "Confirmed")
                processed.append((name, ticket_type, "Confirmed"))
            else:
                self._log_transaction(name, ticket_type, "Sold Out")
                processed.append((name, ticket_type, "Sold Out"))

        # Process Regular requests
        while self.regular_queue:
            name, ticket_type, reg_time = self.regular_queue.popleft()
            if self.regular_tickets > 0:
                self.regular_tickets -= 1
                self._log_transaction(name, ticket_type, "Confirmed")
                processed.append((name, ticket_type, "Confirmed"))
            else:
                self._log_transaction(name, ticket_type, "Sold Out")
                processed.append((name, ticket_type, "Sold Out"))
        
        return processed

    def cancel_ticket(self, name, ticket_type):
        """Cancel a ticket and free up availability."""
        # Input validation
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        
        ticket_type_lower = ticket_type.lower()
        if ticket_type_lower not in ["vip", "regular"]:
            raise ValueError("Invalid ticket type. Must be 'VIP' or 'Regular'")
        
        name = name.strip()
        
        # Check if ticket can be cancelled (must have been purchased)
        if ticket_type_lower == "vip":
            if self.vip_tickets < self.initial_vip_tickets:
                self.vip_tickets += 1
                self._log_transaction(name, "VIP", "Cancelled")
                return True
            else:
                return False
        else:
            if self.regular_tickets < self.initial_regular_tickets:
                self.regular_tickets += 1
                self._log_transaction(name, "Regular", "Cancelled")
                return True
            else:
                return False

    def get_sales_summary(self):
        """Return a summary of tickets sold and remaining availability."""
        vip_sold = self.initial_vip_tickets - self.vip_tickets
        regular_sold = self.initial_regular_tickets - self.regular_tickets
        
        return {
            "VIP": {
                "sold": vip_sold,
                "remaining": self.vip_tickets,
                "total": self.initial_vip_tickets
            },
            "Regular": {
                "sold": regular_sold,
                "remaining": self.regular_tickets,
                "total": self.initial_regular_tickets
            }
        }

    def get_queue_status(self):
        """Return the number of pending requests in each queue."""
        return {
            "VIP_queue": len(self.vip_queue),
            "Regular_queue": len(self.regular_queue)
        }

    def _log_transaction(self, name, ticket_type, status):
        """Log transaction to CSV file."""
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, ticket_type, time.strftime("%Y-%m-%d %H:%M:%S"), status])

    def get_availability(self):
        """Return current ticket availability."""
        return {
            "VIP": self.vip_tickets,
            "Regular": self.regular_tickets
        }