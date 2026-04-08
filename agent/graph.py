# from langgraph.graph import StateGraph, END
# from agent.state import  AllergenState
# from agent.nodes import scrape_node, detect_node, search_alternatives_node, validate_node

# def should_search_alternatives(state: AllergenState) -> str:
#     """
#     Conditional edge — decides where to go after detect_node.
#     If allergen found → search alternatives
#     If safe → end
#     If unknown (scraping failed) → end
#     """
#     if state["is_safe"] is None:
#         return "end"  # scraping failed, nothing to do
#     if state["is_safe"]:
#         return "end"  # safe product, no alternatives needed
#     return "search"   # allergen found, find alternatives


# def build_graph():
#     graph = StateGraph(AllergenState)

#     # Add nodes
#     graph.add_node("scrape", scrape_node)
#     graph.add_node("detect", detect_node)
#     graph.add_node("search_alternatives", search_alternatives_node)
#     graph.add_node("validate", validate_node)

#     # Add edges
#     graph.set_entry_point("scrape")
#     graph.add_edge("scrape", "detect")

#     graph.add_conditional_edges(
#         "detect",
#         should_search_alternatives,
#         {
#             "end": END,
#             "search": "search_alternatives"
#         }
#     )

#     graph.add_edge("search_alternatives", "validate")
#     graph.add_edge("validate", END)

#     return graph.compile()

# allergen_graph = build_graph()

from langgraph.graph import StateGraph, END
from agent.state import AllergenState
from agent.nodes import scrape_node, detect_node, search_alternatives_node, validate_node

def should_search_alternatives(state: AllergenState) -> str:
    if state["is_safe"] is None:
        return "end"
    if state["is_safe"]:
        return "end"
    return "search"

def build_graph():
    """Full graph — scrape + detect + search + validate"""
    graph = StateGraph(AllergenState)
    graph.add_node("scrape", scrape_node)
    graph.add_node("detect", detect_node)
    graph.add_node("search_alternatives", search_alternatives_node)
    graph.add_node("validate", validate_node)
    graph.set_entry_point("scrape")
    graph.add_edge("scrape", "detect")
    graph.add_conditional_edges(
        "detect",
        should_search_alternatives,
        {
            "end": END,
            "search": "search_alternatives"
        }
    )
    graph.add_edge("search_alternatives", "validate")
    graph.add_edge("validate", END)
    return graph.compile()

def build_phase1_graph():
    """Phase 1 — scrape + detect only, no alternatives"""
    graph = StateGraph(AllergenState)
    graph.add_node("scrape", scrape_node)
    graph.add_node("detect", detect_node)
    graph.set_entry_point("scrape")
    graph.add_edge("scrape", "detect")
    graph.add_edge("detect", END)
    return graph.compile()

def build_phase2_graph():
    """Phase 2 — search + validate alternatives only"""
    graph = StateGraph(AllergenState)
    graph.add_node("search_alternatives", search_alternatives_node)
    graph.add_node("validate", validate_node)
    graph.set_entry_point("search_alternatives")
    graph.add_edge("search_alternatives", "validate")
    graph.add_edge("validate", END)
    return graph.compile()

# All three available for import
allergen_graph = build_graph()
allergen_graph_phase1 = build_phase1_graph()
allergen_graph_phase2 = build_phase2_graph()