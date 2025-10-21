from config import Config
from tempmail.moemail import MoeMail
from tempmail.tempmailhub import TempMailHub
from automation.dreamina import DreaminaRegister
from services.gptload import GptloadService
import os

def main():
    try:
        Config.validate()
        
        print("=== Dreamina自动化注册程序 ===\n")
        
        if Config.TEMPMAIL_TYPE == "moemail":
            print("使用MoeMail临时邮箱服务")
            tempmail_service = MoeMail(Config.MOEMAIL_API_KEY, Config.MOEMAIL_BASE_URL)
        elif Config.TEMPMAIL_TYPE == "tempmailhub":
            print(f"使用TempMailHub临时邮箱服务 (渠道: {Config.TEMPMAILHUB_CHANNEL})")
            tempmail_service = TempMailHub(Config.TEMPMAILHUB_API_KEY, Config.TEMPMAILHUB_CHANNEL, Config.TEMPMAILHUB_BASE_URL)
        else:
            raise ValueError(f"不支持的临时邮箱类型: {Config.TEMPMAIL_TYPE}")
        
        if Config.PROXY_URL:
            print(f"使用代理: {Config.PROXY_URL}\n")
        else:
            print("未配置代理\n")
        
        print(f"计划注册账号数量: {Config.REGISTER_COUNT}\n")
        
        success_count = 0
        fail_count = 0
        
        for i in range(Config.REGISTER_COUNT):
            print(f"\n{'='*50}")
            print(f"开始注册第 {i+1}/{Config.REGISTER_COUNT} 个账号")
            print(f"{'='*50}\n")
            
            try:
                register = DreaminaRegister(tempmail_service, Config.PROXY_URL)
                sessionid = register.register()
                success_count += 1
                print(f"\n✓ 第 {i+1} 个账号注册成功")
            except Exception as e:
                fail_count += 1
                print(f"\n✗ 第 {i+1} 个账号注册失败: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*50}")
        print("=== 批量注册完成 ===")
        print(f"成功: {success_count} 个")
        print(f"失败: {fail_count} 个")
        print(f"SessionID已保存到key.txt")
        print(f"{'='*50}")
        
        if success_count > 0 and Config.GPTLOAD_AUTH_KEY:
            print(f"\n{'='*50}")
            print("=== 推送Keys到Gptload ===")
            try:
                if not os.path.exists("key.txt"):
                    print("警告: key.txt文件不存在，跳过推送")
                else:
                    with open("key.txt", "r", encoding="utf-8") as f:
                        keys = [line.strip() for line in f if line.strip()]
                    
                    if not keys:
                        print("警告: key.txt为空，跳过推送")
                    else:
                        print(f"读取到 {len(keys)} 个keys")
                        
                        gptload = GptloadService(Config.GPTLOAD_API_URL, Config.GPTLOAD_AUTH_KEY)
                        
                        print(f"查找channel: {Config.GPTLOAD_CHANNEL_NAME}")
                        group_id = gptload.find_group_by_name(Config.GPTLOAD_CHANNEL_NAME)
                        
                        if not group_id:
                            print(f"错误: 未找到名为 '{Config.GPTLOAD_CHANNEL_NAME}' 的group")
                        else:
                            print(f"找到group_id: {group_id}")
                            print("开始推送keys...")
                            
                            result = gptload.push_keys(group_id, keys)
                            
                            print(f"✓ 推送成功!")
                            print(f"  任务类型: {result.get('task_type')}")
                            print(f"  Group名称: {result.get('group_name')}")
                            print(f"  总数: {result.get('total')}")
                            print(f"  开始时间: {result.get('started_at')}")
            except Exception as e:
                print(f"✗ 推送失败: {e}")
                import traceback
                traceback.print_exc()
            
            print(f"{'='*50}")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
