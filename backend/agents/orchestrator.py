from groq import Groq
from database.vectordb.chroma import (
    get_domain_knowledge_collection,
    get_agent_experience_collection,
    get_decision_history_collection
)
from config import settings
import json

class OrchestratorAgent:
    def __init__(self):
        self.llm = Groq(api_key=settings.groq_api_keys[0])
        self.domain_knowledge = get_domain_knowledge_collection()
        self.agent_experience = get_agent_experience_collection()
        self.decision_history = get_decision_history_collection()

    def analyze(self, problem_statement: str, dataset_info: dict) -> dict:
        knowledge = self.domain_knowledge.query(
            query_texts=[problem_statement],
            n_results=3
        )
        experience = self.agent_experience.query(
            query_texts=[problem_statement],
            n_results=3
        )

        context = f"""
        Relevant knowledge: {knowledge['documents']}
        Past experience: {experience['documents']}
        """

        prompt = f"""
        You are an ML pipeline orchestrator.
        
        Problem: {problem_statement}
        Dataset info: {json.dumps(dataset_info)}
        
        Context from memory:
        {context}
        
        Respond with a JSON object containing:
        - problem_type: classification/regression/clustering
        - recommended_first_agent: which agent to run first
        - reasoning: why you made this decision
        - suggested_steps: list of steps in order
        """

        response = self.llm.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        return json.loads(response.choices[0].message.content)

    def delegate(self, plan: dict) -> str:
        return plan.get("recommended_first_agent")

    def remember(self, decision: dict, outcome: dict) -> None:
        self.decision_history.add(
            documents=[json.dumps(decision)],
            metadatas=[{"outcome": json.dumps(outcome)}],
            ids=[f"decision_{decision.get('problem_type')}_{len(str(decision))}"]
        )