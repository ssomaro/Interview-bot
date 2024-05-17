
def generate_questions_prompt():
    return """
    I am sharing a resume and a job description with you.
    Your task is to generate only three interview questions that would be suitable to ask the candidate.

    Resume: {resume_text}
    Job Description: {job_desc}

    Respond in JSON format only, with an array of three questions like thiswith out any  \n or spaces between the questions:
    {{"questions": ["Question 1","Question 2","Question 3"]}}
    """

def generate_feedback_prompt():
    return """
    The following are interview responses from a candidate. Please generate a summary if the candidate is suitable for the job or not.
    Provide feedback on the responses, be specific and provide feedback on each question. Be critical and provide feedback on the responses.

    {responses}
    """
