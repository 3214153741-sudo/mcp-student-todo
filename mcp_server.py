from pydantic import BaseModel
from flask import Flask, request, jsonify

app = Flask(__name__)
todo_store = []

class TodoItem(BaseModel):
    plan_time: str
    content: str

def add_todo(plan_time: str, content: str) -> str:
    """添加一条待办日程"""
    item = TodoItem(plan_time=plan_time, content=content)
    todo_store.append(item)
    return f"✅ 已添加任务：[{plan_time}] {content}"

def list_todo() -> list:
    """查询全部待办清单，返回列表"""
    return [i.model_dump() for i in todo_store]

@app.route("/mcp", methods=["POST"])
def handle_mcp():
    data = request.json
    action = data.get("action")
    args = data.get("args", {})
    if action == "list_todo":
        return jsonify({
            "result": "查询成功",
            "todo_list": list_todo()
        })
    elif action == "add_todo":
        # 从 args 拿到参数
        plan_time = args.get("plan_time")
        content = args.get("content")
        msg = add_todo(plan_time, content)
        return jsonify({
            "result": msg,
            "todo_list": list_todo()
        })
    return jsonify({"result": "未知指令", "todo_list": []})

if __name__ == "__main__":
    app.run(port=8000, debug=False)
