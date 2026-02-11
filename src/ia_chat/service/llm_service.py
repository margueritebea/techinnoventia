"""
Service de gestion des LLM locaux avec llama-cpp-python
Supporte conversation contextualisée et streaming
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass

from llama_cpp import Llama

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration d'un modèle LLM"""
    name: str
    path: str
    context_size: int = 2048
    threads: int = 4
    temperature: float = 0.7
    max_tokens: int = 512


class LLMService:
    """
    Service singleton pour gérer les modèles LLM locaux
    Optimisé pour CPU uniquement (pas de GPU)
    Configuration via variables d'environnement (.env)
    """
    
    # Modèles disponibles (chemins depuis .env)
    MODELS = {
        'llama3': ModelConfig(
            name='Llama-3.2-3B-Instruct',
            path=os.getenv(
                'LLAMA3_MODEL_PATH',
                '/opt/kgm_models/Llama-3.2-3B-Instruct-Q4_K_M.gguf'
            ),
            context_size=int(os.getenv('LLM_CONTEXT_SIZE', '2048')),
            threads=int(os.getenv('LLM_THREADS', '4')),
        ),
        'mistral': ModelConfig(
            name='Mistral-Nemo-Instruct',
            path=os.getenv(
                'MISTRAL_MODEL_PATH',
                '/opt/kgm_models/Mistral-Nemo-Instruct-2407.Q5_K_M.gguf'
            ),
            context_size=int(os.getenv('LLM_CONTEXT_SIZE', '4096')),
            threads=int(os.getenv('LLM_THREADS', '4')),
        ),
        'qwen': ModelConfig(
            name='Qwen2-VL-7B-Instruct',
            path=os.getenv(
                'QWEN_MODEL_PATH',
                '/opt/kgm_models/Qwen2-VL-7B-Instruct-Q2_K.gguf'
            ),
            context_size=int(os.getenv('LLM_CONTEXT_SIZE', '2048')),
            threads=int(os.getenv('LLM_THREADS', '4')),
        ),
    }
    
    # Prompt système par défaut (français conversationnel)
    DEFAULT_SYSTEM_PROMPT = (
        "Tu es un assistant IA utile, amical et conversationnel. "
        "Réponds de manière naturelle, concise et pertinente. "
        "Si tu ne sais pas quelque chose, dis-le honnêtement. "
        "Adapte ton niveau de langue à l'utilisateur."
    )
    
    _instances: Dict[str, Llama] = {}
    
    @classmethod
    def get_model(cls, model_key: str = 'llama3') -> Llama:
        """
        Récupère ou charge un modèle LLM (pattern singleton par modèle)
        
        Args:
            model_key: Clé du modèle ('llama3', 'mistral', 'qwen')
        
        Returns:
            Instance Llama chargée en mémoire
        """
        if model_key not in cls.MODELS:
            raise ValueError(f"Modèle inconnu: {model_key}. Disponibles: {list(cls.MODELS.keys())}")
        
        # Singleton : charge une seule fois
        if model_key not in cls._instances:
            config = cls.MODELS[model_key]
            model_path = Path(config.path)
            
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Modèle non trouvé: {config.path}\n"
                    f"Vérifie que le fichier existe dans /opt/kgm_models/"
                )
            
            logger.info(f"Chargement du modèle {config.name} ({model_path.stat().st_size / 1e9:.2f} GB)...")
            
            try:
                cls._instances[model_key] = Llama(
                    model_path=str(model_path),
                    n_ctx=config.context_size,
                    n_threads=config.threads,
                    n_gpu_layers=0,  # CPU uniquement
                    verbose=False,
                )
                logger.info(f"✓ Modèle {config.name} chargé avec succès")
            except Exception as e:
                logger.error(f"✗ Erreur chargement modèle: {e}")
                raise
        
        return cls._instances[model_key]
    
    @classmethod
    def chat(
        cls,
        messages: List[Dict[str, str]],
        model_key: str = 'llama3',
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False,
        system_prompt: Optional[str] = None,
    ) -> str | Generator[str, None, None]:
        """
        Interface de chat conversationnel (compatible OpenAI format)
        
        Args:
            messages: Liste de messages [{"role": "user|assistant|system", "content": "..."}]
            model_key: Modèle à utiliser
            max_tokens: Nombre max de tokens générés
            temperature: Créativité (0.0 = déterministe, 1.0 = créatif)
            stream: Si True, retourne un générateur pour streaming
            system_prompt: Prompt système custom (écrase le défaut)
        
        Returns:
            Réponse complète (str) ou générateur de chunks (Generator)
        
        Example:
            >>> messages = [
            ...     {"role": "user", "content": "Bonjour, qui es-tu ?"}
            ... ]
            >>> response = LLMService.chat(messages)
            >>> print(response)
        """
        llm = cls.get_model(model_key)
        
        # Injection du système prompt si absent
        if not any(msg.get('role') == 'system' for msg in messages):
            system_msg = {
                'role': 'system',
                'content': system_prompt or cls.DEFAULT_SYSTEM_PROMPT
            }
            messages = [system_msg] + messages
        
        logger.debug(f"Chat with {len(messages)} messages (stream={stream})")
        
        try:
            response = llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                stop=["<|end|>", "<|endoftext|>"],  # Tokens de fin
            )
            
            if stream:
                # Générateur pour streaming
                def stream_generator():
                    for chunk in response:
                        delta = chunk['choices'][0]['delta']
                        if 'content' in delta:
                            yield delta['content']
                return stream_generator()
            else:
                # Réponse complète
                return response['choices'][0]['message']['content'].strip()
        
        except Exception as e:
            logger.error(f"Erreur génération: {e}")
            raise
    
    @classmethod
    def simple_query(
        cls,
        query: str,
        model_key: str = 'llama3',
        max_tokens: int = 512,
    ) -> str:
        """
        Requête simple sans historique (wrapper pour prototypage rapide)
        
        Args:
            query: Question de l'utilisateur
            model_key: Modèle à utiliser
            max_tokens: Tokens max
        
        Returns:
            Réponse du modèle
        """
        messages = [{"role": "user", "content": query}]
        return cls.chat(messages, model_key=model_key, max_tokens=max_tokens)
    
    @classmethod
    def unload_model(cls, model_key: str):
        """Décharge un modèle de la mémoire"""
        if model_key in cls._instances:
            del cls._instances[model_key]
            logger.info(f"Modèle {model_key} déchargé")
    
    @classmethod
    def unload_all(cls):
        """Décharge tous les modèles"""
        cls._instances.clear()
        logger.info("Tous les modèles déchargés")


# Test unitaire isolé (lance avec `python -m ia_chat.services.llm_service`)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("TEST ISOLATION LLMService")
    print("=" * 60)
    
    # Test 1 : Simple query
    print("\n[TEST 1] Simple query")
    try:
        response = LLMService.simple_query(
            "Bonjour ! En une phrase, présente-toi.",
            max_tokens=100
        )
        print(f"✓ Réponse : {response}")
    except Exception as e:
        print(f"✗ Erreur : {e}")
    
    # Test 2 : Conversation avec historique
    print("\n[TEST 2] Conversation contextuelle")
    try:
        messages = [
            {"role": "user", "content": "Mon prénom est Alice."},
            {"role": "assistant", "content": "Enchanté Alice ! Comment puis-je t'aider ?"},
            {"role": "user", "content": "Quel est mon prénom ?"},
        ]
        response = LLMService.chat(messages, max_tokens=50)
        print(f"✓ Réponse : {response}")
    except Exception as e:
        print(f"✗ Erreur : {e}")
    
    # Test 3 : Streaming
    print("\n[TEST 3] Streaming (réponse progressive)")
    try:
        messages = [{"role": "user", "content": "Compte de 1 à 5."}]
        print("✓ Stream : ", end="", flush=True)
        for chunk in LLMService.chat(messages, max_tokens=50, stream=True):
            print(chunk, end="", flush=True)
        print()
    except Exception as e:
        print(f"\n✗ Erreur : {e}")
    
    print("\n" + "=" * 60)
    print("Tests terminés !")
    print("=" * 60)
