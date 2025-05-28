def process_response(response):
    """
    Process the response from the agent.
    
    Args:
        response (str): The response string to be processed.
        
    Returns:
        str: The processed response.
    """
    if not response:
        return "No response received."
    
    # Here you can add any specific processing logic you need
    # For example, cleaning up the response, formatting, etc.
    
    # For now, we will just return the response as is
    return response.strip()