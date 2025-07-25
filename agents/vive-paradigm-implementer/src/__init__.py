"""
Vive Paradigm Implementer Agent Package

体験駆動型学習を実現するエージェントパッケージ
"""

from .vive_agent import ViveParadigmImplementer
from .prototype_generator import PrototypeGenerator
from .learning_guide import LearningGuideGenerator
from .template_manager import TemplateManager

__version__ = "1.0.0"
__author__ = "NSada2025"

__all__ = [
    "ViveParadigmImplementer",
    "PrototypeGenerator", 
    "LearningGuideGenerator",
    "TemplateManager"
]