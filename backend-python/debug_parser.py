from query_parser import QueryParser, QueryNode, Term, And, Or, Not

def print_visual_tree(node: QueryNode, prefix: str = "", is_last: bool = True):
    """
    Recursively prints the query tree in a visual format using ASCII characters.
    """
    # Determine the connector for the current node
    connector = "└── " if is_last else "├── "
    
    # Print the current node
    if isinstance(node, Term):
        print(f"{prefix}{connector}Term: '{node.word}'")
        return
    
    if isinstance(node, And):
        print(f"{prefix}{connector}AND")
        children = [node.left, node.right]
    elif isinstance(node, Or):
        print(f"{prefix}{connector}OR")
        children = [node.left, node.right]
    elif isinstance(node, Not):
        print(f"{prefix}{connector}NOT")
        children = [node.operand]
    else:
        print(f"{prefix}{connector}Unknown Node")
        return

    # Prepare prefix for children
    child_prefix = prefix + ("    " if is_last else "│   ")
    
    # Recursively print children
    for i, child in enumerate(children):
        is_last_child = (i == len(children) - 1)
        print_visual_tree(child, child_prefix, is_last_child)

def print_parse_tree(query: str):
    print(f"Query: {query}")
    parser = QueryParser(query)
    try:
        tree = parser.parse()
        print("Parse Tree:")
        print_visual_tree(tree)
    except Exception as e:
        print(f"Error parsing query: {e}")
    print("-" * 40)

if __name__ == "__main__":
    # Examples
    queries = [
        "apple banana",
        "apple AND banana",
        "apple OR banana",
        "NOT apple",
        "(apple OR banana) AND cherry",
        "machine learning OR artificial intelligence"
    ]

    for q in queries:
        print_parse_tree(q)

    while True:
        user_input = input("\nEnter a query to parse (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break
        print_parse_tree(user_input)
