import os
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
#from openai import OpenAI
import openai
import anthropic

load_dotenv()

#신버전
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), http_client=None)
#구버전
openai.api_key = os.getenv("OPENAI_API_KEY")
anthropic_client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = Flask(__name__)

class MCPAgent:
    def __init__(self, name, role, model):
        self.name = name
        self.role = role
        self.model = model
        self.context = []

    def add_to_context(self, speaker, message):
        self.context.append([speaker, message])

    def respond(self, input_message):
        debug = []
        def log(msg):
            debug.append(msg)

        log(f"[{self.name}] 역할: {self.role}")
        log(f"[{self.name}] 모델: {self.model}")
        for idx, (sp, msg) in enumerate(self.context):
            log(f"[컨텍스트 {idx+1}] {sp}: {msg}")
        log(f"[입력 메시지] {input_message}")

        if self.model == "claude":
            prompt = f"{self.role}\n\n"
            for sp, msg in self.context:
                prompt += f"{sp}: {msg}\n"
            prompt += f"User: {input_message}"
            response =  anthropic_client.completion(
                        prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                        stop_sequences=["\n\nHuman:"],
                        model="claude-1",  # 또는 "claude-instant-1"
                        max_tokens_to_sample=500,
                        temperature=0.7
                        )
            reply = response["completion"].strip()
        else:
            messages = [{"role": "system", "content": self.role}]
            for sp, msg in self.context:
                messages.append({"role": "assistant" if sp == self.name else "user", "content": msg})
            messages.append({"role": "user", "content": input_message})
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            reply = response.choices[0].message.content.strip()

        self.add_to_context(self.name, reply)
        log(f"[응답] {reply}")
        return reply, "\n".join(debug)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mcp-turn", methods=["POST"])
def mcp_turn():
    data = request.json
    claude_agent = MCPAgent("Claude", data["claude_role"], "claude")
    gpt_agent = MCPAgent("GPT", data["gpt_role"], "gpt")
    claude_agent.context = data.get("claude_context", [])
    gpt_agent.context = data.get("gpt_context", [])
    current_message = data["current_message"]
    current_speaker = data["current_speaker"]

    if current_speaker == "claude":
        reply, debug = claude_agent.respond(current_message)
        next_speaker = "gpt"
    else:
        reply, debug = gpt_agent.respond(current_message)
        next_speaker = "claude"

    return jsonify({
        "reply": reply,
        "current_message": reply,
        "current_speaker": next_speaker,
        "claude_context": claude_agent.context,
        "gpt_context": gpt_agent.context,
        "debug_log": debug
    })

if __name__ == "__main__":
    app.run(debug=True)
