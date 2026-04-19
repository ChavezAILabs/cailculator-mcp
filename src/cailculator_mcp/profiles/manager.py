"""
Profile Manager - CAILculator v2.0
Dynamic Domain Orchestrator

Responsible for:
- Discovering and listing available profiles
- Loading specific profile logic (terminology, mapping)
- Managing the 'Custom Profile' request pipeline
"""

import os
import json
import importlib
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ProfileManager:
    """
    Manages the lifecycle and orchestration of domain profiles.
    """
    
    def __init__(self, profiles_dir: Optional[str] = None):
        if profiles_dir is None:
            profiles_dir = os.path.dirname(os.path.abspath(__file__))
        self.profiles_dir = profiles_dir
        self.active_profile: Optional[Dict] = None
        self.active_name: str = "general_data"  # Default
        
    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        Enumerates all available profiles on disk.
        Includes a 'Custom Request' entry for commercial leads.
        """
        profiles = []
        
        # 1. Scan directory for manifest.json files
        for entry in os.listdir(self.profiles_dir):
            full_path = os.path.join(self.profiles_dir, entry)
            manifest_path = os.path.join(full_path, "manifest.json")
            
            if os.path.isdir(full_path) and os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                        profiles.append(manifest)
                except Exception as e:
                    logger.error(f"Failed to load manifest for {entry}: {e}")
        
        # 2. Add the Commercial 'Custom' entry
        profiles.append({
            "name": "custom_request",
            "tier": "Commercial",
            "scope": "Bespoke high-stakes embeddings for LHC, F1, or Biotech",
            "contact": "iknowpi@gmail.com",
            "note": "Contact us to build a verified bridge for your specialized data."
        })
        
        return profiles

    def load_profile(self, name: str) -> bool:
        """
        Loads the logic for a specific profile into the active session.
        """
        manifest_path = os.path.join(self.profiles_dir, name, "manifest.json")
        if not os.path.exists(manifest_path):
            logger.error(f"Profile {name} not found.")
            return False
            
        try:
            with open(manifest_path, 'r') as f:
                self.active_profile = json.load(f)
                self.active_name = name
                return True
        except Exception as e:
            logger.error(f"Error loading profile {name}: {e}")
            return False

    def get_mapper(self, category: Optional[str] = None):
        """Returns the mapping function for the active profile."""
        try:
            module = importlib.import_module(f"..{self.active_name}.coefficient_mapping", package=__name__)
            # Look for common mapper names or default
            if self.active_name == "quant_equity":
                return getattr(module, "map_ohlcv_to_sedenion")
            elif self.active_name == "rhi":
                return getattr(module, "get_parametric_lift")
            elif self.active_name == "journalism":
                # Journalism profile supports sub-categories
                if category == "politics":
                    return getattr(module, "map_politics_to_sedenion")
                elif category == "public_health":
                    return getattr(module, "map_public_health_to_sedenion")
                elif category == "poverty":
                    return getattr(module, "map_poverty_to_sedenion")
                return getattr(module, "map_politics_to_sedenion") # Default
            else:
                return getattr(module, "map_generic_to_sedenion", None)
        except Exception as e:
            logger.error(f"Failed to load mapper for {self.active_name}: {e}")
            return None

    def get_translator(self):
        """Returns the translation function for the active profile."""
        try:
            module = importlib.import_module(f"..{self.active_name}.terminology", package=__name__)
            return getattr(module, "translate_output")
        except Exception as e:
            logger.error(f"Failed to load translator for {self.active_name}: {e}")
            return lambda x, level: x # Identity fallback

    def get_gateway_labels(self):
        """Returns the domain-specific labels for structural pathways."""
        try:
            module = importlib.import_module(f"..{self.active_name}.gateway_labels", package=__name__)
            return getattr(module, "get_label")
        except Exception as e:
            logger.error(f"Failed to load gateway labels for {self.active_name}: {e}")
            return lambda pid: f"Pattern {pid}"
