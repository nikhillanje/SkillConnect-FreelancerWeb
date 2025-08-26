document.addEventListener("DOMContentLoaded", function () {
    const signupBtn = document.getElementById("signup-btn");
    if (signupBtn) {
        signupBtn.addEventListener("click", function () {
            window.location.href = signupBtn.dataset.url; // take URL from data attribute
        });
    }
});
