from typing import List, Dict

class DASSEngine:
    """
    Calculates Depression, Anxiety, and Stress scores from 21-item questionnaire.
    Multiplies subscale scores by 2 according to standard DASS-21 guidelines.
    """
    
    @staticmethod
    def calculate_scores(answers: List[int]) -> Dict[str, any]:
        if len(answers) != 21:
            raise ValueError("Exactly 21 answers are required for DASS-21 evaluation.")
        
        # DASS-21 Question Index Mapping (0-indexed)
        # Depression: Q3, Q5, Q10, Q13, Q16, Q17, Q21 -> indices: 2, 4, 9, 12, 15, 16, 20
        depression_idx = [2, 4, 9, 12, 15, 16, 20]
        # Anxiety: Q2, Q4, Q7, Q9, Q15, Q19, Q20 -> indices: 1, 3, 6, 8, 14, 18, 19
        anxiety_idx = [1, 3, 6, 8, 14, 18, 19]
        # Stress: Q1, Q6, Q8, Q11, Q12, Q14, Q18 -> indices: 0, 5, 7, 10, 11, 13, 17
        stress_idx = [0, 5, 7, 10, 11, 13, 17]
        
        dep_raw = sum(answers[i] for i in depression_idx) * 2
        anx_raw = sum(answers[i] for i in anxiety_idx) * 2
        str_raw = sum(answers[i] for i in stress_idx) * 2
        
        # Overall Severity Classification based on Stress/Depression
        max_score = max(dep_raw, anx_raw, str_raw)
        if max_score <= 9:
            severity = "Normal"
        elif max_score <= 13:
            severity = "Mild"
        elif max_score <= 20:
            severity = "Moderate"
        elif max_score <= 27:
            severity = "Severe"
        else:
            severity = "Extremely Severe"
            
        return {
            "depression_score": dep_raw,
            "anxiety_score": anx_raw,
            "stress_score": str_raw,
            "severity_level": severity
        }