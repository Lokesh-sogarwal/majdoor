// JavaScript for handling the popup form
document.addEventListener('DOMContentLoaded', () => {
    const openFormButton = document.getElementById('openForm');
    const popupForm = document.getElementById('popupForm');
    const closeFormButton = document.getElementById('closeForm');

    // Show the popup form
    openFormButton.addEventListener('click', () => {
        popupForm.style.display = 'flex';
    });

    // Close the popup form
    closeFormButton.addEventListener('click', () => {
        popupForm.style.display = 'none';
    });

    // Close the form when clicking outside the content
    window.addEventListener('click', (e) => {
        if (e.target === popupForm) {
            popupForm.style.display = 'none';
        }
    });
});
