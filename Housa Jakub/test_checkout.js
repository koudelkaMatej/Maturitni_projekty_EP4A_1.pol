const axios = require('axios');

// Need to run this against the running server.
// Assuming server is on port 3000 (default in server.js usually)

async function testCheckout() {
    try {
        const payload = {
            email: 'jakubhousa@protonmail.com', // Known existing user
            firstName: 'Jakub',
            lastName: 'Housa',
            address: 'Test St 123',
            city: 'Kladno',
            zipCode: '27201',
            items: [
                {
                    id: 'subscription', // Slug for subscription
                    quantity: 1,
                    isSubscription: true
                }
            ]
        };

        console.log('Sending payload:', payload);

        const response = await axios.post('http://localhost:3000/api/checkout', payload);
        console.log('Response:', response.data);

    } catch (error) {
        console.error('Error:', error.response ? error.response.data : error.message);
    }
}

testCheckout();
