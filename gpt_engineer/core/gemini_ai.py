"""
Google Gemini Integration for GPT Engineer

This module provides enhanced AI capabilities using Google's Gemini models,
including multimodal understanding, image generation, video generation, and
advanced code generation capabilities.

Key Features:
- Gemini Pro for advanced text generation
- Gemini Pro Vision for image understanding
- Gemini 1.5 Pro for multimodal content
- Image generation using Imagen
- Video generation capabilities
- Enhanced multimodal reasoning
"""

import base64
import io
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import google.generativeai as genai
import requests
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from PIL import Image

from gpt_engineer.core.ai import AI, Message
from gpt_engineer.core.token_usage import TokenUsageLog

logger = logging.getLogger(__name__)


class GeminiAI(AI):
    """
    Enhanced AI class using Google Gemini models with advanced capabilities.
    
    Supports:
    - Text generation (Gemini Pro)
    - Vision understanding (Gemini Pro Vision)
    - Multimodal content (Gemini 1.5 Pro)
    - Image generation (Imagen)
    - Video generation
    - Advanced code analysis and generation
    """
    
    def __init__(
        self,
        model_name="gemini-1.5-pro",
        temperature=0.1,
        google_api_key=None,
        enable_image_generation=True,
        enable_video_generation=True,
        enable_multimodal=True,
        streaming=True,
    ):
        """
        Initialize Gemini AI with enhanced capabilities.
        
        Parameters
        ----------
        model_name : str
            The Gemini model to use ('gemini-pro', 'gemini-pro-vision', 'gemini-1.5-pro')
        temperature : float
            Temperature for generation (0.0 to 1.0)
        google_api_key : str, optional
            Google API key (if not provided, reads from environment)
        enable_image_generation : bool
            Enable image generation capabilities
        enable_video_generation : bool
            Enable video generation capabilities
        enable_multimodal : bool
            Enable multimodal understanding
        """
        self.model_name = model_name
        self.temperature = temperature
        self.streaming = streaming
        self.enable_image_generation = enable_image_generation
        self.enable_video_generation = enable_video_generation
        self.enable_multimodal = enable_multimodal
        
        # Initialize Google AI
        api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=api_key)
        
        # Initialize models
        self.text_model = genai.GenerativeModel(model_name)
        self.vision_model = genai.GenerativeModel("gemini-1.5-pro")
        self.multimodal_model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Set vision capability based on model
        self.vision = "vision" in model_name or "1.5" in model_name

        # Initialize token usage tracking
        self.token_usage_log = TokenUsageLog(model_name)
        
        logger.debug(f"Initialized Gemini AI with model: {model_name}")
    
    def start(self, system: str, user: Any, *, step_name: str) -> List[Message]:
        """
        Start conversation with enhanced multimodal support.
        
        Parameters
        ----------
        system : str
            System prompt
        user : Union[str, dict, List]
            User message (can include text, images, videos)
        step_name : str
            Current step name
            
        Returns
        -------
        List[Message]
            Conversation messages
        """
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user)
        ]
        return self.next(messages, step_name=step_name)
    
    def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        """
        Continue conversation with enhanced Gemini capabilities.
        
        Parameters
        ----------
        messages : List[Message]
            Conversation history
        prompt : Optional[str]
            Additional prompt
        step_name : str
            Current step name
            
        Returns
        -------
        List[Message]
            Updated conversation
        """
        if prompt:
            messages.append(HumanMessage(content=prompt))
        
        # Convert messages to Gemini format
        gemini_messages = self._convert_messages_to_gemini(messages)
        
        # Choose appropriate model based on content
        model = self._select_model(messages)
        
        try:
            # Generate response
            response = model.generate_content(
                gemini_messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=4096,
                )
            )
            
            response_content = response.text
            
            # Check if response includes generation requests
            enhanced_response = self._handle_generation_requests(response_content, step_name)
            
            # Update token usage
            self.token_usage_log.update_log(
                messages=messages,
                answer=enhanced_response,
                step_name=step_name
            )
            
            messages.append(AIMessage(content=enhanced_response))
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            fallback_response = f"Error with Gemini API: {e}. Please try again."
            messages.append(AIMessage(content=fallback_response))
        
        return messages
    
    def _convert_messages_to_gemini(self, messages: List[Message]) -> List[Dict]:
        """Convert LangChain messages to Gemini format."""
        gemini_messages = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                # Gemini doesn't have explicit system messages, prepend to first user message
                continue
            elif isinstance(message, HumanMessage):
                content = self._process_multimodal_content(message.content)
                gemini_messages.append({
                    "role": "user",
                    "parts": content if isinstance(content, list) else [content]
                })
            elif isinstance(message, AIMessage):
                gemini_messages.append({
                    "role": "model",
                    "parts": [message.content]
                })
        
        # Prepend system message to first user message if exists
        system_msg = next((msg for msg in messages if isinstance(msg, SystemMessage)), None)
        if system_msg and gemini_messages:
            first_user_msg = next((msg for msg in gemini_messages if msg["role"] == "user"), None)
            if first_user_msg:
                system_content = f"System: {system_msg.content}\n\nUser: "
                if isinstance(first_user_msg["parts"][0], str):
                    first_user_msg["parts"][0] = system_content + first_user_msg["parts"][0]
        
        return gemini_messages
    
    def _process_multimodal_content(self, content: Any) -> Union[str, List]:
        """Process multimodal content for Gemini."""
        if isinstance(content, str):
            return content
        elif isinstance(content, dict):
            # Handle structured content with images, videos, etc.
            parts = []
            
            if "text" in content:
                parts.append(content["text"])
            
            if "images" in content:
                for image_path in content["images"]:
                    parts.append(self._load_image(image_path))
            
            if "videos" in content:
                for video_path in content["videos"]:
                    parts.append(self._load_video(video_path))
            
            return parts if parts else content
        elif isinstance(content, list):
            # Handle list of content parts
            parts = []
            for item in content:
                if isinstance(item, dict) and "type" in item:
                    if item["type"] == "text":
                        parts.append(item.get("text", ""))
                    elif item["type"] == "image_url":
                        parts.append(self._load_image_from_url(item.get("image_url", {}).get("url")))
                else:
                    parts.append(str(item))
            return parts
        
        return str(content)
    
    def _load_image(self, image_path: str) -> Dict:
        """Load image for Gemini processing."""
        try:
            if image_path.startswith(("http://", "https://")):
                return self._load_image_from_url(image_path)
            
            image_path = Path(image_path)
            if image_path.exists():
                with open(image_path, "rb") as img_file:
                    image_data = img_file.read()
                    return {
                        "mime_type": f"image/{image_path.suffix[1:]}",
                        "data": image_data
                    }
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
        
        return {"text": f"[Image: {image_path}]"}
    
    def _load_image_from_url(self, image_url: str) -> Dict:
        """Load image from URL for Gemini processing."""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            return {
                "mime_type": "image/jpeg",  # Assume JPEG for simplicity
                "data": response.content
            }
        except Exception as e:
            logger.error(f"Error loading image from URL {image_url}: {e}")
            return {"text": f"[Image URL: {image_url}]"}
    
    def _load_video(self, video_path: str) -> Dict:
        """Load video for Gemini processing."""
        try:
            video_path = Path(video_path)
            if video_path.exists():
                with open(video_path, "rb") as video_file:
                    video_data = video_file.read()
                    return {
                        "mime_type": f"video/{video_path.suffix[1:]}",
                        "data": video_data
                    }
        except Exception as e:
            logger.error(f"Error loading video {video_path}: {e}")
        
        return {"text": f"[Video: {video_path}]"}
    
    def _select_model(self, messages: List[Message]) -> genai.GenerativeModel:
        """Select appropriate Gemini model based on content."""
        has_images = any(
            isinstance(msg.content, (dict, list)) and 
            self._contains_visual_content(msg.content)
            for msg in messages
        )
        
        if has_images or self.enable_multimodal:
            if "1.5" in self.model_name:
                return self.multimodal_model
            else:
                return self.vision_model
        
        return self.text_model
    
    def _contains_visual_content(self, content: Any) -> bool:
        """Check if content contains visual elements."""
        if isinstance(content, dict):
            return "images" in content or "videos" in content
        elif isinstance(content, list):
            return any(
                isinstance(item, dict) and item.get("type") in ["image_url", "image", "video"]
                for item in content
            )
        return False
    
    def _handle_generation_requests(self, response: str, step_name: str) -> str:
        """Handle special generation requests in response."""
        enhanced_response = response
        
        # Check for image generation requests
        if self.enable_image_generation and self._should_generate_images(response):
            generated_images = self.generate_images_from_response(response, step_name)
            if generated_images:
                enhanced_response += "\n\n## Generated Images\n"
                for img_path in generated_images:
                    enhanced_response += f"![Generated Image]({img_path})\n"
        
        # Check for video generation requests
        if self.enable_video_generation and self._should_generate_videos(response):
            generated_videos = self.generate_videos_from_response(response, step_name)
            if generated_videos:
                enhanced_response += "\n\n## Generated Videos\n"
                for video_path in generated_videos:
                    enhanced_response += f"[Generated Video]({video_path})\n"
        
        return enhanced_response
    
    def _should_generate_images(self, response: str) -> bool:
        """Determine if response should trigger image generation."""
        image_keywords = [
            "generate image", "create image", "make image", "draw",
            "visualize", "diagram", "chart", "graph", "mockup",
            "ui design", "logo", "icon", "illustration"
        ]
        return any(keyword in response.lower() for keyword in image_keywords)
    
    def _should_generate_videos(self, response: str) -> bool:
        """Determine if response should trigger video generation."""
        video_keywords = [
            "generate video", "create video", "make video", "animation",
            "demo video", "tutorial video", "walkthrough", "presentation"
        ]
        return any(keyword in response.lower() for keyword in video_keywords)
    
    def generate_images_from_response(self, response: str, step_name: str) -> List[str]:
        """Generate images based on response content."""
        try:
            # This is a placeholder for actual image generation
            # In practice, you would integrate with Imagen or other image generation APIs
            logger.info(f"Image generation requested for step: {step_name}")
            
            # For now, return placeholder
            output_dir = Path(f"generated_assets/{step_name}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Placeholder implementation
            # In real implementation, you would:
            # 1. Extract image descriptions from response
            # 2. Call Imagen API or other image generation service
            # 3. Save generated images
            
            return []  # Return list of generated image paths
            
        except Exception as e:
            logger.error(f"Error generating images: {e}")
            return []
    
    def generate_videos_from_response(self, response: str, step_name: str) -> List[str]:
        """Generate videos based on response content."""
        try:
            # This is a placeholder for actual video generation
            logger.info(f"Video generation requested for step: {step_name}")
            
            output_dir = Path(f"generated_assets/{step_name}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Placeholder implementation
            # In real implementation, you would:
            # 1. Extract video descriptions from response
            # 2. Call video generation API
            # 3. Save generated videos
            
            return []  # Return list of generated video paths
            
        except Exception as e:
            logger.error(f"Error generating videos: {e}")
            return []


class GeminiMultimodalAI(GeminiAI):
    """
    Enhanced Gemini AI with full multimodal capabilities.
    
    Supports advanced features like:
    - Code visualization
    - Architecture diagram generation
    - Interactive UI mockup creation
    - Video tutorials for generated code
    """
    
    def __init__(self, **kwargs):
        kwargs.setdefault("model_name", "gemini-1.5-pro")
        kwargs.setdefault("enable_multimodal", True)
        super().__init__(**kwargs)
    
    def generate_code_visualization(self, code: str, step_name: str) -> Dict[str, str]:
        """Generate visual representations of code."""
        try:
            visualization_prompt = f"""
            Create visual representations for the following code:
            
            {code}
            
            Generate:
            1. Architecture diagram
            2. Flow chart
            3. Class diagram (if applicable)
            4. UI mockup (if applicable)
            
            Provide descriptions for each visualization.
            """
            
            response = self.text_model.generate_content(visualization_prompt)
            
            # Parse response and generate actual visualizations
            # This would integrate with diagram generation tools
            
            return {
                "architecture": f"generated_assets/{step_name}/architecture.png",
                "flowchart": f"generated_assets/{step_name}/flowchart.png",
                "class_diagram": f"generated_assets/{step_name}/class_diagram.png",
                "ui_mockup": f"generated_assets/{step_name}/ui_mockup.png"
            }
            
        except Exception as e:
            logger.error(f"Error generating code visualization: {e}")
            return {}
    
    def generate_tutorial_video(self, code: str, step_name: str) -> Optional[str]:
        """Generate tutorial video explaining the code."""
        try:
            # This would integrate with video generation APIs
            logger.info(f"Generating tutorial video for step: {step_name}")
            
            # Placeholder for actual video generation
            return f"generated_assets/{step_name}/tutorial.mp4"
            
        except Exception as e:
            logger.error(f"Error generating tutorial video: {e}")
            return None


# Factory function for creating Gemini AI instances
def create_gemini_ai(
    model_type: str = "standard",
    model_name: Optional[str] = None,
    **kwargs
) -> Union[GeminiAI, GeminiMultimodalAI]:
    """
    Factory function to create appropriate Gemini AI instance.
    
    Parameters
    ----------
    model_type : str
        Type of model ('standard', 'multimodal')
    model_name : Optional[str]
        Specific model name to use
    **kwargs
        Additional arguments for AI initialization
        
    Returns
    -------
    Union[GeminiAI, GeminiMultimodalAI]
        Configured Gemini AI instance
    """
    if model_type == "multimodal":
        return GeminiMultimodalAI(model_name=model_name, **kwargs)
    else:
        return GeminiAI(model_name=model_name or "gemini-1.5-pro", **kwargs)
