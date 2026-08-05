import os
from dotenv import load_dotenv

# 加载当前目录下的 .env 文件
load_dotenv()


class Settings:
    # 读取环境变量，如果读取不到则默认为 None 或空字符串
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

    # 可以在这里做个简单的校验
    def validate_keys(self):
        if not self.OPENAI_API_KEY and not self.DEEPSEEK_API_KEY:
            print("⚠️ 警告: 未在 .env 中找到任何 API Key，请检查配置！")


settings = Settings()