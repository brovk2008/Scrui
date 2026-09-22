"""
Interactive State Machine Compiler (Layer 5)
Synthesizes mined behavioral states and event listeners into
clean, type-safe React/Vue state management patterns and interaction contracts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class StateHookContract:
    """Blueprint of a component state hook."""
    name: str
    state_type: str  # boolean, string, number, null
    initial_value: str
    setter_name: str
    purpose: str
    event_trigger: str  # onClick, onKeyDown, onScroll, onMouseEnter


@dataclass
class StateMachineSpec:
    """Complete collection of interactive state contracts for the UI."""
    contracts: list[StateHookContract] = field(default_factory=list)
    state_logic_snippet: str = ""
    accessibility_rules: list[str] = field(default_factory=list)


def compile_state_machine(
    behavior_report: Any = None,
    event_data: Optional[dict] = None,
) -> StateMachineSpec:
    """
    Compile behavioral findings into state hook declarations and logic snippets.
    """
    contracts: list[StateHookContract] = [
        StateHookContract(
            name="isMobileMenuOpen",
            state_type="boolean",
            initial_value="false",
            setter_name="setIsMobileMenuOpen",
            purpose="Controls visibility of the slide-over mobile navigation menu",
            event_trigger="onClick on mobile hamburger icon button",
        ),
        StateHookContract(
            name="activeTab",
            state_type="string",
            initial_value="'all'",
            setter_name="setActiveTab",
            purpose="Filters feature or pricing cards based on selected category",
            event_trigger="onClick on segmented pill buttons",
        ),
        StateHookContract(
            name="expandedAccordionId",
            state_type="string | null",
            initial_value="null",
            setter_name="setExpandedAccordionId",
            purpose="Controls single-expanded state for FAQ questions with smooth accordion disclosure",
            event_trigger="onClick on question row trigger",
        ),
        StateHookContract(
            name="isScrolled",
            state_type="boolean",
            initial_value="false",
            setter_name="setIsScrolled",
            purpose="Adds glassmorphic blur and border shadow to sticky header when window.scrollY > 20",
            event_trigger="window.addEventListener('scroll', ...)",
        ),
    ]

    # Additional contracts from behavior_report
    if behavior_report and getattr(behavior_report, "disclosure_widgets_found", 0) > 0:
        contracts.append(StateHookContract(
            name="openModalId",
            state_type="string | null",
            initial_value="null",
            setter_name="setOpenModalId",
            purpose="Renders backdrop overlay and focus trap for interactive dialogs",
            event_trigger="onClick on demo trigger button",
        ))

    # Formulate React state code snippet
    snippet = """// Interactive State Blueprint
const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
const [activeTab, setActiveTab] = useState('all');
const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
const [isScrolled, setIsScrolled] = useState(false);

useEffect(() => {
  const handleScroll = () => {
    setIsScrolled(window.scrollY > 20);
  };
  window.addEventListener('scroll', handleScroll, { passive: true });
  return () => window.removeEventListener('scroll', handleScroll);
}, []);

const toggleFaq = (index: number) => {
  setExpandedFaq(prev => prev === index ? null : index);
};"""

    a11y_rules = [
        "Include aria-expanded={isMobileMenuOpen} on mobile toggle button",
        "Include aria-controls='mobile-menu' and id='mobile-menu' on drawer",
        "Add role='tablist' and aria-selected={activeTab === tab.id} on segmented filters",
        "Close modals on Escape key press and restore focus to trigger element",
        "Trap keyboard focus within modals when opened",
    ]

    return StateMachineSpec(
        contracts=contracts,
        state_logic_snippet=snippet,
        accessibility_rules=a11y_rules,
    )
