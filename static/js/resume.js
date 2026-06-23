/**
 * resume.js — Resume upload, list, and management UI
 */
document.addEventListener("DOMContentLoaded", async () => {
    requireAuth();

    const uploadForm = document.getElementById("resume-upload-form");
    const uploadResult = document.getElementById("upload-result");
    const parsedData = document.getElementById("parsed-data");
    const resumeList = document.getElementById("resume-list");
    const uploadStatus = document.getElementById("upload-status");

    await loadResumeList();

    async function loadResumeList() {
        if (!resumeList) return;
        resumeList.innerHTML = `<p style="color:var(--text-muted);">Loading resumes...</p>`;
        try {
            const res = await API.get("/resume/");
            if (res && res.ok) {
                const resumes = await res.json();
                renderResumeList(resumes);
            }
        } catch (e) {
            resumeList.innerHTML = `<p style="color:var(--danger);">Failed to load resumes.</p>`;
        }
    }

    function renderResumeList(resumes) {
        if (!resumeList) return;
        if (resumes.length === 0) {
            resumeList.innerHTML = `<p style="color:var(--text-muted); text-align:center; padding:2rem;">No resumes uploaded yet. Upload your first resume above.</p>`;
            return;
        }
        resumeList.innerHTML = "";
        resumes.forEach(r => {
            const skills = r.parsed?.skills?.slice(0, 6).join(", ") || "—";
            const name = r.parsed?.name || r.file_name;
            const date = new Date(r.created_at?.$date || r.created_at).toLocaleDateString();
            const card = document.createElement("div");
            card.className = "resume-card";
            card.innerHTML = `
                <div class="resume-card-header">
                    <div>
                        <h3 class="resume-card-name">${name}</h3>
                        <p class="resume-card-file">${r.file_name}</p>
                    </div>
                    <span class="resume-card-date">${date}</span>
                </div>
                <div class="resume-card-skills">
                    <span class="skills-label">Skills:</span> ${skills}
                </div>
                <div class="resume-card-actions">
                    ${r.storage_name ? `<a href="/api/resume/view/${r.storage_name}" target="_blank" class="btn btn-primary btn-sm">👁️ View Resume</a>` : ''}
                    <a href="/ats" class="btn btn-outline btn-sm">📊 ATS Score</a>
                    <a href="/cover-letter" class="btn btn-outline btn-sm">✉️ Cover Letter</a>
                    <button class="btn btn-danger btn-sm" onclick="deleteResume('${r._id}', this)">🗑 Delete</button>
                </div>
            `;
            resumeList.appendChild(card);
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById("resume_file");
            if (!fileInput || fileInput.files.length === 0) return;

            const formData = new FormData();
            formData.append("file", fileInput.files[0]);

            const submitBtn = e.target.querySelector("button[type=submit]");
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<span class="spinner"></span> Uploading & Parsing...`;
            if (uploadStatus) {
                uploadStatus.innerHTML = `<p class="status-processing">⏳ AI is parsing your resume...</p>`;
                uploadStatus.style.display = "block";
            }

            try {
                const res = await API.postForm("/resume/upload", formData);
                if (res && res.ok) {
                    const data = await res.json();
                    if (uploadResult) {
                        uploadResult.style.display = "block";
                        const p = data.parsed;
                        if (parsedData) {
                            parsedData.innerHTML = `
                                <div class="parsed-data-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
                                    <div class="parsed-section">
                                        <h4>👤 ${p.name || "Name not detected"}</h4>
                                        <p>${p.email || ""} ${p.phone ? "· " + p.phone : ""}</p>
                                        <p>${p.location || ""}</p>
                                        ${p.linkedin ? `<p><a href="${p.linkedin}" target="_blank">LinkedIn</a></p>` : ''}
                                        ${p.portfolio ? `<p><a href="${p.portfolio}" target="_blank">Portfolio</a></p>` : ''}
                                    </div>
                                    <div class="parsed-section">
                                        <h5>📝 Summary</h5>
                                        <p style="font-size: 0.9rem; line-height: 1.4;">${p.summary || "—"}</p>
                                    </div>
                                    <div class="parsed-section">
                                        <h5>🛠 Skills (${p.skills?.length || 0})</h5>
                                        <div class="skill-tags">${(p.skills || []).map(s => `<span class="skill-tag">${s}</span>`).join("")}</div>
                                    </div>
                                    <div class="parsed-section">
                                        <h5>💼 Experience (${p.experience?.length || 0} roles)</h5>
                                        ${(p.experience || []).map(ex => `<p><strong>${ex.title}</strong> at ${ex.company} <br/><small>${ex.start}–${ex.end || "Present"}</small></p>`).join("")}
                                    </div>
                                    <div class="parsed-section">
                                        <h5>🎓 Education</h5>
                                        ${(p.education || []).map(ed => `<p>${ed.degree} ${ed.field ? 'in ' + ed.field : ''} <br/><small>${ed.school} (${ed.year || ""})</small></p>`).join("")}
                                    </div>
                                    <div class="parsed-section">
                                        <h5>🚀 Projects (${p.projects?.length || 0})</h5>
                                        ${(p.projects || []).map(prj => `<p><strong>${prj.name}</strong><br/><small>${prj.description || ""}</small></p>`).join("")}
                                    </div>
                                    <div class="parsed-section">
                                        <h5>🏆 Certificates (${p.certificates?.length || 0})</h5>
                                        ${(p.certificates || []).map(c => `<p><strong>${c.name}</strong><br/><small>${c.issuer || ""} (${c.date || ""})</small></p>`).join("")}
                                    </div>
                                    <div class="parsed-section">
                                        <h5>📚 Courses (${p.courses?.length || 0})</h5>
                                        ${(p.courses || []).map(c => `<p><strong>${c.name}</strong><br/><small>${c.platform || ""} (${c.date || ""})</small></p>`).join("")}
                                    </div>
                                </div>
                            `;
                        }
                    }
                    if (uploadStatus) uploadStatus.style.display = "none";
                    showToast("Resume uploaded and parsed successfully!");
                    await loadResumeList();
                    fileInput.value = "";
                } else {
                    const err = await res.json();
                    showToast(err.error || "Upload failed", "error");
                    if (uploadStatus) uploadStatus.innerHTML = `<p style="color:var(--danger);">Upload failed: ${err.error}</p>`;
                }
            } catch (err) {
                console.error(err);
                showToast("An error occurred during upload", "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }
});

async function deleteResume(resumeId, btn) {
    if (!confirm("Delete this resume? This cannot be undone.")) return;
    btn.disabled = true;
    try {
        const res = await API.delete(`/resume/${resumeId}`);
        if (res && res.ok) {
            showToast("Resume deleted.");
            btn.closest(".resume-card").remove();
        } else {
            showToast("Failed to delete resume.", "error");
        }
    } catch (e) {
        showToast("Error deleting resume.", "error");
    } finally {
        btn.disabled = false;
    }
}
