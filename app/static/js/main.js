// PhishGuard front-end helpers

document.addEventListener("DOMContentLoaded", function () {
    // Auto-dismiss flash alerts after 5 seconds
    document.querySelectorAll(".alert-dismissible").forEach(function (alertEl) {
        setTimeout(function () {
            const alert = bootstrap.Alert.getOrCreateInstance(alertEl);
            if (alert) alert.close();
        }, 5000);
    });

    // Character counter for email body textarea on the analyze page
    const bodyField = document.getElementById("email_body");
    const counter = document.getElementById("body-char-count");
    if (bodyField && counter) {
        const updateCount = () => {
            counter.textContent = bodyField.value.length + " characters";
        };
        bodyField.addEventListener("input", updateCount);
        updateCount();
    }

    // Confirm before deleting a detection record (admin)
    document.querySelectorAll(".confirm-delete").forEach(function (form) {
        form.addEventListener("submit", function (e) {
            if (!confirm("Delete this detection record? This cannot be undone.")) {
                e.preventDefault();
            }
        });
    });
});
