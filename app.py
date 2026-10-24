from flask import Flask, render_template, request, jsonify
import asyncio
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("DOUBAO_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

async def call_mcp(prompt: str):
    cmd = ["python", "mcp_server.py"]
    async with stdio_client(cmd) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_list = [
                {
                    "type":"function",
                    "function":{
                        "name":t.name,
                        "description":t.description,
                        "parameters":t.inputSchema
                    }
                }
                for t in tools.tools
            ]
            resp = client.chat.completions.create(
                model=os.getenv("DOUBAO_MODEL_ID"),
                messages=[{"role":"user","content":prompt}],
                tools=tool_list
            )
            msg = resp.choices[0].message
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    res = await session.call_tool(tc.function.name, arguments=eval(tc.function.arguments))
                    return res.content[0].text
            return msg.content

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    txt = request.json["msg"]
    ret = asyncio.run(call_mcp(txt))
    return jsonify({"reply":ret})

@app.route("/todos")
def get_todos():
    ret = asyncio.run(call_mcp("查询全部待办"))
    arr = []
    lines = ret.splitlines()[1:]
    for line in lines:
        if line.strip():
            sp = line.split("] ")
            if len(sp)==2:
                time_part = sp[0].strip("[")
                content = sp[1]
                arr.append({"plan_time":time_part, "content":content})
    return jsonify(arr)

if __name__ == "__main__":
    app.run(debug=True)
