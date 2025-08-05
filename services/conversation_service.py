"""
Conversation Service for Advanced AI Chatbot
Implements memory management, context awareness, and natural language processing
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from models import ConversationMemory, CrossModuleMemory, ConversationMessage, GPTModeSession
from services.ai_service_manager import AIServiceManager
from services.rag_service import RAGService

logger = logging.getLogger(__name__)


class ConversationService:
    """Advanced conversation service with memory management and context awareness."""
    
    def __init__(self):
        self.ai_service = AIServiceManager()
        self.rag_service = RAGService()
        
        # Intent patterns for natural language understanding
        self.intent_patterns = {
            "greeting": [
                r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b",
                r"\b(start|begin|ready|let's go|let's begin)\b"
            ],
            "question": [
                r"\b(what|how|why|when|where|who|which|can you|could you|would you)\b",
                r"\b(explain|tell me|describe|clarify|help)\b"
            ],
            "answer": [
                r"\b(it's|it is|this is|that is|my|our|we|i)\b",
                r"\b(about|regarding|concerning|related to)\b"
            ],
            "clarification": [
                r"\b(what do you mean|i don't understand|can you explain|clarify)\b",
                r"\b(rephrase|repeat|say that again)\b"
            ],
            "edit_request": [
                r"\b(edit|change|modify|update|revise|correct)\b",
                r"\b(wrong|incorrect|not right|different)\b"
            ],
            "skip": [
                r"\b(skip|pass|next|move on|continue|not applicable)\b",
                r"\b(don't know|not sure|no idea)\b"
            ]
        }
    
    async def create_conversation_memory(
        self, 
        db: AsyncSession, 
        project_id: str, 
        session_id: str, 
        module_id: str
    ) -> ConversationMemory:
        """Create a new conversation memory for a session."""
        try:
            # Check if memory already exists
            result = await db.execute(
                select(ConversationMemory).where(
                    and_(
                        ConversationMemory.project_id == project_id,
                        ConversationMemory.session_id == session_id,
                        ConversationMemory.module_id == module_id
                    )
                )
            )
            existing_memory = result.scalar_one_or_none()
            
            if existing_memory:
                return existing_memory
            
            # Create new memory
            memory = ConversationMemory(
                project_id=project_id,
                session_id=session_id,
                module_id=module_id,
                conversation_history=[],
                context_summary="",
                user_profile={},
                conversation_state={
                    "current_question": 0,
                    "questions_answered": 0,
                    "total_questions": 0,
                    "conversation_flow": "welcome",
                    "last_intent": None
                }
            )
            
            db.add(memory)
            await db.commit()
            await db.refresh(memory)
            
            return memory
            
        except Exception as e:
            logger.error(f"Error creating conversation memory: {e}")
            await db.rollback()
            raise
    
    async def get_or_create_cross_module_memory(
        self, 
        db: AsyncSession, 
        project_id: str
    ) -> CrossModuleMemory:
        """Get or create cross-module memory for a project."""
        try:
            result = await db.execute(
                select(CrossModuleMemory).where(CrossModuleMemory.project_id == project_id)
            )
            memory = result.scalar_one_or_none()
            
            if not memory:
                memory = CrossModuleMemory(
                    project_id=project_id,
                    business_context={},
                    user_preferences={},
                    project_goals={},
                    key_insights=[],
                    completed_modules=[],
                    module_outputs={},
                    context_embeddings=[]
                )
                db.add(memory)
                await db.commit()
                await db.refresh(memory)
            
            return memory
            
        except Exception as e:
            logger.error(f"Error getting cross-module memory: {e}")
            await db.rollback()
            raise
    
    async def add_message_to_memory(
        self, 
        db: AsyncSession, 
        memory_id: str, 
        role: str, 
        content: str, 
        message_type: str = "text",
        context_data: dict = None
    ) -> ConversationMessage:
        """Add a message to conversation memory."""
        try:
            # Detect intent
            intent, confidence = self._detect_intent(content)
            
            # Estimate token count (rough approximation)
            tokens_used = len(content.split()) * 1.3  # Rough token estimation
            
            message = ConversationMessage(
                conversation_memory_id=memory_id,
                role=role,
                content=content,
                message_type=message_type,
                context_data=context_data or {},
                intent=intent,
                confidence=confidence,
                tokens_used=int(tokens_used)
            )
            
            db.add(message)
            await db.commit()
            await db.refresh(message)
            
            return message
            
        except Exception as e:
            logger.error(f"Error adding message to memory: {e}")
            await db.rollback()
            raise
    
    def _detect_intent(self, text: str) -> Tuple[str, float]:
        """Detect the intent of a user message."""
        text_lower = text.lower()
        max_confidence = 0.0
        detected_intent = "general"
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    confidence = len(matches) / len(text_lower.split())
                    if confidence > max_confidence:
                        max_confidence = confidence
                        detected_intent = intent
        
        return detected_intent, max_confidence
    
    async def get_conversation_context(
        self, 
        db: AsyncSession, 
        memory_id: str, 
        max_messages: int = 10
    ) -> Dict[str, Any]:
        """Get conversation context for AI processing."""
        try:
            # Get recent messages
            result = await db.execute(
                select(ConversationMessage)
                .where(ConversationMessage.conversation_memory_id == memory_id)
                .order_by(ConversationMessage.created_at.desc())
                .limit(max_messages)
            )
            messages = result.scalars().all()
            
            # Get memory object
            result = await db.execute(
                select(ConversationMemory).where(ConversationMemory.id == memory_id)
            )
            memory = result.scalar_one_or_none()
            
            if not memory:
                return {"messages": [], "context": "", "state": {}}
            
            # Format messages for AI context
            formatted_messages = []
            for msg in reversed(messages):  # Reverse to get chronological order
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                    "intent": msg.intent,
                    "timestamp": msg.created_at.isoformat()
                })
            
            return {
                "messages": formatted_messages,
                "context": memory.context_summary,
                "state": memory.conversation_state,
                "user_profile": memory.user_profile
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return {"messages": [], "context": "", "state": {}}
    
    async def update_conversation_state(
        self, 
        db: AsyncSession, 
        memory_id: str, 
        state_updates: dict
    ):
        """Update conversation state."""
        try:
            result = await db.execute(
                select(ConversationMemory).where(ConversationMemory.id == memory_id)
            )
            memory = result.scalar_one_or_none()
            
            if memory:
                memory.conversation_state.update(state_updates)
                memory.last_updated = datetime.now(timezone.utc)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error updating conversation state: {e}")
            await db.rollback()
    
    async def generate_context_summary(
        self, 
        db: AsyncSession, 
        memory_id: str
    ) -> str:
        """Generate a summary of conversation context for memory management."""
        try:
            context = await self.get_conversation_context(db, memory_id, max_messages=20)
            
            if not context["messages"]:
                return ""
            
            # Create summary prompt
            messages_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in context["messages"][-10:]  # Last 10 messages
            ])
            
            summary_prompt = f"""
            Based on the following conversation, create a concise summary of the key points, 
            user preferences, and important information that should be remembered for future context.
            
            Conversation:
            {messages_text}
            
            Summary:
            """
            
            summary = await self.ai_service.generate_content(
                prompt=summary_prompt,
                temperature=0.3,
                max_tokens=200
            )
            
            # Update memory with new summary
            result = await db.execute(
                select(ConversationMemory).where(ConversationMemory.id == memory_id)
            )
            memory = result.scalar_one_or_none()
            
            if memory:
                memory.context_summary = summary
                memory.last_updated = datetime.now(timezone.utc)
                await db.commit()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating context summary: {e}")
            return ""
    
    async def process_natural_message(
        self, 
        db: AsyncSession, 
        project_id: str, 
        session_id: str, 
        module_id: str, 
        user_message: str,
        module_questions: List[str]
    ) -> Dict[str, Any]:
        """Process a natural language message with full context awareness."""
        try:
            # Get or create conversation memory
            memory = await self.create_conversation_memory(db, project_id, session_id, module_id)
            
            # Get cross-module memory
            cross_memory = await self.get_or_create_cross_module_memory(db, project_id)
            
            # Add user message to memory
            await self.add_message_to_memory(
                db, memory.id, "user", user_message, "text"
            )
            
            # Get conversation context
            context = await self.get_conversation_context(db, memory.id)
            
            # Detect intent
            intent, confidence = self._detect_intent(user_message)
            
            # Update conversation state
            current_state = memory.conversation_state
            current_question = current_state.get("current_question", 0)
            
            # Process based on intent and context
            if intent == "greeting" and current_question == 0:
                # Welcome message and first question
                response = await self._handle_greeting(db, memory, module_questions, context, cross_memory)
            elif intent == "question":
                # User is asking a question
                response = await self._handle_user_question(db, memory, user_message, context, cross_memory)
            elif intent == "edit_request":
                # User wants to edit something
                response = await self._handle_edit_request(db, memory, user_message, context)
            elif intent == "skip":
                # User wants to skip current question
                response = await self._handle_skip(db, memory, module_questions, context)
            else:
                # Treat as potential answer to current question
                response = await self._handle_potential_answer(
                    db, memory, user_message, module_questions, context, cross_memory
                )
            
            # Add assistant response to memory
            await self.add_message_to_memory(
                db, memory.id, "assistant", response["message"], "response"
            )
            
            # Update conversation state
            await self.update_conversation_state(db, memory.id, {
                "current_question": response.get("current_question", current_question),
                "last_intent": intent,
                "conversation_flow": response.get("flow", "normal")
            })
            
            # Generate context summary if needed (every 5 messages)
            message_count = len(context["messages"])
            if message_count % 5 == 0:
                await self.generate_context_summary(db, memory.id)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing natural message: {e}")
            return {
                "message": "I'm having trouble processing that. Could you please rephrase?",
                "is_question": True,
                "current_question": module_questions[0] if module_questions else "",
                "flow": "error"
            }
    
    async def _handle_greeting(
        self, 
        db: AsyncSession, 
        memory: ConversationMemory, 
        module_questions: List[str], 
        context: dict, 
        cross_memory: CrossModuleMemory
    ) -> Dict[str, Any]:
        """Handle greeting and start conversation."""
        # Generate personalized welcome message
        welcome_prompt = f"""
        You are a helpful business consultant. Generate a warm, personalized welcome message 
        for starting a conversation about {memory.module_id}.
        
        Context from previous modules: {cross_memory.business_context}
        User preferences: {cross_memory.user_preferences}
        
        Make it conversational and encouraging. Then ask the first question naturally.
        """
        
        welcome_message = await self.ai_service.generate_content(
            prompt=welcome_prompt,
            temperature=0.7
        )
        
        first_question = module_questions[0] if module_questions else ""
        
        return {
            "message": f"{welcome_message}\n\n{first_question}",
            "is_question": True,
            "current_question": 0,
            "flow": "welcome"
        }
    
    async def _handle_user_question(
        self, 
        db: AsyncSession, 
        memory: ConversationMemory, 
        user_message: str, 
        context: dict, 
        cross_memory: CrossModuleMemory
    ) -> Dict[str, Any]:
        """Handle when user asks a question."""
        # Generate contextual answer
        answer_prompt = f"""
        You are a helpful business consultant. The user is asking: "{user_message}"
        
        Conversation context: {context['context']}
        Business context: {cross_memory.business_context}
        
        Provide a helpful, contextual answer. If the question is about the current process,
        guide them back to the current question naturally.
        """
        
        answer = await self.ai_service.generate_content(
            prompt=answer_prompt,
            temperature=0.7
        )
        
        # Get current question
        current_state = memory.conversation_state
        current_question = current_state.get("current_question", 0)
        module_questions = self._get_module_questions(memory.module_id)
        
        if current_question < len(module_questions):
            current_q = module_questions[current_question]
            return {
                "message": f"{answer}\n\nNow, back to our current question: {current_q}",
                "is_question": True,
                "current_question": current_question,
                "flow": "clarification"
            }
        else:
            return {
                "message": answer,
                "is_question": False,
                "flow": "answer"
            }
    
    async def _handle_edit_request(
        self, 
        db: AsyncSession, 
        memory: ConversationMemory, 
        user_message: str, 
        context: dict
    ) -> Dict[str, Any]:
        """Handle edit requests."""
        return {
            "message": "I'd be happy to help you edit that! What would you like to change?",
            "is_question": False,
            "flow": "edit"
        }
    
    async def _handle_skip(
        self, 
        db: AsyncSession, 
        memory: ConversationMemory, 
        module_questions: List[str], 
        context: dict
    ) -> Dict[str, Any]:
        """Handle skip requests."""
        current_state = memory.conversation_state
        current_question = current_state.get("current_question", 0)
        
        if current_question + 1 < len(module_questions):
            next_question = module_questions[current_question + 1]
            return {
                "message": f"Alright, let's move on to the next question: {next_question}",
                "is_question": True,
                "current_question": current_question + 1,
                "flow": "skip"
            }
        else:
            return {
                "message": "Great! We've covered all the questions. Let me create a summary of what we've discussed.",
                "is_question": False,
                "module_complete": True,
                "flow": "complete"
            }
    
    async def _handle_potential_answer(
        self, 
        db: AsyncSession, 
        memory: ConversationMemory, 
        user_message: str, 
        module_questions: List[str], 
        context: dict, 
        cross_memory: CrossModuleMemory
    ) -> Dict[str, Any]:
        """Handle potential answers to current questions."""
        current_state = memory.conversation_state
        current_question = current_state.get("current_question", 0)
        
        if current_question >= len(module_questions):
            # All questions answered, generate summary
            return await self._generate_completion_summary(db, memory, context, cross_memory)
        
        # Validate answer using AI
        validation_prompt = f"""
        Current question: "{module_questions[current_question]}"
        User's response: "{user_message}"
        
        Determine if this is a valid answer to the question. Consider:
        1. Does it address the question?
        2. Is it relevant and meaningful?
        3. Does it provide useful information?
        
        Respond with "VALID" or "INVALID" and a brief explanation.
        """
        
        validation_result = await self.ai_service.generate_content(
            prompt=validation_prompt,
            temperature=0.3
        )
        
        is_valid = "VALID" in validation_result.upper()
        
        if is_valid:
            # Valid answer, move to next question
            next_question_idx = current_question + 1
            
            if next_question_idx >= len(module_questions):
                # Last question answered
                return await self._generate_completion_summary(db, memory, context, cross_memory)
            else:
                # Generate natural transition
                transition_prompt = f"""
                The user just answered: "{user_message}"
                Next question: "{module_questions[next_question_idx]}"
                
                Create a natural, conversational transition to the next question.
                Acknowledge their answer briefly and smoothly introduce the next question.
                """
                
                transition = await self.ai_service.generate_content(
                    prompt=transition_prompt,
                    temperature=0.7
                )
                
                return {
                    "message": transition,
                    "is_question": True,
                    "current_question": next_question_idx,
                    "flow": "transition"
                }
        else:
            # Invalid answer, ask for clarification
            clarification_prompt = f"""
            The user's response "{user_message}" doesn't seem to fully answer the question: "{module_questions[current_question]}"
            
            Create a friendly, helpful clarification request that:
            1. Acknowledges their response
            2. Explains what kind of information is needed
            3. Encourages them to provide more details
            """
            
            clarification = await self.ai_service.generate_content(
                prompt=clarification_prompt,
                temperature=0.7
            )
            
            return {
                "message": clarification,
                "is_question": True,
                "current_question": current_question,
                "flow": "clarification"
            }
    
    async def _generate_completion_summary(
        self, 
        db: AsyncSession, 
        memory: ConversationMemory, 
        context: dict, 
        cross_memory: CrossModuleMemory
    ) -> Dict[str, Any]:
        """Generate completion summary."""
        summary_prompt = f"""
        Generate a comprehensive summary of the conversation for {memory.module_id}.
        
        Conversation context: {context['context']}
        Business context: {cross_memory.business_context}
        
        Create a detailed, professional summary that captures all key points discussed.
        """
        
        summary = await self.ai_service.generate_content(
            prompt=summary_prompt,
            temperature=0.5
        )
        
        return {
            "message": f"Perfect! Here's a summary of what we've discussed:\n\n{summary}",
            "is_question": False,
            "module_complete": True,
            "summary": summary,
            "flow": "complete"
        }
    
    def _get_module_questions(self, module_id: str) -> List[str]:
        """Get questions for a module from the chatbot service."""
        # This should be implemented to get questions from your module configuration
        # For now, returning empty list - this will be passed from the chatbot service
        return [] 