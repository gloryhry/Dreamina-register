import time
import random
from typing import Optional
from DrissionPage import ChromiumPage, ChromiumOptions
from tempmail.base import TempMailBase
from utils.password import generate_password
from config import Config

class DreaminaRegister:
    def __init__(self, tempmail_service: TempMailBase, proxy_url: Optional[str] = None):
        self.tempmail_service = tempmail_service
        self.proxy_url = proxy_url
        self.page = None
        self.email_address = None
        self.password = None
        
    def init_browser(self):
        options = ChromiumOptions()
        options.incognito()
        
        if Config.HEADLESS:
            options.headless()
        
        if self.proxy_url:
            options.set_proxy(self.proxy_url)
        
        options.set_argument('--blink-settings=imagesEnabled=false')
        options.set_argument('--disable-images')
        
        self.page = ChromiumPage(options)
    
    def step_1_to_5(self):
        print("步骤1: 打开Dreamina网站...")
        self.page.get("https://dreamina.capcut.com/ai-tool/home")
        time.sleep(1)
        
        print(f"页面标题: {self.page.title}")
        
        print("步骤2: 点击Sign in按钮...")
        sign_in_btn = self.page.ele("text=Create", timeout=30)
        if not sign_in_btn:
            print("尝试备用定位...")
            sign_in_btn = self.page.ele("text=Sign in", timeout=30)
        
        if sign_in_btn:
            print("找到Sign in按钮")
            sign_in_btn.click()
            # time.sleep(1)
        else:
            raise ValueError("无法找到Sign in按钮")
        
        print("步骤3: 点击Continue with email...")
        continue_email = self.page.ele("text=Continue with email", timeout=30)
        if continue_email:
            continue_email.click()
            # time.sleep(1)
        else:
            raise ValueError("无法找到Continue with email")
        
        print("步骤4: 点击Sign up...")
        sign_up = self.page.ele("text=Sign up", timeout=30)
        if sign_up:
            sign_up.click()
            # time.sleep(1)
        else:
            raise ValueError("无法找到Sign up")
        
        print("步骤1-5完成")
    
    def step_6_to_8(self):
        print("步骤5: 生成临时邮箱...")
        email_data = self.tempmail_service.create_email()
        self.email_address = email_data["address"]
        print(f"生成的邮箱: {self.email_address}")
        
        print("步骤6: 填入邮箱地址...")
        email_input = self.page.ele("@placeholder=Enter email")
        email_input.input(self.email_address)
        # time.sleep(1)
        
        print("步骤7: 生成并填入密码...")
        self.password = generate_password()
        print(f"生成的密码: {self.password}")
        password_input = self.page.ele("@@type=password@@placeholder=Enter password")
        password_input.input(self.password)
        # time.sleep(1)
        
        print("步骤8: 点击Continue按钮...")
        continue_btn = self.page.ele("@text()=Continue", timeout=5)
        continue_btn.click()
        # time.sleep(3)
        
        print("步骤6-8完成")
    
    def step_9_to_10(self):
        print("步骤9: 等待验证码邮件...")
        verification_code = self.tempmail_service.wait_for_verification_code(self.email_address, timeout=60)
        
        if not verification_code:
            raise ValueError("未能获取验证码")
        
        print(f"获取到验证码: {verification_code}")
        
        print("步骤10: 填入验证码...")
        hidden_input = self.page.ele("@@class=lv-input lv-input-size-default@@maxlength=6")
        hidden_input.input(verification_code)
        # time.sleep(3)
        
        print("步骤9-10完成")
    
    def step_11_to_14(self):
        print("步骤11: 填入年份...")
        year = random.randint(1991, 2004)
        year_input = self.page.ele("@placeholder=Year")
        year_input.input(str(year))
        # time.sleep(1)
        
        print("步骤12: 选择月份...")
        month_selector = self.page.ele("@@class=lv-select-view-input@@placeholder=Month")
        month_selector.click()
        # time.sleep(2)
        
        months = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        selected_month = random.choice(months)
        month_option = self.page.ele(f"text={selected_month}")
        month_option.click()
        # time.sleep(1)
        
        print("步骤13: 选择日期...")
        day_selector = self.page.ele("@@class=lv-select-view-input@@placeholder=Day")
        day_selector.click()
        # time.sleep(2)
        
        day = random.randint(1, 28)
        day_option = self.page.ele(f"text={day}")
        day_option.click()
        # time.sleep(1)
        
        print("步骤14: 点击Next按钮...")
        next_btn = self.page.ele("@text()=Next")
        next_btn.click()
        # time.sleep(5)
        
        print("步骤11-14完成")
    
    def step_15_to_16(self, output_file: str = "key.txt", account_file: str = "account.txt"):
        print("步骤15: 等待页面跳转并获取Cookie...")
        continue_ = self.page.ele("text=What role best describes you?", timeout=30)
        
        cookies = self.page.cookies()
        sessionid = None
        
        for cookie in cookies:
            if cookie.get("name") == "sessionid":
                sessionid = cookie.get("value")
                break
        
        if not sessionid:
            raise ValueError("未能获取sessionid")
        
        print(f"获取到sessionid: {sessionid}")
        
        print("步骤16: 保存到key.txt...")
        formatted_sessionid = f"us-{sessionid}"
        
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(formatted_sessionid + "\n")
        
        print(f"已保存: {formatted_sessionid}")
        
        print(f"保存账号信息到{account_file}...")
        account_info = f"{self.email_address}:{self.password}"
        try:
            with open(account_file, "a", encoding="utf-8") as f:
                f.write(account_info + "\n")
            print(f"已保存账号: {account_info}")
        except Exception as e:
            print(f"警告: 保存账号信息失败: {e}")
        
        print("步骤15-16完成")
        
        return formatted_sessionid
    
    def register(self, output_file: str = "key.txt", account_file: str = "account.txt") -> str:
        try:
            self.init_browser()
            
            self.step_1_to_5()
            self.step_6_to_8()
            self.step_9_to_10()
            self.step_11_to_14()
            sessionid = self.step_15_to_16(output_file, account_file)
            
            print(f"\n注册成功!")
            print(f"邮箱: {self.email_address}")
            print(f"密码: {self.password}")
            print(f"SessionID: {sessionid}")
            
            return sessionid
            
        except Exception as e:
            print(f"注册失败: {e}")
            raise
        finally:
            if self.page:
                time.sleep(1)
                self.page.quit()
