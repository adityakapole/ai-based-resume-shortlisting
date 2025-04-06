from typing import Dict, Any, List, Tuple
import sys
sys.path.append('/Users/adityakapole/Downloads/Accenture')
from utils.helpers import calculate_similarity_threshold

class ShortlistingAgent:
    """Agent for shortlisting candidates based on evaluation scores"""
    
    def __init__(self, similarity_threshold=8.0):
        """Initialize the Shortlisting Agent"""
        self.default_similarity_threshold = similarity_threshold
    
    def calculate_final_score(self, similarity_score: float, recruiting_score: float) -> float:
        """Calculate final score as average of similarity and recruiting scores"""
        if similarity_score is None:
            return recruiting_score
        if recruiting_score is None:
            return similarity_score
        
        return (similarity_score + recruiting_score) / 2
    
    def should_shortlist(self, similarity_score: float, recruiting_score: float = None, job_title: str = None) -> Tuple[bool, str]:
        """Determine if a candidate should be shortlisted based on scores"""
        # Calculate threshold based on job title if provided
        if job_title:
            threshold = calculate_similarity_threshold(job_title)
        else:
            threshold = self.default_similarity_threshold
        
        # Early rejection based on similarity score
        if similarity_score < threshold:
            return False, f"Similarity score ({similarity_score:.1f}) below threshold ({threshold:.1f})"
        
        # If we have a recruiting score, calculate final score
        if recruiting_score is not None:
            final_score = self.calculate_final_score(similarity_score, recruiting_score)
            if final_score < threshold:
                return False, f"Final score ({final_score:.1f}) below threshold ({threshold:.1f})"
            return True, f"Final score ({final_score:.1f}) meets or exceeds threshold ({threshold:.1f})"
        
        # If only similarity score is available
        return True, f"Similarity score ({similarity_score:.1f}) meets or exceeds threshold ({threshold:.1f})"
    
    def shortlist_candidates(self, candidates: List[Dict[str, Any]], job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Shortlist candidates based on evaluation scores"""
        job_title = job_data.get("job_title", None)
        shortlisted = []
        rejected = []
        
        for candidate in candidates:
            similarity_score = candidate.get("similarity_score")
            recruiting_score = candidate.get("recruiting_score", {}).get("overall_score") if "recruiting_score" in candidate else None
            
            should_shortlist, reason = self.should_shortlist(similarity_score, recruiting_score, job_title)
            
            candidate["shortlisted"] = should_shortlist
            candidate["shortlisting_reason"] = reason
            
            if should_shortlist:
                shortlisted.append(candidate)
            else:
                rejected.append(candidate)
        
        return {"shortlisted": shortlisted, "rejected": rejected}
    
    def get_top_candidates(self, shortlisted_candidates: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top N shortlisted candidates based on final score"""
        # Calculate final score for each candidate
        for candidate in shortlisted_candidates:
            similarity_score = candidate.get("similarity_score", 0)
            recruiting_score = candidate.get("recruiting_score", {}).get("overall_score", 0)
            candidate["final_score"] = self.calculate_final_score(similarity_score, recruiting_score)
        
        # Sort by final score (descending)
        sorted_candidates = sorted(shortlisted_candidates, key=lambda x: x.get("final_score", 0), reverse=True)
        
        # Return top N candidates
        return sorted_candidates[:limit]
