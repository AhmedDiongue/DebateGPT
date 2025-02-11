import traceback
import datetime
import json

#Logger for Debate
class DebateLogger:
    def __init__(self, log_file="debate_logs.ndjson"):
        self.log_file = log_file
        self.init_log_file()

    def init_log_file(self):
        with open(self.log_file, "a") as f:
            f.write("")

    def current_time(self):
        return datetime.datetime.now().isoformat()
    
    def write_entry(self, entry):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_traceback(self):
        return traceback.format_exc()
    
    def log_query(self, prompt, response):
        entry = {
            "time": self.current_time(), 
            "type": "query", 
            "success": True,
            "prompt": prompt,
            "response": response
        }
        self.write_entry(entry)

    def log_error(self, prompt, error):
        entry= {
            "time": self.current_time(), 
            "type": "query", 
            "success": False, 
            "prompt": prompt, 
            "message": str(error), 
            "traceback": self.get_traceback()
        }
        self.write_entry(entry)
        