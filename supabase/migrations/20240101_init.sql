-- 创建志愿者积分表
CREATE TABLE IF NOT EXISTS volunteer_points (
    id SERIAL PRIMARY KEY,
    activity_type TEXT,
    activity_time_name TEXT,
    category TEXT,
    name TEXT,
    score TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建志愿者积分使用情况表
CREATE TABLE IF NOT EXISTS volunteer_usage (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    total_points INTEGER DEFAULT 0,
    used_points INTEGER DEFAULT 0,
    course_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建获取志愿者积分汇总的存储过程
CREATE OR REPLACE FUNCTION get_volunteer_summary()
RETURNS TABLE (
    name TEXT,
    total_score BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        volunteer_points.name,
        SUM(CAST(volunteer_points.score AS INTEGER)) as total_score
    FROM 
        volunteer_points
    GROUP BY 
        volunteer_points.name
    ORDER BY 
        volunteer_points.name;
END;
$$ LANGUAGE plpgsql;

-- 创建RLS策略
ALTER TABLE volunteer_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE volunteer_usage ENABLE ROW LEVEL SECURITY;

-- 创建公共访问策略
CREATE POLICY "允许公共读取志愿者积分" ON volunteer_points
    FOR SELECT USING (true);

CREATE POLICY "允许公共读取积分使用情况" ON volunteer_usage
    FOR SELECT USING (true);

-- 创建服务角色访问策略
CREATE POLICY "允许服务角色完全访问志愿者积分" ON volunteer_points
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "允许服务角色完全访问积分使用情况" ON volunteer_usage
    FOR ALL USING (auth.role() = 'service_role');