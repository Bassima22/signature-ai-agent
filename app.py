import gradio as gr
from agent import app  # This imports your compiled LangGraph
from tools import get_db_connection
import pandas as pd

# Function to handle the chat logic
def chat_with_agent(message, history):
    # Convert Gradio history format into the format LangGraph expects
    langgraph_history = []
    for turn in history:
        # history format can be [user, ai] or {"role": "user", "content": "..."}
        if isinstance(turn, list) or isinstance(turn, tuple):
            user_text, ai_text = turn
            if user_text: langgraph_history.append(("user", user_text))
            if ai_text: langgraph_history.append(("assistant", ai_text))
        elif isinstance(turn, dict):
            langgraph_history.append((turn["role"], turn["content"]))
    
    # Run the agent
    try:
        # We pass the history plus the current new message
        inputs = {"messages": langgraph_history + [("user", message)]}
        result = app.invoke(inputs, config={"recursion_limit": 25})
        
        # Get the final AI response from the message list
        final_msg = ""
        for msg in reversed(result["messages"]):
            # Look for the last message that has text and is NOT a tool call
            if hasattr(msg, "content") and msg.content and not (hasattr(msg, "tool_calls") and msg.tool_calls):
                final_msg = msg.content
                break
        return final_msg
    except Exception as e:
        return f"System Error: {str(e)}"

# Function to pull data for the "Live Shop Status" table
def get_db_status():
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT model, detailing_status, last_finish_date FROM vehicles", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame({"Status": ["Database not found or locked"]})

# Build the Gradio UI
with gr.Blocks(title="Signature Coordinator") as demo:
    gr.Markdown("# 🏎️ Signature x Sima Media AI Coordinator")
    gr.Markdown("Real-time coordination between detailing staff and media teams.")
    
    with gr.Row():
        # Left side: The Chat
        with gr.Column(scale=2):
            gr.ChatInterface(
                fn=chat_with_agent,
                examples=["What cars are in the shop?", "What are the outdoor shoot rules?", "Schedule the BMW for the Showroom at 3 PM."],
            )
        
        # Right side: The Database View
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Live Shop Status")
            db_view = gr.DataFrame(value=get_db_status, every=2) # Auto-refresh every 2 seconds
            gr.Button("Manual Refresh").click(fn=get_db_status, outputs=db_view)

if __name__ == "__main__":
    # server_name="0.0.0.0" is essential for the Docker step
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)