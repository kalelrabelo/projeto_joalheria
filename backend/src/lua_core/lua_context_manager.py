import time
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """Representa um turno de conversa"""
    timestamp: datetime
    user_input: str
    ai_response: str
    intent: str
    confidence: float
    tokens_used: int = 0
    
    def __post_init__(self):
        # Mascarar dados sensíveis no input
        self.user_input = self._mask_sensitive_data(self.user_input)
    
    def _mask_sensitive_data(self, text: str) -> str:
        """Mascarar dados sensíveis como CPF, telefone, etc."""
        # Mascarar CPF (xxx.xxx.xxx-xx)
        text = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', 'XXX.XXX.XXX-XX', text)
        
        # Mascarar telefone ((xx) xxxxx-xxxx)
        text = re.sub(r'\(\d{2}\)\s*\d{4,5}-\d{4}', '(XX) XXXXX-XXXX', text)
        
        # Mascarar email
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email@masked.com', text)
        
        return text

@dataclass
class UserSession:
    """Sessão de usuário com contexto e limites"""
    user_id: int
    session_id: str
    created_at: datetime
    last_activity: datetime
    conversation_turns: List[ConversationTurn] = field(default_factory=list)
    total_tokens: int = 0
    request_count: int = 0
    
    # Configurações de limite
    max_turns: int = 50
    max_tokens: int = 10000
    max_requests_per_hour: int = 100
    ttl_minutes: int = 60
    
    def is_expired(self) -> bool:
        """Verificar se a sessão expirou"""
        expiry_time = self.last_activity + timedelta(minutes=self.ttl_minutes)
        return datetime.now() > expiry_time
    
    def is_within_limits(self) -> Tuple[bool, str]:
        """Verificar se está dentro dos limites"""
        # Verificar número de turnos
        if len(self.conversation_turns) >= self.max_turns:
            return False, f"Limite de {self.max_turns} turnos de conversa atingido"
        
        # Verificar tokens
        if self.total_tokens >= self.max_tokens:
            return False, f"Limite de {self.max_tokens} tokens atingido"
        
        # Verificar rate limiting (requests por hora)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_requests = sum(1 for turn in self.conversation_turns 
                            if turn.timestamp > one_hour_ago)
        
        if recent_requests >= self.max_requests_per_hour:
            return False, f"Limite de {self.max_requests_per_hour} requests por hora atingido"
        
        return True, ""
    
    def add_turn(self, user_input: str, ai_response: str, intent: str, 
                confidence: float, tokens_used: int = 0):
        """Adicionar novo turno à conversa"""
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_input=user_input,
            ai_response=ai_response,
            intent=intent,
            confidence=confidence,
            tokens_used=tokens_used
        )
        
        self.conversation_turns.append(turn)
        self.total_tokens += tokens_used
        self.request_count += 1
        self.last_activity = datetime.now()
    
    def get_context_summary(self, max_turns: int = 5) -> str:
        """Obter resumo do contexto recente"""
        recent_turns = self.conversation_turns[-max_turns:]
        
        context_parts = []
        for turn in recent_turns:
            context_parts.append(f"Usuário: {turn.user_input}")
            context_parts.append(f"Assistente: {turn.ai_response}")
        
        return "\n".join(context_parts)
    
    def purge_old_data(self, retention_minutes: int = 30):
        """Purgar dados antigos para privacidade"""
        cutoff_time = datetime.now() - timedelta(minutes=retention_minutes)
        
        # Remover turnos antigos
        self.conversation_turns = [
            turn for turn in self.conversation_turns 
            if turn.timestamp > cutoff_time
        ]
        
        # Recalcular tokens
        self.total_tokens = sum(turn.tokens_used for turn in self.conversation_turns)

class LuaContextManager:
    """Gerenciador de contexto e sessões da IA Lua"""
    
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.cleanup_interval = 300  # 5 minutos
        self.last_cleanup = time.time()
        
        # Configurações de privacidade
        self.pii_retention_minutes = 30
        self.session_cleanup_minutes = 120
        
        # Métricas
        self.total_sessions_created = 0
        self.total_requests_processed = 0
        self.total_tokens_used = 0
    
    def get_or_create_session(self, user_id: int, session_id: str = None) -> UserSession:
        """Obter ou criar sessão do usuário"""
        if session_id is None:
            session_id = f"user_{user_id}_{int(time.time())}"
        
        # Verificar se sessão existe e não expirou
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if not session.is_expired():
                return session
            else:
                # Remover sessão expirada
                del self.sessions[session_id]
        
        # Criar nova sessão
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.sessions[session_id] = session
        self.total_sessions_created += 1
        
        logger.info(f"Nova sessão criada: {session_id} para usuário {user_id}")
        return session
    
    def process_request(self, user_id: int, user_input: str, ai_response: str, 
                       intent: str, confidence: float, tokens_used: int = 0,
                       session_id: str = None) -> Dict[str, Any]:
        """Processar request e atualizar contexto"""
        
        # Obter sessão
        session = self.get_or_create_session(user_id, session_id)
        
        # Verificar limites
        within_limits, limit_message = session.is_within_limits()
        if not within_limits:
            logger.warning(f"Limite atingido para usuário {user_id}: {limit_message}")
            return {
                "success": False,
                "error": limit_message,
                "session_id": session.session_id
            }
        
        # Adicionar turno à conversa
        session.add_turn(user_input, ai_response, intent, confidence, tokens_used)
        
        # Atualizar métricas globais
        self.total_requests_processed += 1
        self.total_tokens_used += tokens_used
        
        # Cleanup periódico
        self._periodic_cleanup()
        
        return {
            "success": True,
            "session_id": session.session_id,
            "context_summary": session.get_context_summary(),
            "tokens_used": tokens_used,
            "total_tokens": session.total_tokens,
            "turns_count": len(session.conversation_turns)
        }
    
    def get_session_context(self, session_id: str, max_turns: int = 5) -> Optional[str]:
        """Obter contexto da sessão"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        if session.is_expired():
            del self.sessions[session_id]
            return None
        
        return session.get_context_summary(max_turns)
    
    def _periodic_cleanup(self):
        """Limpeza periódica de sessões e dados"""
        current_time = time.time()
        
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        # Remover sessões expiradas
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Sessão expirada removida: {session_id}")
        
        # Purgar dados antigos das sessões ativas
        for session in self.sessions.values():
            session.purge_old_data(self.pii_retention_minutes)
        
        self.last_cleanup = current_time
        
        if expired_sessions:
            logger.info(f"Cleanup concluído: {len(expired_sessions)} sessões removidas")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obter métricas do sistema"""
        active_sessions = len(self.sessions)
        total_active_tokens = sum(session.total_tokens for session in self.sessions.values())
        
        return {
            "active_sessions": active_sessions,
            "total_sessions_created": self.total_sessions_created,
            "total_requests_processed": self.total_requests_processed,
            "total_tokens_used": self.total_tokens_used,
            "active_tokens": total_active_tokens,
            "average_tokens_per_session": total_active_tokens / max(active_sessions, 1)
        }
    
    def force_cleanup_user_data(self, user_id: int):
        """Forçar limpeza de dados de um usuário específico"""
        sessions_to_remove = [
            session_id for session_id, session in self.sessions.items()
            if session.user_id == user_id
        ]
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        logger.info(f"Dados do usuário {user_id} removidos: {len(sessions_to_remove)} sessões")
        return len(sessions_to_remove)

