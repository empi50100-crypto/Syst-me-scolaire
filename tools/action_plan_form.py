#!/usr/bin/env python3
"""
Action Plan Form - TYPE HINT ONLY version
Évite l'import circulaire en n'utilisant pas l'héritage de classe
"""

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

# TYPE CHECKING ONLY - pas d'import réel à l'exécution
if TYPE_CHECKING:
    from mcp_ideation_autonomous.agent.schemas import ActionPlanSchema


class ActionPlanForm:
    """
    Formulaire de plan d'action - VERSION TYPE HINT UNIQUEMENT
    
    Cette classe utilise l'approche TYPE HINT au lieu de l'héritage
    pour éviter les problèmes d'import circulaire.
    """
    
    # Champs définis manuellement (pas via Pydantic inheritance)
    title: str = ""
    description: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    status: str = "draft"  # draft, active, completed, cancelled
    tasks: List[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    def __init__(self, **data):
        """Initialisation manuelle des attributs"""
        # Initialiser les valeurs par défaut
        self.tasks = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Appliquer les données fournies
        for key, value in data.items():
            if hasattr(self, key) or not key.startswith('_'):
                setattr(self, key, value)
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire"""
        return {
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'tasks': self.tasks or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
        }
    
    @classmethod
    def from_schema(cls, schema_instance) -> 'ActionPlanForm':
        """Créer une instance depuis un ActionPlanSchema"""
        if hasattr(schema_instance, 'dict'):
            # C'est un Pydantic model
            data = schema_instance.dict()
        else:
            # C'est un objet standard
            data = {
                'title': getattr(schema_instance, 'title', ''),
                'description': getattr(schema_instance, 'description', None),
                'priority': getattr(schema_instance, 'priority', 'medium'),
                'status': getattr(schema_instance, 'status', 'draft'),
                'tasks': getattr(schema_instance, 'tasks', []),
                'created_by': getattr(schema_instance, 'created_by', None),
            }
        return cls(**data)
    
    def update_status(self, new_status: str):
        """Mettre à jour le statut"""
        valid_statuses = ['draft', 'active', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"Statut invalide. Choix: {valid_statuses}")
        self.status = new_status
        self.updated_at = datetime.now()
    
    def add_task(self, task_title: str, task_description: str = None):
        """Ajouter une tâche"""
        task = {
            'id': len(self.tasks or []) + 1,
            'title': task_title,
            'description': task_description,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
        }
        if self.tasks is None:
            self.tasks = []
        self.tasks.append(task)
        self.updated_at = datetime.now()
    
    def __repr__(self):
        return f"<ActionPlanForm title='{self.title}' status='{self.status}'>"


# TYPE HINT pour l'équivalence avec ActionPlanSchema
# Cette variable permet aux IDE de comprendre la compatibilité
ActionPlanFormType = ActionPlanForm
