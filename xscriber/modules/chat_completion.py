import os
import re
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import openai
from django.conf import settings


class ChatCompletionProcessor:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.trd_ontology_prompts = {
            "overview": "Extract or update the overview/summary section from the transcription",
            "requirements": "Extract or update functional requirements from the transcription",
            "technical_specs": "Extract or update technical specifications from the transcription",
            "architecture": "Extract or update system architecture details from the transcription",
            "constraints": "Extract or update system constraints and limitations from the transcription",
            "assumptions": "Extract or update assumptions made in the transcription",
            "acceptance_criteria": "Extract or update acceptance criteria from the transcription",
            "dependencies": "Extract or update external dependencies from the transcription"
        }

    def parse_trd_ontology(self, trd_content: str) -> Dict[str, str]:
        ontology = {}

        sections = {
            "overview": r"# Overview\n(.*?)(?=\n# |\Z)",
            "requirements": r"# Requirements\n(.*?)(?=\n# |\Z)",
            "technical_specs": r"# Technical Specifications\n(.*?)(?=\n# |\Z)",
            "architecture": r"# Architecture\n(.*?)(?=\n# |\Z)",
            "constraints": r"# Constraints\n(.*?)(?=\n# |\Z)",
            "assumptions": r"# Assumptions\n(.*?)(?=\n# |\Z)",
            "acceptance_criteria": r"# Acceptance Criteria\n(.*?)(?=\n# |\Z)",
            "dependencies": r"# Dependencies\n(.*?)(?=\n# |\Z)"
        }

        for section_name, pattern in sections.items():
            match = re.search(pattern, trd_content, re.DOTALL | re.IGNORECASE)
            ontology[section_name] = match.group(1).strip() if match else ""

        return ontology

    def update_trd_section(self, section_name: str, existing_content: str, new_transcription: str) -> str:
        prompt_template = self.trd_ontology_prompts.get(section_name, "Update this section with new information")

        system_prompt = f"""You are a technical documentation expert. Your task is to {prompt_template}.

        Given the existing content and new transcription, update the section to include relevant new information while preserving existing content that is still valid.

        CRITICAL RULES:
        1. NEVER include section headers (like # Overview, ## Requirements, etc.) in your response
        2. Only return the CONTENT of the section, not the header
        3. Only include information relevant to the {section_name} section
        4. Merge new information with existing content thoughtfully
        5. Remove contradictory information, preferring the newer transcription
        6. Maintain professional technical writing style
        7. Use markdown formatting appropriately (bullets, bold, etc.) but NO headers
        8. If no relevant information exists in the transcription, return the existing content unchanged
        9. Replace the entire content, don't append to it
        """

        user_prompt = f"""Existing {section_name} content:
        {existing_content}

        New transcription to incorporate:
        {new_transcription}

        Please update the {section_name} section:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Failed to update {section_name} section: {str(e)}")
            return existing_content

    def update_trd_sections(self, ontology: Dict[str, str], new_transcription: str) -> Dict[str, str]:
        updated_ontology = {}

        for section_name, existing_content in ontology.items():
            updated_content = self.update_trd_section(section_name, existing_content, new_transcription)
            updated_ontology[section_name] = updated_content

        return updated_ontology

    def generate_trd_document(self, ontology: Dict[str, str]) -> str:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Clean up section content - remove any header text or prompt artifacts
        def clean_content(content):
            if not content or content.strip() in ["", "To be defined"]:
                return "To be defined"

            # Remove any line that looks like a header or prompt artifact
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # Skip lines that look like headers or prompt artifacts
                if (line.startswith('#') or
                    'existing' in line.lower() and 'content' in line.lower() or
                    'new transcription to incorporate' in line.lower() or
                    'please update' in line.lower()):
                    continue
                if line:
                    cleaned_lines.append(line)

            return '\n'.join(cleaned_lines) if cleaned_lines else "To be defined"

        trd_content = f"""# Technical Requirements Document

## Overview
{clean_content(ontology.get("overview", "To be defined"))}

## Requirements
{clean_content(ontology.get("requirements", "To be defined"))}

## Technical Specifications
{clean_content(ontology.get("technical_specs", "To be defined"))}

## Architecture
{clean_content(ontology.get("architecture", "To be defined"))}

## Constraints
{clean_content(ontology.get("constraints", "To be defined"))}

## Assumptions
{clean_content(ontology.get("assumptions", "To be defined"))}

## Acceptance Criteria
{clean_content(ontology.get("acceptance_criteria", "To be defined"))}

## Dependencies
{clean_content(ontology.get("dependencies", "To be defined"))}

---
*Generated by X-Scriber on {timestamp}*
"""

        return trd_content

    def process_transcription_to_trd(self, transcription: str, existing_trd: str = "") -> str:
        if existing_trd:
            ontology = self.parse_trd_ontology(existing_trd)
        else:
            ontology = {section: "" for section in self.trd_ontology_prompts.keys()}

        updated_ontology = self.update_trd_sections(ontology, transcription)
        return self.generate_trd_document(updated_ontology)

    def save_trd_document(self, trd_content: str, output_path: str) -> bool:
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(trd_content)

            return True
        except Exception as e:
            print(f"Failed to save TRD document: {str(e)}")
            return False