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
