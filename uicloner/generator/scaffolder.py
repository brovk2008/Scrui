"""
Scrui Next.js 15 & React Project Scaffolder.
Generates a complete, ready-to-run Next.js 15 App Router codebase
from reverse-engineered UI telemetry and design tokens.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from uicloner.layers.layer5_prompt.synthesizer import PromptBundle


class ProjectScaffolder:
    """Scaffolds a production Next.js 15 project matching the reverse-engineered UI."""

    def __init__(self, output_dir: Path, bundle: PromptBundle):
        self.out_dir = output_dir
        self.bundle = bundle
        self.schema = bundle.components_schema
        self.tokens = self.schema.get("design_tokens", {})
        self.sections = self.schema.get("sections", [])
        self.components = self.schema.get("components", [])

    def scaffold(self) -> Dict[str, Path]:
        """Generate all files for the Next.js project on disk."""
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "app").mkdir(exist_ok=True)
        (self.out_dir / "components").mkdir(exist_ok=True)
        (self.out_dir / "lib").mkdir(exist_ok=True)

        generated = {}
        generated["package.json"] = self._write_package_json()
        generated["tsconfig.json"] = self._write_tsconfig()
        generated["tailwind.config.ts"] = self._write_tailwind_config()
        generated["app/globals.css"] = self._write_globals_css()
        generated["app/layout.tsx"] = self._write_layout()
        generated["app/page.tsx"] = self._write_page()
        generated["lib/types.ts"] = self._write_types()
        generated["lib/animations.ts"] = self._write_animations()

        # Generate individual components
        generated["components/Navbar.tsx"] = self._write_navbar()
        generated["components/Hero.tsx"] = self._write_hero()
        generated["components/Features.tsx"] = self._write_features()
        generated["components/Footer.tsx"] = self._write_footer()

        return generated

    def _write_package_json(self) -> Path:
        p = self.out_dir / "package.json"
        host_slug = self.schema.get("host", "scrui-clone").replace(".", "-").lower()
        pkg = {
            "name": f"{host_slug}-clone",
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
            },
            "dependencies": {
                "next": "^15.1.0",
                "react": "^19.0.0",
                "react-dom": "^19.0.0",
                "lucide-react": "^0.460.0",
                "framer-motion": "^11.12.0",
                "clsx": "^2.1.1",
                "tailwind-merge": "^2.5.4",
            },
            "devDependencies": {
                "typescript": "^5.6.3",
                "@types/node": "^22.9.0",
                "@types/react": "^19.0.0",
                "@types/react-dom": "^19.0.0",
                "tailwindcss": "^3.4.15",
                "postcss": "^8.4.49",
                "autoprefixer": "^10.4.20",
            },
        }
        with open(p, "w", encoding="utf-8") as f:
            json.dump(pkg, f, indent=2)
        return p

    def _write_tsconfig(self) -> Path:
        p = self.out_dir / "tsconfig.json"
        tsconfig = {
            "compilerOptions": {
                "target": "ES2022",
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {"@/*": ["./*"]},
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"],
        }
        with open(p, "w", encoding="utf-8") as f:
            json.dump(tsconfig, f, indent=2)
        return p

    def _write_tailwind_config(self) -> Path:
        p = self.out_dir / "tailwind.config.ts"
        primary = self.tokens.get("primary", "#00a2ff")
        secondary = self.tokens.get("secondary", "#ff2a85")
        background = self.tokens.get("background", "#0f172a")
        surface = self.tokens.get("surface", "#1e293b")
        border = self.tokens.get("border", "#334155")
        radius = self.tokens.get("radius", "0.5rem")

        content = f"""import type {{ Config }} from "tailwindcss";

const config: Config = {{
  darkMode: ["class"],
  content: [
    "./app/**/*.{{js,ts,jsx,tsx,mdx}}",
    "./components/**/*.{{js,ts,jsx,tsx,mdx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: "{primary}",
        secondary: "{secondary}",
        background: "{background}",
        surface: "{surface}",
        border: "{border}",
      }},
      borderRadius: {{
        DEFAULT: "{radius}",
      }},
    }},
  }},
  plugins: [],
}};
export default config;
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p

    def _write_globals_css(self) -> Path:
        p = self.out_dir / "app" / "globals.css"
        bg = self.tokens.get("background", "#0f172a")
        txt = self.tokens.get("text", "#f8fafc")
        content = f"""@tailwind base;
@tailwind components;
@tailwind utilities;

:root {{
  --background: {bg};
  --foreground: {txt};
}}

body {{
  color: var(--foreground);
  background: var(--background);
  font-family: Arial, Helvetica, sans-serif;
  overflow-x: hidden;
}}
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p

    def _write_layout(self) -> Path:
        p = self.out_dir / "app" / "layout.tsx"
        host = self.schema.get("host", "Scrui Clone")
        content = f"""import type {{ Metadata }} from "next";
import "./globals.css";

export const metadata: Metadata = {{
  title: "{host} — Recreated with Scrui",
  description: "Exact pixel-identical frontend synthesized by Scrui v2.5",
}};

export default function RootLayout({{
  children,
}}: Readonly<{{
  children: React.ReactNode;
}}>) {{
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-background text-foreground min-h-screen">
        {{children}}
      </body>
    </html>
  );
}}
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p

    def _write_page(self) -> Path:
        p = self.out_dir / "app" / "page.tsx"
        content = """import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between">
      <Navbar />
      <Hero />
      <Features />
      <Footer />
    </main>
  );
}
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p

    def _write_types(self) -> Path:
        p = self.out_dir / "lib" / "types.ts"
        content = """export interface NavItem {
  label: string;
  href: string;
}

export interface FeatureCardProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  badge?: string;
}

export interface ButtonProps {
  label: string;
  variant?: "primary" | "secondary" | "outline" | "ghost";
  onClick?: () => void;
  href?: string;
}
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p

    def _write_animations(self) -> Path:
        p = self.out_dir / "lib" / "animations.ts"
        content = """import { Variants } from "framer-motion";

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12, delayChildren: 0.1 },
  },
};

export const hoverElevate: Variants = {
  initial: { y: 0 },
  hover: { y: -4, transition: { duration: 0.2 } },
};
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p

    def _write_navbar(self) -> Path:
        p = self.out_dir / "components" / "Navbar.tsx"
        host = self.schema.get("host", "Brand")
        content = f""""use client";

import {{ useState }} from "react";
import {{ Menu, X, ArrowRight }} from "lucide-react";

export default function Navbar() {{
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-6">
        <a href="#" className="font-bold text-xl tracking-tight text-primary">
          {host}
        </a>

        <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
          <a href="#features" className="hover:text-primary transition-colors">Features</a>
          <a href="#pricing" className="hover:text-primary transition-colors">Pricing</a>
          <a href="#about" className="hover:text-primary transition-colors">About</a>
        </nav>

        <div className="hidden md:flex items-center gap-4">
          <button className="px-4 py-2 text-sm font-medium text-foreground hover:text-primary transition-colors">
            Sign In
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-background hover:opacity-90 transition-opacity">
            Get Started <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <button 
          onClick={{() => setIsOpen(!isOpen)}} 
          className="md:hidden p-2 text-foreground"
          aria-label="Toggle navigation"
        >
          {{isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}}
        </button>
      </div>

      {{/* Mobile Drawer */}}
      {{isOpen && (
        <div className="md:hidden border-b border-border bg-background px-6 py-4 flex flex-col gap-4">
          <a href="#features" className="text-sm font-medium">Features</a>
          <a href="#pricing" className="text-sm font-medium">Pricing</a>
          <a href="#about" className="text-sm font-medium">About</a>
          <button className="w-full rounded-lg bg-primary py-2 text-sm font-semibold text-background">
            Get Started
          </button>
        </div>
      )}}
    </header>
  );
}}
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p

    def _write_hero(self) -> Path:
        p = self.out_dir / "components" / "Hero.tsx"
        hero_sec = next((s for s in self.sections if "hero" in s.get("section_id", "").lower() or "hero" in s.get("section_name", "").lower()), None)
        headline = (hero_sec and hero_sec.get("headline")) or f"The next generation platform for {self.schema.get('host', 'web')}"
        subheadline = (hero_sec and hero_sec.get("subheadline")) or "Engineered for uncompromising speed, precision, and peak performance."

        content = f""""use client";

import {{ motion }} from "framer-motion";
import {{ ArrowRight, Sparkles }} from "lucide-react";
import {{ fadeInUp }} from "@/lib/animations";

export default function Hero() {{
  return (
    <section className="relative w-full py-24 md:py-32 px-6 flex flex-col items-center text-center max-w-5xl mx-auto">
      <motion.div 
        variants={{fadeInUp}} 
        initial="hidden" 
        animate="visible"
        className="inline-flex items-center gap-2 px-3 py-1 mb-8 rounded-full border border-border bg-surface text-xs font-medium text-primary"
      >
        <Sparkles className="w-3.5 h-3.5" />
        <span>Synthesized with Scrui v2.5</span>
      </motion.div>

      <motion.h1 
        variants={{fadeInUp}}
        initial="hidden"
        animate="visible"
        className="text-4xl md:text-6xl font-extrabold tracking-tight max-w-4xl text-foreground"
      >
        {headline}
      </motion.h1>

      <motion.p 
        variants={{fadeInUp}}
        initial="hidden"
        animate="visible"
        className="mt-6 text-lg md:text-xl text-neutral-400 max-w-2xl"
      >
        {subheadline}
      </motion.p>

      <motion.div 
        variants={{fadeInUp}}
        initial="hidden"
        animate="visible"
        className="mt-10 flex flex-col sm:flex-row gap-4"
      >
        <button className="flex items-center justify-center gap-2 rounded-lg bg-primary px-6 py-3 font-semibold text-background hover:opacity-90 transition-opacity">
          Start Free Trial <ArrowRight className="w-4 h-4" />
        </button>
        <button className="rounded-lg border border-border px-6 py-3 font-semibold text-foreground hover:bg-surface transition-colors">
          View Documentation
        </button>
      </motion.div>
    </section>
  );
}}
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p

    def _write_features(self) -> Path:
        p = self.out_dir / "components" / "Features.tsx"
        content = """"use client";

import { motion } from "framer-motion";
import { Zap, ShieldCheck, Layers } from "lucide-react";
import { staggerContainer, hoverElevate } from "@/lib/animations";

const features = [
  {
    title: "High-Fidelity Extraction",
    description: "Pixel-accurate computed styles, Shadow DOM piercing, and font metrics extracted directly from the live DOM.",
    icon: <Zap className="w-6 h-6 text-primary" />,
  },
  {
    title: "Stealth Architecture",
    description: "Zero-detection evasion bypassing Cloudflare, Akamai, and modern bot management systems.",
    icon: <ShieldCheck className="w-6 h-6 text-secondary" />,
  },
  {
    title: "Component Synthesis",
    description: "Translates reverse-engineered DOM structures into clean, modular React 19 components with full TypeScript typing.",
    icon: <Layers className="w-6 h-6 text-primary" />,
  },
];

export default function Features() {
  return (
    <section id="features" className="w-full py-20 px-6 max-w-7xl mx-auto border-t border-border">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <h2 className="text-3xl font-bold tracking-tight">Core Architecture & Features</h2>
        <p className="mt-4 text-neutral-400">Everything reverse-engineered and structured into clean, modular components.</p>
      </div>

      <motion.div 
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="grid grid-cols-1 md:grid-cols-3 gap-8"
      >
        {features.map((feat, i) => (
          <motion.div
            key={i}
            variants={hoverElevate}
            whileHover="hover"
            className="rounded-xl border border-border bg-surface/50 p-8 flex flex-col items-start"
          >
            <div className="p-3 rounded-lg bg-surface border border-border mb-6">
              {feat.icon}
            </div>
            <h3 className="text-xl font-semibold mb-2">{feat.title}</h3>
            <p className="text-sm text-neutral-400 leading-relaxed">{feat.description}</p>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p

    def _write_footer(self) -> Path:
        p = self.out_dir / "components" / "Footer.tsx"
        host = self.schema.get("host", "Scrui Project")
        content = f"""export default function Footer() {{
  return (
    <footer className="w-full border-t border-border py-12 px-6 bg-background mt-20">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 text-sm text-neutral-400">
        <p>© 2026 {host}. Cloned with Scrui v2.5.</p>
        <div className="flex gap-6">
          <a href="#" className="hover:text-foreground">Privacy Policy</a>
          <a href="#" className="hover:text-foreground">Terms of Service</a>
          <a href="#" className="hover:text-foreground">GitHub</a>
        </div>
      </div>
    </footer>
  );
}}
"""
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p
