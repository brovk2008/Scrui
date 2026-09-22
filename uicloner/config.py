"""
UI Cloner — High-Fidelity UI Extraction & Cloning Engine
Configuration system using Pydantic v2.
"""
from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BrowserEngine(str, Enum):
    NODRIVER = "nodriver"
    PATCHRIGHT = "patchright"
    CAMOUFOX = "camoufox"


class ProxyTier(str, Enum):
    RESIDENTIAL = "residential"
    ISP = "isp"
    DATACENTER = "datacenter"
    NONE = "none"


class ImageStorageFormat(str, Enum):
    BASE64 = "base64"       # Inline as data URIs
    RAW = "raw"             # Save as files, reference by path
    BOTH = "both"           # Save files AND embed base64 in JSON data
    EXTERNAL_URL = "url"    # Keep original URLs (no downloading)


class FontStorageFormat(str, Enum):
    BASE64 = "base64"
    RAW = "raw"
    EXTERNAL_URL = "url"


class VideoStorageFormat(str, Enum):
    RAW = "raw"
    EXTERNAL_URL = "url"


class OutputDataFormat(str, Enum):
    JSONL = "jsonl"         # One JSON object per line (streaming-friendly)
    JSON = "json"           # Single JSON file per category
    BOTH = "both"           # Both formats


class TLSImpersonate(str, Enum):
    CHROME120 = "chrome120"
    CHROME124 = "chrome124"
    CHROME131 = "chrome131"
    FIREFOX120 = "firefox120"
    SAFARI18 = "safari18"


class PromptTarget(str, Enum):
    NEXTJS = "nextjs"       # Next.js 15 App Router + Tailwind + Framer Motion
    REACT = "react"         # React 19 + Tailwind CSS
    V0 = "v0"               # v0.dev / Lovable / Bolt.new prompt
    CURSOR = "cursor"       # Cursor / Windsurf / Claude Code project rules & spec
    VUE = "vue"             # Vue 3 + Tailwind CSS
    SVELTE = "svelte"       # SvelteKit + Tailwind CSS


# ---------------------------------------------------------------------------
# Sub-config models
# ---------------------------------------------------------------------------

class BrowserConfig(BaseModel):
    primary_engine: BrowserEngine = BrowserEngine.NODRIVER
    fallback_chain: list[BrowserEngine] = [
        BrowserEngine.PATCHRIGHT,
        BrowserEngine.CAMOUFOX,
    ]
    headless: bool = False   # False = headed (lower detection), True = headless
    virtual_display: bool = True  # Use Xvfb virtual display
    max_concurrent_sessions: int = Field(default=5, ge=1, le=50)
    session_timeout_seconds: int = Field(default=300, ge=30)
    page_load_timeout_seconds: int = Field(default=60, ge=10)
    network_idle_timeout_ms: int = Field(default=2000, ge=500)


class FingerprintConfig(BaseModel):
    enabled: bool = True
    os_distribution: dict[str, int] = {
        "windows": 70,
        "macos": 25,
        "linux": 5,
    }
    browser_distribution: dict[str, int] = {
        "chrome": 80,
        "firefox": 20,
    }
    screen_min: tuple[int, int] = (1280, 720)
    screen_max: tuple[int, int] = (2560, 1440)
    locale: list[str] = ["en-US", "en-GB"]


class EvasionConfig(BaseModel):
    webdriver_patch: bool = True
    canvas_noise: bool = True
    canvas_noise_seed: Optional[str] = None  # None = random per session
    webgl_spoof: bool = True
    webgl_renderer: str = "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)"
    webgl_vendor: str = "Google Inc. (NVIDIA)"
    behavior_simulation: bool = True
    mouse_speed_ms_range: tuple[int, int] = (150, 500)
    webrtc_disabled: bool = True
    # Honeypot detection
    detect_honeypots: bool = True


class NetworkConfig(BaseModel):
    tls_impersonate: TLSImpersonate = TLSImpersonate.CHROME131
    http_version: int = Field(default=3, ge=1, le=3)
    proxy_tier: ProxyTier = ProxyTier.NONE
    proxy_list: list[str] = []   # "host:port:user:pass" or "host:port"
    rotate_proxy_after_n_requests: int = 5
    rate_limit_jitter_seconds: tuple[float, float] = (2.0, 8.0)
    request_timeout_seconds: int = 30
    max_retries: int = 3
    retry_backoff_base: float = 2.0


class ExtractionConfig(BaseModel):
    inline_assets: bool = True
    capture_shadow_dom: bool = True
    extract_animations: bool = True
    extract_event_listeners: bool = True
    record_temporal_mutations: bool = True
    capture_canvas: bool = True
    capture_webgl: bool = True
    extract_js: bool = True
    js_deobfuscate: bool = True
    # Wait strategy
    wait_for_network_idle: bool = True
    extra_wait_ms: int = 500
    # Scroll to trigger lazy-loaded content
    auto_scroll: bool = True
    scroll_pause_ms: int = 800
    # Lottie animation inlining
    inline_lottie: bool = True
    # IntersectionObserver rebinding for scroll-triggered animations
    rebind_scroll_animations: bool = True
    # GSAP ScrollTrigger capture
    capture_gsap_scroll_trigger: bool = True


class CrawlerConfig(BaseModel):
    """Multi-page crawl settings — disabled by default (single URL mode)."""
    enabled: bool = False
    max_pages: int = Field(default=50, ge=1, le=5000)
    max_depth: int = Field(default=3, ge=1, le=10)
    # Stay on same domain
    same_domain_only: bool = True
    # URL patterns to ignore
    exclude_patterns: list[str] = [
        r".*\.(pdf|zip|exe|dmg|pkg|msi|deb|rpm|tar\.gz)$",
        r".*/cdn-cgi/.*",
        r".*#.*",          # anchor-only links
    ]
    # Respect robots.txt
    respect_robots_txt: bool = True
    # Crawl delay between pages
    page_delay_seconds: float = Field(default=2.0, ge=0.5)
    # Sitemap sources to seed crawl
    parse_sitemap_xml: bool = True
    # URL priority: sitemap > internal links
    prioritize_sitemap: bool = True
    # Screenshot every page
    screenshot_all_pages: bool = True
    # Max concurrent crawl workers
    max_concurrent: int = Field(default=2, ge=1, le=10)


class UIAnalysisConfig(BaseModel):
    """Controls deep UI element analysis."""
    enabled: bool = True
    # Component detection
    detect_buttons: bool = True
    detect_forms: bool = True
    detect_navigation: bool = True
    detect_modals: bool = True
    detect_carousels: bool = True
    detect_accordions: bool = True
    detect_tabs: bool = True
    detect_tooltips: bool = True
    detect_dropdowns: bool = True
    # Accessibility audit
    run_accessibility_audit: bool = True
    # Color palette extraction
    extract_color_palette: bool = True
    # Typography extraction
    extract_typography: bool = True
    # Design tokens extraction
    extract_design_tokens: bool = True
    # Responsive breakpoints
    capture_breakpoints: list[int] = [375, 768, 1024, 1280, 1440, 1920]
    # VLM-powered element description (requires HF key)
    vlm_describe_elements: bool = False
    # Component boundary detection
    detect_component_boundaries: bool = True
    # Behavioral state exploration (hover, focus, disclosures)
    explore_states: bool = True
    probe_hover_transitions: bool = True
    probe_focus_states: bool = True
    probe_disclosure_widgets: bool = True


class StorageConfig(BaseModel):
    """Controls how each asset type is stored."""
    images: ImageStorageFormat = ImageStorageFormat.BASE64
    fonts: FontStorageFormat = FontStorageFormat.BASE64
    videos: VideoStorageFormat = VideoStorageFormat.RAW
    stylesheets: Literal["inline", "file"] = "inline"
    scripts: Literal["inline", "file", "deobfuscated"] = "deobfuscated"
    data_format: OutputDataFormat = OutputDataFormat.JSONL
    max_asset_size_mb: float = Field(default=50.0, ge=0.1)
    compress_data: bool = False
    # Content-hash deduplication — assets with identical content stored once
    deduplicate_assets: bool = True
    # Shared asset store across multiple clones (saves disk space)
    shared_asset_store: bool = False
    shared_asset_dir: Optional[Path] = None
    # SQLite index for fast asset lookup by hash/URL/mime
    build_sqlite_index: bool = True
    # Convert images to WebP for smaller size (if raw/both mode)
    convert_images_to_webp: bool = False
    webp_quality: int = Field(default=85, ge=1, le=100)


class HuggingFaceConfig(BaseModel):
    provider: str = "huggingface"  # huggingface, groq, openrouter, gemini, ollama
    api_key: Optional[str] = Field(default=None, description="API key for selected provider")
    vlm_model: str = "Qwen/Qwen2.5-VL-7B-Instruct"
    code_model: str = "Qwen/Qwen2.5-Coder-7B-Instruct"
    # Free provider keys and endpoints
    groq_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    ollama_endpoint: str = "http://localhost:11434"
    use_local: bool = False  # If True, use local Ollama / CUDA GPU
    inference_timeout: int = 120
    max_new_tokens: int = 2048


class CaptchaConfig(BaseModel):
    enabled: bool = False
    provider: str = "2captcha"  # 2captcha, nocaptcha, ddddocr_local
    two_captcha_api_key: Optional[str] = None
    nocaptcha_api_key: Optional[str] = None
    use_local_ocr: bool = False  # Use local Python OCR for image/slider challenges
    auto_detect: bool = True
    timeout_seconds: int = 120
    poll_interval_seconds: float = 3.0
    # Supported types
    solve_recaptcha_v2: bool = True
    solve_recaptcha_v3: bool = True
    solve_hcaptcha: bool = True
    solve_turnstile: bool = True
    solve_image: bool = True


class ValidationConfig(BaseModel):
    run_pixel_diff: bool = True
    run_vlm_check: bool = False  # Requires LLM API key
    auto_correct: bool = True    # Closed-loop visual auto-correction
    max_auto_correct_iterations: int = Field(default=3, ge=1, le=10)
    fidelity_threshold_percent: float = Field(default=95.0, ge=0, le=100)
    pixel_diff_threshold: int = Field(default=5, ge=0, le=50)


class OutputConfig(BaseModel):
    base_dir: Path = Path("./clones")
    format: Literal["single_file_html", "multi_file", "both"] = "both"
    embed_rrweb_replay: bool = True
    minify_html: bool = False
    generate_fidelity_report: bool = True
    root_folder_prefix: str = "site_cloned_"
    site_folder_name: Optional[str] = None  # None = use site slug (e.g., "stripe", "github")
    data_folder_name: str = "data_structure"  # Configurable structured data directory name


class PreflightConfig(BaseModel):
    """Configuration for Layer -1 Pre-Flight Profiler & Predictive Telemetry."""
    enabled: bool = True
    probe_timeout_seconds: float = 6.0
    estimate_timeline: bool = True
    save_preflight_report: bool = True


class PromptGenConfig(BaseModel):
    """Configuration for Layer 5: UI-to-Prompt Synthesizer (Optional)."""
    enabled: bool = False  # Optional by default
    target: PromptTarget = PromptTarget.NEXTJS
    include_screenshot_context: bool = True
    include_state_machine: bool = True
    include_motion_specs: bool = True
    include_copy_inventory: bool = True
    output_subfolder: str = "prompt"


# ---------------------------------------------------------------------------
# Master config
# ---------------------------------------------------------------------------

class UICloneConfig(BaseModel):
    """Master configuration for the UI Cloning Engine."""

    # Sub-configs
    preflight: PreflightConfig = PreflightConfig()
    prompt_gen: PromptGenConfig = PromptGenConfig()
    browser: BrowserConfig = BrowserConfig()
    fingerprint: FingerprintConfig = FingerprintConfig()
    evasion: EvasionConfig = EvasionConfig()
    network: NetworkConfig = NetworkConfig()
    extraction: ExtractionConfig = ExtractionConfig()
    crawler: CrawlerConfig = CrawlerConfig()
    analysis: UIAnalysisConfig = UIAnalysisConfig()
    storage: StorageConfig = StorageConfig()
    huggingface: HuggingFaceConfig = HuggingFaceConfig()
    captcha: CaptchaConfig = CaptchaConfig()
    validation: ValidationConfig = ValidationConfig()
    output: OutputConfig = OutputConfig()

    # Runtime secrets (loaded from env if not in config)
    hf_api_key: Optional[str] = Field(default=None, exclude=True)
    two_captcha_key: Optional[str] = Field(default=None, exclude=True)
    groq_key: Optional[str] = Field(default=None, exclude=True)
    openrouter_key: Optional[str] = Field(default=None, exclude=True)
    gemini_key: Optional[str] = Field(default=None, exclude=True)
    nocaptcha_key: Optional[str] = Field(default=None, exclude=True)

    def model_post_init(self, __context):
        # Load secrets from environment variables
        if not self.hf_api_key:
            self.hf_api_key = os.environ.get("HF_API_KEY") or os.environ.get("HUGGINGFACE_API_KEY")
        if not self.two_captcha_key:
            self.two_captcha_key = os.environ.get("TWO_CAPTCHA_KEY")
        if not self.groq_key:
            self.groq_key = os.environ.get("GROQ_API_KEY")
        if not self.openrouter_key:
            self.openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        if not self.gemini_key:
            self.gemini_key = os.environ.get("GEMINI_API_KEY")
        if not self.nocaptcha_key:
            self.nocaptcha_key = os.environ.get("NOCAPTCHA_API_KEY")

        # Propagate to sub-configs
        if self.hf_api_key and not self.huggingface.api_key:
            self.huggingface.api_key = self.hf_api_key
        if self.groq_key and not self.huggingface.groq_api_key:
            self.huggingface.groq_api_key = self.groq_key
        if self.openrouter_key and not self.huggingface.openrouter_api_key:
            self.huggingface.openrouter_api_key = self.openrouter_key
        if self.gemini_key and not self.huggingface.gemini_api_key:
            self.huggingface.gemini_api_key = self.gemini_key
        if self.two_captcha_key and not self.captcha.two_captcha_api_key:
            self.captcha.two_captcha_api_key = self.two_captcha_key
        if self.nocaptcha_key and not self.captcha.nocaptcha_api_key:
            self.captcha.nocaptcha_api_key = self.nocaptcha_key

    @classmethod
    def from_yaml(cls, path: str | Path) -> "UICloneConfig":
        """Load config from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        return cls(**data)

    def save_yaml(self, path: str | Path) -> None:
        """Save config to a YAML file."""
        data = self.model_dump(exclude_none=True)
        # Convert Path objects to strings
        data["output"]["base_dir"] = str(data["output"]["base_dir"])
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def default(cls) -> "UICloneConfig":
        return cls()


# Global config instance (can be replaced at runtime)
_global_config: Optional[UICloneConfig] = None


def get_config() -> UICloneConfig:
    global _global_config
    if _global_config is None:
        # Try to load from config.yaml in cwd
        cfg_path = Path("config.yaml")
        if cfg_path.exists():
            _global_config = UICloneConfig.from_yaml(cfg_path)
        else:
            _global_config = UICloneConfig.default()
    return _global_config


def set_config(config: UICloneConfig) -> None:
    global _global_config
    _global_config = config
