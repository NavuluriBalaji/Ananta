"""
Enhanced Steps for Gemini AI Integration

This module provides enhanced steps that leverage Google Gemini's unique capabilities
including multimodal understanding, image generation, video generation, and
advanced code analysis.

Functions
---------
gemini_gen_code : function
    Generate code using Gemini with enhanced multimodal capabilities.

gemini_gen_visual_assets : function
    Generate visual assets (images, diagrams, videos) for the project.

gemini_analyze_images : function
    Analyze images in the prompt for better code generation.

gemini_generate_documentation : function
    Generate comprehensive documentation with visual elements.

gemini_create_tutorials : function
    Create interactive tutorials and video content.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from gpt_engineer.core.base_memory import BaseMemory
from gpt_engineer.core.chat_to_files import chat_to_files_dict
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.gemini_ai import GeminiAI, GeminiMultimodalAI
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.prompt import Prompt

logger = logging.getLogger(__name__)


def gemini_gen_code(
    ai: GeminiAI, 
    prompt: Prompt, 
    memory: BaseMemory, 
    preprompts_holder: PrepromptsHolder,
    generate_assets: bool = True
) -> FilesDict:
    """
    Generate code using Gemini with enhanced multimodal capabilities.
    
    This function leverages Gemini's advanced understanding of images, diagrams,
    and multimodal content to generate better code that matches visual specifications.
    
    Parameters
    ----------
    ai : GeminiAI
        The Gemini AI model instance
    prompt : Prompt
        The user prompt (may include images and other media)
    memory : BaseMemory
        Memory interface for storing data
    preprompts_holder : PrepromptsHolder
        Holder for preprompt messages
    generate_assets : bool
        Whether to generate visual assets along with code
        
    Returns
    -------
    FilesDict
        Dictionary of generated files
    """
    preprompts = preprompts_holder.get_preprompts()
    
    # Enhanced system prompt for Gemini
    system_prompt = _setup_gemini_system_prompt(preprompts, generate_assets)
    
    # Process multimodal prompt
    enhanced_prompt = _enhance_prompt_with_context(prompt, ai)
    
    # Generate code with Gemini
    messages = ai.start(
        system_prompt, 
        enhanced_prompt.to_langchain_content(), 
        step_name="gemini_gen_code"
    )
    
    chat = messages[-1].content.strip()
    memory.log("gemini_code_gen_log.txt", "\n\n".join(x.pretty_repr() for x in messages))
    
    # Extract files from response
    files_dict = chat_to_files_dict(chat)
    
    # Generate additional assets if requested
    if generate_assets and isinstance(ai, GeminiMultimodalAI):
        assets = _generate_project_assets(ai, files_dict, prompt, memory)
        files_dict.update(assets)
    
    return files_dict


def gemini_gen_visual_assets(
    ai: GeminiMultimodalAI,
    files_dict: FilesDict,
    prompt: Prompt,
    memory: BaseMemory,
    asset_types: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Generate visual assets for the project using Gemini's capabilities.
    
    Parameters
    ----------
    ai : GeminiMultimodalAI
        Multimodal Gemini AI instance
    files_dict : FilesDict
        Current project files
    prompt : Prompt
        Original project prompt
    memory : BaseMemory
        Memory interface
    asset_types : Optional[List[str]]
        Types of assets to generate ('diagrams', 'mockups', 'videos', 'tutorials')
        
    Returns
    -------
    Dict[str, str]
        Dictionary mapping asset types to file paths
    """
    if asset_types is None:
        asset_types = ['diagrams', 'mockups', 'videos', 'tutorials']
    
    assets = {}
    
    try:
        # Generate architecture diagrams
        if 'diagrams' in asset_types:
            diagrams = ai.generate_code_visualization(
                str(files_dict), 
                "visual_assets"
            )
            assets.update(diagrams)
        
        # Generate UI mockups
        if 'mockups' in asset_types:
            mockups = _generate_ui_mockups(ai, files_dict, prompt)
            assets.update(mockups)
        
        # Generate tutorial videos
        if 'videos' in asset_types or 'tutorials' in asset_types:
            tutorial_video = ai.generate_tutorial_video(
                str(files_dict),
                "tutorial"
            )
            if tutorial_video:
                assets['tutorial_video'] = tutorial_video
        
        # Log generated assets
        memory.log("generated_assets.json", json.dumps(assets, indent=2))
        
    except Exception as e:
        logger.error(f"Error generating visual assets: {e}")
    
    return assets


def gemini_analyze_images(
    ai: GeminiAI,
    prompt: Prompt,
    memory: BaseMemory
) -> Dict[str, str]:
    """
    Analyze images in the prompt to extract design requirements.
    
    Parameters
    ----------
    ai : GeminiAI
        Gemini AI instance with vision capabilities
    prompt : Prompt
        Prompt containing images
    memory : BaseMemory
        Memory interface
        
    Returns
    -------
    Dict[str, str]
        Analysis results for each image
    """
    if not prompt.image_urls or not ai.vision:
        return {}
    
    analysis_results = {}
    
    try:
        analysis_prompt = """
        Analyze the provided images and extract:
        1. UI/UX design requirements
        2. Architecture patterns shown
        3. Color schemes and styling
        4. Component layouts
        5. User flow implications
        6. Technical requirements inferred from visuals
        
        Provide detailed analysis for code generation.
        """
        
        # Create multimodal content
        multimodal_content = {
            "text": analysis_prompt,
            "images": prompt.image_urls
        }
        
        messages = ai.start(
            "You are an expert at analyzing visual designs and extracting technical requirements.",
            multimodal_content,
            step_name="image_analysis"
        )
        
        analysis = messages[-1].content.strip()
        analysis_results["image_analysis"] = analysis
        
        memory.log("image_analysis.txt", analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing images: {e}")
        analysis_results["error"] = str(e)
    
    return analysis_results


def gemini_generate_documentation(
    ai: GeminiMultimodalAI,
    files_dict: FilesDict,
    prompt: Prompt,
    memory: BaseMemory,
    include_visuals: bool = True
) -> FilesDict:
    """
    Generate comprehensive documentation with visual elements.
    
    Parameters
    ----------
    ai : GeminiMultimodalAI
        Multimodal Gemini AI instance
    files_dict : FilesDict
        Project files
    prompt : Prompt
        Original prompt
    memory : BaseMemory
        Memory interface
    include_visuals : bool
        Whether to include visual elements in documentation
        
    Returns
    -------
    FilesDict
        Documentation files
    """
    doc_prompt = f"""
    Generate comprehensive documentation for this project:
    
    Original Requirements:
    {prompt.text}
    
    Generated Code:
    {files_dict.to_chat()}
    
    Create:
    1. README.md with project overview
    2. API_DOCUMENTATION.md
    3. SETUP_GUIDE.md
    4. USER_GUIDE.md
    5. DEVELOPMENT_GUIDE.md
    6. ARCHITECTURE.md
    
    {'Include references to visual assets and diagrams.' if include_visuals else ''}
    """
    
    messages = ai.start(
        "You are a technical documentation expert. Create clear, comprehensive documentation.",
        doc_prompt,
        step_name="documentation_generation"
    )
    
    response = messages[-1].content.strip()
    memory.log("documentation_generation.txt", response)
    
    # Extract documentation files
    docs_dict = chat_to_files_dict(response)
    
    # Generate visual documentation assets if requested
    if include_visuals:
        visual_docs = _generate_documentation_visuals(ai, files_dict, "docs")
        docs_dict.update(visual_docs)
    
    return docs_dict


def gemini_create_tutorials(
    ai: GeminiMultimodalAI,
    files_dict: FilesDict,
    prompt: Prompt,
    memory: BaseMemory
) -> Dict[str, str]:
    """
    Create interactive tutorials and learning materials.
    
    Parameters
    ----------
    ai : GeminiMultimodalAI
        Multimodal Gemini AI instance
    files_dict : FilesDict
        Project files
    prompt : Prompt
        Original prompt
    memory : BaseMemory
        Memory interface
        
    Returns
    -------
    Dict[str, str]
        Tutorial files and assets
    """
    tutorial_prompt = f"""
    Create interactive tutorials for this project:
    
    Project: {prompt.text}
    Code: {files_dict.to_chat()}
    
    Generate:
    1. Step-by-step setup tutorial
    2. Code walkthrough tutorial
    3. Feature demonstration scripts
    4. Troubleshooting guide
    5. Video tutorial script
    
    Make tutorials beginner-friendly and interactive.
    """
    
    messages = ai.start(
        "You are an expert tutorial creator. Make engaging, educational content.",
        tutorial_prompt,
        step_name="tutorial_creation"
    )
    
    response = messages[-1].content.strip()
    memory.log("tutorial_creation.txt", response)
    
    # Extract tutorial files
    tutorials_dict = chat_to_files_dict(response)
    
    # Generate video tutorial
    video_path = ai.generate_tutorial_video(str(files_dict), "tutorial")
    if video_path:
        tutorials_dict["tutorial_video.mp4"] = f"Video tutorial available at: {video_path}"
    
    return tutorials_dict


def _setup_gemini_system_prompt(preprompts: Dict, generate_assets: bool) -> str:
    """Setup enhanced system prompt for Gemini."""
    base_prompt = (
        preprompts["roadmap"]
        + preprompts["generate"].replace("FILE_FORMAT", preprompts["file_format"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )
    
    if generate_assets:
        asset_prompt = """
        
        ENHANCED CAPABILITIES:
        - If the prompt includes images, analyze them carefully for design requirements
        - Generate visual assets when appropriate (mention in comments where diagrams would help)
        - Consider user experience and visual design in your code generation
        - Suggest visual documentation and tutorials where beneficial
        - Think about multimedia aspects of the project
        """
        base_prompt += asset_prompt
    
    return base_prompt


def _enhance_prompt_with_context(prompt: Prompt, ai: GeminiAI) -> Prompt:
    """Enhance prompt with additional context for better generation."""
    if prompt.image_urls and ai.vision:
        # Add image analysis context
        enhanced_text = f"""
        {prompt.text}
        
        VISUAL CONTEXT:
        Images have been provided that show design requirements, UI mockups, or architectural diagrams.
        Please analyze these images carefully and incorporate their requirements into the generated code.
        """
        
        return Prompt(
            text=enhanced_text,
            image_urls=prompt.image_urls,
            entrypoint_prompt=prompt.entrypoint_prompt
        )
    
    return prompt


def _generate_project_assets(
    ai: GeminiMultimodalAI,
    files_dict: FilesDict,
    prompt: Prompt,
    memory: BaseMemory
) -> FilesDict:
    """Generate additional project assets."""
    assets = FilesDict()
    
    try:
        # Generate project structure diagram
        structure_prompt = f"""
        Create a project structure visualization file (ASCII art or markdown diagram) 
        for this project based on the generated files:
        
        {files_dict.to_chat()}
        
        Show file relationships and dependencies.
        """
        
        messages = ai.start(
            "Create clear project structure documentation.",
            structure_prompt,
            step_name="project_structure"
        )
        
        structure_doc = messages[-1].content.strip()
        assets["PROJECT_STRUCTURE.md"] = structure_doc
        
        # Generate setup visualization
        if "requirements.txt" in files_dict or "package.json" in files_dict:
            setup_prompt = f"""
            Create a visual setup guide (markdown with ASCII diagrams) for this project:
            
            Files: {list(files_dict.keys())}
            Original prompt: {prompt.text}
            
            Include dependency installation and running instructions.
            """
            
            setup_messages = ai.start(
                "Create clear setup documentation with visual elements.",
                setup_prompt,
                step_name="setup_guide"
            )
            
            setup_doc = setup_messages[-1].content.strip()
            assets["SETUP_VISUAL_GUIDE.md"] = setup_doc
        
    except Exception as e:
        logger.error(f"Error generating project assets: {e}")
    
    return assets


def _generate_ui_mockups(ai: GeminiMultimodalAI, files_dict: FilesDict, prompt: Prompt) -> Dict[str, str]:
    """Generate UI mockups for the project."""
    mockups = {}
    
    try:
        # Check if this is a UI project
        ui_files = [f for f in files_dict.keys() if any(ext in f.lower() for ext in ['.html', '.css', '.js', '.jsx', '.vue', '.svelte'])]
        
        if ui_files:
            mockup_prompt = f"""
            Create UI mockup descriptions for this web project:
            
            Original requirements: {prompt.text}
            UI Files: {ui_files}
            
            Describe the visual layout, components, and user interface elements.
            """
            
            messages = ai.start(
                "You are a UI/UX designer. Create detailed mockup descriptions.",
                mockup_prompt,
                step_name="ui_mockups"
            )
            
            mockup_description = messages[-1].content.strip()
            mockups["UI_MOCKUPS.md"] = mockup_description
    
    except Exception as e:
        logger.error(f"Error generating UI mockups: {e}")
    
    return mockups


def _generate_documentation_visuals(ai: GeminiMultimodalAI, files_dict: FilesDict, step_name: str) -> FilesDict:
    """Generate visual documentation assets."""
    visual_docs = FilesDict()
    
    try:
        # Generate architecture overview
        arch_prompt = f"""
        Create a detailed architecture description with ASCII diagrams for:
        
        Files: {list(files_dict.keys())}
        
        Include:
        1. Component relationships
        2. Data flow
        3. System architecture
        4. Deployment structure
        """
        
        messages = ai.start(
            "Create clear architectural documentation with visual elements.",
            arch_prompt,
            step_name=f"{step_name}_architecture"
        )
        
        arch_doc = messages[-1].content.strip()
        visual_docs["ARCHITECTURE_VISUAL.md"] = arch_doc
        
    except Exception as e:
        logger.error(f"Error generating documentation visuals: {e}")
    
    return visual_docs
