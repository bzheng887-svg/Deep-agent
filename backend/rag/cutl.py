import datetime
import pytz

beijing_tz = pytz.timezone("Asia/Shanghai")
current_time_beijing = datetime.datetime.now(beijing_tz)

# 转换为 ISO 8601 字符串格式
timestamp_str = current_time_beijing.isoformat()
print(timestamp_str)  # 2026-06-12T18:30:45.123456+08:00