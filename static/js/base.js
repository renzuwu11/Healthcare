document.addEventListener("DOMContentLoaded", function () {
  const dropdowns = document.querySelectorAll(".dropdown-toggle");

  dropdowns.forEach((dropdown) => {
    dropdown.addEventListener("click", function (event) {
      event.preventDefault();
      this.nextElementSibling.style.display = "block";
    });

    // Close dropdown if clicking outside
    document.addEventListener("click", function (e) {
      if (!dropdown.contains(e.target)) {
        dropdown.nextElementSibling.style.display = "none";
      }
    });
  });
});

document.querySelector(".user-dropdown").addEventListener("click", function () {
  const dropdownContent = this.querySelector(".profile-dropdown-content");
  dropdownContent.style.display =
    dropdownContent.style.display === "block" ? "none" : "block";
});

document.getElementById('logout-button').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent default anchor behavior
    fetch('/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect; // Redirect to main page
        }
    })
    .catch(error => {
        console.error('Error during logout:', error);
    });
});