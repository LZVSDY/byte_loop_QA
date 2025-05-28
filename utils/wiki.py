import wikipedia


def search_wikipedia(query: str, num_results: int = 5, language = "en") -> list:
    """
    Search Wikipedia for a given query and return a list of summaries.

    Args:
        query (str): The search term to look up on Wikipedia.
        num_results (int): The number of results to return. Default is 5.

    Returns:
        list: A list of summaries for the top search results.
    """
    wikipedia.set_lang(language)  # Set the language for Wikipedia search
    
    try:
        search_results = wikipedia.search(query, results=num_results)
        print(f"Found {len(search_results)} results for '{query}': {search_results}")
        summaries = []
        for title in search_results:
            summary = wikipedia.summary(title, sentences=1)
            # print(f"Summary for '{title}': {summary}")
            summaries.append(summary)
        return summaries
    except Exception as e:
        print(f"Error searching Wikipedia: {e}")
        return []
    
if __name__ == "__main__":
    # Example usage
    query = "Python programming"
    summaries = search_wikipedia(query, num_results=3, language="en")
    for i, summary in enumerate(summaries):
        print(f"Result {i+1}: {summary}")
        
"""
Found 5 results for 'Python programming': ['Python (programming language)', 'History of Python', 'Python syntax and semantics', 'Mojo (programming language)', 'Python Conference']
Result 1: Python is a high-level, general-purpose programming language.
Result 2: The programming language Python was conceived in the late 1980s, and its implementation was started in December 1989 by Guido van Rossum at CWI in the Netherlands as a successor to ABC capable of exception handling and interfacing with the Amoeba operating system.
Result 3: The syntax of the Python programming language is the set of rules that defines how a Python program will be written and interpreted (by both the runtime system and by human readers).
Result 4: Mojo is a programming language in the Python family that is currently under development.
Result 5: The Python Conference (also called PyCon: 564 ) is the largest annual convention for the discussion and promotion of the Python programming language.
"""