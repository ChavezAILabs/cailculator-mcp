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

    _PROFILE_METADATA = {
        "rhi":          {"tier": "Academic",    "scope": "Riemann Hypothesis Investigation — prime embeddings (log p → 16D root) and spectral structure."},
        "quant_equity": {"tier": "Quant",       "scope": "Market regime detection from OHLCV: volatility anchors, technical indicators, Chavez Transform stability."},
        "journalism":   {"tier": "Journalist",  "scope": "Structural tipping points and signal robustness in gathered data (e.g. FEC campaign finance)."},
        "general_data": {"tier": "Individual",  "scope": "General-purpose numerical structure analysis."},
        "developer_v1": {"tier": "Individual",  "scope": "Developer / debugging profile."},
    }

    def __init__(self, profiles_dir: Optional[str] = None):
        if profiles_dir is None:
            profiles_dir = os.path.dirname(os.path.abspath(__file__))
        self.profiles_dir = profiles_dir
        self.active_profile: Optional[Dict] = None
        self.active_name: str = "general_data"  # Default

    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        A directory is a profile if it has a manifest.json OR a coefficient_mapping.py
        / terminology.py module. Manifest data wins when present; otherwise a built-in
        descriptor is used. Always appends the commercial 'custom_request' lead entry.
        """
        profiles = []
        for entry in sorted(os.listdir(self.profiles_dir)):
            full_path = os.path.join(self.profiles_dir, entry)
            if not os.path.isdir(full_path) or entry.startswith("__"):
                continue
            manifest_path = os.path.join(full_path, "manifest.json")
            is_profile = (
                os.path.exists(manifest_path)
                or os.path.exists(os.path.join(full_path, "coefficient_mapping.py"))
                or os.path.exists(os.path.join(full_path, "terminology.py"))
            )
            if not is_profile:
                continue
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r") as f:
                        profiles.append(json.load(f))
                    continue
                except Exception as e:
                    logger.error(f"Failed to load manifest for {entry}: {e}")
            meta = self._PROFILE_METADATA.get(entry, {})
            profiles.append({
                "name": entry,
                "tier": meta.get("tier", "Individual"),
                "scope": meta.get("scope", f"{entry} domain profile."),
            })

        profiles.append({
            "name": "custom_request",
            "tier": "Commercial",
            "scope": "Bespoke high-stakes embeddings for LHC, F1, or Biotech",
            "contact": "iknowpi@gmail.com",
            "note": "Contact us to build a verified bridge for your specialized data.",
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
