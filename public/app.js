const tg = window.Telegram?.WebApp;

if (tg) {
  tg.ready();
  tg.expand();
}

const user = tg?.initDataUnsafe?.user;
const welcome = document.getElementById("welcome");

if (welcome) {
  const name = user?.first_name || "بك";
  welcome.textContent = `أهلاً ${name} 👋`;
}

document.querySelectorAll("button").forEach((button) => {
  button.addEventListener("touchstart", () => {
    button.style.transition = "transform .08s ease";
  }, { passive: true });
});

document.querySelectorAll(".task button").forEach((button) => {
  button.addEventListener("click", () => {
    button.textContent = "جاري الفتح...";
    setTimeout(() => {
      button.textContent = "شاهد ▶";
    }, 700);
  });
});
