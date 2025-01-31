import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.fundamentals import fundamentals_agent
from agents.portfolio_manager import portfolio_management_agent
from agents.technicals import technical_analyst_agent
from agents.risk_manager import risk_management_agent
from agents.sentiment import sentiment_agent
from agents.warren_buffett import warren_buffett_agent
from agents.valuation import valuation_agent
from graph.state import AgentState
from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage
from utils.progress import progress

def create_workflow(selected_analysts=None):
    """Create the workflow with selected analysts."""
    workflow = StateGraph(AgentState)
    workflow.add_node("start_node", start)

    # Default to all analysts if none selected
    if selected_analysts is None:
        selected_analysts = ["technical_analyst", "fundamentals_analyst", "sentiment_analyst", "valuation_analyst"]

    # Dictionary of all available analysts
    analyst_nodes = {
        "technical_analyst": ("technical_analyst_agent", technical_analyst_agent),
        "fundamentals_analyst": ("fundamentals_agent", fundamentals_agent),
        "sentiment_analyst": ("sentiment_agent", sentiment_agent),
        "valuation_analyst": ("valuation_agent", valuation_agent),
        "warren_buffett": ("warren_buffett_agent", warren_buffett_agent),
    }

    # Add selected analyst nodes
    for analyst_key in selected_analysts:
        node_name, node_func = analyst_nodes[analyst_key]
        workflow.add_node(node_name, node_func)
        workflow.add_edge("start_node", node_name)

    # Always add risk and portfolio management
    workflow.add_node("risk_management_agent", risk_management_agent)
    workflow.add_node("portfolio_management_agent", portfolio_management_agent)

    # Connect selected analysts to risk management
    for analyst_key in selected_analysts:
        node_name = analyst_nodes[analyst_key][0]
        workflow.add_edge(node_name, "risk_management_agent")

    workflow.add_edge("risk_management_agent", "portfolio_management_agent")
    workflow.add_edge("portfolio_management_agent", END)

    workflow.set_entry_point("start_node")
    return workflow

def start(state: AgentState):
    """Initialize the workflow with the input message."""
    return state

def run_hedge_fund(tickers, start_date, end_date, portfolio, show_reasoning=False,
                  selected_analysts=None, model_name="gpt-4-turbo-preview", model_provider="openai"):
    """Run the hedge fund analysis."""
    progress.start()

    try:
        workflow = create_workflow(selected_analysts) if selected_analysts else create_workflow()
        agent = workflow.compile()

        final_state = agent.invoke({
            "messages": [HumanMessage(content="Make trading decisions based on the provided data.")],
            "data": {
                "tickers": tickers,
                "portfolio": portfolio,
                "start_date": start_date,
                "end_date": end_date,
                "analyst_signals": {},
            },
            "metadata": {
                "show_reasoning": show_reasoning,
                "model_name": model_name,
                "model_provider": model_provider,
                "temperature": 0.7,
                "max_tokens": 1500,
            },
        })

        return {
            "decisions": parse_hedge_fund_response(final_state["messages"][-1].content),
            "analyst_signals": final_state["data"]["analyst_signals"],
        }
    finally:
        progress.stop()

def parse_hedge_fund_response(response):
    """Parse the hedge fund response."""
    import json
    try:
        return json.loads(response)
    except:
        print(f"Error parsing response: {response}")
        return None
