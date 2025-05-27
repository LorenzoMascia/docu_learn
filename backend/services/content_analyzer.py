import spacy
from collections import Counter
from typing import Dict, List, Any
import re

class ContentAnalyzer:
    def __init__(self):
        try:
            # Load English model (download with: python -m spacy download en_core_web_sm)
            self.nlp = spacy.load("en_core_web_sm")
        except IOError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            raise
    
    def analyze(self, parsed_document: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document content and extract key information"""
        text = parsed_document['text']
        sections = parsed_document.get('sections', [])
        
        return {
            'key_concepts': self._extract_key_concepts(text),
            'difficulty_level': self._assess_difficulty(text),
            'topics': self._identify_topics(text),
            'section_analysis': self._analyze_sections(sections),
            'readability_score': self._calculate_readability(text),
            'suggested_quiz_count': self._suggest_quiz_count(text)
        }
    
    def _extract_key_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Extract important concepts using NLP"""
        doc = self.nlp(text)
        
        # Extract named entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Extract noun phrases
        noun_phrases = [chunk.text for chunk in doc.noun_chunks 
                       if len(chunk.text.split()) <= 3]
        
        # Count frequency and filter
        concept_counts = Counter(noun_phrases)
        key_concepts = []
        
        for concept, count in concept_counts.most_common(20):
            if count > 1 and len(concept) > 3:
                key_concepts.append({
                    'concept': concept,
                    'frequency': count,
                    'importance': min(count * 0.1, 1.0)  # Normalized importance
                })
        
        return key_concepts
    
    def _assess_difficulty(self, text: str) -> str:
        """Assess text difficulty level"""
        doc = self.nlp(text)
        
        # Simple metrics
        avg_sentence_length = len([token for token in doc if not token.is_punct]) / len(list(doc.sents))
        complex_words = len([token for token in doc if len(token.text) > 6 and token.is_alpha])
        total_words = len([token for token in doc if token.is_alpha])
        
        complexity_ratio = complex_words / total_words if total_words > 0 else 0
        
        if avg_sentence_length > 20 or complexity_ratio > 0.3:
            return "Advanced"
        elif avg_sentence_length > 15 or complexity_ratio > 0.2:
            return "Intermediate"
        else:
            return "Basic"
    
    def _identify_topics(self, text: str) -> List[str]:
        """Identify main topics/subjects"""
        doc = self.nlp(text)
        
        # Look for academic/scientific terms
        topics = []
        topic_keywords = {
            'biology': ['cell', 'organism', 'evolution', 'genetics', 'ecosystem'],
            'chemistry': ['molecule', 'atom', 'reaction', 'compound', 'element'],
            'physics': ['energy', 'force', 'motion', 'wave', 'particle'],
            'mathematics': ['equation', 'theorem', 'proof', 'function', 'variable'],
            'history': ['century', 'war', 'empire', 'revolution', 'civilization'],
            'literature': ['author', 'novel', 'poem', 'character', 'theme']
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if sum(text_lower.count(keyword) for keyword in keywords) > 3:
                topics.append(topic.title())
        
        return topics
    
    def _analyze_sections(self, sections: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Analyze individual sections"""
        analyzed_sections = []
        
        for section in sections:
            content = section.get('content', '')
            if len(content.strip()) < 50:  # Skip very short sections
                continue
                
            analyzed_sections.append({
                'title': section.get('title', 'Untitled'),
                'word_count': len(content.split()),
                'key_points': self._extract_key_points(content),
                'quiz_potential': len(content.split()) // 50  # Rough estimate
            })
        
        return analyzed_sections
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text"""
        sentences = re.split(r'[.!?]+', text)
        
        # Simple scoring based on sentence characteristics
        key_sentences = []
        for sentence in sentences[:10]:  # Limit to first 10 sentences
            sentence = sentence.strip()
            if (len(sentence) > 20 and 
                len(sentence) < 200 and
                not sentence.lower().startswith(('however', 'therefore', 'moreover'))):
                key_sentences.append(sentence)
        
        return key_sentences[:5]  # Return top 5
    
    def _calculate_readability(self, text: str) -> float:
        """Simple readability score (0-1, higher = more readable)"""
        if not text:
            return 0.0
            
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        avg_sentence_length = words / sentences if sentences > 0 else words
        
        # Inverse relationship: shorter sentences = higher readability
        readability = max(0, min(1, 1 - (avg_sentence_length - 10) / 20))
        return round(readability, 2)
    
    def _suggest_quiz_count(self, text: str) -> int:
        """Suggest number of quiz questions based on content length"""
        word_count = len(text.split())
        
        if word_count < 500:
            return 3
        elif word_count < 1500:
            return 5
        elif word_count < 3000:
            return 8
        else:
            return 10