from dotenv import load_dotenv
load_dotenv()  
import os
from typing import Annotated, TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage
from tools import (
    get_vehicle_status, 
    list_all_vehicles,
    analyze_shoot_request, 
    confirm_booking, 
    get_business_rules, 
    create_daily_production_report,
    log_agent_thought
)

# 1. API KEY
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# 2. Tools & Model
tools = [get_vehicle_status, list_all_vehicles, analyze_shoot_request, confirm_booking, get_business_rules, create_daily_production_report]
# We use temperature 0 to make the model more predictable and less likely to loop
model = ChatGroq(model="llama-3.1-8b-instant", temperature=0).bind_tools(tools)

# 3. State Definition
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 4. Logic Node
def call_model(state: AgentState):
    # This is the "Brain" instruction. It must be present in every turn.
    sys_msg = SystemMessage(content=(
        "You are the Signature Coordinator. "
        "When a tool gives you information, summarize it for the user and STOP. "
        "Do not call the same tool twice. If you have the answer, just give it."
        "When you use a tool, do NOT mention the tool's name to the user. "
        "Just provide the information directly in a clean list or sentence. "
        "Example: Instead of saying 'The tool returned...', just say 'We have the following cars...'"
    ))
    
    # We always put the system message at the start
    messages = [sys_msg] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

# 5. The Workflow
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    # Only continue if the AI specifically asked to use a tool
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", ToolNode(tools))
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
workflow.add_edge("action", "agent")
app = workflow.compile()

# --- THE CHAT LOOP ---
if __name__ == "__main__":
    print("\n" + "="*40)
    print(" SIGNATURE COORDINATOR: LOOP-FIX ACTIVE")
    print("="*40)
    
    # We keep history here
    chat_history = []

    while True:
        user_input = input("\nCoordinator (User): ")
        if user_input.lower() in ["exit", "quit"]: break
        
        # Add only the new user message to history
        new_user_msg = HumanMessage(content=user_input)
        
        try:
            # We run the graph
            # Note: We pass the history which will be updated automatically
            result = app.invoke({"messages": chat_history + [new_user_msg]}, config={"recursion_limit": 10})
            
            # Update history with the full result
            chat_history = result["messages"]
            
            # Find the very last text response from the AI
            final_text = ""
            for msg in reversed(chat_history):
                if msg.content and not (hasattr(msg, "tool_calls") and msg.tool_calls):
                    final_text = msg.content
                    break
            
            print(f"Agent: {final_text}")
            log_agent_thought(user_input, "Final response generated", "Llama-8B", final_text)
            
        except Exception as e:
            print(f"Agent Error: {e}")
            print("Hint: If it says recursion limit, try restarting the script.")