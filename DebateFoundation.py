from openai import OpenAI
from DebateLogger import DebateLogger
import json
import os
from dotenv import load_dotenv

#Load the .env file
load_dotenv()

#API calling infrastructure        
class DebateFoundation: 
    def __init__(self):
        #Initialize OpenAI API and logger
        self.api = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  
        self.logger = DebateLogger()       
       
    def query_llm(self, prompt, context=None):  
        """Queries OpenAI's API and returns the response."""
        try:
            response = self.api.chat.completions.create(
                model="gpt-4", 
                messages=[{
                    "role": "user", 
                    "content": prompt
                }], 
                temperature=0.7, 
                stream=False 
            )
            self.logger.log_query(prompt, response.choices[0].message.content)
            return response.choices[0].message.content
        except Exception as e:
            self.logger.log_error(prompt, f"API Request failed: {str(e)}")
            return None 

if __name__ == "__main__": 
    test = DebateFoundation()
    prompt = "Tell me the ten hottest peppers on the planet and what regions they are native to."
    response = test.query_llm(prompt)
    print(response) 
