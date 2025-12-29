"""
Firebase Service

This module provides Firebase integration for user authentication and data persistence.
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import Dict, Any, Optional, List
from datetime import datetime
import os


class FirebaseService:
    """
    Service for Firebase operations including authentication and Firestore database.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase Admin SDK (singleton pattern)"""
        if not FirebaseService._initialized:
            try:
                # Path to service account credentials
                cred_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'firebase-credentials.json'
                )
                
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    self.db = firestore.client()
                    FirebaseService._initialized = True
                    print("✅ Firebase initialized successfully")
                else:
                    print(f"⚠️  Firebase credentials not found at {cred_path}")
                    self.db = None
            except Exception as e:
                print(f"❌ Error initializing Firebase: {e}")
                self.db = None
    
    # ==================== User Management ====================
    
    def create_user(self, email: str, password: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new user in Firebase Authentication.
        
        Args:
            email: User email
            password: User password
            display_name: Optional display name
        
        Returns:
            Dict with user information
        """
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            
            # Create user profile in Firestore
            self.db.collection('users').document(user.uid).set({
                'email': email,
                'display_name': display_name or email.split('@')[0],
                'created_at': firestore.SERVER_TIMESTAMP,
                'total_assessments': 0,
                'total_questions_answered': 0,
                'average_score': 0.0
            })
            
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': display_name
            }
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from Firebase.
        
        Args:
            uid: User ID
        
        Returns:
            User data or None
        """
        try:
            user = auth.get_user(uid)
            user_doc = self.db.collection('users').document(uid).get()
            
            if user_doc.exists:
                return {
                    'uid': user.uid,
                    'email': user.email,
                    'display_name': user.display_name,
                    **user_doc.to_dict()
                }
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token.
        
        Args:
            id_token: Firebase ID token from client
        
        Returns:
            Decoded token or None
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None
    
    # ==================== Session Management ====================
    
    def save_session(
        self,
        user_id: str,
        session_id: str,
        topic: str,
        difficulty: str,
        questions: List[Dict[str, Any]],
        performance_history: List[Dict[str, Any]]
    ) -> bool:
        """
        Save assessment session to Firestore.
        
        Args:
            user_id: User ID
            session_id: Session ID
            topic: Assessment topic
            difficulty: Current difficulty
            questions: List of questions with answers
            performance_history: Performance records
        
        Returns:
            Success status
        """
        try:
            session_data = {
                'user_id': user_id,
                'session_id': session_id,
                'topic': topic,
                'difficulty': difficulty,
                'questions': questions,
                'performance_history': performance_history,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'status': 'in_progress'
            }
            
            self.db.collection('sessions').document(session_id).set(session_data)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session from Firestore.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session data or None
        """
        try:
            doc = self.db.collection('sessions').document(session_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update session in Firestore.
        
        Args:
            session_id: Session ID
            updates: Fields to update
        
        Returns:
            Success status
        """
        try:
            updates['updated_at'] = firestore.SERVER_TIMESTAMP
            self.db.collection('sessions').document(session_id).update(updates)
            return True
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    def complete_session(
        self,
        session_id: str,
        total_questions: int,
        correct_answers: int,
        average_score: float
    ) -> bool:
        """
        Mark session as complete and update user statistics.
        
        Args:
            session_id: Session ID
            total_questions: Total questions answered
            correct_answers: Number of correct answers
            average_score: Average score
        
        Returns:
            Success status
        """
        try:
            # Update session status
            self.db.collection('sessions').document(session_id).update({
                'status': 'completed',
                'completed_at': firestore.SERVER_TIMESTAMP,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'average_score': average_score
            })
            
            # Get session to find user_id
            session = self.get_session(session_id)
            if session and 'user_id' in session:
                # Update user statistics
                user_ref = self.db.collection('users').document(session['user_id'])
                user_ref.update({
                    'total_assessments': firestore.Increment(1),
                    'total_questions_answered': firestore.Increment(total_questions),
                    'last_assessment_date': firestore.SERVER_TIMESTAMP
                })
            
            return True
        except Exception as e:
            print(f"Error completing session: {e}")
            return False
    
    def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's assessment sessions.
        
        Args:
            user_id: User ID
            limit: Maximum number of sessions to return
            status: Filter by status (in_progress, completed)
        
        Returns:
            List of sessions
        """
        try:
            query = self.db.collection('sessions').where('user_id', '==', user_id)
            
            if status:
                query = query.where('status', '==', status)
            
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
    
    # ==================== Leaderboard ====================
    
    def get_leaderboard(self, topic: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get leaderboard data.
        
        Args:
            topic: Filter by topic (optional)
            limit: Number of top users to return
        
        Returns:
            List of top users with scores
        """
        try:
            query = self.db.collection('sessions').where('status', '==', 'completed')
            
            if topic:
                query = query.where('topic', '==', topic)
            
            query = query.order_by('average_score', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            leaderboard = []
            
            for doc in docs:
                data = doc.to_dict()
                user = self.get_user(data.get('user_id'))
                if user:
                    leaderboard.append({
                        'display_name': user.get('display_name', 'Anonymous'),
                        'topic': data.get('topic'),
                        'average_score': data.get('average_score'),
                        'total_questions': data.get('total_questions'),
                        'correct_answers': data.get('correct_answers')
                    })
            
            return leaderboard
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []


# Singleton instance
firebase_service = FirebaseService()
