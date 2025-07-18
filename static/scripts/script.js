document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const messageElement = document.getElementById('message');
    const loginButton = document.getElementById('loginButton');

    loginForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent actual form submission

        const username = usernameInput.value;
        const password = passwordInput.value;

        // Clear previous messages
        messageElement.textContent = '';
        messageElement.className = '';
        
        loginButton.disabled = true;
        loginButton.textContent = 'Logging in...';

        // Simulate API call / authentication
        setTimeout(() => {
            if (username === 'admin' && password === 'password') {
                messageElement.textContent = 'Login successful! Welcome, admin.';
                messageElement.className = 'success';
                // Here you would typically redirect the user or update the UI
                console.log('Login successful');
            } else if (username === '' || password === '') {
                messageElement.textContent = 'Username and password cannot be empty.';
                messageElement.className = 'error';
            } else {
                messageElement.textContent = 'Invalid username or password.';
                messageElement.className = 'error';
                console.log('Login failed');
            }
            loginButton.disabled = false;
            loginButton.textContent = 'Login';
        }, 1000); // Simulate network delay
    });
});

