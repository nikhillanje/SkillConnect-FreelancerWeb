document.addEventListener("DOMContentLoaded", function () {

    // 🔹 Toggle Password visibility
    function togglePasswordVisibility() {
        const passwordInput = document.getElementById('password');
        passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
    }

    function toggleRePasswordVisibility() {
        const rePasswordInput = document.getElementById('re_enter_password');
        rePasswordInput.type = rePasswordInput.type === 'password' ? 'text' : 'password';
    }
    // 🔹 Send OTP (no alert, just open modal)
    async function handleMobileVerification() {
        const mobileNumber = document.getElementById('mobileNumber').value.trim();
        if (mobileNumber.length !== 10 || isNaN(mobileNumber)) {
            return; // silently ignore
        }

        try {
            const response = await fetch("/send-otp/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ phone: mobileNumber })
            });

            const data = await response.json();
            if (data.success) {
                document.getElementById('otp-modal').style.display = 'flex';
                document.getElementById('display-mobile-number').textContent = mobileNumber;
            }
        } catch (err) {
            console.error("Error sending OTP:", err);
        }
    }

    // 🔹 Verify OTP (no alert, just enable button)
    async function handleOtpVerification() {
        const mobileNumber = document.getElementById('mobileNumber').value.trim();
        const otpCode = document.getElementById('otpCode').value.trim();

        if (otpCode.length !== 4 || isNaN(otpCode)) {
            return; // silently ignore
        }

        try {
            const response = await fetch("/verify-otp/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ phone: mobileNumber, otp: otpCode })
            });

            const data = await response.json();
            if (data.success) {
                document.getElementById('otp-modal').style.display = 'none';
                document.querySelector('.create-account-btn').disabled = false;
            }
        } catch (err) {
            console.error("Error verifying OTP:", err);
        }
    }



    // 🔹 Close OTP modal
    document.querySelector('.close-btn').addEventListener('click', () => {
        document.getElementById('otp-modal').style.display = 'none';
    });

    // 🔹 Attach handlers
    document.querySelector('.verify-btn').addEventListener('click', handleMobileVerification);
    document.querySelector('.verify-otp-btn').addEventListener('click', handleOtpVerification);



    // 🔹 Password match + validation before form submit
    document.getElementById('signupForm').addEventListener('submit', function (event) {
        const password = document.getElementById('password').value.trim();
        const repassword = document.getElementById('re_enter_password').value.trim();
        const errorMsg = document.getElementById('password-error');
        const createAccountBtn = document.querySelector('.create-account-btn');

        if (password !== repassword) {
            event.preventDefault();
            errorMsg.style.display = "block";
            errorMsg.textContent = "Passwords do not match!";
            return;
        } else {
            errorMsg.style.display = "none";
        }

        if (!document.getElementById('terms').checked) {
            event.preventDefault();
            alert("You must agree to the terms and conditions.");
            return;
        }

        if (createAccountBtn.disabled) {
            event.preventDefault();
            alert("Please verify your mobile number first.");
            return;
        }
    });

});
