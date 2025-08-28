import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

@dataclass
class LLMMetrics:
    """Métricas de chamadas LLM"""
    timestamp: datetime
    user_id: int
    session_id: str
    intent: str
    confidence: float
    latency_ms: float
    tokens_input: int
    tokens_output: int
    tokens_total: int
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário para logging"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "intent": self.intent,
            "confidence": self.confidence,
            "latency_ms": self.latency_ms,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "tokens_total": self.tokens_total,
            "success": self.success,
            "error_type": self.error_type,
            "error_message": self.error_message
        }

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    active_sessions: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    total_tokens_used: int = 0
    requests_per_minute: float = 0.0
    error_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_sessions": self.active_sessions,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "average_latency_ms": self.average_latency_ms,
            "total_tokens_used": self.total_tokens_used,
            "requests_per_minute": self.requests_per_minute,
            "error_rate": self.error_rate
        }

class LuaObservability:
    """Sistema de observabilidade para IA Lua"""
    
    def __init__(self, max_metrics_history: int = 10000):
        self.max_metrics_history = max_metrics_history
        self.metrics_history: deque = deque(maxlen=max_metrics_history)
        self.user_metrics: Dict[int, List[LLMMetrics]] = defaultdict(list)
        self.intent_metrics: Dict[str, List[LLMMetrics]] = defaultdict(list)
        
        # Métricas em tempo real
        self.current_metrics = SystemMetrics()
        
        # Rate limiting tracking
        self.request_timestamps: deque = deque(maxlen=1000)
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Configurações de retenção
        self.metrics_retention_hours = 24
        self.user_metrics_retention_hours = 6
        
    def record_llm_call(self, user_id: int, session_id: str, intent: str, 
                       confidence: float, latency_ms: float, tokens_input: int,
                       tokens_output: int, success: bool, error_type: str = None,
                       error_message: str = None):
        """Registrar chamada LLM"""
        
        metric = LLMMetrics(
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            intent=intent,
            confidence=confidence,
            latency_ms=latency_ms,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_input + tokens_output,
            success=success,
            error_type=error_type,
            error_message=error_message
        )
        
        with self.lock:
            # Adicionar às métricas históricas
            self.metrics_history.append(metric)
            self.user_metrics[user_id].append(metric)
            self.intent_metrics[intent].append(metric)
            
            # Atualizar métricas em tempo real
            self._update_current_metrics(metric)
            
            # Adicionar timestamp para rate limiting
            self.request_timestamps.append(time.time())
        
        # Log estruturado (apenas metadados, sem conteúdo)
        logger.info("LLM call recorded", extra={
            "type": "llm_metrics",
            "data": metric.to_dict()
        })
    
    def _update_current_metrics(self, metric: LLMMetrics):
        """Atualizar métricas em tempo real"""
        self.current_metrics.total_requests += 1
        
        if metric.success:
            self.current_metrics.successful_requests += 1
        else:
            self.current_metrics.failed_requests += 1
        
        self.current_metrics.total_tokens_used += metric.tokens_total
        
        # Calcular latência média
        total_latency = (self.current_metrics.average_latency_ms * 
                        (self.current_metrics.total_requests - 1) + metric.latency_ms)
        self.current_metrics.average_latency_ms = total_latency / self.current_metrics.total_requests
        
        # Calcular taxa de erro
        if self.current_metrics.total_requests > 0:
            self.current_metrics.error_rate = (
                self.current_metrics.failed_requests / self.current_metrics.total_requests
            )
        
        # Calcular requests por minuto (últimos 60 segundos)
        current_time = time.time()
        recent_requests = sum(1 for ts in self.request_timestamps 
                            if current_time - ts <= 60)
        self.current_metrics.requests_per_minute = recent_requests
    
    def get_system_metrics(self) -> SystemMetrics:
        """Obter métricas do sistema"""
        with self.lock:
            return self.current_metrics
    
    def get_user_metrics(self, user_id: int, hours: int = 1) -> Dict[str, Any]:
        """Obter métricas de um usuário específico"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            user_metrics = [
                m for m in self.user_metrics[user_id] 
                if m.timestamp > cutoff_time
            ]
        
        if not user_metrics:
            return {
                "user_id": user_id,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0,
                "average_latency_ms": 0.0,
                "error_rate": 0.0
            }
        
        total_requests = len(user_metrics)
        successful_requests = sum(1 for m in user_metrics if m.success)
        failed_requests = total_requests - successful_requests
        total_tokens = sum(m.tokens_total for m in user_metrics)
        average_latency = sum(m.latency_ms for m in user_metrics) / total_requests
        error_rate = failed_requests / total_requests if total_requests > 0 else 0.0
        
        return {
            "user_id": user_id,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "total_tokens": total_tokens,
            "average_latency_ms": average_latency,
            "error_rate": error_rate,
            "period_hours": hours
        }
    
    def get_intent_metrics(self, intent: str, hours: int = 1) -> Dict[str, Any]:
        """Obter métricas de uma intenção específica"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            intent_metrics = [
                m for m in self.intent_metrics[intent] 
                if m.timestamp > cutoff_time
            ]
        
        if not intent_metrics:
            return {
                "intent": intent,
                "total_requests": 0,
                "average_confidence": 0.0,
                "success_rate": 0.0,
                "average_latency_ms": 0.0
            }
        
        total_requests = len(intent_metrics)
        average_confidence = sum(m.confidence for m in intent_metrics) / total_requests
        success_rate = sum(1 for m in intent_metrics if m.success) / total_requests
        average_latency = sum(m.latency_ms for m in intent_metrics) / total_requests
        
        return {
            "intent": intent,
            "total_requests": total_requests,
            "average_confidence": average_confidence,
            "success_rate": success_rate,
            "average_latency_ms": average_latency,
            "period_hours": hours
        }
    
    def get_error_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Obter resumo de erros"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            error_metrics = [
                m for m in self.metrics_history 
                if m.timestamp > cutoff_time and not m.success
            ]
        
        error_types = defaultdict(int)
        error_messages = defaultdict(int)
        
        for metric in error_metrics:
            if metric.error_type:
                error_types[metric.error_type] += 1
            if metric.error_message:
                error_messages[metric.error_message] += 1
        
        return {
            "total_errors": len(error_metrics),
            "error_types": dict(error_types),
            "common_error_messages": dict(sorted(error_messages.items(), 
                                                key=lambda x: x[1], reverse=True)[:10]),
            "period_hours": hours
        }
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Obter tendências de performance"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp > cutoff_time
            ]
        
        if not recent_metrics:
            return {"message": "Dados insuficientes para análise de tendências"}
        
        # Agrupar por hora
        hourly_data = defaultdict(list)
        for metric in recent_metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_data[hour_key].append(metric)
        
        trends = []
        for hour, metrics in sorted(hourly_data.items()):
            total_requests = len(metrics)
            successful_requests = sum(1 for m in metrics if m.success)
            average_latency = sum(m.latency_ms for m in metrics) / total_requests
            total_tokens = sum(m.tokens_total for m in metrics)
            
            trends.append({
                "hour": hour.isoformat(),
                "total_requests": total_requests,
                "success_rate": successful_requests / total_requests,
                "average_latency_ms": average_latency,
                "total_tokens": total_tokens
            })
        
        return {
            "trends": trends,
            "period_hours": hours
        }
    
    def cleanup_old_metrics(self):
        """Limpar métricas antigas"""
        cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
        user_cutoff_time = datetime.now() - timedelta(hours=self.user_metrics_retention_hours)
        
        with self.lock:
            # Limpar métricas de usuário
            for user_id in list(self.user_metrics.keys()):
                self.user_metrics[user_id] = [
                    m for m in self.user_metrics[user_id] 
                    if m.timestamp > user_cutoff_time
                ]
                
                # Remover usuários sem métricas recentes
                if not self.user_metrics[user_id]:
                    del self.user_metrics[user_id]
            
            # Limpar métricas de intenção
            for intent in list(self.intent_metrics.keys()):
                self.intent_metrics[intent] = [
                    m for m in self.intent_metrics[intent] 
                    if m.timestamp > cutoff_time
                ]
                
                if not self.intent_metrics[intent]:
                    del self.intent_metrics[intent]
        
        logger.info("Métricas antigas removidas", extra={
            "type": "metrics_cleanup",
            "cutoff_time": cutoff_time.isoformat()
        })
    
    def export_metrics(self, format: str = "json") -> Dict[str, Any]:
        """Exportar métricas para análise externa"""
        with self.lock:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "system_metrics": self.current_metrics.to_dict(),
                "total_metrics_records": len(self.metrics_history),
                "active_users": len(self.user_metrics),
                "tracked_intents": len(self.intent_metrics)
            }
        
        return export_data

