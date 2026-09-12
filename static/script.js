document.addEventListener("DOMContentLoaded", function () {
    // 1. Confirm before deleting a student
    const deleteLinks = document.querySelectorAll("a[href*='/delete/']");
    deleteLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            const confirmDelete = confirm("Are you sure you want to delete this student?");
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });

    // 2. Validate Mark input before submitting forms
    const studentForms = document.querySelectorAll("form");
    studentForms.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const markInput = form.querySelector("input[name='mark']");
            if (markInput) {
                const markValue = parseFloat(markInput.value);
                if (isNaN(markValue) || markValue < 0 || markValue > 100) {
                    alert("Mark must be a number between 0 and 100!");
                    event.preventDefault();
                }
            }
        });
    });
});