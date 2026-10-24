from mcp.server.fastmcp import FastMCP
import sqlite3
import requests
import os
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("todo-server")

# 初始化数据库
def init_db():
    conn = sqlite3.connect("todo.db")
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        plan_time TEXT,
        create_time DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# 工具1：新增待办
@mcp.tool()
def add_todo(content: str, plan_time: str) -> str:
    """
    添加一条学生待办任务
    :param content: 任务内容，例如：高数作业
    :param plan_time: 计划执行时间，例如：2026-10-25 19:00
    """
    conn = sqlite3.connect("todo.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO todos(content, plan_time) VALUES (?, ?)", (content, plan_time))
    conn.commit()
    conn.close()
    return f"✅ 成功添加待办：{content}，计划时间：{plan_time}"

# 工具2：查询全部待办
@mcp.tool()
def query_todo() -> str:
    """查询所有已经保存的待办日程"""
    conn = sqlite3.connect("todo.db")
    cur = conn.cursor()
    rows = cur.execute("SELECT id, content, plan_time FROM todos ORDER BY plan_time").fetchall()
    conn.close()
    if not rows:
        return "📋 当前没有待办任务"
    res = "📋 待办列表：\n"
    for r in rows:
        res += f"{r[0]}. [{r[2]}] {r[1]}\n"
    return res

# 工具3：获取天气
@mcp.tool()
def get_weather(location: str = "guangzhou") -> str:
    """
    获取指定城市实时天气，用来辅助安排日程
    :param location: 城市编码，默认guangzhou
    """
    key = os.getenv("WEATHER_API_KEY")
    url = f"https://devapi.qweather.com/v7/weather/now?location={location}&key={key}"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    if data.get("code") != "200":
        return "天气查询失败"
    now = data["now"]
    return f"🌤 广州当前天气：{now['text']}，温度：{now['temp']}℃"

if __name__ == "__main__":
    mcp.run()
