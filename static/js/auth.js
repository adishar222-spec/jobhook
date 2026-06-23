/**
 * auth.js — Login, register, and auth guard
 */
document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access_token");
    const publicPaths = ["/auth/login", "/auth/register", "/"];
    const isPublic = publicPaths.some(p => window.location.pathname === p);

    // Redirect logic
    if (token) {
        // If logged in and on a public auth page, redirect to dashboard
        if (window.location.pathname === "/auth/login" || window.location.pathname === "/auth/register") {
            window.location.href = "/dashboard";
            return;
        }
    } else {
        // If not logged in and not on a public page, redirect to login
        if (!isPublic) {
            window.location.href = "/auth/login";
            return;
        }
    }

    // Toggle navigation element visibility based on auth status
    const protectedIds = ["nav-dashboard", "nav-resume", "nav-jobs", "nav-courses", "nav-saved-courses", "nav-ats", "nav-cover", "nav-tracker", "logout-btn"];
    const loginBtnNav = document.getElementById("login-btn-nav");

    if (token) {
        // Logged in: show protected navigation, hide login button
        protectedIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = "";
        });
        if (loginBtnNav) loginBtnNav.style.display = "none";
    } else {
        // Logged out: hide protected navigation, show login button (except on login page itself)
        protectedIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = "none";
        });
        if (loginBtnNav) {
            if (window.location.pathname === "/auth/login") {
                loginBtnNav.style.display = "none";
            } else {
                loginBtnNav.style.display = "";
            }
        }
    }

    // Hamburger nav toggle (backup — also in base.html inline)
    const hamburger = document.getElementById("hamburger");
    const navLinks = document.getElementById("nav-links");
    if (hamburger && navLinks) {
        hamburger.addEventListener("click", () => navLinks.classList.toggle("open"));
    }
});
