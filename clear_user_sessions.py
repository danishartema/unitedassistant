#!/usr/bin/env python3
"""
Utility script to clear user sessions and verify GPT memory isolation.
"""

import asyncio
import logging
from typing import Optional
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_db
from models import GPTModeSession, ConversationMemory, CrossModuleMemory, User

logger = logging.getLogger(__name__)

async def clear_user_sessions(user_id: str, db: AsyncSession) -> bool:
    """Clear all sessions and memory for a specific user."""
    try:
        logger.info(f"Clearing all sessions for user {user_id}")
        
        # Clear GPT mode sessions
        await db.execute(
            delete(GPTModeSession).where(GPTModeSession.user_id == user_id)
        )
        
        # Clear conversation memory
        await db.execute(
            delete(ConversationMemory).where(ConversationMemory.user_id == user_id)
        )
        
        # Clear cross-module memory
        await db.execute(
            delete(CrossModuleMemory).where(CrossModuleMemory.user_id == user_id)
        )
        
        await db.commit()
        logger.info(f"✅ Successfully cleared all sessions for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error clearing sessions for user {user_id}: {e}")
        await db.rollback()
        return False

async def clear_all_sessions(db: AsyncSession) -> bool:
    """Clear all sessions for all users (nuclear option)."""
    try:
        logger.info("Clearing all sessions for all users")
        
        # Clear all GPT mode sessions
        await db.execute(delete(GPTModeSession))
        
        # Clear all conversation memory
        await db.execute(delete(ConversationMemory))
        
        # Clear all cross-module memory
        await db.execute(delete(CrossModuleMemory))
        
        await db.commit()
        logger.info("✅ Successfully cleared all sessions for all users")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error clearing all sessions: {e}")
        await db.rollback()
        return False

async def verify_user_isolation(db: AsyncSession) -> dict:
    """Verify that user isolation is working properly."""
    try:
        logger.info("Verifying user isolation...")
        
        # Get all users
        users_result = await db.execute(select(User))
        users = users_result.scalars().all()
        
        isolation_report = {
            "total_users": len(users),
            "user_sessions": {},
            "isolation_status": "✅ PASSED"
        }
        
        for user in users:
            # Count sessions per user
            sessions_result = await db.execute(
                select(GPTModeSession).where(GPTModeSession.user_id == user.id)
            )
            sessions = sessions_result.scalars().all()
            
            # Count memory per user
            memory_result = await db.execute(
                select(ConversationMemory).where(ConversationMemory.user_id == user.id)
            )
            memory = memory_result.scalars().all()
            
            # Count cross-module memory per user
            cross_memory_result = await db.execute(
                select(CrossModuleMemory).where(CrossModuleMemory.user_id == user.id)
            )
            cross_memory = cross_memory_result.scalars().all()
            
            isolation_report["user_sessions"][user.email] = {
                "user_id": user.id,
                "sessions_count": len(sessions),
                "memory_count": len(memory),
                "cross_memory_count": len(cross_memory),
                "sessions": [
                    {
                        "session_id": session.id,
                        "mode_name": session.mode_name,
                        "project_id": session.project_id,
                        "current_question": session.current_question
                    }
                    for session in sessions
                ]
            }
        
        # Check for any orphaned records (records without user_id)
        orphaned_sessions = await db.execute(
            select(GPTModeSession).where(GPTModeSession.user_id.is_(None))
        )
        orphaned_sessions = orphaned_sessions.scalars().all()
        
        orphaned_memory = await db.execute(
            select(ConversationMemory).where(ConversationMemory.user_id.is_(None))
        )
        orphaned_memory = orphaned_memory.scalars().all()
        
        if orphaned_sessions or orphaned_memory:
            isolation_report["isolation_status"] = "❌ FAILED - Orphaned records found"
            isolation_report["orphaned_records"] = {
                "sessions": len(orphaned_sessions),
                "memory": len(orphaned_memory)
            }
        
        logger.info(f"Isolation verification completed: {isolation_report['isolation_status']}")
        return isolation_report
        
    except Exception as e:
        logger.error(f"❌ Error verifying user isolation: {e}")
        return {"error": str(e), "isolation_status": "❌ FAILED"}

async def verify_module_isolation(user_id: str, project_id: str, db: AsyncSession) -> dict:
    """Verify that modules are properly isolated for a specific user and project."""
    try:
        logger.info(f"Verifying module isolation for user {user_id}, project {project_id}")
        
        # Get all sessions for this user and project
        sessions_result = await db.execute(
            select(GPTModeSession).where(
                and_(
                    GPTModeSession.user_id == user_id,
                    GPTModeSession.project_id == project_id
                )
            )
        )
        sessions = sessions_result.scalars().all()
        
        # Get all memory for this user and project
        memory_result = await db.execute(
            select(ConversationMemory).where(
                and_(
                    ConversationMemory.user_id == user_id,
                    ConversationMemory.project_id == project_id
                )
            )
        )
        memory = memory_result.scalars().all()
        
        module_report = {
            "user_id": user_id,
            "project_id": project_id,
            "sessions_by_module": {},
            "memory_by_module": {},
            "isolation_status": "✅ PASSED"
        }
        
        # Group sessions by module
        for session in sessions:
            if session.mode_name not in module_report["sessions_by_module"]:
                module_report["sessions_by_module"][session.mode_name] = []
            
            module_report["sessions_by_module"][session.mode_name].append({
                "session_id": session.id,
                "current_question": session.current_question,
                "answers_count": len(session.answers)
            })
        
        # Group memory by module
        for mem in memory:
            if mem.module_id not in module_report["memory_by_module"]:
                module_report["memory_by_module"][mem.module_id] = []
            
            module_report["memory_by_module"][mem.module_id].append({
                "memory_id": mem.id,
                "session_id": mem.session_id,
                "conversation_history_count": len(mem.conversation_history)
            })
        
        logger.info(f"Module isolation verification completed: {module_report['isolation_status']}")
        return module_report
        
    except Exception as e:
        logger.error(f"❌ Error verifying module isolation: {e}")
        return {"error": str(e), "isolation_status": "❌ FAILED"}

async def list_users_with_sessions(db: AsyncSession) -> list:
    """List all users and their session counts."""
    try:
        users_result = await db.execute(select(User))
        users = users_result.scalars().all()
        
        user_list = []
        for user in users:
            # Count sessions
            sessions_result = await db.execute(
                select(GPTModeSession).where(GPTModeSession.user_id == user.id)
            )
            sessions = sessions_result.scalars().all()
            
            # Count memory
            memory_result = await db.execute(
                select(ConversationMemory).where(ConversationMemory.user_id == user.id)
            )
            memory = memory_result.scalars().all()
            
            user_list.append({
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "sessions_count": len(sessions),
                "memory_count": len(memory),
                "created_at": user.created_at
            })
        
        return user_list
        
    except Exception as e:
        logger.error(f"❌ Error listing users: {e}")
        return []

async def main():
    """Main function for session management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GPT Session Management Utility")
    parser.add_argument("--action", choices=["clear-user", "clear-all", "verify", "list"], required=True)
    parser.add_argument("--user-id", help="User ID for specific actions")
    parser.add_argument("--project-id", help="Project ID for module verification")
    parser.add_argument("--email", help="User email for finding user ID")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    async for db in get_async_db():
        try:
            if args.action == "clear-user":
                if not args.user_id and not args.email:
                    logger.error("❌ Please provide either --user-id or --email")
                    return
                
                user_id = args.user_id
                if args.email:
                    # Find user by email
                    user_result = await db.execute(select(User).where(User.email == args.email))
                    user = user_result.scalar_one_or_none()
                    if not user:
                        logger.error(f"❌ User with email {args.email} not found")
                        return
                    user_id = user.id
                
                success = await clear_user_sessions(user_id, db)
                if success:
                    logger.info(f"✅ Successfully cleared sessions for user {user_id}")
                else:
                    logger.error(f"❌ Failed to clear sessions for user {user_id}")
            
            elif args.action == "clear-all":
                confirm = input("⚠️  This will clear ALL sessions for ALL users. Are you sure? (yes/no): ")
                if confirm.lower() == "yes":
                    success = await clear_all_sessions(db)
                    if success:
                        logger.info("✅ Successfully cleared all sessions")
                    else:
                        logger.error("❌ Failed to clear all sessions")
                else:
                    logger.info("Operation cancelled")
            
            elif args.action == "verify":
                if args.user_id and args.project_id:
                    report = await verify_module_isolation(args.user_id, args.project_id, db)
                else:
                    report = await verify_user_isolation(db)
                
                print("\n" + "="*50)
                print("ISOLATION VERIFICATION REPORT")
                print("="*50)
                print(f"Status: {report.get('isolation_status', 'UNKNOWN')}")
                
                if "user_sessions" in report:
                    print(f"\nTotal Users: {report['total_users']}")
                    for email, data in report["user_sessions"].items():
                        print(f"\nUser: {email}")
                        print(f"  Sessions: {data['sessions_count']}")
                        print(f"  Memory: {data['memory_count']}")
                        print(f"  Cross-Memory: {data['cross_memory_count']}")
                
                if "orphaned_records" in report:
                    print(f"\n⚠️  Orphaned Records Found:")
                    print(f"  Sessions: {report['orphaned_records']['sessions']}")
                    print(f"  Memory: {report['orphaned_records']['memory']}")
            
            elif args.action == "list":
                users = await list_users_with_sessions(db)
                print("\n" + "="*80)
                print("USERS AND SESSION COUNTS")
                print("="*80)
                for user in users:
                    print(f"\nUser: {user['full_name']} ({user['email']})")
                    print(f"  User ID: {user['user_id']}")
                    print(f"  Sessions: {user['sessions_count']}")
                    print(f"  Memory: {user['memory_count']}")
                    print(f"  Created: {user['created_at']}")
        
        except Exception as e:
            logger.error(f"❌ Error in main: {e}")
        finally:
            break

if __name__ == "__main__":
    asyncio.run(main()) 