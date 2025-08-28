import logging
import json
import uuid
from datetime import datetime
from flask import request, g
from typing import Dict, Any

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adicionar ID de correlação se disponível
        if hasattr(g, 'correlation_id'):
            log_entry['correlation_id'] = g.correlation_id
        
        # Adicionar informações da requisição se disponível
        if request:
            try:
                log_entry['request'] = {
                    'method': request.method,
                    'path': request.path,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', '')
                }
            except RuntimeError:
                # Fora do contexto da aplicação
                pass
        
        # Adicionar dados extras se fornecidos
        if hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(app):
    """Configurar logging estruturado para a aplicação"""
    
    # Configurar formatter estruturado
    formatter = StructuredFormatter()
    
    # Handler para arquivo
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Handler para console (desenvolvimento)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Configurar logger da aplicação
    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Configurar logger do SQLAlchemy
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    return app.logger

def generate_correlation_id():
    """Gerar ID único para correlação de logs"""
    return str(uuid.uuid4())

def log_with_correlation(logger, level, message, extra_data=None):
    """Log com ID de correlação e dados extras"""
    record = logging.LogRecord(
        name=logger.name,
        level=level,
        pathname='',
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    
    if extra_data:
        record.extra_data = extra_data
    
    logger.handle(record)

class AuditLogger:
    """Logger específico para auditoria"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def log_user_action(self, user_id: int, action: str, resource: str, 
                       resource_id: int = None, details: Dict[str, Any] = None):
        """Log de ações do usuário para auditoria"""
        audit_data = {
            'type': 'user_action',
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'resource_id': resource_id,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        log_with_correlation(
            self.logger, 
            logging.INFO, 
            f"User {user_id} performed {action} on {resource}",
            audit_data
        )
    
    def log_system_event(self, event_type: str, details: Dict[str, Any] = None):
        """Log de eventos do sistema"""
        system_data = {
            'type': 'system_event',
            'event_type': event_type,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        log_with_correlation(
            self.logger,
            logging.INFO,
            f"System event: {event_type}",
            system_data
        )
    
    def log_security_event(self, event_type: str, user_id: int = None, 
                          ip_address: str = None, details: Dict[str, Any] = None):
        """Log de eventos de segurança"""
        security_data = {
            'type': 'security_event',
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        log_with_correlation(
            self.logger,
            logging.WARNING,
            f"Security event: {event_type}",
            security_data
        )

