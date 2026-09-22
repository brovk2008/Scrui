"""
Layer 5: UI-to-Prompt Synthesizer (Spec-to-Code Prompt Architect)
Optional final layer that converts the entire reverse-engineered UI
(components, layout tree, design tokens, copy, state machines, motion)
into an exact Master Prompt and Technical Specification for AI coding models
(Claude 3.7 Sonnet, GPT-4o, Cursor, v0.dev, Lovable, Bolt.new).
"""
from __future__ import annotations

from uicloner.layers.layer5_prompt.synthesizer import (
    UIPromptSynthesizer,
    PromptBundle,
    generate_ui_prompt,
)
from uicloner.layers.layer5_prompt.ast_reducer import SemanticSection, ComponentSpec, reduce_dom_to_components
from uicloner.layers.layer5_prompt.token_compiler import compile_design_tokens, DesignTokenSpec
from uicloner.layers.layer5_prompt.state_compiler import compile_state_machine, StateMachineSpec
from uicloner.layers.layer5_prompt.motion_compiler import compile_motion_specs, MotionSpec
from uicloner.layers.layer5_prompt.icon_matcher import IconMatcher, MatchedIcon

__all__ = [
    "UIPromptSynthesizer",
    "PromptBundle",
    "generate_ui_prompt",
    "SemanticSection",
    "ComponentSpec",
    "reduce_dom_to_components",
    "compile_design_tokens",
    "DesignTokenSpec",
    "compile_state_machine",
    "StateMachineSpec",
    "compile_motion_specs",
    "MotionSpec",
    "IconMatcher",
    "MatchedIcon",
]
