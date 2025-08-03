"""
Chatbot service for GPT FINAL FLOW modules with sequential questioning and module transitions.
"""
import json
import os
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from openai import OpenAI
from config import settings
from services.ai_service_manager import ai_service_manager

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service for managing GPT FINAL FLOW chatbot interactions."""
    
    def __init__(self):
        # Use the AI service manager for OpenAI operations
        self.ai_manager = ai_service_manager
        
        # Keep direct OpenAI client for backward compatibility
        try:
            self.client = OpenAI(api_key=settings.openai_api_key)
            if not settings.openai_api_key:
                logger.warning("OpenAI API key not configured. Some features may not work.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
            
        self.gpt_flow_path = Path("GPT FINAL FLOW")
        if not self.gpt_flow_path.exists():
            logger.error("GPT FINAL FLOW directory not found!")
            raise FileNotFoundError("GPT FINAL FLOW directory not found")
            
        self.modules = self._load_modules()
        logger.info(f"ChatbotService initialized with {len(self.modules)} modules")
        
    def _load_modules(self) -> Dict[str, Dict[str, Any]]:
        """Load all GPT FINAL FLOW modules with their prompts and questions."""
        modules = {}
        
        # Define module order and their specific questions
        module_configs = {
            "1_The Offer Clarifier GPT": {
                "name": "Offer Clarifier GPT",
                "description": "Define your product or service clearly",
                "questions": [
                    "What is your product, service, or offer called?",
                    "What is the #1 outcome or transformation your customer gets from this offer?",
                    "What are 3–5 key features or deliverables included?",
                    "How is the offer delivered? (Live, digital, coaching, physical, etc.)",
                    "What format is it in? (Course, membership, service, SaaS, etc.)",
                    "What's the price or pricing model?",
                    "What makes your offer different from others like it? (USP)",
                    "Who is this offer for? Describe your ideal customer.",
                    "What 2–3 big problems does this offer solve for them?"
                ],
                "system_prompt_file": "System Prompt/The Offer Clarifier.txt",
                "output_template_file": "Output template/✅ OFFER CLARIFIER – OUTCOME SUMMARY REPORT For Frsutrated Freddie.txt",
                "rag_files": []
            },
            "2_Avatar Creator and Empathy Map GPT": {
                "name": "Avatar Creator and Empathy Map GPT",
                "description": "Build a complete customer avatar step-by-step",
                "questions": [
                    "Who is your ideal customer? (Think about someone you've helped before or would love to work with)",
                    "What name would you like to give this customer avatar? (e.g., 'Freelancer Fran' or 'Agency Eric')",
                    "What's their age range? (e.g., '25–35' or '40–50')",
                    "What's their job or profession? (Are they self-employed, business owner, teacher, consultant, etc.?)",
                    "Where do they live or work? (Big city, small town, suburban area? Work from home or office?)",
                    "Roughly how much do they earn per year? (e.g., 'under $50K,' '$75–100K,' or '6 figures')",
                    "Are they married or single? Kids? (Family structure helps tailor your message)",
                    "What brands, influencers, or content do they follow? (e.g., Gary Vee, Shark Tank, Etsy, Jenna Kutcher)",
                    "Where do they get information? (Blogs, YouTube, webinars, events, social media?)",
                    "What's a quote or phrase they might say? (Something that captures their mindset)",
                    "What are their biggest frustrations or fears? (What problems are they facing?)",
                    "What are their wants, dreams, or goals? (Personal, financial, or lifestyle goals?)",
                    "What values matter to them? (Quality, freedom, trust, family, efficiency, etc.?)",
                    "Why would they buy from you? (What makes your product/service a 'yes' for them?)",
                    "What objections might stop them from buying? (Price, lack of trust, uncertainty?)",
                    "Are they the decision-maker? (Do they buy for themselves or need someone else's buy-in?)",
                    "What is their life like before finding your product/service? (Describe their current state)",
                    "What is life like after they use your product/service? (Describe their new state)",
                    "What emotional transformation do they experience? (From: frustrated, stuck, confused To: empowered, confident, excited)"
                ],
                "system_prompt_file": "System Prompt/Avatar Creator and Empathy Map GPT.txt",
                "output_template_file": "Output template/Customer Avatar_ Stuck Steve.txt",
                "rag_files": ["RAG/DM-Copy-Hack-Customer-Avatar.txt"]
            },
            "3_Before State Research GPT": {
                "name": "Before State Research GPT",
                "description": "Research and enhance the customer's before state",
                "questions": [
                    "What specific pain points does your avatar experience daily?",
                    "What are their biggest frustrations with current solutions?",
                    "What fears or concerns hold them back from taking action?",
                    "What does their typical day look like when struggling with this problem?",
                    "What emotions do they feel when facing this challenge?",
                    "What have they tried before that didn't work?",
                    "What are the consequences of not solving this problem?",
                    "What triggers make this problem feel urgent?",
                    "What does success look like to them right now?",
                    "What resources or support do they currently lack?"
                ],
                "system_prompt_file": "System Prompt/Before State Research GPT.txt",
                "output_template_file": "Output template/Customer Avatar_ Stuck Steve - Enhanced Before and After.txt",
                "rag_files": ["RAG/Avatar Creation Guide.txt"]
            },
            "4_After State Research GPT": {
                "name": "After State Research GPT",
                "description": "Research and enhance the customer's after state",
                "questions": [
                    "What would be the ideal outcome for your avatar?",
                    "How would their daily life change after using your solution?",
                    "What new opportunities would open up for them?",
                    "What emotions would they feel after achieving success?",
                    "What would their new routine look like?",
                    "How would their relationships improve?",
                    "What financial benefits would they experience?",
                    "What would their new level of confidence look like?",
                    "What goals would they be able to achieve?",
                    "How would their self-image change?"
                ],
                "system_prompt_file": "System Prompt/After State Enhancement GPT.txt",
                "output_template_file": "Output template/🌞 After State – Stuck Steve (Expanded Narrative).txt",
                "rag_files": ["RAG/Avatar Creation Guide.txt"]
            },
            "5_Avatar Validator GPT": {
                "name": "Avatar Validator GPT",
                "description": "Validate and refine the customer avatar",
                "questions": [
                    "Does this avatar represent your most profitable customer type?",
                    "Are there any gaps in the avatar profile that need filling?",
                    "What aspects of the avatar could be more specific?",
                    "How well does this avatar align with your offer?",
                    "What objections might this avatar have that we haven't addressed?",
                    "Are there any conflicting traits in the avatar profile?",
                    "How realistic is this avatar based on your experience?",
                    "What additional research would strengthen this avatar?",
                    "How does this avatar compare to your actual customers?",
                    "What would make this avatar even more compelling?"
                ],
                "system_prompt_file": "System Prompt/Avatar Validator GPT.txt",
                "output_template_file": None,
                "rag_files": ["RAG/Avatar Creation Guide.txt"]
            },
            "6_TriggerGPT": {
                "name": "TriggerGPT",
                "description": "Discover what triggers your perfect customer to need your service",
                "questions": [
                    "What life events might trigger your avatar to seek a solution?",
                    "What business challenges could prompt them to take action?",
                    "What emotional states would make them more receptive?",
                    "What external pressures might influence their decision?",
                    "What timing factors are important for your avatar?",
                    "What content would resonate with them during these triggers?",
                    "What entry point offers would work best for each trigger?",
                    "How urgent are these triggers for your avatar?",
                    "What objections might arise during trigger moments?",
                    "How can you create urgency around these triggers?"
                ],
                "system_prompt_file": "System Prompt/TriggerGPT.txt",
                "output_template_file": "Output template/Frustrated Freddie - Trigger GPT.txt",
                "rag_files": [
                    "RAG/Brainstorming Your Triggering Events.txt",
                    "RAG/Identifying The Triggering Events.txt",
                    "RAG/PSS-Workbook_MOD 3 - Identifying The Triggering Event.txt",
                    "RAG/PSS-WS-03-03-TypeOfTriggeringEvents.txt",
                    "RAG/PSS-WS-03-04-HowtoRankYourTriggeringEvents.txt"
                ]
            },
            "7_EPO Builder GPT - Copy": {
                "name": "EPO Builder GPT",
                "description": "Build effective entry point offers",
                "questions": [
                    "What is the main problem your entry point offer will solve?",
                    "What format will work best for your avatar? (PDF, video, webinar, etc.)",
                    "What specific value will this offer provide?",
                    "How will you deliver this offer?",
                    "What's the ideal length or duration for this offer?",
                    "What call-to-action will you use?",
                    "How will you follow up after the offer?",
                    "What objections might arise with this offer?",
                    "How will you measure the success of this offer?",
                    "What's the next step after someone consumes this offer?"
                ],
                "system_prompt_file": "System Prompt/EPO Builder GPT.txt",
                "output_template_file": None,
                "rag_files": ["RAG/drive-download-20250614T003233Z-1-001.txt"]
            },
            "8_SCAMPER Synthesizer": {
                "name": "SCAMPER Synthesizer",
                "description": "Use SCAMPER technique to generate creative ideas",
                "questions": [
                    "What could you SUBSTITUTE in your current approach?",
                    "What could you COMBINE with your existing solution?",
                    "What could you ADAPT from other industries?",
                    "What could you MODIFY or MAGNIFY in your offer?",
                    "What could you PUT TO OTHER USES?",
                    "What could you ELIMINATE from your current process?",
                    "What could you REVERSE or REARRANGE?",
                    "How could you make your solution more accessible?",
                    "What new delivery methods could you explore?",
                    "How could you create more value with less effort?"
                ],
                "system_prompt_file": "System Prompt/SCAMPER Synthesizer.txt",
                "output_template_file": "Output template/🧠 EDDIE's Dead Lead Revival Kit.txt",
                "rag_files": ["RAG/scamper.txt"]
            },
            "9_Wildcard Idea Bot": {
                "name": "Wildcard Idea Bot",
                "description": "Generate wild and creative ideas",
                "questions": [
                    "What's the most outrageous idea you could try?",
                    "What would you do if money and time were unlimited?",
                    "What's something completely opposite to your current approach?",
                    "What would your avatar's dream solution look like?",
                    "What's an idea that seems impossible but would be amazing?",
                    "What would you do if you had to start over completely?",
                    "What's an idea that combines two completely different things?",
                    "What would you do if you had to solve this in 24 hours?",
                    "What's an idea that would make your competitors jealous?",
                    "What would you do if you had unlimited resources?"
                ],
                "system_prompt_file": "System Prompt/Wildcard Idea Bot GPT.txt",
                "output_template_file": "Output template/Wildcard Idea Bot - Frustrated Freddie.txt",
                "rag_files": []
            },
            "10_Concept Crafter GPT": {
                "name": "Concept Crafter GPT",
                "description": "Craft compelling concepts and ideas",
                "questions": [
                    "What's the core concept behind your best idea?",
                    "How can you make this concept more compelling?",
                    "What story can you tell around this concept?",
                    "How can you make this concept more relatable?",
                    "What emotions should this concept evoke?",
                    "How can you make this concept more memorable?",
                    "What metaphors or analogies work for this concept?",
                    "How can you simplify this concept?",
                    "What makes this concept unique?",
                    "How can you test this concept quickly?"
                ],
                "system_prompt_file": "System Prompt/Concept Crafter Bot (1).txt",
                "output_template_file": None,
                "rag_files": []
            },
            "11_Hook & Headline GPT": {
                "name": "Hook & Headline GPT",
                "description": "Create compelling hooks and headlines",
                "questions": [
                    "What's the main benefit your avatar wants?",
                    "What's their biggest pain point?",
                    "What would make them stop scrolling?",
                    "What's the most surprising thing about your solution?",
                    "What's a common misconception in your industry?",
                    "What's the transformation they're seeking?",
                    "What's the cost of inaction?",
                    "What's the most emotional aspect of their problem?",
                    "What's the quickest win they could get?",
                    "What's the most compelling proof you have?"
                ],
                "system_prompt_file": "System Prompt/Hook & Headline GPT.txt",
                "output_template_file": None,
                "rag_files": []
            },
            "12_Campaign Concept Generator GPT": {
                "name": "Campaign Concept Generator GPT",
                "description": "Generate complete campaign concepts",
                "questions": [
                    "What's the main objective of this campaign?",
                    "Who is the primary target audience?",
                    "What's the key message you want to convey?",
                    "What channels will you use for this campaign?",
                    "What's the timeline for this campaign?",
                    "What's the budget for this campaign?",
                    "What metrics will you use to measure success?",
                    "What's the call-to-action for this campaign?",
                    "What's the unique angle for this campaign?",
                    "How will you follow up after the campaign?"
                ],
                "system_prompt_file": "System Prompt/Campaign Concept Generator GPT.txt",
                "output_template_file": "Output template/Campaign Strategy Report for Frustrated Freddie_ The Eureka Ideation Machine.txt",
                "rag_files": []
            },
            "13_Ideation Injection Bot": {
                "name": "Ideation Injection Bot",
                "description": "Inject additional creative ideas",
                "questions": [
                    "What's one idea you haven't tried yet?",
                    "What's something your competitors are doing that you could improve?",
                    "What's a trend you could leverage?",
                    "What's a customer request you haven't fulfilled?",
                    "What's a problem you've noticed that no one is solving?",
                    "What's a skill or resource you have that you're not using?",
                    "What's a partnership opportunity you could explore?",
                    "What's a new market you could enter?",
                    "What's a product extension you could create?",
                    "What's a process you could automate or improve?"
                ],
                "system_prompt_file": "System Prompt/Idea Injection Bot.txt",
                "output_template_file": None,
                "rag_files": []
            }
        }
        
        for module_id, config in module_configs.items():
            module_path = self.gpt_flow_path / module_id
            if module_path.exists():
                # Load system prompt
                system_prompt = ""
                if config["system_prompt_file"]:
                    prompt_file = module_path / config["system_prompt_file"]
                    if prompt_file.exists():
                        try:
                            with open(prompt_file, 'r', encoding='utf-8') as f:
                                system_prompt = f.read()
                        except Exception as e:
                            logger.warning(f"Could not load system prompt for {module_id}: {e}")
                
                # Load output template
                output_template = ""
                if config["output_template_file"]:
                    template_file = module_path / config["output_template_file"]
                    if template_file.exists():
                        try:
                            with open(template_file, 'r', encoding='utf-8') as f:
                                output_template = f.read()
                        except Exception as e:
                            logger.warning(f"Could not load output template for {module_id}: {e}")
                
                # Load RAG files
                rag_content = []
                for rag_file in config["rag_files"]:
                    rag_path = module_path / rag_file
                    if rag_path.exists():
                        try:
                            with open(rag_path, 'r', encoding='utf-8') as f:
                                rag_content.append(f.read())
                        except Exception as e:
                            logger.warning(f"Could not load RAG file {rag_file} for {module_id}: {e}")
                
                modules[module_id] = {
                    **config,
                    "system_prompt": system_prompt,
                    "output_template": output_template,
                    "rag_content": rag_content,
                    "module_id": module_id
                }
        
        return modules
    
    def get_available_modules(self) -> List[Dict[str, Any]]:
        """Get list of available modules."""
        return [
            {
                "id": module_id,
                "name": module["name"],
                "description": module["description"],
                "question_count": len(module["questions"])
            }
            for module_id, module in self.modules.items()
        ]
    
    def get_module_questions(self, module_id: str) -> List[str]:
        """Get questions for a specific module."""
        if module_id not in self.modules:
            raise ValueError(f"Module {module_id} not found")
        return self.modules[module_id]["questions"]
    
    async def get_next_question(
        self, 
        module_id: str, 
        current_question: int, 
        previous_answers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Get the next question for a module with context."""
        if module_id not in self.modules:
            raise ValueError(f"Module {module_id} not found")
        
        module = self.modules[module_id]
        questions = module["questions"]
        
        if current_question >= len(questions):
            return {
                "done": True,
                "message": f"All questions for {module['name']} have been answered!",
                "module_complete": True
            }
        
        # Build context from previous answers
        context = ""
        if previous_answers:
            context = "Previous answers:" + chr(10)
            for q_num, answer in previous_answers.items():
                if answer and answer.strip():  # Only include non-empty answers
                    context += f"Q{q_num}: {answer}" + chr(10)
        
        # Get the current question
        question = questions[current_question]
        
        # Generate enhanced question using GPT if system prompt is available
        if module["system_prompt"]:
            try:
                enhanced_question = await self._enhance_question(
                    module["system_prompt"],
                    question,
                    context,
                    module["rag_content"]
                )
            except Exception as e:
                logger.warning(f"Could not enhance question: {e}")
                enhanced_question = question
        else:
            enhanced_question = question
        
        return {
            "question_number": current_question,
            "question": enhanced_question,
            "total_questions": len(questions),
            "module_name": module["name"],
            "done": False,
            "can_skip": True,  # Allow skipping questions
            "validation_rules": self._get_validation_rules(module_id, current_question)
        }
    
    def _get_validation_rules(self, module_id: str, question_index: int) -> Dict[str, Any]:
        """Get validation rules for a specific question."""
        module = self.modules[module_id]
        questions = module["questions"]
        
        if question_index >= len(questions):
            return {}
        
        question = questions[question_index]
        
        # Define validation rules based on question content
        validation_rules = {
            "required": True,
            "min_length": 3,
            "max_length": 1000,
            "allow_skip": True,
            "skip_message": "You can skip this question if you're not sure or want to come back later."
        }
        
        # Custom validation rules based on question type
        if "email" in question.lower():
            validation_rules["type"] = "email"
            validation_rules["pattern"] = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        elif "price" in question.lower() or "cost" in question.lower():
            validation_rules["type"] = "number"
            validation_rules["min_value"] = 0
        elif "age" in question.lower():
            validation_rules["type"] = "number"
            validation_rules["min_value"] = 13
            validation_rules["max_value"] = 120
        elif "name" in question.lower():
            validation_rules["min_length"] = 2
            validation_rules["max_length"] = 100
        
        return validation_rules
    
    def validate_answer(self, module_id: str, question_index: int, answer: str) -> Dict[str, Any]:
        """Validate an answer against the question's validation rules."""
        validation_rules = self._get_validation_rules(module_id, question_index)
        
        # Check if answer is empty (skip case)
        if not answer or not answer.strip():
            if validation_rules.get("allow_skip", True):
                return {
                    "valid": True,
                    "skipped": True,
                    "message": "Question skipped successfully."
                }
            else:
                return {
                    "valid": False,
                    "skipped": False,
                    "message": "This question cannot be skipped."
                }
        
        # Check required field
        if validation_rules.get("required", True) and not answer.strip():
            return {
                "valid": False,
                "skipped": False,
                "message": "This question is required."
            }
        
        # Check length
        if len(answer.strip()) < validation_rules.get("min_length", 3):
            return {
                "valid": False,
                "skipped": False,
                "message": f"Answer must be at least {validation_rules.get('min_length', 3)} characters long."
            }
        
        if len(answer.strip()) > validation_rules.get("max_length", 1000):
            return {
                "valid": False,
                "skipped": False,
                "message": f"Answer must be no more than {validation_rules.get('max_length', 1000)} characters long."
            }
        
        # Check type-specific validation
        if validation_rules.get("type") == "email":
            import re
            email_pattern = validation_rules.get("pattern", r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
            if not re.match(email_pattern, answer.strip()):
                return {
                    "valid": False,
                    "skipped": False,
                    "message": "Please enter a valid email address."
                }
        
        elif validation_rules.get("type") == "number":
            try:
                value = float(answer.strip())
                if "min_value" in validation_rules and value < validation_rules["min_value"]:
                    return {
                        "valid": False,
                        "skipped": False,
                        "message": f"Value must be at least {validation_rules['min_value']}."
                    }
                if "max_value" in validation_rules and value > validation_rules["max_value"]:
                    return {
                        "valid": False,
                        "skipped": False,
                        "message": f"Value must be no more than {validation_rules['max_value']}."
                    }
            except ValueError:
                return {
                    "valid": False,
                    "skipped": False,
                    "message": "Please enter a valid number."
                }
        
        return {
            "valid": True,
            "skipped": False,
            "message": "Answer is valid."
        }
    
    async def _enhance_question(
        self, 
        system_prompt: str, 
        question: str, 
        context: str = "", 
        rag_content: list = None
    ) -> str:
        try:
            # Build the prompt parts safely
            prompt_parts = [
                "You are an expert AI assistant following this system prompt:",
                "",
                system_prompt,
                "",
                f"Current question to enhance: {question}",
                ""
            ]
            if context:
                prompt_parts.append("Context from previous answers:\n" + context)
                prompt_parts.append("")
            if rag_content:
                prompt_parts.append("Additional context from RAG files:\n" + "\n".join(rag_content))
                prompt_parts.append("")
            prompt_parts.append(
                "Please enhance this question to be more engaging, specific, and helpful. "
                "Make it conversational and encouraging. Return only the enhanced question, nothing else."
            )
            prompt = "\n".join(prompt_parts)

            # Use AI service manager for content generation
            enhanced = await self.ai_manager.generate_content(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500,
                service="openai"  # Prefer OpenAI for question enhancement
            )
            
            return enhanced if enhanced else question
            
        except Exception as e:
            logger.error(f"Error enhancing question: {e}")
            return question
    
    async def generate_module_summary(
        self, 
        module_id: str, 
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate a comprehensive summary for a completed module with rate limiting."""
        if module_id not in self.modules:
            raise ValueError(f"Module {module_id} not found")
        
        module = self.modules[module_id]
        
        try:
            # Build the summary prompt with proper newline handling
            template_part = ("Use this output template as a guide:\n" + module['output_template']) if module['output_template'] else ""
            rag_part = ("Additional context from RAG files:\n" + "\n".join(module['rag_content'])) if module['rag_content'] else ""
            
            prompt = f"""You are an expert AI assistant following this system prompt:

{module['system_prompt']}

The user has completed all questions for {module['name']}. Here are their answers:

{chr(10).join([f"Q{i+1}: {answer}" for i, answer in enumerate(answers.values())])}

{template_part}

{rag_part}

Please generate a comprehensive summary report that includes:
1. A detailed analysis of their responses
2. Key insights and recommendations
3. Next steps or action items
4. Any areas that might need clarification

Format the response as a professional report with clear sections and actionable insights."""

            # Add retry logic with exponential backoff for rate limiting
            max_retries = 3
            base_delay = 1
            
            for attempt in range(max_retries):
                try:
                    # Use AI service manager for content generation
                    summary = await self.ai_manager.generate_content(
                        prompt=prompt,
                        temperature=0.7,
                        max_tokens=2000,
                        service="openai"  # Prefer OpenAI for summary generation
                    )
                    
                    return {
                        "module_name": module["name"],
                        "module_id": module_id,
                        "summary": summary,
                        "answers": answers,
                        "completion_message": f"Congratulations! You've completed {module['name']}. Here's your comprehensive summary:"
                    }
                    
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limited, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise e
            
        except Exception as e:
            logger.error(f"Error generating module summary: {e}")
            return {
                "module_name": module["name"],
                "module_id": module_id,
                "summary": f"Module completed with {len(answers)} answers. Summary generation failed: {str(e)}",
                "answers": answers,
                "completion_message": f"You've completed {module['name']}!"
            }
    
    async def check_module_completion_ready(
        self, 
        module_id: str, 
        current_question: int
    ) -> bool:
        """Check if a module is ready for completion."""
        if module_id not in self.modules:
            return False
        
        questions = self.modules[module_id]["questions"]
        return current_question >= len(questions)
    
    def get_next_module(self, current_module_id: str) -> Optional[str]:
        """Get the next module in the sequence."""
        module_ids = list(self.modules.keys())
        try:
            current_index = module_ids.index(current_module_id)
            if current_index + 1 < len(module_ids):
                return module_ids[current_index + 1]
        except ValueError:
            pass
        return None
    
    async def generate_combined_summary(self, completed_modules: dict) -> str:
        """Generate a combined summary for all completed modules."""
        try:
            # Create a comprehensive prompt for combining all module summaries
            combined_prompt = """
            You are an expert business strategist. Below are summaries from different modules of a business development process.
            Please create a comprehensive, well-structured summary that ties everything together.
            
            Module Summaries:
            """
            
            for module_id, module_data in completed_modules.items():
                if isinstance(module_data, dict):
                    if "summary" in module_data:
                        # New format from All GPTs mode
                        combined_prompt += f"\n\n## {module_data.get('module_name', 'Module')}\n{module_data['summary']}"
                    else:
                        # Old format from traditional Q&A
                        combined_prompt += f"\n\n{str(module_data)}"
                else:
                    combined_prompt += f"\n\n{str(module_data)}"
            
            combined_prompt += """
            
            Please create a comprehensive summary that:
            1. Synthesizes all the information into a cohesive business strategy
            2. Highlights key insights and actionable recommendations
            3. Shows how all the pieces work together
            4. Is written in a professional, engaging tone
            5. Is structured with clear sections and bullet points where appropriate
            6. Includes a table of contents for easy navigation
            
            Format the response as a complete business strategy document with:
            - Executive Summary
            - Key Findings from Each Module
            - Strategic Recommendations
            - Action Plan
            - Next Steps
            
            Make it comprehensive and actionable for business owners.
            """
            
            # Use AI service manager for the combined summary
            response = await self.ai_manager.generate_text(
                prompt=combined_prompt,
                max_tokens=3000,
                temperature=0.7
            )
            
            return response.get("text", "Failed to generate combined summary")
            
        except Exception as e:
            logger.error(f"Error generating combined summary: {e}")
            return f"Error generating combined summary: {str(e)}"

    async def generate_welcome_message(self, module_id: str) -> str:
        """Generate a friendly welcome message for starting a conversational chat."""
        try:
            if module_id not in self.modules:
                return "Hi there! How can I assist you today?"
            
            module_info = self.modules[module_id]
            module_name = module_info["name"]
            
            # Generate contextual welcome message based on module
            if "Offer Clarifier" in module_name:
                welcome_prompt = """
                You are a friendly, helpful business assistant. The user is about to start working on defining their product or service offer.
                
                Generate a warm, welcoming message that:
                1. Greets them warmly and introduces yourself as their business assistant
                2. Explains that you're here to help them clarify their offer
                3. Mentions that you'll guide them through some questions to understand their business better
                4. Sounds natural and conversational, not robotic
                5. Encourages them to share what they're working on
                
                Start with something like "Hi 👋 I'm here to help!" and make it feel like a real conversation.
                Keep it friendly and under 3 sentences.
                """
            else:
                welcome_prompt = """
                You are a friendly, helpful business assistant. The user is about to start working on their business strategy.
                
                Generate a warm, welcoming message that:
                1. Greets them warmly and introduces yourself as their business assistant
                2. Explains that you're here to help them with their business development
                3. Mentions that you'll guide them through some questions to understand their needs better
                4. Sounds natural and conversational, not robotic
                5. Encourages them to share what they're working on
                
                Start with something like "Hi 👋 I'm here to help!" and make it feel like a real conversation.
                Keep it friendly and under 3 sentences.
                """
            
            response = await self.ai_manager.generate_text(
                prompt=welcome_prompt,
                max_tokens=150,
                temperature=0.8
            )
            
            return response.get("text", "Hi 👋 I'm here to help! Just let me know what you need support with today.")
            
        except Exception as e:
            logger.error(f"Error generating welcome message: {e}")
            return "Hi 👋 I'm here to help! Just let me know what you need support with today."

    async def process_conversational_message(
        self, 
        module_id: str, 
        current_question: int, 
        previous_answers: Dict[str, str], 
        user_message: str
    ) -> Dict[str, Any]:
        """Process a conversational message and determine the appropriate response."""
        try:
            questions = self.get_module_questions(module_id)
            
            # Check if module is complete
            if current_question >= len(questions):
                # Module is complete, generate summary
                summary_data = await self.generate_module_summary(module_id, previous_answers)
                return {
                    "message": "Great! I have all the information I need. Let me create a summary of what we've discussed.",
                    "is_question": False,
                    "module_complete": True,
                    "summary": summary_data.get("summary", ""),
                    "answer_provided": False
                }
            
            # Check if user wants to edit summary
            if any(keyword in user_message.lower() for keyword in ["edit", "update", "change", "modify", "summary"]):
                if previous_answers:
                    return {
                        "message": "I'd be happy to help you edit the summary! What would you like to change?",
                        "is_question": False,
                        "current_question": questions[current_question] if current_question < len(questions) else None,
                        "answer_provided": False
                    }
                else:
                    return {
                        "message": "We haven't created a summary yet. Let's continue with our conversation first!",
                        "is_question": False,
                        "current_question": questions[current_question] if current_question < len(questions) else None,
                        "answer_provided": False
                    }
            
            # Check if this is a valid answer to the current question
            validation_result = self.validate_answer(module_id, current_question, user_message)
            
            if validation_result["valid"]:
                # Valid answer provided
                next_question_idx = current_question + 1
                
                if next_question_idx >= len(questions):
                    # This was the last question
                    return {
                        "message": "Perfect! That's exactly what I needed to know. Let me create a comprehensive summary of everything we've discussed.",
                        "is_question": False,
                        "module_complete": True,
                        "answer_provided": True
                    }
                else:
                    # Move to next question with natural transition
                    next_question = questions[next_question_idx]
                    transition_message = await self._generate_natural_transition(
                        module_id, current_question, user_message, next_question
                    )
                    
                    return {
                        "message": transition_message,
                        "is_question": True,
                        "current_question": next_question,
                        "answer_provided": True
                    }
            else:
                # Invalid answer, ask for clarification
                clarification_message = await self._generate_clarification_message(
                    module_id, current_question, user_message, validation_result["message"]
                )
                
                return {
                    "message": clarification_message,
                    "is_question": True,
                    "current_question": questions[current_question],
                    "answer_provided": False
                }
                
        except Exception as e:
            logger.error(f"Error processing conversational message: {e}")
            return {
                "message": "I'm having trouble processing that. Could you please rephrase your response?",
                "is_question": True,
                "current_question": questions[current_question] if current_question < len(questions) else None,
                "answer_provided": False
            }

    async def _generate_natural_transition(
        self, 
        module_id: str, 
        current_question: int, 
        user_answer: str, 
        next_question: str
    ) -> str:
        """Generate a natural transition message between questions."""
        try:
            transition_prompt = f"""
            You are a friendly business assistant having a natural conversation with a client.
            
            The client just answered: "{user_answer}"
            
            Now you need to ask the next question: "{next_question}"
            
            Generate a natural, conversational transition that:
            1. Acknowledges their previous answer briefly and positively
            2. Smoothly introduces the next question
            3. Sounds like a real person, not a robot
            4. Keeps the conversation flowing naturally
            5. Is friendly and encouraging
            
            Make it sound like you're genuinely interested in their business and want to help them succeed.
            Keep it under 2 sentences and make it conversational.
            """
            
            response = await self.ai_manager.generate_text(
                prompt=transition_prompt,
                max_tokens=100,
                temperature=0.8
            )
            
            return response.get("text", f"Great! Now, {next_question}")
            
        except Exception as e:
            logger.error(f"Error generating natural transition: {e}")
            return f"Great! Now, {next_question}"

    async def _generate_clarification_message(
        self, 
        module_id: str, 
        current_question: int, 
        user_message: str, 
        validation_error: str
    ) -> str:
        """Generate a friendly clarification message when validation fails."""
        try:
            clarification_prompt = f"""
            You are a friendly business assistant. The user's response didn't quite match what you need.
            
            User's response: "{user_message}"
            What you need: "{validation_error}"
            Current question: "{self.get_module_questions(module_id)[current_question]}"
            
            Generate a friendly, helpful clarification message that:
            1. Acknowledges their response positively
            2. Gently explains what you need instead
            3. Provides a helpful example or suggestion
            4. Sounds encouraging, not critical
            5. Keeps the conversation friendly and supportive
            
            Make it sound like you're helping a friend, not correcting them.
            Keep it under 3 sentences.
            """
            
            response = await self.ai_manager.generate_text(
                prompt=clarification_prompt,
                max_tokens=150,
                temperature=0.8
            )
            
            return response.get("text", f"I appreciate your response! To help you better, could you please {validation_error}")
            
        except Exception as e:
            logger.error(f"Error generating clarification message: {e}")
            return f"I appreciate your response! To help you better, could you please {validation_error}"


# Global instance
chatbot_service = ChatbotService() 