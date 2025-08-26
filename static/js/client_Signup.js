// 🔹 Toggle password visibility
function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
}

function toggleRePasswordVisibility() {
    const rePasswordInput = document.getElementById('re_enter_password');
    rePasswordInput.type = rePasswordInput.type === 'password' ? 'text' : 'password';
}

// 🔹 Handle mobile verification
function handleMobileVerification() {
    const mobileNumber = document.getElementById('mobileNumber').value.trim();
    if (mobileNumber.length === 10) { // ✅ must be exactly 10 digits
        document.getElementById('otp-modal').style.display = 'flex';
        document.getElementById('display-mobile-number').textContent = mobileNumber;
    } else {
        alert("Enter a valid 10-digit mobile number.");
    }
}

// 🔹 Handle OTP verification
function handleOtpVerification() {
    const otpCode = document.getElementById('otpCode').value.trim();
    if (otpCode.length === 4) { // ✅ OTP must be 4 digits
        document.getElementById('otp-modal').style.display = 'none';
        document.querySelector('.create-account-btn').disabled = false;
    } else {
        alert("Enter a valid 4-digit OTP.");
    }
}

// 🔹 Close OTP modal
document.querySelector('.close-btn').addEventListener('click', () => {
    document.getElementById('otp-modal').style.display = 'none';
});

// 🔹 Button click events
document.querySelector('.verify-btn').addEventListener('click', handleMobileVerification);
document.querySelector('.verify-otp-btn').addEventListener('click', handleOtpVerification);

// 🔹 Form validation before submit
document.getElementById('signupForm').addEventListener('submit', function (event) {
    const password = document.getElementById('password').value.trim();
    const repassword = document.getElementById('re_enter_password').value.trim();
    const errorMsg = document.getElementById('password-error');
    const createAccountBtn = document.querySelector('.create-account-btn');

    // ✅ Passwords must match
    if (password !== repassword) {
        event.preventDefault();
        errorMsg.style.display = "block";
        errorMsg.textContent = "Passwords do not match!";
        return;
    } else {
        errorMsg.style.display = "none";
    }

    // ✅ Terms must be checked
    if (!document.getElementById('terms').checked) {
        event.preventDefault();
        alert("You must agree to the terms and conditions.");
        return;
    }

    // ✅ OTP must be verified (button enabled only after OTP verification)
    if (createAccountBtn.disabled) {
        event.preventDefault();
        alert("Please verify your mobile number first.");
        return;
    }
});
