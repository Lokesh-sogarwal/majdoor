const passwordInput = document.querySelector('#password'); // Update to match your `id` if necessary
const confirmPasswordInput = document.querySelector('#confirm_password'); // Update to match your `id` if necessary
const phoneInput = document.querySelector('#phone_no'); // Update to match your `id` if necessary
const passwordStrength = document.getElementById('password-strength');
const phoneError = document.getElementById('phone-error');
const passwordMatch = document.getElementById('password-match');

// Password validation
passwordInput.addEventListener('input', () => {
    const value = passwordInput.value;
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(value);
    const hasUppercase = /[A-Z]/.test(value);
    const hasLowercase = /[a-z]/.test(value);
    const hasDigit = /\d/.test(value);
    const lengthValid = value.length >= 8 && value.length <= 15;

    if (lengthValid && hasSpecialChar && hasUppercase && hasLowercase && hasDigit) {
        passwordStrength.textContent = 'Strong password!';
        passwordStrength.className = 'valid';
    } else {
        passwordStrength.textContent = 'Password must be 8-15 characters, include uppercase, lowercase, digit, and a special character.';
        passwordStrength.className = 'error';
    }
});

// Phone number validation
phoneInput.addEventListener('input', () => {
    const value = phoneInput.value;
    const isValid = /^\d{10}$/.test(value);

    if (isValid) {
        phoneError.textContent = 'Valid phone number.';
        phoneError.className = 'valid';
    } else {
        phoneError.textContent = 'Phone number must be exactly 10 digits.';
        phoneError.className = 'error';
    }
});

// Confirm password validation
confirmPasswordInput.addEventListener('input', () => {
    const passwordValue = passwordInput.value;
    const confirmPasswordValue = confirmPasswordInput.value;

    if (passwordValue === confirmPasswordValue) {
        passwordMatch.textContent = 'Passwords match.';
        passwordMatch.className = 'valid';
    } else {
        passwordMatch.textContent = 'Passwords do not match.';
        passwordMatch.className = 'error';
    }
});