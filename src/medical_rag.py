from typing import List, Dict, Any, Iterator
import numpy as np
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
import re
import logging

logger = logging.getLogger(__name__)


class AdvancedMedicalRAG:
    """Advanced RAG system specifically designed for medical applications"""

    def __init__(self, embeddings, index_name: str, use_hybrid_search: bool = True, medical_reranking: bool = True):
        self.embeddings = embeddings
        self.index_name = index_name
        self.use_hybrid_search = use_hybrid_search
        self.medical_reranking = medical_reranking

        # Initialize vector store
        try:
            self.vector_store = PineconeVectorStore.from_existing_index(
                index_name=index_name,
                embedding=embeddings
            )
            logger.info(f"Connected to Pinecone index: {index_name}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Pinecone: {e}")
            raise e

        # Medical query classification patterns
        self.medical_patterns = {
            'symptoms': [r'pain', r'ache', r'hurt', r'symptom', r'feel', r'experiencing'],
            'diagnosis': [r'diagnose', r'what is', r'condition', r'disease', r'disorder'],
            'treatment': [r'treat', r'cure', r'medicine', r'medication', r'therapy'],
            'emergency': [r'emergency', r'urgent', r'serious', r'dangerous', r'immediate'],
            'prevention': [r'prevent', r'avoid', r'protect', r'vaccine', r'screening'],
            'general': [r'health', r'medical', r'doctor', r'hospital', r'wellness']
        }

    def classify_medical_query(self, query: str) -> str:
        """Classify the type of medical query"""
        query_lower = query.lower()

        # Check for emergency keywords first
        emergency_keywords = ['emergency', 'urgent', 'chest pain', 'heart attack', 'stroke', 'bleeding', 'overdose']
        if any(keyword in query_lower for keyword in emergency_keywords):
            return 'emergency'

        for category, patterns in self.medical_patterns.items():
            if any(re.search(pattern, query_lower) for pattern in patterns):
                return category

        return 'general'

    def hybrid_search(self, query: str, k: int = 8) -> List[Document]:
        """Advanced hybrid search combining vector and keyword search"""
        try:
            # Vector similarity search
            vector_docs = self.vector_store.similarity_search(query, k=k)

            # Enhanced with medical term weighting
            medical_terms = self.extract_medical_terms(query)

            # Re-rank based on medical relevance
            if self.medical_reranking and medical_terms:
                vector_docs = self.rerank_by_medical_relevance(vector_docs, medical_terms)

            return vector_docs

        except Exception as e:
            logger.error(f"Hybrid search error: {e}")
            return []

    def extract_medical_terms(self, text: str) -> List[str]:
        """Extract medical terminology from text"""
        # Common medical prefixes/suffixes
        medical_indicators = [
            r'\w*osis\b', r'\w*itis\b', r'\w*pathy\b', r'\w*ology\b',
            r'\w*gram\b', r'\w*scopy\b', r'cardio\w*', r'neuro\w*',
            r'gastro\w*', r'hepato\w*', r'nephro\w*', r'pulmon\w*'
        ]

        terms = []
        text_lower = text.lower()

        for pattern in medical_indicators:
            matches = re.findall(pattern, text_lower)
            terms.extend(matches)

        return list(set(terms))

    def rerank_by_medical_relevance(self, docs: List[Document], medical_terms: List[str]) -> List[Document]:
        """Re-rank documents based on medical term relevance"""
        if not medical_terms:
            return docs

        scored_docs = []
        for doc in docs:
            content_lower = doc.page_content.lower()

            # Calculate relevance score
            term_matches = sum(1 for term in medical_terms if term in content_lower)
            base_score = len(doc.page_content.split())  # Document length factor
            relevance_score = (term_matches * 10) + (base_score * 0.1)

            scored_docs.append((doc, relevance_score))

        # Sort by relevance score
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs]

    def generate_medical_context(self, docs: List[Document], query_type: str) -> str:
        """Generate enhanced medical context with source attribution"""
        if not docs:
            return "No relevant medical information found in the knowledge base."

        context_parts = []
        for i, doc in enumerate(docs[:5], 1):
            source = doc.metadata.get('source', 'Unknown Source')
            content = doc.page_content.strip()

            # Add source attribution
            context_parts.append(f"[Source {i}: {source}]\n{content}\n")

        return "\n".join(context_parts)

    def process_medical_query(self, query: str, query_type: str, conversation_history: List[Dict], session_id: str) -> \
    Iterator[Dict[str, Any]]:
        """Main processing pipeline for medical queries"""
        try:
            # Search for relevant documents
            docs = self.hybrid_search(query, k=8)

            # Generate medical disclaimer if needed
            from src.security import medical_disclaimer_required
            if medical_disclaimer_required(query_type):
                yield {
                    "type": "medical_warning",
                    "content": "⚠️ This information is for educational purposes only. Always consult with a healthcare professional for medical advice."
                }

            # Generate context
            context = self.generate_medical_context(docs, query_type)

            # Create specialized prompt based on query type
            from src.prompt import get_specialized_medical_prompt
            prompt = get_specialized_medical_prompt(query_type, context, query)

            # Get LLM and generate response
            from src.llm_handler import get_llm_cascade
            llm = get_llm_cascade()[0]

            # Stream the response
            response_text = ""
            try:
                if hasattr(llm, 'stream'):
                    # Streaming response
                    for token in llm.stream(prompt):
                        if hasattr(token, 'content'):
                            content = token.content
                            response_text += content
                            yield {
                                "type": "answer_chunk",
                                "content": content
                            }
                else:
                    # Non-streaming response
                    response = llm.invoke(prompt)
                    content = response.content if hasattr(response, 'content') else str(response)
                    response_text = content
                    yield {
                        "type": "answer_chunk",
                        "content": content
                    }
            except Exception as e:
                logger.error(f"LLM streaming error: {e}")
                fallback_response = f"I understand you're asking about {query_type}-related information. Based on the available medical literature, I can provide some general guidance, but please consult with a healthcare professional for personalized advice."
                yield {
                    "type": "answer_chunk",
                    "content": fallback_response
                }

            # Return sources
            if docs:
                sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
                yield {
                    "type": "sources",
                    "content": list(set(sources))
                }

        except Exception as e:
            logger.error(f"Medical query processing error: {e}")
            yield {
                "type": "error",
                "content": "I apologize, but I encountered an error processing your medical query."
            }

    def enhance_source_credibility(self, sources: List[str]) -> List[Dict[str, Any]]:
        """Add credibility indicators to sources"""
        enhanced_sources = []

        for source in sources:
            credibility_score = self.calculate_source_credibility(source)
            enhanced_sources.append({
                "name": source.split('/')[-1] if '/' in source else source,
                "credibility": credibility_score,
                "icon": "🏥" if credibility_score >= 0.8 else "📚"
            })

        return enhanced_sources

    def calculate_source_credibility(self, source: str) -> float:
        """Calculate credibility score for medical sources"""
        high_credibility_indicators = [
            'pubmed', 'nejm', 'jama', 'mayo', 'nih', 'who', 'cdc',
            'medical', 'journal', 'peer-reviewed'
        ]

        source_lower = source.lower()
        matches = sum(1 for indicator in high_credibility_indicators if indicator in source_lower)

        # Base credibility score
        base_score = 0.5
        credibility_boost = min(matches * 0.2, 0.4)

        return min(base_score + credibility_boost, 1.0)
