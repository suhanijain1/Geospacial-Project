from langgraph.graph import StateGraph

def inc(state):
    # state is a dict
    x = state.get("x", 0)
    state["x"] = x + 1
    return state

g = StateGraph(dict)
g.add_node("inc", inc)
g.set_entry_point("inc")
compiled = g.compile()
print(compiled.invoke({"x": 1}))   # expected {'x': 2}