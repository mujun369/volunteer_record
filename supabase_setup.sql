-- Supabase数据库设置脚本
-- 请在Supabase SQL编辑器中运行此脚本

-- 1. 创建volunteer_points表（如果不存在）
CREATE TABLE IF NOT EXISTS volunteer_points (
    id SERIAL PRIMARY KEY,
    activity_type TEXT NOT NULL,
    activity_time_name TEXT NOT NULL,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 创建volunteer_usage表（如果不存在）
CREATE TABLE IF NOT EXISTS volunteer_usage (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    used_points INTEGER NOT NULL DEFAULT 0,
    course_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 禁用行级安全策略（用于开发/演示环境）
ALTER TABLE volunteer_points DISABLE ROW LEVEL SECURITY;
ALTER TABLE volunteer_usage DISABLE ROW LEVEL SECURITY;

-- 4. 或者，如果您想启用RLS并允许所有操作（更安全的选择）
-- 取消注释以下行来启用RLS并创建允许所有操作的策略：

-- ALTER TABLE volunteer_points ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE volunteer_usage ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Allow all operations on volunteer_points" ON volunteer_points
--     FOR ALL USING (true) WITH CHECK (true);

-- CREATE POLICY "Allow all operations on volunteer_usage" ON volunteer_usage
--     FOR ALL USING (true) WITH CHECK (true);

-- 5. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_volunteer_points_name ON volunteer_points(name);
CREATE INDEX IF NOT EXISTS idx_volunteer_usage_name ON volunteer_usage(name);
CREATE INDEX IF NOT EXISTS idx_volunteer_points_created_at ON volunteer_points(created_at);
CREATE INDEX IF NOT EXISTS idx_volunteer_usage_created_at ON volunteer_usage(created_at);

-- 6. 插入一些测试数据（可选）
-- INSERT INTO volunteer_points (activity_type, activity_time_name, category, name, score) 
-- VALUES 
--     ('线下活动', '测试活动', '志愿服务', '测试用户', 10),
--     ('线上直播', '在线讲座', '技术分享', '测试用户', 5);

-- INSERT INTO volunteer_usage (name, used_points, course_count) 
-- VALUES 
--     ('测试用户', 3, 1);
