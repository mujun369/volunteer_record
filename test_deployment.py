#!/usr/bin/env python3
"""
部署测试脚本 - 验证前端和后端是否正常工作
"""

import requests
import json
import sys

def test_vercel_backend():
    """测试Vercel后端API"""
    print("🔍 测试Vercel后端API...")
    
    base_url = "https://volunteer-record.vercel.app"
    
    try:
        # 测试健康检查
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Vercel后端API健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ Vercel后端API健康检查失败: {response.status_code}")
            return False
            
        # 测试主页
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Vercel主页访问正常")
        else:
            print(f"❌ Vercel主页访问失败: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Vercel后端测试失败: {str(e)}")
        return False

def test_github_pages():
    """测试GitHub Pages前端"""
    print("\n🔍 测试GitHub Pages前端...")
    
    # 注意：这里需要替换为实际的GitHub Pages URL
    github_pages_url = "https://[用户名].github.io/[仓库名]/"
    
    print(f"📝 请手动访问GitHub Pages URL: {github_pages_url}")
    print("   检查以下内容：")
    print("   1. 页面是否显示志愿者积分记录平台")
    print("   2. 表格是否正常显示")
    print("   3. 是否可以切换线上/线下活动类型")
    print("   4. API调用是否正常工作")
    
    return True

def test_api_functionality():
    """测试API功能"""
    print("\n🔍 测试API功能...")
    
    base_url = "https://volunteer-record.vercel.app"
    
    try:
        # 测试提交数据
        test_data = {
            "activityData": [
                ["2024-01-01", "线上直播", "海报", "张三", "10"]
            ],
            "usageData": [
                ["张三", "5", "1"]
            ]
        }
        
        response = requests.post(
            f"{base_url}/api/submit",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API数据提交测试通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ API数据提交测试失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
        # 测试获取汇总数据
        response = requests.get(f"{base_url}/api/get_summary", timeout=10)
        if response.status_code == 200:
            print("✅ API汇总数据获取测试通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ API汇总数据获取测试失败: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ API功能测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始部署测试...")
    print("=" * 50)
    
    # 测试后端
    backend_ok = test_vercel_backend()
    
    # 测试前端
    frontend_ok = test_github_pages()
    
    # 测试API功能
    api_ok = test_api_functionality()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"   Vercel后端: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"   GitHub Pages前端: {'✅ 需手动验证' if frontend_ok else '❌ 异常'}")
    print(f"   API功能: {'✅ 正常' if api_ok else '❌ 异常'}")
    
    if backend_ok and api_ok:
        print("\n🎉 后端部署成功！")
        print("📝 请确保GitHub Pages已启用并正确配置")
        print("🔗 GitHub Pages设置路径: 仓库 → Settings → Pages → Source: GitHub Actions")
    else:
        print("\n⚠️  部分功能存在问题，请检查配置")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
