document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const loginMessage = document.getElementById('login-message');

    // Define the required credentials
    const VALID_USERNAME = 'admin';
    const VALID_PASSWORD = '12345';
    
    // Check if the user is already "logged in" (has a session flag)
    if (localStorage.getItem('isLoggedIn') === 'true') {
        window.location.href = '/dashboard'; 
        return;
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            
            loginMessage.textContent = 'Verifying credentials...';

            // --- 🎯 DEMO LOGIN LOGIC: Local Check ---
            if (username === VALID_USERNAME && password === VALID_PASSWORD) {
                // Successful login: Set flag and redirect
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('username', username);
                
                loginMessage.textContent = 'Login successful! Redirecting...';
                
                // Add a small delay for the user to see the success message
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 500);

            } else {
                // Failed login
                loginMessage.textContent = 'Invalid username or password. Please use the credentials provided in the disclaimer.';
                loginMessage.style.color = '#dc3545'; // Set color to red
            }
        });
    }
});