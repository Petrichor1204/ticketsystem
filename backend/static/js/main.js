async function registerUser(event) {
    event.preventDefault();
    
    const formData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        ticket_type: document.getElementById('ticketType').value
    };

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        const data = await response.json();
        alert(data.message);
        updateAvailability();
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while registering');
    }
}

async function updateAvailability() {
    try {
        const response = await fetch('/availability');
        const data = await response.json();
        document.getElementById('vipAvailable').textContent = data.VIP;
        document.getElementById('regularAvailable').textContent = data.Regular;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Update queue status
async function updateQueue() {
    try {
        const response = await fetch('/queue');
        const data = await response.json();
        
        const vipList = document.getElementById('vipQueue');
        const regularList = document.getElementById('regularQueue');
        
        vipList.innerHTML = '';
        regularList.innerHTML = '';
        
        data['VIP Queue'].forEach(user => {
            vipList.innerHTML += `<li>${user.first_name} ${user.last_name}</li>`;
        });
        
        data['Regular Queue'].forEach(user => {
            regularList.innerHTML += `<li>${user.first_name} ${user.last_name}</li>`;
        });
    } catch (error) {
        console.error('Error:', error);
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    updateAvailability();
    updateQueue();
    setInterval(updateQueue, 5000); // Update queue every 5 seconds
});