"""
Ontology generation service.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from ..utils.llm_client import LLMClient
from ..utils.locale import get_language_instruction

logger = logging.getLogger(__name__)


def _to_pascal_case(name: str) -> str:
    """Convert a name to PascalCase."""
    parts = re.split(r'[^a-zA-Z0-9]+', name)
    # Handle camelCase chunks.
    words = []
    for part in parts:
        words.extend(re.sub(r'([a-z])([A-Z])', r'\1_\2', part).split('_'))
    # Join words.
    result = ''.join(word.capitalize() for word in words if word)
    return result if result else 'Unknown'


ONTOLOGY_SYSTEM_PROMPT = """You are an ontology architect for social simulation.

Given source content and a simulation requirement, generate an ontology in JSON.
Return valid JSON only (no markdown).

Required output schema:
{
  "entity_types": [
    {
      "name": "PascalCaseName",
      "description": "Short description in <= 100 chars",
      "attributes": [{"name": "snake_case_name", "type": "text", "description": "..." }],
      "examples": ["example1", "example2"]
    }
  ],
  "edge_types": [
    {
      "name": "UPPER_SNAKE_CASE",
      "description": "Short description in <= 100 chars",
      "source_targets": [{"source": "EntityTypeA", "target": "EntityTypeB"}],
      "attributes": []
    }
  ],
  "analysis_summary": "A concise summary of the ontology rationale"
}

Guidelines:
- Prefer 6-10 entity types and 6-10 edge types when content supports it.
- Keep the ontology practical and simulation-oriented.
- Distinguish concrete people/entities from abstract collective entities.
- Keep generated type and attribute names in English.
"""


class OntologyGenerator:
    """
    Generate ontology definitions from content and simulation requirements.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
    
    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate ontology JSON from document text and requirements."""
        user_message = self._build_user_message(
            document_texts, 
            simulation_requirement,
            additional_context
        )
        
        lang_instruction = get_language_instruction()
        system_prompt = f"{ONTOLOGY_SYSTEM_PROMPT}\n\n{lang_instruction}\nIMPORTANT: Entity type names MUST be in English PascalCase (e.g., 'PersonEntity', 'MediaOrganization'). Relationship type names MUST be in English UPPER_SNAKE_CASE (e.g., 'WORKS_FOR'). Attribute names MUST be in English snake_case. Only description fields and analysis_summary should use the specified language above."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Call LLM
        result = self.llm_client.chat_json(
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        
        # 
        result = self._validate_and_process(result)
        
        return result
    
    # LLM max（5）
    MAX_TEXT_LENGTH_FOR_LLM = 50000
    
    def _build_user_message(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str]
    ) -> str:
        """"""
        
        # 
        combined_text = "\n\n---\n\n".join(document_texts)
        original_length = len(combined_text)
        
        # 5，（LLMcontent，graph）
        if len(combined_text) > self.MAX_TEXT_LENGTH_FOR_LLM:
            combined_text = combined_text[:self.MAX_TEXT_LENGTH_FOR_LLM]
            combined_text += f"\n\n...({original_length}，{self.MAX_TEXT_LENGTH_FOR_LLM})..."
        
        message = f"""## simulation

{simulation_requirement}

## content

{combined_text}
"""
        
        if additional_context:
            message += f"""
## description

{additional_context}
"""
        
        message += """
content，simulationtypetype。

****：
1. 10type
2. 2type：Person（） Organization（）
3. 8contenttype
4. type，
5. name、uuid、group_id ， full_name、org_name 
"""
        
        return message
    
    def _validate_and_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """"""
        
        # 
        if "entity_types" not in result:
            result["entity_types"] = []
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""
        
        # type
        # name PascalCase ， edge source_targets 
        entity_name_map = {}
        for entity in result["entity_types"]:
            # entity name PascalCase（Zep API ）
            if "name" in entity:
                original_name = entity["name"]
                entity["name"] = _to_pascal_case(original_name)
                if entity["name"]!= original_name:
                    logger.warning(f"Entity type name '{original_name}' auto-converted to '{entity['name']}'")
                entity_name_map[original_name] = entity["name"]
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            # description100
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."
        
        # type
        for edge in result["edge_types"]:
            # edge name SCREAMING_SNAKE_CASE（Zep API ）
            if "name" in edge:
                original_name = edge["name"]
                edge["name"] = original_name.upper()
                if edge["name"]!= original_name:
                    logger.warning(f"Edge type name '{original_name}' auto-converted to '{edge['name']}'")
            # source_targets name， PascalCase 
            for st in edge.get("source_targets", []):
                if st.get("source") in entity_name_map:
                    st["source"] = entity_name_map[st["source"]]
                if st.get("target") in entity_name_map:
                    st["target"] = entity_name_map[st["target"]]
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []
            if len(edge.get("description", "")) > 100:
                edge["description"] = edge["description"][:97] + "..."
        
        # Zep API ： 10 type， 10 edgetype
        MAX_ENTITY_TYPES = 10
        MAX_EDGE_TYPES = 10

        # ： name ，
        seen_names = set()
        deduped = []
        for entity in result["entity_types"]:
            name = entity.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                deduped.append(entity)
            elif name in seen_names:
                logger.warning(f"Duplicate entity type '{name}' removed during validation")
        result["entity_types"] = deduped

        # type
        person_fallback = {
            "name": "Person",
            "description": "Any individual person not fitting other specific person types.",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "Full name of the person"},
                {"name": "role", "type": "text", "description": "Role or occupation"}
            ],
            "examples": ["ordinary citizen", "anonymous netizen"]
        }
        
        organization_fallback = {
            "name": "Organization",
            "description": "Any organization not fitting other specific organization types.",
            "attributes": [
                {"name": "org_name", "type": "text", "description": "Name of the organization"},
                {"name": "org_type", "type": "text", "description": "Type of organization"}
            ],
            "examples": ["small business", "community group"]
        }
        
        # type
        entity_names = {e["name"] for e in result["entity_types"]}
        has_person = "Person" in entity_names
        has_organization = "Organization" in entity_names
        
        # type
        fallbacks_to_add = []
        if not has_person:
            fallbacks_to_add.append(person_fallback)
        if not has_organization:
            fallbacks_to_add.append(organization_fallback)
        
        if fallbacks_to_add:
            current_count = len(result["entity_types"])
            needed_slots = len(fallbacks_to_add)
            
            # 10 ，type
            if current_count + needed_slots > MAX_ENTITY_TYPES:
                # 
                to_remove = current_count + needed_slots - MAX_ENTITY_TYPES
                # （type）
                result["entity_types"] = result["entity_types"][:-to_remove]
            
            # type
            result["entity_types"].extend(fallbacks_to_add)
        
        # （）
        if len(result["entity_types"]) > MAX_ENTITY_TYPES:
            result["entity_types"] = result["entity_types"][:MAX_ENTITY_TYPES]
        
        if len(result["edge_types"]) > MAX_EDGE_TYPES:
            result["edge_types"] = result["edge_types"][:MAX_EDGE_TYPES]
        
        return result
    
    def generate_python_code(self, ontology: Dict[str, Any]) -> str:
        """
        Python（ontology.py）
        
        Args:
            ontology: 
            
        Returns:
            Python
        """
        code_lines = [
            '"""',
            'type',
            'MiroFish，simulation',
            '"""',
            '',
            'from pydantic import Field',
            'from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel',
            '',
            '',
            '# ============== type ==============',
            '',
        ]
        
        # type
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            desc = entity.get("description", f"A {name} entity.")
            
            code_lines.append(f'class {name}(EntityModel):')
            code_lines.append(f' """{desc}"""')
            
            attrs = entity.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f' {attr_name}: EntityText = Field(')
                    code_lines.append(f' description="{attr_desc}",')
                    code_lines.append(f' default=None')
                    code_lines.append(f' )')
            else:
                code_lines.append(' pass')
            
            code_lines.append('')
            code_lines.append('')
        
        code_lines.append('# ============== type ==============')
        code_lines.append('')
        
        # type
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            # PascalCase
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            desc = edge.get("description", f"A {name} relationship.")
            
            code_lines.append(f'class {class_name}(EdgeModel):')
            code_lines.append(f' """{desc}"""')
            
            attrs = edge.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f' {attr_name}: EntityText = Field(')
                    code_lines.append(f' description="{attr_desc}",')
                    code_lines.append(f' default=None')
                    code_lines.append(f' )')
            else:
                code_lines.append(' pass')
            
            code_lines.append('')
            code_lines.append('')
        
        # type
        code_lines.append('# ============== typeconfiguration ==============')
        code_lines.append('')
        code_lines.append('ENTITY_TYPES = {')
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            code_lines.append(f' "{name}": {name},')
        code_lines.append('}')
        code_lines.append('')
        code_lines.append('EDGE_TYPES = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code_lines.append(f' "{name}": {class_name},')
        code_lines.append('}')
        code_lines.append('')
        
        # edgesource_targets
        code_lines.append('EDGE_SOURCE_TARGETS = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            source_targets = edge.get("source_targets", [])
            if source_targets:
                st_list = ', '.join([
                    f'{{"source": "{st.get("source", "Entity")}", "target": "{st.get("target", "Entity")}"}}'
                    for st in source_targets
                ])
                code_lines.append(f' "{name}": [{st_list}],')
        code_lines.append('}')
        
        return '\n'.join(code_lines)
