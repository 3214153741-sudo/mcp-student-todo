from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
MCP_URL = "http://127.0.0.1:8000/mcp"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/chat', methods=["POST"])
def chat():
    msg = request.json.get("msg", "")
    # 固定测试：把文字拆成时间+内容（你后续可以加时间解析，现在先调试通）
    plan_time = "2026-10-25 19:00"
    content = msg

    # 重点：带上 args 字典，匹配MCP服务的入参
    resp = requests.post(MCP_URL, json={
        "action": "add_todo",
        "args": {
            "plan_time": plan_time,
            "content": content
        }
    })
    data = resp.json()
    # 拿到MCP返回的完整任务列表，传给前端渲染右侧面板
    return jsonify({
        "reply": data["result"],
        "todos": data["todo_list"]
    })

@app.route("/get_todos")
def get_todos():
    # 调用MCP获取最新清单
    resp = requests.post(MCP_URL, json={"action": "list_todo"})
    data = resp.json()
    return jsonify(data["todo_list"])

if __name__ == "__main__":
    app.run(debug=True)
