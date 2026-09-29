from .ai_service import AIService
from .schemas import RoadmapData, WeekGen, TaskGen, AnalysisResult, AdjustmentSuggestion, MonthlySummary
from typing import Dict, Any

class MockAIService(AIService):
    def generate_roadmap(self, goal_info: Dict[str, Any]) -> RoadmapData:
        duration_weeks = 8 # default mock
        if 'start_date' in goal_info and 'target_date' in goal_info:
            delta = (goal_info['target_date'] - goal_info['start_date']).days
            duration_weeks = max(1, delta // 7)
            
        goal_name = goal_info.get("name", "").lower()
        category = str(goal_info.get("category", "")).lower()
        
        weeks = []
        if "python" in goal_name or "coding" in category:
            python_weeks = [
                ("Python Basics", "Variables, Data Types, Operators, Input/Output", [
                    ("Variables & Types", "Understand basic types", 2.0),
                    ("I/O Operations", "Practice print and input", 2.0),
                    ("Operators", "Learn math and logic operators", 1.0)
                ]),
                ("Control Flow", "Conditions, Loops, Practice problems", [
                    ("If Statements", "Conditionals logic", 2.0),
                    ("For and While Loops", "Iteration practice", 3.0)
                ]),
                ("Functions & Modules", "Reusable code", [
                    ("Writing Functions", "Def and returns", 2.5),
                    ("Using Modules", "Importing stdlib", 2.5)
                ]),
                ("Data Structures", "Lists, Dicts, Sets, Tuples", [
                    ("Lists & Tuples", "Sequential data", 2.0),
                    ("Dicts & Sets", "Key-value and unique items", 3.0)
                ]),
                ("File I/O & Exception Handling", "Read files and catch errors", [
                    ("Reading/Writing Files", "Open and close files", 2.0),
                    ("Try/Except", "Error handling", 3.0)
                ]),
                ("OOP", "Classes, Inheritance", [
                    ("Classes & Objects", "Defining classes", 3.0),
                    ("Inheritance", "Subclassing", 2.0)
                ]),
                ("Project 1", "Build a CLI app", [
                    ("Planning", "Design CLI app", 1.0),
                    ("Implementation", "Code the app", 4.0)
                ]),
                ("Project 2", "Build a web scraper", [
                    ("Requests & BS4", "Fetch and parse", 2.5),
                    ("Data Extraction", "Save data to CSV", 2.5)
                ])
            ]
            
            for i in range(1, duration_weeks + 1):
                idx = (i - 1) % len(python_weeks)
                title, desc, t_list = python_weeks[idx]
                
                tasks = []
                for t_i, (t_title, t_desc, t_hours) in enumerate(t_list, 1):
                    tasks.append(TaskGen(title=t_title, description=t_desc, estimated_hours=t_hours, order=t_i))
                    
                weeks.append(WeekGen(
                    week_number=i, title=title, description=desc, estimated_hours=sum(t[2] for t in t_list), tasks=tasks
                ))
                
        elif "dsa" in goal_name or "algorithm" in goal_name:
            dsa_weeks = [
                ("Arrays & Strings", "Basic arrays and string manipulations", [("Array problems", "Two pointers, sliding window", 5.0)]),
                ("Linked Lists", "Singly and doubly linked lists", [("LL operations", "Reverse, cycle detection", 5.0)]),
                ("Stacks & Queues", "LIFO and FIFO structures", [("Stack problems", "Valid parentheses, monotonic stack", 5.0)]),
                ("Trees", "Binary trees, BST", [("Tree traversals", "DFS, BFS on trees", 5.0)]),
                ("Graphs", "Graph representation", [("Graph search", "BFS, DFS, shortest path", 5.0)]),
                ("Dynamic Programming", "Memoization and tabulation", [("1D DP", "Fibonacci, climbing stairs", 5.0)])
            ]
            for i in range(1, duration_weeks + 1):
                idx = (i - 1) % len(dsa_weeks)
                title, desc, t_list = dsa_weeks[idx]
                
                tasks = []
                for t_i, (t_title, t_desc, t_hours) in enumerate(t_list, 1):
                    tasks.append(TaskGen(title=t_title, description=t_desc, estimated_hours=t_hours, order=t_i))
                    
                weeks.append(WeekGen(
                    week_number=i, title=title, description=desc, estimated_hours=sum(t[2] for t in t_list), tasks=tasks
                ))
                
        elif "fitness" in category or "bench" in goal_name:
            for i in range(1, duration_weeks + 1):
                tasks = [
                    TaskGen(title=f"Workout A (Week {i})", description="Push exercises.", estimated_hours=1.5, order=1),
                    TaskGen(title=f"Workout B (Week {i})", description="Pull exercises.", estimated_hours=1.5, order=2)
                ]
                weeks.append(WeekGen(
                    week_number=i, title=f"Progressive Overload Week {i}", description=f"Increase weight by 5%.", estimated_hours=3.0, tasks=tasks
                ))
        else:
            for i in range(1, duration_weeks + 1):
                tasks = [
                    TaskGen(title=f"Step 1 for {goal_name}", description="Initial task.", estimated_hours=2.0, order=1),
                    TaskGen(title=f"Step 2 for {goal_name}", description="Follow-up task.", estimated_hours=3.0, order=2)
                ]
                weeks.append(WeekGen(
                    week_number=i, title=f"Phase {i}", description=f"Working on goals.", estimated_hours=5.0, tasks=tasks
                ))
            
        return RoadmapData(weeks=weeks)

    def analyze_week(self, checkin_data: Dict[str, Any], goal_info: Dict[str, Any], progress: Dict[str, Any]) -> AnalysisResult:
        completion_pct = progress.get("task_completion_pct", 0)
        problems = checkin_data.get("problems_faced", "").lower()
        self_rating = checkin_data.get("self_rating", 5)
        
        summary = "You made solid progress this week."
        adjustment = "none"
        recommendations = ["Keep up the good work!"]
        
        if completion_pct < 50:
            summary = "It looks like you had a tough time completing your tasks this week."
            adjustment = "reduce"
            recommendations = ["Consider reducing the number of tasks next week.", "Focus on smaller, manageable goals."]
        elif completion_pct > 90:
            summary = "Excellent work! You crushed your tasks this week."
            recommendations = ["You're doing great, maybe take on a challenge next week!"]
            
        if self_rating < 4:
            summary += " You rated your week pretty low, take it easy."
            
        reasons = ["Time constraints"]
        if "loop" in problems:
            reasons.append("Struggled with loops concept")
            recommendations.append("Review loops documentation and do 2 extra practice problems.")
            
        return AnalysisResult(
            summary=summary,
            went_well=["Attempted tasks"],
            delayed=["Unfinished tasks"],
            reasons=reasons,
            recommendations=recommendations,
            next_week_focus=["Catch up on delayed items"],
            roadmap_adjustment_type=adjustment
        )

    def suggest_adjustment(self, analysis: Dict[str, Any], roadmap: Dict[str, Any], remaining_weeks: int) -> AdjustmentSuggestion:
        return AdjustmentSuggestion(
            adjustment_type=analysis.get("roadmap_adjustment_type", "reduce"),
            details={"action": "modify_tasks", "target": "next_week"}
        )

    def generate_monthly_summary(self, goal: Dict[str, Any], checkins: list, progress_records: list) -> MonthlySummary:
        return MonthlySummary(
            month="Current Month",
            overall_progress="Good consistent progress based on recent check-ins.",
            key_achievements=["Completed fundamentals", "Hit consistent streaks"],
            areas_for_improvement=["Time estimation for complex tasks"],
            focus_next_month="Advanced topics and building a project"
        )
