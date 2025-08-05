"""
LangChain-based Conversation Service for Advanced AI Chatbot
Implements conversation memory, RAG retrieval, and context-aware responses
"""

import logging
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from pathlib import Path
import os

from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from models import ConversationMemory, CrossModuleMemory, ConversationMessage, GPTModeSession
from services.ai_service_manager import AIServiceManager
from config import settings

logger = logging.getLogger(__name__)

class LangChainConversationService:
    """Advanced conversation service with LangChain memory and RAG capabilities."""
    
    def __init__(self):
        self.ai_service = AIServiceManager()
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_stores = {}  # Cache for module-specific vector stores
        self.conversation_chains = {}  # Cache for conversation chains
        
    async def load_module_content(self, module_id: str) -> List[Document]:
        """Load and process content for a specific GPT module."""
        try:
            # Define the path to GPT modules
            gpt_modules_path = Path("GPT FINAL FLOW")
            
            # Map module IDs to folder names
            module_mapping = {
                "offer_clarifier": "1_The Offer Clarifier GPT",
                "avatar_creator": "2_Avatar Creator and Empathy Map GPT", 
                "before_state": "3_Before State Research GPT",
                "after_state": "4_After State Research GPT",
                "avatar_validator": "5_Avatar Validator GPT",
                "trigger_gpt": "6_TriggerGPT",
                "epo_builder": "7_EPO Builder GPT - Copy",
                "scamper_synthesizer": "8_SCAMPER Synthesizer",
                "wildcard_idea": "9_Wildcard Idea Bot",
                "concept_crafter": "10_Concept Crafter GPT",
                "hook_headline": "11_Hook & Headline GPT",
                "campaign_concept": "12_Campaign Concept Generator GPT",
                "ideation_injection": "13_Ideation Injection Bot"
            }
            
            # Get the folder name for this module
            folder_name = module_mapping.get(module_id, module_id)
            module_path = gpt_modules_path / folder_name
            
            if not module_path.exists():
                logger.warning(f"Module path not found: {module_path}")
                return []
            
            documents = []
            
            # Load system prompts - prioritize conversational versions
            system_prompt_path = module_path / "System Prompt"
            if system_prompt_path.exists():
                # First, look for conversational prompts
                conversational_prompts = list(system_prompt_path.glob("*Conversational*.txt"))
                regular_prompts = list(system_prompt_path.glob("*.txt"))
                
                # Use conversational prompts if available, otherwise use regular prompts
                prompt_files = conversational_prompts if conversational_prompts else regular_prompts
                
                for file_path in prompt_files:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append(Document(
                            page_content=content,
                            metadata={
                                "source": str(file_path),
                                "type": "system_prompt",
                                "module": module_id,
                                "is_conversational": "Conversational" in file_path.name
                            }
                        ))
            
            # Load RAG content
            rag_path = module_path / "RAG"
            if rag_path.exists():
                for file_path in rag_path.glob("*.txt"):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append(Document(
                            page_content=content,
                            metadata={
                                "source": str(file_path),
                                "type": "rag_content",
                                "module": module_id
                            }
                        ))
            
            # Load output templates
            output_path = module_path / "Output template"
            if output_path.exists():
                for file_path in output_path.glob("*.txt"):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append(Document(
                            page_content=content,
                            metadata={
                                "source": str(file_path),
                                "type": "output_template",
                                "module": module_id
                            }
                        ))
            
            logger.info(f"Loaded {len(documents)} documents for module {module_id}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading module content for {module_id}: {e}")
            return []
    
    async def create_vector_store(self, module_id: str) -> FAISS:
        """Create or retrieve vector store for a module."""
        if module_id in self.vector_stores:
            return self.vector_stores[module_id]
        
        try:
            # Load documents for this module
            documents = await self.load_module_content(module_id)
            
            if not documents:
                logger.warning(f"No documents found for module {module_id}")
                return None
            
            # Split documents into chunks
            texts = self.text_splitter.split_documents(documents)
            
            # Create vector store
            vector_store = FAISS.from_documents(texts, self.embeddings)
            
            # Cache the vector store
            self.vector_stores[module_id] = vector_store
            
            logger.info(f"Created vector store for module {module_id} with {len(texts)} chunks")
            return vector_store
            
        except Exception as e:
            logger.error(f"Error creating vector store for {module_id}: {e}")
            return None
    
    async def create_conversation_chain(self, module_id: str, memory_id: str) -> ConversationalRetrievalChain:
        """Create a conversation chain with memory and RAG."""
        try:
            # Get or create vector store
            vector_store = await self.create_vector_store(module_id)
            
            if not vector_store:
                logger.error(f"Could not create vector store for module {module_id}")
                return None
            
            # Create memory
            memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=10  # Keep last 10 exchanges
            )
            
            # Create LLM
            llm = ChatOpenAI(
                model_name=settings.openai_model,
                temperature=0.7,
                openai_api_key=settings.openai_api_key
            )
            
            # Create custom conversational prompt template
            conversational_prompt = PromptTemplate(
                input_variables=["context", "question", "chat_history"],
                template="""You are a friendly, conversational business assistant helping users clarify their product or service offers. Your goal is to have a natural, flowing conversation that feels like talking to a knowledgeable business consultant.

## 🎯 YOUR ROLE
- Be warm, engaging, and conversational
- Ask questions naturally as part of the conversation flow
- Remember what the user has shared and build on it
- Help them think through their business offering step by step
- Make them feel comfortable sharing their ideas

## 💬 CONVERSATION STYLE
- Use a friendly, casual tone
- Ask follow-up questions to dig deeper
- Acknowledge their responses and show understanding
- Share insights and observations about their business
- Guide them toward clarity without being pushy

## 📋 INFORMATION TO GATHER (through natural conversation)
As you chat, naturally gather these details about their offer:
1. Product/Service Name - What do they call it?
2. Core Transformation - What's the main result customers get?
3. Key Features - What's included? What makes it valuable?
4. Delivery Method - How do customers access it?
5. Format - Is it a course, service, software, membership, etc.?
6. Pricing - What's the cost structure?
7. Unique Value - What makes it different from alternatives?
8. Target Audience - Who is this perfect for?
9. Problems Solved - What pain points does it address?

## 🔄 CONVERSATION FLOW
1. Start with a warm greeting and ask about their business
2. Listen and respond naturally to what they share
3. Ask thoughtful follow-up questions to get more details
4. Acknowledge their insights and help them think deeper
5. Guide them toward clarity on each aspect of their offer
6. Summarize what you've learned and ask for confirmation
7. Offer to create a summary when they're ready

## 🎯 CONVERSATION TECHNIQUES
- "Tell me more about..." - Encourage elaboration
- "That's interesting! How does that work?" - Show curiosity
- "So if I understand correctly..." - Confirm understanding
- "What made you decide to..." - Explore their thinking
- "How do your customers typically..." - Understand their market
- "What would you say is the biggest..." - Identify key points

## 📝 WHEN READY TO SUMMARIZE
When you have enough information, say something like:
"Great! I feel like I have a good understanding of your offer now. Would you like me to create a summary of everything we've discussed? This will help you see how clear and compelling your offer is, and you can make any adjustments before we move forward."

## 🚫 AVOID
- Rigid question lists
- Formal business language
- Pushing for specific answers
- Making assumptions about their business
- Rushing through the conversation

## ✅ REMEMBER
Your goal is to help them think through their offer in a natural, comfortable way. The conversation should feel like talking to a smart friend who really understands business and wants to help them succeed.

## CONTEXT INFORMATION
{context}

## CONVERSATION HISTORY
{chat_history}

## USER'S QUESTION
{question}

Please respond in a warm, conversational way that helps them think through their business offering naturally."""
            )
            
            # Create conversation chain with custom prompt
            chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 3}
                ),
                memory=memory,
                return_source_documents=True,
                verbose=True,
                combine_docs_chain_kwargs={"prompt": conversational_prompt}
            )
            
            # Cache the chain
            chain_key = f"{module_id}_{memory_id}"
            self.conversation_chains[chain_key] = chain
            
            logger.info(f"Created conversation chain for {module_id}")
            return chain
            
        except Exception as e:
            logger.error(f"Error creating conversation chain for {module_id}: {e}")
            return None
    
    async def get_conversation_context(self, db: AsyncSession, memory_id: str) -> Dict[str, Any]:
        """Get conversation context from database."""
        try:
            # Get conversation memory
            memory_query = select(ConversationMemory).where(
                ConversationMemory.id == memory_id
            )
            memory_result = await db.execute(memory_query)
            memory = memory_result.scalar_one_or_none()
            
            if not memory:
                return {"history": [], "summary": "", "context": {}}
            
            # Get recent messages
            messages_query = select(ConversationMessage).where(
                ConversationMessage.conversation_memory_id == memory_id
            ).order_by(ConversationMessage.created_at.desc()).limit(10)
            
            messages_result = await db.execute(messages_query)
            messages = messages_result.scalars().all()
            
            # Format conversation history
            history = []
            for msg in reversed(messages):  # Reverse to get chronological order
                history.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                })
            
            return {
                "history": history,
                "summary": memory.context_summary,
                "context": memory.conversation_state,
                "user_profile": memory.user_profile
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return {"history": [], "summary": "", "context": {}}
    
    async def process_message_with_langchain(
        self,
        db: AsyncSession,
        project_id: str,
        session_id: str,
        module_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """Process a message using LangChain with memory and RAG."""
        try:
            # Get or create conversation memory
            memory_query = select(ConversationMemory).where(
                and_(
                    ConversationMemory.project_id == project_id,
                    ConversationMemory.session_id == session_id,
                    ConversationMemory.module_id == module_id
                )
            )
            memory_result = await db.execute(memory_query)
            memory = memory_result.scalar_one_or_none()
            
            if not memory:
                # Create new memory
                memory = ConversationMemory(
                    project_id=project_id,
                    session_id=session_id,
                    module_id=module_id
                )
                db.add(memory)
                await db.commit()
                await db.refresh(memory)
            
            # Create conversation chain
            chain = await self.create_conversation_chain(module_id, memory.id)
            
            if not chain:
                return {
                    "success": False,
                    "message": "Failed to initialize conversation chain",
                    "error": "Vector store creation failed"
                }
            
            # Process the message
            result = await chain.ainvoke({
                "question": user_message,
                "chat_history": []
            })
            
            # Extract response and sources
            response = result.get("answer", "I'm sorry, I couldn't process your message.")
            source_documents = result.get("source_documents", [])
            
            # Save message to database
            user_msg = ConversationMessage(
                conversation_memory_id=memory.id,
                role="user",
                content=user_message,
                message_type="text"
            )
            db.add(user_msg)
            
            # Save assistant response
            assistant_msg = ConversationMessage(
                conversation_memory_id=memory.id,
                role="assistant",
                content=response,
                message_type="text",
                context_data={
                    "sources": [doc.metadata.get("source", "") for doc in source_documents],
                    "module_id": module_id
                }
            )
            db.add(assistant_msg)
            
            # Update memory
            memory.conversation_history = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": response}
            ]
            memory.last_updated = datetime.now(timezone.utc)
            
            await db.commit()
            
            # Check if conversation is complete (you can implement your own logic)
            is_complete = self._check_conversation_complete(response, user_message)
            
            return {
                "success": True,
                "message": response,
                "sources": [doc.metadata.get("source", "") for doc in source_documents],
                "module_complete": is_complete,
                "memory_id": memory.id
            }
            
        except Exception as e:
            logger.error(f"Error processing message with LangChain: {e}")
            return {
                "success": False,
                "message": "I encountered an error processing your message.",
                "error": str(e)
            }
    
    def _check_conversation_complete(self, response: str, user_message: str) -> bool:
        """Check if the conversation is complete based on response content."""
        # Check for conversational completion indicators
        completion_indicators = [
            "would you like me to create a summary",
            "i feel like i have a good understanding",
            "let me create a summary",
            "here's a summary",
            "summary of everything we've discussed",
            "ready to create a summary",
            "shall i summarize",
            "would you like me to summarize"
        ]
        
        response_lower = response.lower()
        for indicator in completion_indicators:
            if indicator in response_lower:
                return True
        
        # Also check if user is asking for summary
        user_summary_requests = [
            "create summary",
            "generate summary", 
            "summarize",
            "summary please",
            "can you summarize",
            "give me a summary"
        ]
        
        user_message_lower = user_message.lower()
        for request in user_summary_requests:
            if request in user_message_lower:
                return True
        
        return False
    
    async def get_conversation_summary(self, db: AsyncSession, memory_id: str) -> str:
        """Generate a summary of the conversation."""
        try:
            # Get conversation memory
            memory_query = select(ConversationMemory).where(
                ConversationMemory.id == memory_id
            )
            memory_result = await db.execute(memory_query)
            memory = memory_result.scalar_one_or_none()
            
            if not memory:
                return "No conversation found."
            
            # Get all messages
            messages_query = select(ConversationMessage).where(
                ConversationMessage.conversation_memory_id == memory_id
            ).order_by(ConversationMessage.created_at)
            
            messages_result = await db.execute(messages_query)
            messages = messages_result.scalars().all()
            
            # Create conversation text
            conversation_text = ""
            for msg in messages:
                conversation_text += f"{msg.role.title()}: {msg.content}\n\n"
            
            # Generate summary using OpenAI
            summary_prompt = f"""
            Please provide a concise summary of the following conversation, focusing on:
            1. Key points discussed
            2. Important insights or findings
            3. Any decisions or conclusions made
            
            Conversation:
            {conversation_text}
            
            Summary:
            """
            
            # Use the AI service to generate summary
            summary_response = await self.ai_service.generate_response(
                prompt=summary_prompt,
                max_tokens=500
            )
            
            # Update memory with summary
            memory.context_summary = summary_response
            await db.commit()
            
            return summary_response
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return "Error generating summary."
    
    async def clear_conversation_memory(self, db: AsyncSession, memory_id: str):
        """Clear conversation memory."""
        try:
            # Delete messages
            await db.execute(
                select(ConversationMessage).where(
                    ConversationMessage.conversation_memory_id == memory_id
                ).delete()
            )
            
            # Delete memory
            await db.execute(
                select(ConversationMemory).where(
                    ConversationMemory.id == memory_id
                ).delete()
            )
            
            await db.commit()
            logger.info(f"Cleared conversation memory {memory_id}")
            
        except Exception as e:
            logger.error(f"Error clearing conversation memory: {e}") 