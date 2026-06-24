/**
 * ats.js — ATS Score Analysis UI
 * Fixed: endpoint /resume/ (was /resume/list), proper response rendering,
 * matched keyword display, and structured AI suggestions rendering.
 */
document.addEventListener("DOMContentLoaded", async () => {
    requireAuth();

    const resumeSelect = document.getElementById("resume-select");
    const jdInput = document.getElementById("jd-input");
    const scoreBtn = document.getElementById("score-btn");
    const resultsContainer = document.getElementById("results-container");
    const scoreValue = document.getElementById("score-value");
    const scoreRing = document.querySelector(".score-ring");
    const ratingLabel = document.getElementById("rating-label");
    const matchedKeywords = document.getElementById("matched-keywords");
    const missingKeywords = document.getElementById("missing-keywords");
    const skillGapMatched = document.getElementById("skill-gap-matched");
    const skillGapMissing = document.getElementById("skill-gap-missing");
    const aiSuggestions = document.getElementById("ai-suggestions");

    // Check if we came from job recommendations with a pending job description
    const pendingJd = sessionStorage.getItem("pending_jd");
    if (pendingJd && jdInput) {
        jdInput.value = pendingJd;
        sessionStorage.removeItem("pending_jd");
    }

    // Load resumes into select — FIXED: was /resume/list, now /resume/
    try {
        const res = await API.get("/resume/");
        if (res && res.ok) {
            const resumes = await res.json();
            if (resumeSelect) {
                if (resumes.length === 0) {
                    resumeSelect.innerHTML = `<option value="">No resumes — upload one first</option>`;
                } else {
                    resumes.forEach(r => {
                        const opt = document.createElement("option");
                        opt.value = r._id;
                        opt.textContent = r.parsed?.name || r.file_name;
                        resumeSelect.appendChild(opt);
                    });
                }
            }
        }
    } catch (e) {
        console.error("Failed to load resumes", e);
    }

    if (scoreBtn) {
        scoreBtn.addEventListener("click", async () => {
            const resumeId = resumeSelect ? resumeSelect.value : "";
            const jd = jdInput ? jdInput.value.trim() : "";

            if (!jd) {
                showToast("Please paste a job description", "error");
                return;
            }
            if (!resumeId) {
                showToast("Please select a resume", "error");
                return;
            }

            scoreBtn.disabled = true;
            scoreBtn.innerHTML = `<span class="spinner"></span> Calculating...`;

            try {
                const payload = { job_description: jd, resume_id: resumeId };
                const res = await API.post("/ats/score", payload);
                if (res && res.ok) {
                    const data = await res.json();
                    renderResults(data);
                } else {
                    const err = await res.json();
                    showToast(err.error || "Failed to calculate score", "error");
                }
            } catch (e) {
                showToast("An error occurred", "error");
                console.error(e);
            } finally {
                scoreBtn.disabled = false;
                scoreBtn.innerHTML = `📊 Calculate ATS Score`;
            }
        });
    }

    function renderResults(data) {
        if (resultsContainer) resultsContainer.style.display = "block";

        const score = data.ats?.score ?? 0;
        if (scoreRing) {
            scoreRing.style.setProperty("--pct", score);
            // Color based on score
            const color = score >= 80 ? "var(--success)" : score >= 60 ? "var(--warning)" : "var(--danger)";
            scoreRing.style.background = `conic-gradient(${color} calc(${score} * 3.6deg), rgba(255,255,255,0.1) 0deg)`;
        }
        if (scoreValue) scoreValue.textContent = `${score}%`;
        if (ratingLabel) {
            ratingLabel.textContent = data.ats?.rating ?? "—";
            const ratingColor = score >= 80 ? "var(--success)" : score >= 60 ? "var(--warning)" : "var(--danger)";
            ratingLabel.style.color = ratingColor;
        }

        // Matched keywords
        if (matchedKeywords) {
            const matched = data.ats?.matched_keywords || [];
            matchedKeywords.innerHTML = matched.length
                ? matched.map(k => `<span class="kw-tag kw-matched">${k}</span>`).join("")
                : `<span style="color:var(--text-muted)">None detected</span>`;
        }

        // Missing keywords
        if (missingKeywords) {
            const missing = data.ats?.missing_keywords || [];
            missingKeywords.innerHTML = missing.length
                ? missing.map(k => `<span class="kw-tag kw-missing">${k}</span>`).join("")
                : `<span style="color:var(--success)">🎉 All keywords covered!</span>`;
        }

        // Skill gap
        if (skillGapMatched) {
            const sgMatched = data.skill_gap?.matched_skills || [];
            skillGapMatched.innerHTML = sgMatched.length
                ? sgMatched.map(s => `<span class="kw-tag kw-matched">${s}</span>`).join("")
                : `<span style="color:var(--text-muted)">None</span>`;
        }
        if (skillGapMissing) {
            const sgMissing = data.skill_gap?.missing_skills || [];
            skillGapMissing.innerHTML = sgMissing.length
                ? sgMissing.map(s => `<span class="kw-tag kw-missing">${s}</span>`).join("")
                : `<span style="color:var(--success)">✅ All skills present!</span>`;
        }

        // AI suggestions
        if (aiSuggestions) {
            const sugg = data.suggestions;
            if (!sugg || sugg.error) {
                aiSuggestions.innerHTML = `<p style="color:var(--text-muted)">No suggestions available.</p>`;
                return;
            }
            let html = "";
            if (sugg.improvements?.length) {
                html += `<h4 style="color:var(--primary);margin-bottom:.5rem;">💡 Improvements</h4><ul class="sugg-list">`;
                sugg.improvements.forEach(i => { html += `<li>${i}</li>`; });
                html += `</ul>`;
            }
            if (sugg.keyword_suggestions?.length) {
                html += `<h4 style="color:var(--secondary);margin:.75rem 0 .5rem;">🔑 Keyword Tips</h4><ul class="sugg-list">`;
                sugg.keyword_suggestions.forEach(k => { html += `<li>${k}</li>`; });
                html += `</ul>`;
            }
            if (sugg.language_upgrades?.length) {
                html += `<h4 style="color:var(--warning);margin:.75rem 0 .5rem;">✍️ Language Upgrades</h4><ul class="sugg-list">`;
                sugg.language_upgrades.forEach(l => { html += `<li>${l}</li>`; });
                html += `</ul>`;
            }
            aiSuggestions.innerHTML = html || `<p style="color:var(--text-muted)">No specific suggestions.</p>`;
        }

        // Scroll to results
        if (resultsContainer) {
            resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });
        }

        // Notify template to show keyword/suggestions sections
        document.dispatchEvent(new Event("ats:results"));
    }
});
