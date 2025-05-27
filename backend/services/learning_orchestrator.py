from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

class LearningOrchestrator:
    def __init__(self, db_service, srs_service, progress_tracker):
        self.db = db_service
        self.srs = srs_service
        self.progress = progress_tracker
    
    def create_learning_session(self, user_id: str, document_id: str, 
                              parsed_doc: Dict, analysis: Dict, 
                              generated_content: Dict) -> Dict[str, Any]:
        """Orchestrate the creation of a complete learning session"""
        
        try:
            # 1. Store document and analysis
            session_id = self._create_session_record(user_id, document_id)
            
            # 2. Store quiz questions
            quiz_id = self._store_quiz(session_id, generated_content.get('quiz', []))
            
            # 3. Store summary
            summary_id = self._store_summary(session_id, generated_content.get('summary', {}))
            
            # 4. Store mind map
            mindmap_id = self._store_mindmap(session_id, generated_content.get('mindmap', {}))
            
            # 5. Initialize spaced repetition schedule
            self.srs.initialize_schedule(user_id, quiz_id)
            
            # 6. Set up progress tracking
            self.progress.initialize_progress(user_id, session_id, analysis)
            
            return {
                'session_id': session_id,
                'quiz_id': quiz_id,
                'summary_id': summary_id,
                'mindmap_id': mindmap_id,
                'next_review': self.srs.get_next_review_time(user_id, quiz_id),
                'estimated_completion_time': self._estimate_completion_time(analysis)
            }
            
        except Exception as e:
            logging.error(f"Learning session creation error: {e}")
            raise
    
    def get_learning_plan(self, user_id: str) -> Dict[str, Any]:
        """Generate personalized learning plan for user"""
        
        # Get user's current progress
        progress_data = self.progress.get_user_progress(user_id)
        
        # Get items due for review
        due_reviews = self.srs.get_due_items(user_id)
        
        # Get weak areas that need reinforcement
        weak_areas = self.progress.get_weak_areas(user_id)
        
        return {
            'due_reviews': due_reviews,
            'weak_areas': weak_areas,
            'recommended_sessions': self._get_recommended_sessions(user_id, weak_areas),
            'daily_goal_progress': progress_data.get('daily_progress', 0),
            'streak': progress_data.get('streak', 0),
            'next_milestone': self._get_next_milestone(progress_data)
        }
    
    def process_quiz_attempt(self, user_id: str, quiz_id: str, 
                           answers: List[int]) -> Dict[str, Any]:
        """Process a quiz attempt and update learning state"""
        
        # Get quiz questions
        quiz_questions = self.db.get_quiz_questions(quiz_id)
        
        # Calculate score
        correct_answers = 0
        results = []
        
        for i, (question, user_answer) in enumerate(zip(quiz_questions, answers)):
            is_correct = question['correct_answer'] == user_answer
            if is_correct:
                correct_answers += 1
            
            results.append({
                'question_id': i,
                'user_answer': user_answer,
                'correct_answer': question['correct_answer'],
                'is_correct': is_correct,
                'explanation': question.get('explanation', '')
            })
        
        score = (correct_answers / len(quiz_questions)) * 100
        
        # Update spaced repetition based on performance
        self.srs.update_schedule(user_id, quiz_id, score)
        
        # Update progress tracking
        self.progress.record_attempt(user_id, quiz_id, score, results)
        
        # Determine next steps
        next_action = self._determine_next_action(score, results)
        
        return {
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': len(quiz_questions),
            'results': results,
            'next_review': self.srs.get_next_review_time(user_id, quiz_id),
            'next_action': next_action,
            'improvement_suggestions': self._generate_improvement_suggestions(results)
        }
    
    def _create_session_record(self, user_id: str, document_id: str) -> str:
        """Create learning session record in database"""
        session_data = {
            'user_id': user_id,
            'document_id': document_id,
            'created_at': datetime.now(),
            'status': 'active'
        }
        
        return self.db.create_learning_session(session_data)
    
    def _store_quiz(self, session_id: str, quiz_questions: List[Dict]) -> str:
        """Store quiz questions in database"""
        quiz_data = {
            'session_id': session_id,
            'questions': quiz_questions,
            'created_at': datetime.now()
        }
        
        return self.db.create_quiz(quiz_data)
    
    def _store_summary(self, session_id: str, summary: Dict) -> str:
        """Store summary in database"""
        summary_data = {
            'session_id': session_id,
            'content': summary,
            'created_at': datetime.now()
        }
        
        return self.db.create_summary(summary_data)
    
    def _store_mindmap(self, session_id: str, mindmap: Dict) -> str:
        """Store mind map in database"""
        mindmap_data = {
            'session_id': session_id,
            'structure': mindmap,
            'created_at': datetime.now()
        }
        
        return self.db.create_mindmap(mindmap_data)
    
    def _estimate_completion_time(self, analysis: Dict) -> int:
        """Estimate completion time in minutes"""
        base_time = 10  # Base 10 minutes
        
        difficulty = analysis.get('difficulty_level', 'Intermediate')
        quiz_count = analysis.get('suggested_quiz_count', 5)
        
        difficulty_multiplier = {
            'Basic': 1.0,
            'Intermediate': 1.3,
            'Advanced': 1.6
        }.get(difficulty, 1.0)
        
        estimated_time = int(base_time * difficulty_multiplier + quiz_count * 2)
        return estimated_time
    
    def _get_recommended_sessions(self, user_id: str, weak_areas: List[str]) -> List[Dict]:
        """Get recommended learning sessions based on weak areas"""
        # This would query for sessions that cover the weak areas
        # Simplified implementation
        return [
            {
                'session_id': 'session_123',
                'title': 'Review: ' + area,
                'estimated_time': 15,
                'priority': 'high'
            }
            for area in weak_areas[:3]
        ]
    
    def _get_next_milestone(self, progress_data: Dict) -> Dict[str, Any]:
        """Calculate next achievement milestone"""
        current_points = progress_data.get('total_points', 0)
        
        milestones = [100, 250, 500, 1000, 2500, 5000]
        
        for milestone in milestones:
            if current_points < milestone:
                return {
                    'target': milestone,
                    'current': current_points,
                    'remaining': milestone - current_points,
                    'progress_percentage': (current_points / milestone) * 100
                }
        
        return {
            'target': 'Master Level',
            'current': current_points,
            'remaining': 0,
            'progress_percentage': 100
        }
    
    def _determine_next_action(self, score: float, results: List[Dict]) -> Dict[str, str]:
        """Determine recommended next action based on performance"""
        if score >= 90:
            return {
                'action': 'advance',
                'message': 'Excellent! Ready for new material.'
            }
        elif score >= 70:
            return {
                'action': 'review_weak',
                'message': 'Good job! Review weak areas before advancing.'
            }
        else:
            return {
                'action': 'repeat',
                'message': 'Practice more with this material before advancing.'
            }
    
    def _generate_improvement_suggestions(self, results: List[Dict]) -> List[str]:
        """Generate suggestions for improvement based on quiz results"""
        suggestions = []
        incorrect_concepts = []
        
        for result in results:
            if not result['is_correct']:
                # In a real implementation, you'd map questions to concepts
                incorrect_concepts.append("concept_placeholder")
        
        if len(incorrect_concepts) > len(results) * 0.5:
            suggestions.append("Consider reviewing the fundamental concepts before retaking the quiz.")
        
        if len(incorrect_concepts) > 0:
            suggestions.append("Focus on understanding rather than memorization.")
        
        suggestions.append("Try creating your own examples for difficult concepts.")
        
        return suggestions