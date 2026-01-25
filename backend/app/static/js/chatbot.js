(function(){
  const body = document.getElementById("chatBody");
  const btn  = document.getElementById("chatToggle");

  // Toggle vis/skjul
  btn.addEventListener("click", () => {
    const hidden = body.style.display === "none";
    body.style.display = hidden ? "block" : "none";
    btn.textContent = hidden ? "Skjul" : "Vis";
  });

  // Send chat
  const logEl = document.getElementById("chatLog");
  const inputEl = document.getElementById("chatInput");
  const sendEl = document.getElementById("chatSend");

  function addMsg(who, text) {
    const wrap = document.createElement("div");
    wrap.style.margin = "8px 0";
    wrap.innerHTML = `<strong>${who}:</strong> <span style="white-space:pre-wrap;"></span>`;
    wrap.querySelector("span").textContent = text;
    logEl.appendChild(wrap);
    logEl.scrollTop = logEl.scrollHeight;
  }

  async function sendMsg() {
    const msg = (inputEl.value || "").trim();
    if (!msg) return;

    addMsg("Du", msg);
    inputEl.value = "";
    inputEl.focus();

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({ message: msg }),
      });

      const ct = (res.headers.get("content-type") || "").toLowerCase();
      if (!ct.includes("application/json")) {
        addMsg("Bot", "Du ser ut til å være logget ut. Last siden på nytt og logg inn igjen, og prøv så på nytt.");
        return;
      }

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        addMsg("Bot", data.reply || "Noe gikk galt. Prøv igjen.");
        return;
      }

      addMsg("Bot", data.reply || "Ingen svar.");
    } catch (e) {
      addMsg("Bot", "Kunne ikke kontakte serveren. Er du pålogget og kjører appen?");
    }
  }

  sendEl.addEventListener("click", sendMsg);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMsg();
    }
  });
})();
