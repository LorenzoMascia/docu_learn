import openai
import json
from typing import Dict, List, Any
import logging

class LLMGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate_quiz(self, content: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate quiz questions based on content and analysis"""
        num_questions = analysis.get('suggested_quiz_count', 5)
        difficulty = analysis.get('difficulty_level', 'Intermediate')
        key_concepts = analysis.get('key_concepts', [])
        
        concepts_text = ", ".join([c['concept'] for c in key_concepts[:5]])
        
        prompt = f"""
        Generate {num_questions} multiple choice questions from the following text.
        Difficulty level: {difficulty}
        Focus on these key concepts: {concepts_text}
        
        Text:
        {content[:2000]}  # Limit content to avoid token limits
        
        Requirements:
        1. Each question should test understanding, not just memorization
        2. Include 4 options (A, B, C, D) with only one correct answer
        3. Make incorrect options plausible but clearly wrong
        4. Vary question types (factual, conceptual, application)
        
        Format as JSON array:
        [
            {{
                "question": "Question text here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Why this answer is correct",
                "difficulty": "Basic|Intermediate|Advanced",
                "concept": "Main concept being tested"
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            quiz_data = json.loads(response.choices[0].message.content)
            return self._validate_quiz(quiz_data)
            
        except Exception as e:
            logging.error(f"Quiz generation error: {e}")
            return self._generate_fallback_quiz(content)
    
    def generate_summary(self, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive summary"""
        key_concepts = analysis.get('key_concepts', [])
        topics = analysis.get('topics', [])
        
        prompt = f"""
        Create a comprehensive summary of this educational content.
        
        Key concepts to highlight: {[c['concept'] for c in key_concepts[:3]]}
        Subject areas: {topics}
        
        Content:
        {content[:3000]}
        
        Provide:
        1. A brief overview (2-3 sentences)
        2. Main points (bullet list)
        3. Key takeaways (3-5 important concepts)
        
        Format as JSON:
        {{
            "overview": "Brief summary here",
            "main_points": ["Point 1", "Point 2", ...],
            "key_takeaways": ["Takeaway 1", "Takeaway 2", ...],
            "complexity_level": "Basic|Intermediate|Advanced"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing educational content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Summary generation error: {e}")
            return self._generate_fallback_summary(content)
    
    def generate_mindmap_data(self, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mind map structure"""
        key_concepts = analysis.get('key_concepts', [])
        sections = analysis.get('section_analysis', [])
        
        prompt = f"""
        Create a mind map structure for this educational content.
        
        Key concepts: {[c['concept'] for c in key_concepts[:8]]}
        Sections: {[s['title'] for s in sections[:5]]}
        
        Content excerpt:
        {content[:2000]}
        
        Create a hierarchical structure with:
        - Central topic
        - Main branches (3-6 major concepts)
        - Sub-branches (supporting details)
        
        Format as JSON:
        {{
            "central_topic": "Main subject",
            "branches": [
                {{
                    "name": "Branch name",
                    "children": [
                        {{"name": "Sub-concept 1"}},
                        {{"name": "Sub-concept 2"}}
                    ]
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational mind maps."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Mind map generation error: {e}")
            return self._generate_fallback_mindmap(key_concepts)
    
    def _validate_quiz(self, quiz_data: List[Dict]) -> List[Dict[str, Any]]:
        """Validate and clean quiz data"""
        validated_quiz = []
        
        for q in quiz_data:
            if (isinstance(q.get('question'), str) and
                isinstance(q.get('options'), list) and
                len(q.get('options', [])) == 4 and
                isinstance(q.get('correct_answer'), int) and
                0 <= q.get('correct_answer', -1) < 4):
                
                validated_quiz.append({
                    'question': q['question'],
                    'options': q['options'],
                    'correct_answer': q['correct_answer'],
                    'explanation': q.get('explanation', ''),
                    'difficulty': q.get('difficulty', 'Intermediate'),
                    'concept': q.get('concept', 'General')
                })
        
        return validated_quiz
    
    def _generate_fallback_quiz(self, content: str) -> List[Dict[str, Any]]:
        """Generate basic quiz if LLM fails"""
        return [{
            'question': 'What is the main topic of this document?',
            'options': ['Topic A', 'Topic B', 'Topic C', 'Topic D'],
            'correct_answer': 0,
            'explanation': 'Fallback question generated due to processing error.',
            'difficulty': 'Basic',
            'concept': 'General'
        }]
    
    def _generate_fallback_summary(self, content: str) -> Dict[str, Any]:
        """Generate basic summary if LLM fails"""
        words = content.split()
        return {
            'overview': f'This document contains approximately {len(words)} words of educational content.',
            'main_points': ['Content processing in progress'],
            'key_takeaways': ['Please try again later'],
            'complexity_level': 'Unknown'
        }
    
    def _generate_fallback_mindmap(self, key_concepts: List[Dict]) -> Dict[str, Any]:
        """Generate basic mindmap if LLM fails"""
        return {
            'central_topic': 'Document Content',
            'branches': [
                {
                    'name': concept.get('concept', 'Concept'),
                    'children': [{'name': 'Details'}]
                } for concept in key_concepts[:3]
            ]
        }