import time
import random
import os
import shutil
import json
from typing import Optional
from DrissionPage import ChromiumPage, ChromiumOptions
from tempmail.base import TempMailBase
from utils.password import generate_password
from utils.proxy_extension import create_proxy_auth_extension
from config import Config

class DreaminaRegister:
    def __init__(self, tempmail_service: TempMailBase, proxy_url: Optional[str] = None):
        self.tempmail_service = tempmail_service
        self.proxy_url = proxy_url
        self.page = None
        self.email_address = None
        self.password = None
        self.proxy_plugin_path = None
        self.user_data_path = None
        
    def init_browser(self):
        self.user_data_path = os.path.join(os.getcwd(), f"user_data_{random.randint(10000, 99999)}_{time.time()}")
        port = random.randint(10000, 50000)
        
        options = ChromiumOptions()
        options.set_user_data_path(self.user_data_path)
        options.set_local_port(port)
        options.incognito()
        
        if Config.HEADLESS:
            options.headless()
            # Docker/Linux 环境必须添加的参数
            options.set_argument('--no-sandbox')
            options.set_argument('--disable-dev-shm-usage')
            options.set_argument('--disable-gpu')
        
        if self.proxy_url:
            print(f"配置代理插件: {self.proxy_url}")
            self.proxy_plugin_path = create_proxy_auth_extension(self.proxy_url)
            options.add_extension(self.proxy_plugin_path)
        
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
        for i in range(3):
            try:
                continue_email = self.page.ele("text=Continue with email", timeout=30)
                if continue_email:
                    continue_email.click()
                    break
            except Exception as e:
                print(f"点击Continue with email失败 (尝试 {i+1}/3): {e}")
                time.sleep(1)
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
    
    def _get_region_prefix(self, location_code: str) -> str:
        """
        根据 location code 返回对应的区域前缀
        支持的区域: HK -> hk-, JP -> jp-, SG -> sg-, 其他 -> us-
        """
        code_to_prefix = {
            "HK": "hk-",
            "JP": "jp-",
            "SG": "sg-",
            "US": "us-"
        }
        return code_to_prefix.get(location_code.upper(), "us-")
    
    def _get_region_from_network(self, timeout: int = 30) -> str:
        """
        通过监听网络请求获取账户区域
        拦截 https://dreamina.capcut.com/lv/v1/user/web/user_info 的响应
        返回区域前缀
        """
        print("监听网络请求以获取账户区域...")
        target_url = "dreamina.capcut.com/lv/v1/user/web/user_info"
        start_time = time.time()
        
        # 启用网络监听
        self.page.listen.start(target_url)
        
        region_prefix = "us-"  # 默认区域
        
        try:
            while time.time() - start_time < timeout:
                # 等待目标请求
                res = self.page.listen.wait(timeout=timeout - (time.time() - start_time))
                if res:
                    try:
                        # 获取响应体
                        response_body = res.response.body
                        if isinstance(response_body, str):
                            data = json.loads(response_body)
                        else:
                            data = response_body
                        
                        # 解析 location.code
                        if "data" in data and "location" in data["data"]:
                            location_code = data["data"]["location"].get("code", "")
                            if location_code:
                                region_prefix = self._get_region_prefix(location_code)
                                print(f"检测到账户区域: {location_code} -> 前缀: {region_prefix}")
                            break
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        print(f"解析 user_info 响应失败: {e}")
                        break
                else:
                    break
        finally:
            self.page.listen.stop()
        
        return region_prefix
    
    def step_15_to_16(self, output_file: str = "key.txt", account_file: str = "account.txt"):
        print("步骤15: 等待页面跳转并获取Cookie...")
        
        # 启用网络监听以获取区域信息
        target_url = "dreamina.capcut.com/lv/v1/user/web/user_info"
        self.page.listen.start(target_url)
        
        region_prefix = "us-"  # 默认区域
        
        continue_ = self.page.ele("text=What role best describes you?", timeout=30)
        
        # 尝试获取 user_info 响应中的区域信息
        try:
            res = self.page.listen.wait(timeout=5)
            if res:
                try:
                    response_body = res.response.body
                    if isinstance(response_body, str):
                        data = json.loads(response_body)
                    else:
                        data = response_body
                    
                    if "data" in data and "location" in data["data"]:
                        location_code = data["data"]["location"].get("code", "")
                        if location_code:
                            region_prefix = self._get_region_prefix(location_code)
                            print(f"检测到账户区域: {location_code} -> 前缀: {region_prefix}")
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"解析 user_info 响应失败: {e}, 使用默认区域前缀 us-")
        finally:
            self.page.listen.stop()
        
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
        formatted_sessionid = f"{region_prefix}{sessionid}"
        
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
            
            return {
                "email": self.email_address,
                "password": self.password,
                "session_id": sessionid
            }
            
        except Exception as e:
            print(f"注册失败: {e}")
            raise
        finally:
            if self.page:
                try:
                    self.page.quit()
                except:
                    pass
            
            if self.proxy_plugin_path and os.path.exists(self.proxy_plugin_path):
                try:
                    shutil.rmtree(self.proxy_plugin_path)
                except Exception as e:
                    print(f"Clean up proxy plugin failed: {e}")

            if self.user_data_path and os.path.exists(self.user_data_path):
                for i in range(10):
                    try:
                        shutil.rmtree(self.user_data_path)
                        break
                    except Exception as e:
                        if i == 9:
                            print(f"Clean up user data failed after retries: {e}")
                        time.sleep(1)
    def login(self, email, password) -> dict:
        """
        登录并获取SessionID
        """
        try:
            self.init_browser()
            self.email_address = email
            self.password = password
            
            print(f"开始登录 Dreamina 账户: {email}")
            
            # 步骤1: 访问页面
            print("步骤1: 打开Dreamina网站...")
            self.page.get("https://dreamina.capcut.com/ai-tool/home")
            time.sleep(1)
            print(f"页面标题: {self.page.title}")

            # 步骤2: 点击 Create 或 Sign in
            print("步骤2: 查找并点击 Create 或 Sign in...")
            create_btn = self.page.ele("text=Create", timeout=30)
            if not create_btn:
                # 尝试其他 Create 选择器
                create_btn = self.page.ele("@@role=menuitem@@text()=Create", timeout=5)
            
            if create_btn:
                print("找到 Create 按钮")
                create_btn.click()
                time.sleep(1)
            else:
                print("尝试 Sign in 按钮...")
                sign_in_types = ["text=Sign in", "@@role=menuitem@@text()=Sign in", "@class:login", "text:Sign in"]
                sign_in_btn = None
                for selector in sign_in_types:
                    sign_in_btn = self.page.ele(selector, timeout=3)
                    if sign_in_btn:
                        print(f"找到 Sign in 按钮 ({selector})")
                        break
                
                if sign_in_btn:
                    sign_in_btn.click()
                else:
                    raise ValueError("无法找到 Create 或 Sign in 按钮")
            
            # 步骤3: Continue with email
            print("步骤3: 点击 Continue with email...")
            continue_email = self.page.ele("text=Continue with email", timeout=30)
            if continue_email:
                continue_email.click()
                time.sleep(0.5)
            else:
                raise ValueError("无法找到 Continue with email 按钮")

            # 步骤4: 填入邮箱
            print("步骤4: 填入邮箱地址...")
            email_input = self.page.ele("@placeholder=Enter email", timeout=10)
            if not email_input:
                email_input = self.page.ele("@type=email", timeout=10)
            
            if email_input:
                email_input.input(email)
                time.sleep(0.5)
            else:
                raise ValueError("无法找到邮箱输入框")

            # 步骤5: 填入密码
            print("步骤5: 填入密码...")
            password_input = self.page.ele("@placeholder=Enter password", timeout=10)
            if not password_input:
                password_input = self.page.ele("@type=password", timeout=10)
            
            if password_input:
                password_input.input(password)
                time.sleep(0.5)
            else:
                raise ValueError("无法找到密码输入框")

            # 步骤6: 点击 Continue
            print("步骤6: 点击 Continue 按钮...")
            continue_btn = self.page.ele("@text()=Continue", timeout=30)
            if continue_btn:
                continue_btn.click()
            else:
                raise ValueError("无法找到 Continue 按钮")

            # 步骤7: 等待 SessionID
            print("步骤7: 等待页面跳转并获取Cookie...")
            
            # 启用网络监听以获取区域信息
            target_url = "dreamina.capcut.com/lv/v1/user/web/user_info"
            self.page.listen.start(target_url)
            
            region_prefix = "us-"  # 默认区域
            
            start_time = time.time()
            sessionid = None
            expires = None
            
            while time.time() - start_time < 60:
                cookies = self.page.cookies()
                for cookie in cookies:
                    if cookie.get("name") == "sessionid":
                        sessionid = cookie.get("value")
                        expires = cookie.get("expiry")
                        break
                if sessionid:
                    break
                time.sleep(1)
            
            # 尝试获取 user_info 响应中的区域信息
            try:
                res = self.page.listen.wait(timeout=5)
                if res:
                    try:
                        response_body = res.response.body
                        if isinstance(response_body, str):
                            data = json.loads(response_body)
                        else:
                            data = response_body
                        
                        if "data" in data and "location" in data["data"]:
                            location_code = data["data"]["location"].get("code", "")
                            if location_code:
                                region_prefix = self._get_region_prefix(location_code)
                                print(f"检测到账户区域: {location_code} -> 前缀: {region_prefix}")
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        print(f"解析 user_info 响应失败: {e}, 使用默认区域前缀 us-")
            finally:
                self.page.listen.stop()
            
            if not sessionid:
                # 尝试检查是否有错误提示
                error_msg = self.page.ele(".lv-message")
                if error_msg:
                    print(f"发现错误提示: {error_msg.text}")
                elif self.page.ele("text=Incorrect email or password"):
                     print("错误提示: Incorrect email or password")
                raise ValueError("未能获取sessionid (可能是登录失败)")

            print(f"获取到sessionid: {sessionid}")
            
            return {
                "email": email,
                "password": password,
                "session_id": f"{region_prefix}{sessionid}",
                "expires": expires
            }

        except Exception as e:
            print(f"登录失败: {e}")
            raise
        finally:
            if self.page:
                try:
                    self.page.quit()
                except:
                    pass
            
            if self.proxy_plugin_path and os.path.exists(self.proxy_plugin_path):
                try:
                    shutil.rmtree(self.proxy_plugin_path)
                except Exception as e:
                    print(f"Clean up proxy plugin failed: {e}")

            if self.user_data_path and os.path.exists(self.user_data_path):
                for i in range(10):
                    try:
                        shutil.rmtree(self.user_data_path)
                        break
                    except Exception as e:
                        if i == 9:
                            print(f"Clean up user data failed after retries: {e}")
                        time.sleep(1)

