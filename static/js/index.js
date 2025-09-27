const text = "Connecting work with skill !!! ";
let i = 0;
let isDeleting = false;
const speed = 100;     // typing speed
const backSpeed = 50;  // deleting speed
const pause = 1000;    // pause before deleting

function typeEffect() {
    const h1 = document.getElementById("typing");

    if (!isDeleting && i <= text.length) {
        h1.innerHTML = text.substring(0, i++);
        setTimeout(typeEffect, speed);
    }
    else if (isDeleting && i >= 0) {
        h1.innerHTML = text.substring(0, i--);
        setTimeout(typeEffect, backSpeed);
    }
    else if (!isDeleting && i > text.length) {
        isDeleting = true;
        setTimeout(typeEffect, pause);
    }
    else if (isDeleting && i < 0) {
        isDeleting = false;
        i = 0;
        setTimeout(typeEffect, speed);
    }
}

typeEffect();
const toggleButtons = document.querySelectorAll(".toggle-btn");
const contents = document.querySelectorAll(".tab-content");

toggleButtons.forEach(button => {
    button.addEventListener("click", () => {
        // Reset active buttons
        toggleButtons.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");

        // Reset content
        contents.forEach(content => content.classList.remove("active"));

        // Show the right one
        const tabId = button.getAttribute("data-tab");
        document.getElementById(tabId).classList.add("active");
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const toggles = document.querySelectorAll(".faq-toggle");

    toggles.forEach(toggle => {
        toggle.addEventListener("click", () => {
            const item = toggle.closest(".faq-item");

            // Close other open FAQs (optional, like accordion)
            document.querySelectorAll(".faq-item").forEach(i => {
                if (i !== item) i.classList.remove("active");
            });

            // Toggle current FAQ
            item.classList.toggle("active");
        });
    });
});

