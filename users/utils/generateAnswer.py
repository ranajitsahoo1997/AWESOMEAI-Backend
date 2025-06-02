from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from celery import shared_task

class AnswerEvaluatorsssss:
    def __init__(self):
        # Initialize Ollama LLM and embeddings
        self.llm = ollama.Ollama(model="llama3.2",num_thread=4,num_ctx=1024)
        self.embeddings = OllamaEmbeddings(model="llama3.2",num_thread=4,num_ctx=1024)
        self.output_parser = StrOutputParser()
        
        # Define the evaluation prompt template
        self.evaluation_prompt = ChatPromptTemplate.from_template(
            """You are an expert educator tasked with grading a student's answer based on the provided question.

            If the student's answer is irrelevant, nonsensical, or consists of meaningless text (e.g., random characters, gibberish, or off-topic responses), then assign a **0% score** and clearly state the reason.

            You must analyze both the **content and context** of the answer in relation to the question. Do not give marks unless the answer demonstrates relevance and effort to address the question.

            **Question Type**: {question_type}
            **Topic**: {topic}
            **Difficulty**: {difficulty}
            **Marks**: {marks}
            
            **Question**: {question}
            **Student Answer**: {answer}
            
            Evaluation Criteria:
            1. Relevance to question (40%)
            2. Content depth/completeness (30%)
            3. Information accuracy (20%)
            4. Logical structure (10%)
            
            At Least Expected length: ~{expected_length} words (Actual: {actual_length})
            - If the actual length is much shorter than expected, consider it in scoring.
            - If the answer is close to or exceeds the expected length and is relevant, this is a good sign.
            
            Provide:
            - Percentage score (0-100%)
            - Brief justification (50 words max)
            - Key missing elements (if any)
            
            Format response as:
            Score: X%
            Justification: ...
            Missing: ...
            """
        )

        
        # Define the evaluation chain
        self.evaluation_chain = (
            {
                "question_type": RunnablePassthrough(),
                "topic": RunnablePassthrough(),
                "difficulty": RunnablePassthrough(),
                "marks": RunnablePassthrough(),
                "question": RunnablePassthrough(),
                "answer": RunnablePassthrough(),
                "expected_length": RunnablePassthrough(),
                "actual_length": RunnablePassthrough(),
            }
            | self.evaluation_prompt
            | self.llm
            | self.output_parser
        )
    
    def calculate_expected_length(self, marks):
        """Calculate expected answer length based on marks"""
        return marks * 30  # 30 words per mark
    
    def get_semantic_similarity(self, text1, text2):
        """Calculate cosine similarity between embeddings of two texts"""
        emb1 = np.array(self.embeddings.embed_query(text1)).reshape(1, -1)
        emb2 = np.array(self.embeddings.embed_query(text2)).reshape(1, -1)
        return cosine_similarity(emb1, emb2)[0][0]
    
    def parse_evaluation_response(self, response):
        """Parse the LLM response to extract score and feedback"""
        score_match = re.search(r"Score:\s*(\d+)%", response)
        justification_match = re.search(r"Justification:\s*(.+?)(?=\nMissing:|$)", response, re.DOTALL)
        missing_match = re.search(r"Missing:\s*(.+)", response, re.DOTALL)
        
        score = int(score_match.group(1)) if score_match else 0
        justification = justification_match.group(1).strip() if justification_match else "No justification provided"
        missing = missing_match.group(1).strip() if missing_match else "None identified"
        
        return {
            "score": score,
            "justification": justification,
            "missing": missing
        }
    
    def evaluate_answer(self, question_type, topic, difficulty, marks, question, answer):
        """Evaluate a student's answer comprehensively"""
        expected_length = self.calculate_expected_length(marks)
        print("expected length")
        actual_length = len(answer.split())
        print("actual_length")
        # Get semantic similarity score
        similarity_score = self.get_semantic_similarity(question, answer)
        print("similarity score")
        # Get evaluation from LLM
        evaluation_response = self.evaluation_chain.invoke({
            "question_type": question_type,
            "topic": topic,
            "difficulty": difficulty,
            "marks": str(marks),
            "question": question,
            "answer": answer,
            "expected_length": str(expected_length),
            "actual_length": str(actual_length)
        })
        print("evaluatuion_response")
        # Parse the response
        evaluation = self.parse_evaluation_response(evaluation_response)
        
        # Combine scores (weighted average: 70% LLM evaluation, 30% semantic similarity)
        combined_score = 0.7 * evaluation["score"] + 0.3 * (similarity_score * 100)
        
        # Length adjustment (penalize answers that are too short)
        length_ratio = min(actual_length / expected_length, 1.5)  # Cap at 1.5x expected length
        if length_ratio < 0.5:  # If less than half expected length
            length_adjustment = 0.8
        elif length_ratio < 0.8:
            length_adjustment = 0.9
        else:
            length_adjustment = 1.0
            
        final_score = min(combined_score * length_adjustment, 100)  # Cap at 100%
        
        return {
            "question": question,
            "answer": answer,
            "marks": marks,
            "expected_length": expected_length,
            "actual_length": actual_length,
            "similarity_score": similarity_score,
            "llm_evaluation": evaluation,
            "combined_score": round(combined_score, 1),
            "final_score": round(final_score, 1),
            "length_adjustment": length_adjustment
        }



@shared_task
def evaluate_answer_taskss(question_type, topic, difficulty, marks, question, answer):
    evaluator = AnswerEvaluatorsssss()
    return evaluator.evaluate_answer(question_type, topic, difficulty, marks, question, answer)