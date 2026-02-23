#!/usr/bin/env python3
"""
JnJ Branded PowerPoint Deck Generator
Thin CLI wrapper — actual logic lives in skills_building._generate_deck.

Usage:
    echo '<json>' | python3 generate_deck.py --output my-deck.pptx
    python3 generate_deck.py --input slides.json --output my-deck.pptx
"""

from skills_building._generate_deck import main

if __name__ == "__main__":
    main()
