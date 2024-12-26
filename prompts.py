system_message = """
    You are an intelligent assistant specializing in creating personalized learning plans. 
    Your primary objective is to design structured, topic-based calendars for users who want to learn a new subject.
    The plans must balance clarity, progression, and practical application.
    You adapt to the user's preferred duration and any provided learning resources to create actionable, detailed schedules. 
    Ensure the final output is formatted as a Python `tasks` array that is clean, logical, and ready to implement.
"""



def generate_prompt(subject, link, total_days, minutes):
    prompt = f"""
        I need a custom learning plan designed for a user based on the following inputs: 
        - **Subject**: {subject}
        - **Maximum number of days**: {total_days}
        - Daily study amount: {minutes} minutes
        - **Learning resource link** (optional): {link}

        Your task:
        1. Create a structured learning plan in Python formatted as a `tasks` array. Each entry in the array should be a tuple containing:
        - A topic or learning goal for the day.
        - A list of activities related to that topic.
        2. Distribute the content evenly across the given days, ensuring logical progression from foundational to advanced topics.
        3. Incorporate periodic review and practice sessions for knowledge consolidation.
        4. If a link is provided, use the materials in the resource to inform the activities and topics.
        5. Keep the activities concise, actionable, and specific while staying within the time constraints..

        **Output example**:
        ```python
        tasks = [
            ("Topic Title 1", ["Activity 1 for Topic Title 1.", "Activity 2 for Topic Title 1."]),
            ("Topic Title 2", ["Activity 1 for Topic Title 2.", "Activity 2 for Topic Title 2."]),
            # Additional topics as needed.
        ]

        """
        
    return prompt
    
