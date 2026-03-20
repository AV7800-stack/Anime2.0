async function pollStatus(jobId) {
  const statusEl = document.getElementById("status");
  const downloadLink = document.getElementById("downloadLink");

  while (true) {
    const res = await fetch(`/api/status/${jobId}`);
    if (!res.ok) throw new Error("Status fetch failed");
    const data = await res.json();
    const percent = Math.round((data.progress || 0) * 100);
    const msg = data.message ? data.message : "";
    statusEl.textContent = `${data.state.toUpperCase()} • ${percent}% ${msg ? "- " + msg : ""}`;

    if (data.state === "done") {
      const result = data.result || {};
      const url = `/api/result/${jobId}`;
      downloadLink.href = url;
      downloadLink.classList.remove("hidden");
      return;
    }

    if (data.state === "failed") {
      throw new Error(data.message || "Generation failed");
    }

    await new Promise((r) => setTimeout(r, 2000));
  }
}

document.getElementById("btnGenerate").addEventListener("click", async () => {
  const btn = document.getElementById("btnGenerate");
  const statusEl = document.getElementById("status");
  const downloadLink = document.getElementById("downloadLink");

  downloadLink.classList.add("hidden");
  statusEl.textContent = "QUEUED...";

  const idea = document.getElementById("idea").value.trim();
  const style = document.getElementById("style").value;
  const language = document.getElementById("language").value;
  const num_scenes = parseInt(document.getElementById("num_scenes").value, 10);

  const enable_lip_sync = document.getElementById("enable_lip_sync").checked;
  const enable_music = document.getElementById("enable_music").checked;
  const low_end = document.getElementById("low_end").checked;
  const enable_upload_youtube = document.getElementById("enable_upload_youtube").checked;

  if (!idea) {
    statusEl.textContent = "Please enter a story idea.";
    return;
  }

  btn.disabled = true;
  btn.textContent = "Generating...";

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        idea,
        style,
        language,
        num_scenes,
        low_end,
        voice_style: "default",
        output_aspect: "16:9",
        enable_lip_sync,
        enable_music,
        enable_upload_youtube,
      }),
    });
    if (!res.ok) throw new Error("Generate request failed");
    const data = await res.json();
    statusEl.textContent = `JOB ${data.job_id} CREATED...`;
    await pollStatus(data.job_id);
  } catch (e) {
    statusEl.textContent = "ERROR: " + e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate Anime";
  }
});

