document.addEventListener("DOMContentLoaded", () => {
    const editBtn = document.getElementById("edit-btn");
    const cancelBtn = document.getElementById("cancel-btn");
    const readonlyView = document.getElementById("readonly-view");
    const editForm = document.getElementById("edit-form");

    if (editBtn) {
        editBtn.addEventListener("click", () => {
            readonlyView.classList.add("hidden");
            editForm.classList.remove("hidden");
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", () => {
            editForm.classList.add("hidden");
            readonlyView.classList.remove("hidden");
        });
    }
});
