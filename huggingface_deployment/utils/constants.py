"""
Constants and configuration for the application.
"""

# Phase templates for the 14-phase workflow
PHASE_TEMPLATES = [
    {
        "title": "Project Overview",
        "description": "Define the project scope, objectives, and high-level requirements.",
        "prompt_template": """
Please provide a comprehensive project overview that includes:
1. Project objectives and goals
2. Target audience and stakeholders
3. High-level requirements
4. Success criteria
5. Key constraints and assumptions

User Input: {user_input}

Based on this information, create a detailed project overview that will guide the subsequent phases of development.
"""
    },
    {
        "title": "Requirements Analysis",
        "description": "Detailed analysis of functional and non-functional requirements.",
        "prompt_template": """
Based on the project overview, analyze and document detailed requirements:
1. Functional requirements (what the system should do)
2. Non-functional requirements (performance, security, usability)
3. Business rules and constraints
4. User stories or use cases
5. Acceptance criteria

User Input: {user_input}

Context from previous phases will help inform this analysis.
"""
    },
    {
        "title": "Stakeholder Analysis",
        "description": "Identify and analyze all project stakeholders and their interests.",
        "prompt_template": """
Conduct a comprehensive stakeholder analysis:
1. Identify all stakeholders (internal and external)
2. Analyze stakeholder interests and influence
3. Define communication strategies
4. Identify potential conflicts and mitigation strategies
5. Create stakeholder engagement plan

User Input: {user_input}
"""
    },
    {
        "title": "Risk Assessment",
        "description": "Identify, analyze, and plan mitigation strategies for project risks.",
        "prompt_template": """
Perform a thorough risk assessment:
1. Identify potential risks (technical, business, operational)
2. Assess probability and impact of each risk
3. Categorize risks by severity
4. Develop mitigation and contingency plans
5. Define risk monitoring strategies

User Input: {user_input}
"""
    },
    {
        "title": "Technical Architecture",
        "description": "Design the technical architecture and system components.",
        "prompt_template": """
Design the technical architecture:
1. System architecture overview
2. Technology stack selection and justification
3. Component design and interactions
4. Data architecture and flow
5. Integration points and APIs
6. Security architecture considerations

User Input: {user_input}
"""
    },
    {
        "title": "Implementation Plan",
        "description": "Create detailed implementation timeline and resource allocation.",
        "prompt_template": """
Develop a comprehensive implementation plan:
1. Project timeline and milestones
2. Resource allocation and team structure
3. Development methodology and processes
4. Quality assurance strategy
5. Deployment and rollout plan
6. Dependencies and critical path analysis

User Input: {user_input}
"""
    },
    {
        "title": "User Experience Design",
        "description": "Design user interfaces and experience workflows.",
        "prompt_template": """
Create user experience design:
1. User personas and journey mapping
2. Information architecture
3. Wireframes and user interface design
4. Interaction design and user flows
5. Accessibility considerations
6. Usability testing plan

User Input: {user_input}
"""
    },
    {
        "title": "Data Management Strategy",
        "description": "Define data models, storage, and management approaches.",
        "prompt_template": """
Develop data management strategy:
1. Data model design and relationships
2. Data storage and database design
3. Data governance and quality standards
4. Backup and recovery procedures
5. Data privacy and compliance
6. Data migration and integration plans

User Input: {user_input}
"""
    },
    {
        "title": "Security Framework",
        "description": "Establish security requirements and implementation strategy.",
        "prompt_template": """
Design comprehensive security framework:
1. Security requirements and threat model
2. Authentication and authorization strategy
3. Data encryption and protection
4. Security monitoring and incident response
5. Compliance requirements
6. Security testing and validation

User Input: {user_input}
"""
    },
    {
        "title": "Testing Strategy",
        "description": "Define comprehensive testing approach and procedures.",
        "prompt_template": """
Create detailed testing strategy:
1. Testing methodology and types
2. Test planning and case development
3. Automated testing framework
4. Performance and load testing
5. Security testing procedures
6. User acceptance testing plan

User Input: {user_input}
"""
    },
    {
        "title": "Deployment Strategy",
        "description": "Plan deployment procedures and infrastructure requirements.",
        "prompt_template": """
Develop deployment strategy:
1. Infrastructure requirements and architecture
2. Deployment automation and CI/CD pipeline
3. Environment management (dev, staging, production)
4. Monitoring and alerting systems
5. Rollback and disaster recovery procedures
6. Performance optimization and scaling

User Input: {user_input}
"""
    },
    {
        "title": "Maintenance Plan",
        "description": "Define ongoing maintenance and support procedures.",
        "prompt_template": """
Create maintenance and support plan:
1. Ongoing maintenance procedures
2. Support team structure and responsibilities
3. Issue tracking and resolution processes
4. Update and patch management
5. Performance monitoring and optimization
6. Documentation and knowledge management

User Input: {user_input}
"""
    },
    {
        "title": "Documentation Package",
        "description": "Compile comprehensive project documentation.",
        "prompt_template": """
Compile comprehensive documentation package:
1. Technical documentation and API references
2. User manuals and training materials
3. System administration guides
4. Troubleshooting and FAQ documents
5. Code documentation and comments
6. Process and procedure documentation

User Input: {user_input}
"""
    },
    {
        "title": "Project Closure",
        "description": "Final project review, lessons learned, and transition planning.",
        "prompt_template": """
Complete project closure activities:
1. Project success evaluation against objectives
2. Lessons learned and best practices
3. Knowledge transfer and handover procedures
4. Team recognition and feedback
5. Final deliverables and acceptance
6. Post-implementation review planning

User Input: {user_input}
"""
    }
]

# Export file extensions
EXPORT_EXTENSIONS = {
    "pdf": ".pdf",
    "word": ".docx",
    "json": ".json"
}

# Maximum file sizes
MAX_EXPORT_SIZE = 50 * 1024 * 1024  # 50MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024   # 10MB

# Rate limiting configuration
RATE_LIMITS = {
    "login": {"max_requests": 5, "window_seconds": 300},  # 5 attempts per 5 minutes
    "register": {"max_requests": 3, "window_seconds": 3600},  # 3 attempts per hour
    "export": {"max_requests": 10, "window_seconds": 3600},  # 10 exports per hour
    "generate": {"max_requests": 30, "window_seconds": 3600}  # 30 generations per hour
}

# OpenAI configuration
OPENAI_CONFIG = {
    "max_tokens": 2000,
    "temperature_range": (0.0, 1.0),
    "max_context_length": 8000,
    "embedding_dimensions": 1536
}

# Database configuration
DB_CONFIG = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600
}

# Cache configuration
CACHE_CONFIG = {
    "default_timeout": 3600,  # 1 hour
    "embedding_timeout": 86400,  # 24 hours
    "user_session_timeout": 1800  # 30 minutes
}
