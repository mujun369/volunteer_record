# Supabase数据库设置指南

## 问题描述
当前应用遇到"new row violates row-level security policy"错误，这是因为Supabase默认启用了行级安全策略(RLS)，但没有配置相应的策略来允许数据插入。

## 解决方案

### 方法1：禁用RLS（推荐用于开发/演示）

1. 登录到您的Supabase项目
2. 进入SQL编辑器
3. 运行以下SQL命令：

```sql
-- 禁用行级安全策略
ALTER TABLE volunteer_points DISABLE ROW LEVEL SECURITY;
ALTER TABLE volunteer_usage DISABLE ROW LEVEL SECURITY;
```

### 方法2：配置RLS策略（推荐用于生产环境）

1. 登录到您的Supabase项目
2. 进入SQL编辑器
3. 运行以下SQL命令：

```sql
-- 启用行级安全策略
ALTER TABLE volunteer_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE volunteer_usage ENABLE ROW LEVEL SECURITY;

-- 创建允许所有操作的策略
CREATE POLICY "Allow all operations on volunteer_points" ON volunteer_points
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on volunteer_usage" ON volunteer_usage
    FOR ALL USING (true) WITH CHECK (true);
```

### 方法3：使用完整的设置脚本

运行项目根目录下的`supabase_setup.sql`文件中的所有SQL命令。

## 验证设置

设置完成后，您可以通过以下方式验证：

1. 访问 https://volunteerrecord.vercel.app/api/health 检查连接状态
2. 尝试提交测试数据
3. 检查Supabase表编辑器中是否有新数据

## 环境变量

确保在Vercel中设置了以下环境变量：

- `SUPABASE_URL`: 您的Supabase项目URL
- `SUPABASE_SERVICE_KEY`: 您的Supabase服务密钥（推荐）
- `SUPABASE_ANON_KEY`: 您的Supabase匿名密钥（备用）

## 注意事项

- 在生产环境中，建议使用更严格的RLS策略
- 确保使用服务密钥而不是匿名密钥来获得完整的数据库访问权限
- 定期备份您的数据库数据
