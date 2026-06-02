#!/usr/bin/env python3
"""
Nintendo Museum Reservation Monitor - Cloud Version
支持 Telegram Bot 推送（Android 友好）
基于你的项目改造，提取核心逻辑用于云服务 24/7 运行
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
from dotenv import load_dotenv

# 常量（与你的 Electron 应用保持一致）
TRIGGER_DELAY = 2  # 页面加载延迟 (秒)
RELOAD_INTERVAL = 10  # 页面刷新间隔 (秒)
CALENDAR_URL = "https://museum-tickets.nintendo.com/en/calendar"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


class NotificationService:
    """推送服务基类"""
    
    def send(self, title: str, body: str) -> bool:
        raise NotImplementedError


class TelegramNotificationService(NotificationService):
    """Telegram Bot 推送服务"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    def send(self, title: str, body: str) -> bool:
        """
        发送 Telegram 消息
        
        Args:
            title: 消息标题
            body: 消息内容
            
        Returns:
            是否成功发送
        """
        try:
            # 与你的 inject.js 逻辑一致
            message = f"🎮 <b>{title}</b>\n\n{body}\n\n<a href='{CALENDAR_URL}'>点击这里抢票</a>"
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ Telegram 通知已发送: {title}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Telegram 通知发送失败: {e}")
            return False


class BarkNotificationService(NotificationService):
    """Bark 推送服务（iOS）"""
    
    def __init__(self, bark_endpoint: str):
        self.bark_endpoint = bark_endpoint
    
    def send(self, title: str, body: str) -> bool:
        """
        发送 Bark 推送通知
        
        Args:
            title: 通知标题
            body: 通知内容
            
        Returns:
            是否成功发送
        """
        try:
            url = f"{self.bark_endpoint.rstrip('/')}/Nintendo%20Museum%20Reservation%20Notifier/{body}"
            
            params = {
                'url': CALENDAR_URL,
                'group': 'Nintendo Museum'
            }
            
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ Bark 通知已发送: {title}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Bark 通知发送失败: {e}")
            return False


class NintendoMuseumMonitor:
    """Nintendo Museum 票务云监控器"""
    
    def __init__(self, target_date: str, notification_service: NotificationService):
        """
        初始化监控器
        
        Args:
            target_date: 目标日期 (格式: YYYY-MM-DD)
            notification_service: 推送服务实例
        """
        self.target_date = target_date
        self.notification_service = notification_service
        self.driver: Optional[webdriver.Chrome] = None
        self.check_count = 0
        self.found_ticket = False
        
    def setup_chrome_driver(self) -> webdriver.Chrome:
        """设置 Chrome WebDriver（云环境优化）"""
        chrome_options = Options()
        
        # 无头模式（云环境必须）
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # 禁用图片加载以提升速度
        prefs = {
            "profile.managed_default_content_settings.images": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"❌ ChromeDriver 初始化失败: {e}")
            logger.error("请确保已安装 Chromium 和 ChromeDriver")
            raise
    
    def check_availability(self) -> bool:
        """
        检查目标日期是否有票（与你的 inject.js 逻辑一致）
        
        Returns:
            如果找到可用票次返回 True
        """
        try:
            # 等待页面加载（模拟 TRIGGER_DELAY）
            time.sleep(TRIGGER_DELAY)
            
            # 查找目标日期的 td 元素: <td data-date="YYYY-MM-DD">
            try:
                wait = WebDriverWait(self.driver, 5)
                td_element = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, f"td[data-date='{self.target_date}']")
                    )
                )
                
                # 检查 DOM 路径中是否有 class="sale" 的元素
                # 原始 JS 路径: td.children[0].children[1].children[0].children[0].children[0].children[0]
                try:
                    sale_element = td_element.find_element(
                        By.XPATH,
                        ".//div/div/div/div/div/div[contains(@class, 'sale')]"
                    )
                    
                    if sale_element:
                        logger.info(f"🎉 发现有票！日期: {self.target_date}")
                        self.found_ticket = True
                        return True
                except:
                    pass
                    
            except Exception as e:
                logger.debug(f"未找到 'sale' 元素: {e}")
                return False
            
        except Exception as e:
            logger.error(f"检查过程中出错: {e}")
            return False
    
    def run(self, max_checks: Optional[int] = None):
        """
        运行监控循环
        
        Args:
            max_checks: 最大检查次数 (None = 无限循环)
        """
        try:
            self.driver = self.setup_chrome_driver()
            logger.info(f"🚀 启动云监控器 - 目标日期: {self.target_date}")
            logger.info(f"📍 刷新间隔: {RELOAD_INTERVAL} 秒")
            logger.info(f"🔄 初始延迟: {TRIGGER_DELAY} 秒")
            
            while True:
                self.check_count += 1
                
                try:
                    logger.info(f"📊 检查 #{self.check_count} - {datetime.now().strftime('%H:%M:%S')}")
                    
                    # 访问日历页面
                    self.driver.get(CALENDAR_URL)
                    
                    # 检查是否有票
                    if self.check_availability():
                        # 发送推送通知
                        self.notification_service.send(
                            "任天堂博物馆有票了！",
                            f"🎮 {self.target_date} 有可用座位，立即前往预订！"
                        )
                    
                    # 检查是否达到最大检查次数
                    if max_checks and self.check_count >= max_checks:
                        logger.info(f"✅ 已达到最大检查次数: {max_checks}")
                        break
                    
                    # 等待后刷新（模拟 RELOAD_INTERVAL）
                    logger.info(f"⏳ 等待 {RELOAD_INTERVAL} 秒后继续...")
                    time.sleep(RELOAD_INTERVAL)
                    
                except KeyboardInterrupt:
                    logger.info("⛔ 用户中断监控")
                    break
                except Exception as e:
                    logger.error(f"检查过程出错: {e}")
                    time.sleep(5)
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("🛑 监控器已关闭")


def main():
    """主函数"""
    
    # 从环境变量读取配置
    target_date = os.getenv('TARGET_DATE')
    service_type = os.getenv('SERVICE_TYPE', 'telegram').lower()
    
    if not target_date:
        target_date = input("请输入目标日期 (YYYY-MM-DD): ")
    
    # 验证日期格式
    try:
        datetime.strptime(target_date, '%Y-%m-%d')
    except ValueError:
        logger.error("❌ 日期格式错误，应为 YYYY-MM-DD")
        sys.exit(1)
    
    # 根据服务类型创建通知服务
    if service_type == 'telegram':
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not telegram_token or not telegram_chat_id:
            logger.error("❌ 缺少环境变量: TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
            sys.exit(1)
        
        notification_service = TelegramNotificationService(telegram_token, telegram_chat_id)
        logger.info("📱 使用 Telegram 通知服务")
        
    elif service_type == 'bark':
        bark_endpoint = os.getenv('BARK_ENDPOINT')
        
        if not bark_endpoint:
            logger.error("❌ 缺少环境变量: BARK_ENDPOINT")
            sys.exit(1)
        
        notification_service = BarkNotificationService(bark_endpoint)
        logger.info("🍎 使用 Bark 通知服务")
        
    else:
        logger.error(f"❌ 未知的服务类型: {service_type}")
        sys.exit(1)
    
    # 启动监控
    monitor = NintendoMuseumMonitor(target_date, notification_service)
    monitor.run()


if __name__ == "__main__":
    main()
