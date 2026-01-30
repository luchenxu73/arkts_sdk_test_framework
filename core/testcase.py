"""Test case model"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.models import TestCaseConfig


class TestCase:
    
    STATUS_PENDING = 'PENDING'      # Pending execution
    STATUS_RUNNING = 'RUNNING'      # Running
    STATUS_PASSED = 'PASSED'        # Passed
    STATUS_FAILED = 'FAILED'        # Failed
    STATUS_SKIPPED = 'SKIPPED'      # Skipped
    
    def __init__(self, config: TestCaseConfig):

        self.config = config
        self.name = config.name
        self.path = config.path
        self.commands = config.commands
        self.tags = config.tags
        self.dependencies = config.dependencies
        self.timeout = config.timeout
        
        self.status = self.STATUS_PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.duration: float = 0.0
        self.output: str = ""
        self.error_message: str = ""
        self.executed_commands: List[Dict[str, Any]] = []
    
    def start(self):
        self.status = self.STATUS_RUNNING
        self.start_time = datetime.now()
    
    def finish(self, success: bool, error_message: str = ""):
        self.end_time = datetime.now()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
        
        if success:
            self.status = self.STATUS_PASSED
        else:
            self.status = self.STATUS_FAILED
            self.error_message = error_message
    
    def skip(self, reason: str = ""):
        self.status = self.STATUS_SKIPPED
        self.error_message = reason
    
    def add_command_result(self, command: str, success: bool, 
                          output: str, exit_code: int, duration: float):

        self.executed_commands.append({
            'command': command,
            'success': success,
            'output': output,
            'exit_code': exit_code,
            'duration': duration
        })
        
        if output:
            self.output += f"\n{'='*60}\n"
            self.output += f"Command: {command}\n"
            self.output += f"{'='*60}\n"
            self.output += output
    
    def get_summary(self) -> Dict[str, Any]:

        return {
            'name': self.name,
            'status': self.status,
            'duration': self.duration,
            'commands_count': len(self.commands),
            'executed_count': len(self.executed_commands),
            'error_message': self.error_message,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    def __str__(self) -> str:
        return f"TestCase(name='{self.name}', status='{self.status}')"
    
    def __repr__(self) -> str:
        return self.__str__()
