/**
 * tracker.js — Kanban board drag-and-drop application tracker
 * Fixed: uses API.patch() for PATCH endpoint; added delete; improved card UI
 */
const STATUSES = ["saved", "applied", "interview", "offer", "rejected"];
const STATUS_ICONS = {
    saved: "🔖", applied: "📤", interview: "💬", offer: "🎉", rejected: "❌"
};

async function loadTracker() {
    requireAuth();
    try {
        const res = await API.get("/tracker/applications");
        if (!res || !res.ok) {
            showToast("Failed to load applications", "error");
            return;
        }
        const apps = await res.json();

        // Clear columns (keep headings)
        STATUSES.forEach(status => {
            const col = document.getElementById(`col-${status}`);
            if (col) {
                const cards = col.querySelectorAll(".kanban-card");
                cards.forEach(c => c.remove());
                const badge = col.querySelector(".col-count");
                if (badge) badge.textContent = 0;
            }
        });

        // Render cards and update counts
        const counts = {};
        STATUSES.forEach(s => counts[s] = 0);

        apps.forEach(app => {
            renderCard(app);
            if (counts[app.status] !== undefined) counts[app.status]++;
        });

        // Update count badges
        STATUSES.forEach(status => {
            const badge = document.getElementById(`count-${status}`);
            if (badge) badge.textContent = counts[status];
        });

        initDragDrop();
    } catch (e) {
        console.error("Tracker load error", e);
    }
}

function renderCard(app) {
    const col = document.getElementById(`col-${app.status}`);
    if (!col) return;

    const card = document.createElement("div");
    card.className = "kanban-card";
    card.draggable = true;
    card.dataset.id = app._id;

    const company = app.job?.company || "Unknown Company";
    const title = app.job?.title || "Unknown Role";
    const ats = app.ats_score || 0;
    const date = app.updated_at
        ? new Date(app.updated_at?.$date || app.updated_at).toLocaleDateString()
        : "—";
    const notes = app.notes ? `<div class="card-notes" title="${app.notes}">📝 ${app.notes.slice(0, 40)}${app.notes.length > 40 ? "…" : ""}</div>` : "";

    card.innerHTML = `
        <div class="card-company">${company}</div>
        <div class="card-role">${title}</div>
        <div class="card-meta">
            <span class="card-score ats-${ats >= 70 ? "good" : ats >= 50 ? "ok" : "low"}">ATS: ${ats}%</span>
            <span class="card-date">${date}</span>
        </div>
        ${notes}
        <button class="card-delete-btn" title="Delete" onclick="deleteApp('${app._id}', this)">✕</button>
    `;
    col.appendChild(card);
}

function initDragDrop() {
    const cards = document.querySelectorAll(".kanban-card");
    const cols = document.querySelectorAll(".kanban-col");

    cards.forEach(card => {
        card.addEventListener("dragstart", e => {
            e.dataTransfer.setData("id", card.dataset.id);
            card.classList.add("dragging");
        });
        card.addEventListener("dragend", () => {
            card.classList.remove("dragging");
        });
    });

    cols.forEach(col => {
        col.addEventListener("dragover", e => {
            e.preventDefault();
            col.classList.add("drag-over");
        });
        col.addEventListener("dragleave", () => {
            col.classList.remove("drag-over");
        });
        col.addEventListener("drop", async e => {
            e.preventDefault();
            col.classList.remove("drag-over");
            const id = e.dataTransfer.getData("id");
            const newStatus = col.dataset.status;
            if (!id || !newStatus) return;

            // FIXED: Use PATCH as required by the backend endpoint
            const res = await API.patch(`/tracker/applications/${id}/status`, { status: newStatus });
            if (res && res.ok) {
                await loadTracker();
            } else {
                showToast("Failed to update status", "error");
            }
        });
    });
}

async function deleteApp(appId, btn) {
    if (!confirm("Remove this application from the tracker?")) return;
    btn.disabled = true;
    try {
        const res = await API.delete(`/tracker/applications/${appId}`);
        if (res && res.ok) {
            btn.closest(".kanban-card").remove();
            showToast("Application removed.");
            await loadTracker(); // refresh counts
        } else {
            showToast("Failed to delete application", "error");
        }
    } catch (e) {
        showToast("Error deleting application", "error");
    }
}

document.addEventListener("DOMContentLoaded", loadTracker);
