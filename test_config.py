#!/usr/bin/env python3
"""
配置验证脚本
验证环境变量是否正确加载
"""

from app.config import config

def main():
    print("=== FastAPI 配置验证 ===\n")
    
    print("📊 应用配置:")
    print(f"  调试模式: {config.debug}")
    print(f"  JWT 算法: {config.algorithm}")
    print(f"  Token 过期时间: {config.access_token_expire_minutes} 分钟")
    print(f"  密钥已设置: {'是' if config.secret_key != 'your-secret-key-change-in-production' else '否（使用默认值）'}")
    
    print("\n🗄️  数据库配置:")
    print(f"  主机: {config.database.host}")
    print(f"  端口: {config.database.port}")
    print(f"  数据库名: {config.database.name}")
    print(f"  用户名: {config.database.user}")
    print(f"  驱动: {config.database.driver}")
    print(f"  连接字符串: {config.database}")
    
    print("\n✅ 配置验证完成！")
    
    # 可选：测试数据库连接
    try:
        from app.db.database import engine
        with engine.connect() as connection:
            print("🔗 数据库连接测试成功！")
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")

if __name__ == "__main__":
    main()
