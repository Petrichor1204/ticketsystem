function showPopup(message, type = 'success', duration = 3000) {
  const popup = document.getElementById('popup-message');
  if (!popup) return;

  popup.textContent = message;
  popup.className = `popup-message show ${type}`;

  // Remove popup after duration
  setTimeout(() => {
    popup.className = 'popup-message';
  }, duration);
}

async function registerUser(event) {
    event.preventDefault();
    
    const firstName = document.getElementById('fname').value.trim();
    const lastName = document.getElementById('lname').value.trim();
    const ticketTypeSelect = document.getElementById('ticketType');
    let ticketType = ticketTypeSelect.value;

    const formData = {
        first_name: firstName,
        last_name: lastName,
        ticket_type: ticketType
    };

    // Update status to show registration is happening
    updateStatusDisplay(ticketType, '—', 'Registering...', `${firstName} ${lastName}`);

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            showPopup(error.error || 'Registration failed');
            updateStatusDisplay('—', '—', 'Failed', '—');
            return;
        }

        const data = await response.json();
        
        // Show user is in queue
        updateStatusDisplay(data.ticket_type, data.queue_position, 'In Queue', `${firstName} ${lastName}`);
        
        // // Wait a moment, then start processing
        // setTimeout(async () => {
        //     await processUserTicket(firstName, lastName, data.ticket_type);
        // }, 1000);

    } catch (error) {
        console.error('Error:', error);
        showPopup('An error occurred while registering');
        updateStatusDisplay('—', '—', 'Error', '—');
    }
}

async function processUserTicket(firstName, lastName, ticketType) {
    // Update status to processing
    updateStatusDisplay(ticketType, 'Processing', 'Processing...');
    
    // Simulate processing delay (2-3 seconds)
    await new Promise(resolve => setTimeout(resolve, 2000));

    try {
        const response = await fetch('/api/process_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName
            })
        });

        if (!response.ok) {
            const error = await response.json();
            showPopup(error.error || 'Processing failed');
            updateStatusDisplay(`${firstName} ${lastName}`, ticketType, '—', 'Failed');
            return;
        }

        const data = await response.json();
        
        // Update status with final result
        const finalStatus = data.status === 'Confirmed' ? 
            '✓ Confirmed' : '✗ Sold Out';
        
        updateStatusDisplay(
            data.ticket_type, 
            '—', 
            finalStatus
        );

        // Update availability
        await updateAvailability();
        await updateQueue();

        // Show success or sold out message
        if (data.status === 'Confirmed') {
            showPopup(`Success! Your ${data.ticket_type} ticket has been confirmed.`);
        } else {
            showPopup(`Sorry, ${data.ticket_type} tickets are sold out.`);
        }

        // Reset form
        document.getElementById('registrationForm').reset();
        document.getElementById('otherTicketDiv').style.display = 'none';

    } catch (error) {
        console.error('Error:', error);
        showPopup('An error occurred during processing');
        updateStatusDisplay(`${firstName} ${lastName}`, ticketType, '—', 'Error');
    }
}

function updateStatusDisplay(ticketType, position, status, customerName) {
    const customerNameEl = document.getElementById('customer-name');
    const ticketTypeEl = document.getElementById('ticket-type');
    const queuePositionEl = document.getElementById('queue-position');
    const purchaseStatusEl = document.getElementById('purchase-status');

    if (customerNameEl) customerNameEl.textContent = customerName || '—';
    if (ticketTypeEl) ticketTypeEl.textContent = ticketType || '—';
    if (queuePositionEl) queuePositionEl.textContent = position;
    if (purchaseStatusEl) {
        purchaseStatusEl.textContent = status;
        
        // Add visual styling based on status
        purchaseStatusEl.className = '';
        if (status.includes('Confirmed')) {
            purchaseStatusEl.style.color = 'green';
            purchaseStatusEl.style.fontWeight = 'bold';
        } else if (status.includes('Sold Out')) {
            purchaseStatusEl.style.color = 'red';
            purchaseStatusEl.style.fontWeight = 'bold';
        } else if (status.includes('Processing') || status.includes('Registering')) {
            purchaseStatusEl.style.color = 'orange';
            purchaseStatusEl.style.fontWeight = 'normal';
        } else {
            purchaseStatusEl.style.color = 'black';
            purchaseStatusEl.style.fontWeight = 'normal';
        }
    }
}

async function updateAvailability() {
    try {
        const response = await fetch('/availability');
        const data = await response.json();
        
        const vipCountEl = document.getElementById('vip-count');
        const regularCountEl = document.getElementById('regular-count');
        
        if (vipCountEl) vipCountEl.textContent = data.VIP;
        if (regularCountEl) regularCountEl.textContent = data.Regular;

        // // Also update if using different IDs
        // const vipAvailableEl = document.getElementById('vipAvailable');
        // const regularAvailableEl = document.getElementById('regularAvailable');
        
        // if (vipAvailableEl) vipAvailableEl.textContent = data.vip_left;
        // if (regularAvailableEl) regularAvailableEl.textContent = data.reg_left;
        
    } catch (error) {
        console.error('Error updating availability:', error);
    }
}

async function updateQueue() {
    try {
        const response = await fetch('/queue');
        const data = await response.json();
        
        const vipList = document.getElementById('vipQueue');
        const regularList = document.getElementById('regularQueue');
        
        if (vipList) {
            vipList.innerHTML = '';
            data['VIP Queue'].forEach(user => {
                vipList.innerHTML += `<li>${user.first_name} ${user.last_name}</li>`;
            });
        }
        
        if (regularList) {
            regularList.innerHTML = '';
            data['Regular Queue'].forEach(user => {
                regularList.innerHTML += `<li>${user.first_name} ${user.last_name}</li>`;
            });
        }
    } catch (error) {
        console.error('Error updating queue:', error);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    updateAvailability();
    updateQueue();
    // Update queue every 5 seconds
    setInterval(() => {
        updateQueue();
        updateAvailability();
    }, 5000);
});

async function startPurchase() {
    const firstName = document.getElementById('fname').value.trim();
    const lastName = document.getElementById('lname').value.trim();
    const ticketType = document.getElementById('ticketType').value;

    if (!firstName || !lastName) {
        showPopup('Please register first!');
        return;
    }

    updateStatusDisplay(ticketType, '—', 'Processing...', `${firstName} ${lastName}`);

    try {
        const response = await fetch('/api/process_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ first_name: firstName, last_name: lastName, ticket_type: ticketType })
        });

        if (!response.ok) {
            const err = await response.json();
            showPopup(err.error || 'Processing failed.');
            return;
        }

        const result = await response.json();

        for (const step of result.updates) {
            updateStatusDisplay(step.ticket_type, '—', `Processing...`, step.name);
            document.getElementById('vip-count').textContent = step.remaining.VIP;
            document.getElementById('regular-count').textContent = step.remaining.Regular;
            await new Promise(resolve => setTimeout(resolve, 1200));
        }


        const finalStatus = result.final_status === 'Confirmed'
            ? '✓ Confirmed'
            : '✗ Sold Out';

        updateStatusDisplay(ticketType, 'Not in queue', finalStatus, `${firstName} ${lastName}`);
        await updateAvailability();

        showPopup(finalStatus === '✓ Confirmed'
            ? 'Your ticket has been confirmed!'
            : 'Sorry, tickets sold out before it reached you.');
            
        // Only clear form inputs, keep status display
        document.getElementById('fname').value = '';
        document.getElementById('lname').value = '';
        document.getElementById('ticketType').value = 'VIP';

    } catch (err) {
        console.error(err);
        showPopup('Error during processing.');
    }
}

async function cancelTicket() {
    const firstName = document.getElementById('fname').value.trim();
    const lastName = document.getElementById('lname').value.trim();
    const ticketType = document.getElementById('ticketType').value;

    if (!firstName || !lastName) {
        showPopup('Please enter the first and last name of the ticket to cancel.');
        return;
    }

    updateStatusDisplay(ticketType, '—', 'Cancelling...', `${firstName} ${lastName}`);

    try {
        const response = await fetch('/api/cancel_ticket', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                ticket_type: ticketType
            })
        });

        // First check if response is ok
        if (!response.ok) {
            const error = await response.json();
            showPopup(error.error || 'Cancellation failed.');
            updateStatusDisplay(ticketType, '—', 'Cancellation Failed');
            return;
        }

        // Only parse JSON after confirming response is ok
        const result = await response.json();

        // Update the status visually
        updateStatusDisplay(ticketType, 'Not in queue', 'Cancelled', `${firstName} ${lastName}`);
        await updateAvailability(); // Also update ticket availability
        await updateQueue(); // Reflect new queue state

        showPopup(result.message || 'Ticket successfully cancelled.');

        // Reset form and UI
        document.getElementById('registrationForm').reset();

    } catch (err) {
        console.error('Error:', err);
        showPopup('Error during cancellation.');
        updateStatusDisplay(`${firstName} ${lastName}`, ticketType, 'Not in queue', 'Error');
    }
}