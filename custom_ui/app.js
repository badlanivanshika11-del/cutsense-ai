document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyzeBtn");
    const videoUrlInput = document.getElementById("videoUrlInput");
    const apiKeyInput = document.getElementById("apiKeyInput");
    const mediaContainer = document.getElementById("mediaContainer");
    const pacingSpeed = document.getElementById("pacingSpeed");
    const cutsPerMin = document.getElementById("cutsPerMin");
    const meterFill = document.getElementById("meterFill");
    const hookEvaluationText = document.getElementById("hookEvaluationText");
    const thumbnailText = document.getElementById("thumbnailText");
    const timelineList = document.getElementById("timelineList");

    let currentReport = null;
    let currentMetadata = null;

    analyzeBtn.addEventListener("click", async () => {
        const url = videoUrlInput.value.trim();
        const apiKey = apiKeyInput.value.trim();

        if (!url) {
            alert("Please enter a YouTube Video or Instagram Reel URL.");
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = "<span>⏳ Deconstructing Edits...</span>";

        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url, api_key: apiKey || null })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Analysis failed");
            }

            currentMetadata = data.metadata;
            currentReport = data.report;

            // 1. Render Video Media Preview
            mediaContainer.innerHTML = `
                <div style="margin-bottom: 10px;">
                    <strong>${currentMetadata.platform}</strong>: <em>${currentMetadata.title}</em> (By: ${currentMetadata.uploader})
                </div>
                ${currentMetadata.thumbnail ? `<img src="${currentMetadata.thumbnail}" style="width: 100%; border-radius: 12px; margin-bottom: 10px;" />` : ''}
            `;

            // 2. Render Pacing Metrics
            pacingSpeed.textContent = currentReport.pacing_rating;
            cutsPerMin.textContent = `${currentReport.estimated_cuts_per_minute} cuts/min`;
            const fillWidth = Math.min(100, Math.max(10, currentReport.estimated_cuts_per_minute * 3));
            meterFill.style.width = `${fillWidth}%`;

            // 3. Render Hook & Thumbnail text
            hookEvaluationText.textContent = currentReport.script_hook_evaluation;
            thumbnailText.textContent = currentReport.thumbnail_analysis;

            // 4. Render Timeline Items with Learn Edit buttons
            timelineList.innerHTML = "";
            currentReport.timeline.forEach(item => {
                const tagClass = item.editing_type.toLowerCase().includes("cut") ? "tag-cyan" : "tag-purple";
                const query = item.tutorial_query || `How to do ${item.editing_type} video editing tutorial`;
                const searchUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`;

                const itemHtml = `
                    <div class="timeline-item">
                        <div class="timeline-top" style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span class="time-code">⏱️ ${item.timestamp_start} - ${item.timestamp_end}</span>
                                &nbsp;
                                <span class="tag ${tagClass}">${item.editing_type}</span>
                            </div>
                            <a href="${searchUrl}" target="_blank" class="secondary-btn" style="text-decoration: none; padding: 4px 12px; font-size: 0.82rem; background: #059669; color: white;">🎓 Learn This Edit</a>
                        </div>
                        <p class="timeline-desc"><strong>Technique:</strong> ${item.description}</p>
                        <p class="timeline-impact">💡 <em>Retention Impact:</em> ${item.engagement_impact}</p>
                    </div>
                `;
                timelineList.innerHTML += itemHtml;
            });

            alert("✅ Video analysis complete!");

        } catch (err) {
            alert("Error during analysis: " + err.message);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = "<span>🚀 Deconstruct Edits</span>";
        }
    });
});
