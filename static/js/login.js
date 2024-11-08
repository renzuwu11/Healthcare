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

window.onload = function () {
  if (window.history && window.history.pushState) {
    window.history.pushState(null, null, window.location.href);
    window.onpopstate = function () {
      window.history.pushState(null, null, window.location.href);
    };
  }

  document.body.classList.add("fade-in");
};

function animatePageAndRedirect(url) {
  document.querySelector(".container").classList.add("blur-out");
  document.querySelector(".header").classList.add("blur-out");
  setTimeout(() => {
    window.location.href = url;
  }, 600);
}

