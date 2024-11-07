// Toggle password visibility
const togglePassword = document.querySelector("#togglePassword");
const password = document.querySelector("#password");

togglePassword.addEventListener("click", function () {
  const type =
    password.getAttribute("type") === "password" ? "text" : "password";
  password.setAttribute("type", type);
  this.textContent = this.textContent === "👁️" ? "👁️‍🗨️" : "👁️";
});
// Show loading overlay on form submit
const loginForm = document.getElementById("loginForm");
const loadingOverlay = document.getElementById("loadingOverlay");

loginForm.addEventListener("submit", function (event) {
  loadingOverlay.style.display = "flex"; // Show the overlay
});
