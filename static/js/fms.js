document.addEventListener("DOMContentLoaded", function () {
  const sidebarButtons = document.querySelectorAll(".sidebar-btn");

  sidebarButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Remove active class from all buttons
      sidebarButtons.forEach((btn) => btn.classList.remove("active"));document.addEventListener("DOMContentLoaded", function () {
        const sidebarButtons = document.querySelectorAll(".sidebar-btn");

        sidebarButtons.forEach((button) => {
          button.addEventListener("click", () => {
            // Remove active class from all buttons
            sidebarButtons.forEach((btn) => btn.classList.remove("active"));
            // Add active class to clicked button
            button.classList.add("active");
          });
        });
      });

      // Add active class to clicked button
      button.classList.add("active");
    });
  });
});
