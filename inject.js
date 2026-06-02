const { contextBridge } = require("electron");

const TRIGGER_DELAY = 2000;
const RELOAD_INTERVAL = 10000;

contextBridge.exposeInMainWorld("electron", {
  inject: (date, config) => {
    setTimeout(() => {
      // Check capacity.
      const td = document.querySelector(`td[data-date="${date}"]`);
      if (td) {
        const name =
          td?.children?.[0]?.children?.[1]?.children?.[0]?.children?.[0]
            ?.children?.[0]?.children?.[0]?.className;
        if (name === "sale") {
          // 根据服务类型调用不同的推送方法
          if (config.service === "bark") {
            sendBarkNotification(config.endpoint);
          } else if (config.service === "telegram") {
            sendTelegramNotification(config.telegramToken, config.telegramChatId);
          }
        }
      }

      setTimeout(() => {
        window.location.reload();
      }, RELOAD_INTERVAL);
    }, TRIGGER_DELAY);
  },
});

// Bark 推送函数
function sendBarkNotification(endpoint) {
  fetch(
    `${endpoint.replace(
      /\/$/,
      ""
    )}/Nintendo%20Museum%20Reservation%20Notifier/Here%20is%20a%20seat.%20Tap%20here%20to%20reserve.?url=https://museum-tickets.nintendo.com/en/calendar`
  ).catch(err => console.error("Bark notification failed:", err));
}

// Telegram 推送函数
function sendTelegramNotification(botToken, chatId) {
  const message = `🎮 <b>任天堂博物馆有票了！</b>\n\n有可用座位，立即前往预订！\n\n<a href="https://museum-tickets.nintendo.com/en/calendar">点击这里抢票</a>`;
  
  fetch("https://api.telegram.org/bot" + botToken + "/sendMessage", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      chat_id: chatId,
      text: message,
      parse_mode: "HTML",
    }),
  }).catch(err => console.error("Telegram notification failed:", err));
}