# backend/src/lua_context_manager.py

from datetime import datetime, timedelta
import json
import threading

class LuaContextManager:
    """Gerenciador de contexto e memória de conversas da Lua"""
    
    def __init__(self):
        self.conversations = {}
        self.context_timeout = 3600  # 1 hora em segundos
        self.lock = threading.Lock()
        
    def get_session_id(self, user_id="default"):
        """Gera ou retorna ID da sessão atual"""
        return f"session_{user_id}_{datetime.now().strftime('%Y%m%d')}"
    
    def add_message(self, session_id, message, message_type="user", data=None):
        """Adiciona mensagem ao contexto da conversa"""
        with self.lock:
            if session_id not in self.conversations:
                self.conversations[session_id] = {
                    "messages": [],
                    "context": {},
                    "last_activity": datetime.now(),
                    "created_at": datetime.now()
                }
            
            message_entry = {
                "id": len(self.conversations[session_id]["messages"]) + 1,
                "text": message,
                "type": message_type,  # user, lua, command, response
                "timestamp": datetime.now().isoformat(),
                "data": data or {}
            }
            
            self.conversations[session_id]["messages"].append(message_entry)
            self.conversations[session_id]["last_activity"] = datetime.now()
            
            # Manter apenas as últimas 50 mensagens por sessão
            if len(self.conversations[session_id]["messages"]) > 50:
                self.conversations[session_id]["messages"] = self.conversations[session_id]["messages"][-50:]
    
    def get_conversation_history(self, session_id, limit=10):
        """Retorna histórico da conversa"""
        with self.lock:
            if session_id not in self.conversations:
                return []
            
            messages = self.conversations[session_id]["messages"]
            return messages[-limit:] if limit else messages
    
    def update_context(self, session_id, key, value):
        """Atualiza contexto da sessão"""
        with self.lock:
            if session_id not in self.conversations:
                self.conversations[session_id] = {
                    "messages": [],
                    "context": {},
                    "last_activity": datetime.now(),
                    "created_at": datetime.now()
                }
            
            self.conversations[session_id]["context"][key] = value
            self.conversations[session_id]["last_activity"] = datetime.now()
    
    def get_context(self, session_id, key=None):
        """Retorna contexto da sessão"""
        with self.lock:
            if session_id not in self.conversations:
                return None if key else {}
            
            context = self.conversations[session_id]["context"]
            return context.get(key) if key else context
    
    def analyze_context_for_command(self, session_id, command):
        """Analisa contexto para melhorar interpretação do comando"""
        context = self.get_context(session_id)
        recent_messages = self.get_conversation_history(session_id, limit=5)
        
        # Análise de contexto para comandos sequenciais
        enhanced_command = command
        context_hints = {}
        
        # Verificar se há funcionário mencionado recentemente
        for msg in reversed(recent_messages):
            if msg["type"] in ["command", "response"] and msg.get("data", {}).get("funcionario"):
                if not any(name in command.lower() for name in ["joão", "maria", "pedro", "ana", "carlos", "josé"]):
                    context_hints["last_employee"] = msg["data"]["funcionario"]
                    break
        
        # Verificar se há valor mencionado recentemente
        for msg in reversed(recent_messages):
            if msg["type"] in ["command", "response"] and msg.get("data", {}).get("valor"):
                if "r$" not in command.lower() and "reais" not in command.lower():
                    context_hints["last_value"] = msg["data"]["valor"]
                    break
        
        # Verificar padrões de comandos sequenciais
        if len(recent_messages) >= 2:
            last_command = None
            for msg in reversed(recent_messages):
                if msg["type"] == "command":
                    last_command = msg["text"]
                    break
            
            if last_command:
                # Comandos de continuação
                if command.lower() in ["sim", "confirma", "ok", "continua"]:
                    enhanced_command = f"confirma: {last_command}"
                elif command.lower() in ["não", "cancela", "para"]:
                    enhanced_command = f"cancela: {last_command}"
                elif "também" in command.lower() or "igual" in command.lower():
                    enhanced_command = f"{command} (baseado em: {last_command})"
        
        return enhanced_command, context_hints
    
    def cleanup_old_sessions(self):
        """Remove sessões antigas para economizar memória"""
        with self.lock:
            cutoff_time = datetime.now() - timedelta(seconds=self.context_timeout)
            sessions_to_remove = []
            
            for session_id, session_data in self.conversations.items():
                if session_data["last_activity"] < cutoff_time:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self.conversations[session_id]
    
    def get_session_summary(self, session_id):
        """Retorna resumo da sessão"""
        with self.lock:
            if session_id not in self.conversations:
                return None
            
            session = self.conversations[session_id]
            
            # Contar tipos de mensagens
            message_counts = {"user": 0, "lua": 0, "command": 0, "response": 0}
            successful_commands = 0
            failed_commands = 0
            
            for msg in session["messages"]:
                msg_type = msg.get("type", "user")
                message_counts[msg_type] = message_counts.get(msg_type, 0) + 1
                
                if msg_type == "response":
                    if msg.get("data", {}).get("status") == "success":
                        successful_commands += 1
                    elif msg.get("data", {}).get("status") == "error":
                        failed_commands += 1
            
            return {
                "session_id": session_id,
                "created_at": session["created_at"].isoformat(),
                "last_activity": session["last_activity"].isoformat(),
                "total_messages": len(session["messages"]),
                "message_counts": message_counts,
                "successful_commands": successful_commands,
                "failed_commands": failed_commands,
                "context_keys": list(session["context"].keys())
            }
    
    def export_conversation(self, session_id):
        """Exporta conversa para análise ou backup"""
        with self.lock:
            if session_id not in self.conversations:
                return None
            
            return {
                "session_id": session_id,
                "exported_at": datetime.now().isoformat(),
                "conversation": self.conversations[session_id]
            }

# Instância global do gerenciador de contexto
context_manager = LuaContextManager()

