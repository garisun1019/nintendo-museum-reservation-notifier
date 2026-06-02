Date.prototype.addDays = function (days) {
  var date = new Date(this.valueOf());
  date.setDate(date.getDate() + days);
  return date;
};

const now = new Date();
document.getElementById("date").value = now
  .addDays(1)
  .toISOString()
  .split("T")[0];

// 处理服务选择切换
const serviceSelect = document.getElementById("service");
const barkConfig = document.getElementById("barkConfig");
const telegramConfig = document.getElementById("telegramConfig");

serviceSelect.addEventListener("change", () => {
  if (serviceSelect.value === "bark") {
    barkConfig.style.display = "block";
    telegramConfig.style.display = "none";
  } else {
    barkConfig.style.display = "none";
    telegramConfig.style.display = "block";
  }
});

// Bark 输入框验证
const endpoint = document.getElementById("endpoint");
endpoint.addEventListener("input", () => {
  endpoint.classList.remove("input-error");
});

// Telegram 输入框验证
const telegramToken = document.getElementById("telegramToken");
const telegramChatId = document.getElementById("telegramChatId");

telegramToken.addEventListener("input", () => {
  telegramToken.classList.remove("input-error");
});

telegramChatId.addEventListener("input", () => {
  telegramChatId.classList.remove("input-error");
});

// 开始按钮
const button = document.getElementById("start");
button.addEventListener("click", () => {
  const date = document.getElementById("date").value;
  const service = serviceSelect.value;

  let config = {
    service: service,
    date: date
  };

  if (service === "bark") {
    if (endpoint.value.length === 0) {
      endpoint.classList.add("input-error");
      alert("The Bark endpoint cannot be empty.");
      return;
    }
    config.endpoint = endpoint.value;
  } else if (service === "telegram") {
    if (telegramToken.value.length === 0) {
      telegramToken.classList.add("input-error");
      alert("The Telegram bot token cannot be empty.");
      return;
    }
    if (telegramChatId.value.length === 0) {
      telegramChatId.classList.add("input-error");
      alert("The Telegram chat ID cannot be empty.");
      return;
    }
    config.telegramToken = telegramToken.value;
    config.telegramChatId = telegramChatId.value;
  }

  window.electron.start(date, config);
});