async function registerUser(event) {
    event.preventDefault();
    
    const firstName = document.getElementById('fname').value.trim();
    const lastName = document.getElementById('lname').value.trim();
    const ticketTypeSelect = document.getElementById('ticketType');
    let ticketType = ticketTypeSelect.value;

    // Handle "other" option
    if (ticketType === 'other') {
        const otherTicket = document.getElementById('otherTicket').value.trim();
        if (!otherTicket) {
            alert('Please specify the ticket type');
            return;
        }
        ticketType = otherTicket;
    }

    const formData = {
        first_name: firstName,
        last_name: lastName,
        ticket_type: ticketType
    };

    // Update status to show registration is happening
    updateStatusDisplay(ticketType, '—', 'Registering...');

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
            alert(error.error || 'Registration failed');
            updateStatusDisplay('—', '—', 'Failed');
            return;
        }

        const data = await response.json();
        
        // Show user is in queue
        updateStatusDisplay(data.ticket_type, data.queue_position, 'In Queue');
        
        // Wait a moment, then start processing
        setTimeout(async () => {
            await processUserTicket(firstName, lastName, data.ticket_type);
        }, 1000);

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while registering');
        updateStatusDisplay('—', '—', 'Error');
    }
}

async function processUserTicket(firstName, lastName, ticketType) {
    // Update status to processing
    updateStatusDisplay(ticketType, 'Processing', 'Processing...');
    
    // Simulate processing delay (2-3 seconds)
    await new Promise(resolve => setTimeout(resolve, 2500));

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
            alert(error.error || 'Processing failed');
            updateStatusDisplay(ticketType, '—', 'Failed');
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
            alert(`Success! Your ${data.ticket_type} ticket has been confirmed.`);
        } else {
            alert(`Sorry, ${data.ticket_type} tickets are sold out.`);
        }

        // Reset form
        document.getElementById('registrationForm').reset();
        document.getElementById('otherTicketDiv').style.display = 'none';

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during processing');
        updateStatusDisplay(ticketType, '—', 'Error');
    }
}

function updateStatusDisplay(ticketType, position, status) {
    const statusTypeEl = document.getElementById('status-type');
    const queuePositionEl = document.getElementById('queue-position');
    const purchaseStatusEl = document.getElementById('purchase-status');

    if (statusTypeEl) statusTypeEl.textContent = ticketType;
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

        // Also update if using different IDs
        const vipAvailableEl = document.getElementById('vipAvailable');
        const regularAvailableEl = document.getElementById('regularAvailable');
        
        if (vipAvailableEl) vipAvailableEl.textContent = data.VIP;
        if (regularAvailableEl) regularAvailableEl.textContent = data.Regular;
        
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