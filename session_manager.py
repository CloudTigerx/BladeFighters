#!/usr/bin/env python3
"""
Session Manager for Blade Fighters Refactoring
Manages context, progress tracking, and session state during refactoring
"""

import json
import os
import time
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class RefactoringSession:
    """Manages a refactoring session with context and progress tracking."""
    
    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"session_{int(time.time())}"
        self.session_file = f"refactoring_sessions/{self.session_name}.json"
        self.start_time = datetime.datetime.now()
        self.current_phase = "planning"
        self.current_task = "initialization"
        self.completed_tasks = []
        self.failed_tasks = []
        self.notes = []
        self.context = {}
        
        # Ensure sessions directory exists
        os.makedirs("refactoring_sessions", exist_ok=True)
        
        # Load existing session if it exists
        self.load_session()
    
    def load_session(self):
        """Load existing session data if available."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    self.__dict__.update(data)
                    print(f"📂 Loaded existing session: {self.session_name}")
            except Exception as e:
                print(f"⚠️  Could not load session: {e}")
    
    def save_session(self):
        """Save current session state."""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.__dict__, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Could not save session: {e}")
    
    def update_context(self, key: str, value: Any):
        """Update session context with new information."""
        self.context[key] = value
        self.save_session()
    
    def add_note(self, note: str, category: str = "general"):
        """Add a note to the session."""
        timestamp = datetime.datetime.now().isoformat()
        self.notes.append({
            'timestamp': timestamp,
            'category': category,
            'note': note
        })
        self.save_session()
    
    def complete_task(self, task_name: str, details: str = ""):
        """Mark a task as completed."""
        timestamp = datetime.datetime.now().isoformat()
        self.completed_tasks.append({
            'task': task_name,
            'timestamp': timestamp,
            'details': details
        })
        self.save_session()
        print(f"✅ Completed: {task_name}")
    
    def fail_task(self, task_name: str, error: str):
        """Mark a task as failed."""
        timestamp = datetime.datetime.now().isoformat()
        self.failed_tasks.append({
            'task': task_name,
            'timestamp': timestamp,
            'error': error
        })
        self.save_session()
        print(f"❌ Failed: {task_name} - {error}")
    
    def set_phase(self, phase: str):
        """Set the current refactoring phase."""
        self.current_phase = phase
        self.save_session()
        print(f"🔄 Phase: {phase}")
    
    def set_task(self, task: str):
        """Set the current task."""
        self.current_task = task
        self.save_session()
        print(f"📋 Task: {task}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        duration = datetime.datetime.now() - self.start_time
        
        return {
            'session_name': self.session_name,
            'start_time': self.start_time.isoformat(),
            'duration': str(duration),
            'current_phase': self.current_phase,
            'current_task': self.current_task,
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'total_notes': len(self.notes)
        }
    
    def print_summary(self):
        """Print a summary of the current session."""
        summary = self.get_session_summary()
        
        print("\n" + "="*60)
        print(f"📊 SESSION SUMMARY: {summary['session_name']}")
        print("="*60)
        
        print(f"⏱️  Duration: {summary['duration']}")
        print(f"🔄 Current Phase: {summary['current_phase']}")
        print(f"📋 Current Task: {summary['current_task']}")
        print(f"✅ Completed Tasks: {summary['completed_tasks']}")
        print(f"❌ Failed Tasks: {summary['failed_tasks']}")
        print(f"📝 Notes: {summary['total_notes']}")
        
        if self.completed_tasks:
            print(f"\n✅ RECENT COMPLETED TASKS:")
            for task in self.completed_tasks[-3:]:  # Last 3
                print(f"   {task['task']} ({task['timestamp']})")
        
        if self.failed_tasks:
            print(f"\n❌ RECENT FAILED TASKS:")
            for task in self.failed_tasks[-3:]:  # Last 3
                print(f"   {task['task']} - {task['error']}")
        
        if self.notes:
            print(f"\n📝 RECENT NOTES:")
            for note in self.notes[-3:]:  # Last 3
                print(f"   [{note['category']}] {note['note']}")


class ContextManager:
    """Manages context information across sessions."""
    
    def __init__(self):
        self.context_file = "refactoring_context.json"
        self.context = self.load_context()
    
    def load_context(self) -> Dict[str, Any]:
        """Load context from file."""
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load context: {e}")
        
        return {
            'project_overview': {},
            'architecture_state': {},
            'known_issues': [],
            'decisions': [],
            'progress': {},
            'resources': []
        }
    
    def save_context(self):
        """Save context to file."""
        try:
            with open(self.context_file, 'w') as f:
                json.dump(self.context, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Could not save context: {e}")
    
    def update_project_overview(self, overview: Dict[str, Any]):
        """Update project overview information."""
        self.context['project_overview'].update(overview)
        self.save_context()
    
    def update_architecture_state(self, state: Dict[str, Any]):
        """Update current architecture state."""
        self.context['architecture_state'].update(state)
        self.save_context()
    
    def add_known_issue(self, issue: str, severity: str = "medium"):
        """Add a known issue to the context."""
        timestamp = datetime.datetime.now().isoformat()
        self.context['known_issues'].append({
            'issue': issue,
            'severity': severity,
            'timestamp': timestamp,
            'resolved': False
        })
        self.save_context()
    
    def resolve_issue(self, issue_index: int):
        """Mark an issue as resolved."""
        if 0 <= issue_index < len(self.context['known_issues']):
            self.context['known_issues'][issue_index]['resolved'] = True
            self.save_context()
    
    def add_decision(self, decision: str, rationale: str = ""):
        """Add a decision to the context."""
        timestamp = datetime.datetime.now().isoformat()
        self.context['decisions'].append({
            'decision': decision,
            'rationale': rationale,
            'timestamp': timestamp
        })
        self.save_context()
    
    def update_progress(self, phase: str, progress: Dict[str, Any]):
        """Update progress for a specific phase."""
        self.context['progress'][phase] = progress
        self.save_context()
    
    def add_resource(self, resource: str, description: str = ""):
        """Add a resource reference."""
        self.context['resources'].append({
            'resource': resource,
            'description': description,
            'added': datetime.datetime.now().isoformat()
        })
        self.save_context()
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context."""
        return {
            'total_issues': len(self.context['known_issues']),
            'resolved_issues': len([i for i in self.context['known_issues'] if i['resolved']]),
            'total_decisions': len(self.context['decisions']),
            'total_resources': len(self.context['resources']),
            'phases_with_progress': len(self.context['progress'])
        }
    
    def print_context_summary(self):
        """Print a summary of the current context."""
        summary = self.get_context_summary()
        
        print("\n" + "="*60)
        print("📚 CONTEXT SUMMARY")
        print("="*60)
        
        print(f"🐛 Issues: {summary['resolved_issues']}/{summary['total_issues']} resolved")
        print(f"🤔 Decisions: {summary['total_decisions']}")
        print(f"📚 Resources: {summary['total_resources']}")
        print(f"📈 Progress Tracking: {summary['phases_with_progress']} phases")
        
        # Show unresolved issues
        unresolved = [i for i in self.context['known_issues'] if not i['resolved']]
        if unresolved:
            print(f"\n⚠️  UNRESOLVED ISSUES:")
            for i, issue in enumerate(unresolved[:3]):  # Show first 3
                print(f"   {i+1}. [{issue['severity']}] {issue['issue']}")
        
        # Show recent decisions
        if self.context['decisions']:
            print(f"\n🤔 RECENT DECISIONS:")
            for decision in self.context['decisions'][-3:]:  # Last 3
                print(f"   {decision['decision']}")


class SessionManager:
    """Main session manager that coordinates sessions and context."""
    
    def __init__(self):
        self.context_manager = ContextManager()
        self.current_session = None
    
    def start_session(self, session_name: str = None) -> RefactoringSession:
        """Start a new refactoring session."""
        self.current_session = RefactoringSession(session_name)
        
        # Add session start note
        self.current_session.add_note("Session started", "session")
        
        print(f"🚀 Started new session: {self.current_session.session_name}")
        return self.current_session
    
    def continue_session(self, session_name: str) -> RefactoringSession:
        """Continue an existing session."""
        session_file = f"refactoring_sessions/{session_name}.json"
        
        if os.path.exists(session_file):
            self.current_session = RefactoringSession(session_name)
            self.current_session.add_note("Session resumed", "session")
            print(f"📂 Continued session: {session_name}")
            return self.current_session
        else:
            print(f"❌ Session not found: {session_name}")
            return self.start_session(session_name)
    
    def list_sessions(self) -> List[str]:
        """List all available sessions."""
        sessions_dir = Path("refactoring_sessions")
        if not sessions_dir.exists():
            return []
        
        sessions = []
        for session_file in sessions_dir.glob("*.json"):
            sessions.append(session_file.stem)
        
        return sorted(sessions)
    
    def print_session_list(self):
        """Print a list of all available sessions."""
        sessions = self.list_sessions()
        
        if not sessions:
            print("📂 No sessions found.")
            return
        
        print("\n📂 AVAILABLE SESSIONS:")
        for i, session_name in enumerate(sessions, 1):
            print(f"   {i}. {session_name}")
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current state of the refactoring project."""
        state = {
            'context': self.context_manager.get_context_summary(),
            'current_session': None
        }
        
        if self.current_session:
            state['current_session'] = self.current_session.get_session_summary()
        
        return state
    
    def print_current_state(self):
        """Print the current state of the refactoring project."""
        print("\n" + "="*60)
        print("🎯 CURRENT REFACTORING STATE")
        print("="*60)
        
        # Print context summary
        self.context_manager.print_context_summary()
        
        # Print session summary if active
        if self.current_session:
            self.current_session.print_summary()


def main():
    """Main function for session management."""
    manager = SessionManager()
    
    print("🎮 Blade Fighters Refactoring Session Manager")
    print("="*50)
    
    # Show available sessions
    manager.print_session_list()
    
    # Start a new session
    session = manager.start_session()
    
    # Initialize context with project information
    manager.context_manager.update_project_overview({
        'name': 'Blade Fighters',
        'type': 'Puzzle Fighting Game',
        'current_state': 'Monolithic',
        'target_state': 'Modular',
        'main_goal': 'Extract core engine and separate modules'
    })
    
    # Add initial context
    manager.context_manager.add_decision(
        "Use incremental refactoring approach",
        "To minimize risk and maintain functionality during transformation"
    )
    
    manager.context_manager.add_known_issue(
        "Attack system tightly coupled to grid",
        "high"
    )
    
    manager.context_manager.add_known_issue(
        "Alpha value clamping implemented",
        "low"
    )
    
    # Print current state
    manager.print_current_state()
    
    print("\n✅ Session manager initialized and ready!")


if __name__ == "__main__":
    main() 