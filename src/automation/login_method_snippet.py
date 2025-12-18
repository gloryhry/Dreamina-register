    def login(self, email, password) -> dict:
        """
        登录并获取SessionID，参考 provided JS logic
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
            
            # 等待 url 变化或者特定的元素出现，这里参考 js 逻辑等待 url 包含 dreamina.capcut.com
            # DrissionPage 的 wait.url_change 也许可用，或者循环检查
            start_time = time.time()
            sessionid = None
            expires = None
            
            while time.time() - start_time < 60:
                cookies = self.page.cookies(as_dict=False) # 获取所有cookie对象列表
                for cookie in cookies:
                    if cookie.get("name") == "sessionid":
                        sessionid = cookie.get("value")
                        expires = cookie.get("expiry") # DrissionPage cookie dict key usually 'expiry' or 'expires'
                        break
                if sessionid:
                    break
                time.sleep(1)
            
            # 尝试获取 user_info 响应中的区域信息
            try:
                res = self.page.listen.wait(timeout=5)
                if res:
                    try:
                        import json
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
                time.sleep(1)
                self.page.quit()
