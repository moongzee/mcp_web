let currentMessage = "";
let currentSpeaker = "claude";
let claudeContext = [];
let gptContext = [];

document.getElementById("chatForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  document.getElementById("chatContainer").innerHTML = "";
  document.getElementById("debugContent").innerText = "";

  const claude_role = document.getElementById("claude_role").value;
  const gpt_role = document.getElementById("gpt_role").value;
  currentMessage = document.getElementById("start_message").value;

  for (let i = 0; i < 10; i++) {
    showLoadingBubble(currentSpeaker);

    const res = await fetch("/mcp-turn", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        claude_role,
        gpt_role,
        current_message: currentMessage,
        current_speaker: currentSpeaker,
        claude_context: claudeContext,
        gpt_context: gptContext
      })
    });
    const data = await res.json();

    removeLoadingBubble();

    const bubble = document.createElement("div");
    bubble.className = "bubble " + (currentSpeaker === "claude" ? "friend" : "me");

    const speakerName = currentSpeaker === "claude" ? "Claude" : "GPT";
    bubble.innerHTML = `<strong>${speakerName}:</strong><br>${data.reply}`;

    document.getElementById("chatContainer").appendChild(bubble);

    // 디버그 로그 갱신
    document.getElementById("debugContent").innerText = data.debug_log;

    // 다음 턴 준비
    currentMessage = data.current_message;
    currentSpeaker = data.current_speaker;
    claudeContext = data.claude_context;
    gptContext = data.gpt_context;

    await new Promise(res => setTimeout(res, 600));
  }
});

function showLoadingBubble(speaker) {
  const loading = document.createElement("div");
  loading.className = "bubble loading " + (speaker === "claude" ? "friend" : "me");
  loading.id = "loadingBubble";

  loading.innerHTML = `
    <strong>${speaker === "claude" ? "Claude" : "GPT"}:</strong><br>
    <img src="/static/load-32_128.gif" alt="로딩 중..." style="height: 24px;">
  `;

  document.getElementById("chatContainer").appendChild(loading);
  document.getElementById("chatContainer").scrollTop = document.getElementById("chatContainer").scrollHeight;
}

function removeLoadingBubble() {
  const loading = document.getElementById("loadingBubble");
  if (loading) loading.remove();
}
