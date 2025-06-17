# 部署指南

## 问题分析

前端页面在GitHub部署和本地环境不一样的主要原因：

1. **API基础URL配置不一致**：前端代码中有两个不同的API_BASE_URL配置
2. **部署环境检测错误**：代码检测GitHub Pages但实际使用Vercel部署
3. **路由配置问题**：Vercel配置没有正确处理API路由

## 解决方案

### 方案1：使用Vercel部署（推荐）

**优势**：
- 前后端统一部署
- 无需跨域问题
- 配置简单

**步骤**：
1. 使用修改后的 `vercel.json` 配置
2. 前端使用 `frontend/index.html`
3. 部署到Vercel

**配置文件**：
- `vercel.json`：已修复路由配置
- `frontend/index.html`：智能检测环境

### 方案2：GitHub Pages + Vercel API

**优势**：
- 前端免费托管在GitHub Pages
- 后端使用Vercel的强大功能

**步骤**：
1. 前端部署到GitHub Pages
2. 后端部署到Vercel
3. 前端调用Vercel API

**配置文件**：
- `.github/workflows/deploy.yml`：GitHub Pages部署配置
- `frontend/github-pages.html`：专门的GitHub Pages版本

## 部署步骤

### Vercel部署
```bash
# 1. 安装Vercel CLI
npm i -g vercel

# 2. 登录Vercel
vercel login

# 3. 部署
vercel --prod
```

### GitHub Pages部署
1. 将 `frontend/github-pages.html` 重命名为 `frontend/index.html`
2. 推送到GitHub
3. 在仓库设置中启用GitHub Pages
4. 选择GitHub Actions作为部署源

## 环境变量配置

确保在Vercel中配置以下环境变量：
- `PYTHON_VERSION=3.9`
- 其他必要的环境变量

## 测试

部署后测试以下功能：
1. 页面加载
2. 数据提交
3. 数据查询
4. 文件导出

## 故障排除

1. **API调用失败**：检查API_BASE_URL配置
2. **CORS错误**：确保后端正确设置CORS头
3. **路由404**：检查vercel.json路由配置
4. **静态资源404**：确保前端文件正确部署
