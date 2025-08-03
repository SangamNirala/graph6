"""
Enhanced AI Image Prompt Generator - Professional Grade
Optimized for all major AI image generators with maximum detail and cross-platform compatibility
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ImagePromptComponents:
    """Structured components for building comprehensive AI image prompts"""
    subject: str = ""
    style: str = ""
    composition: str = ""
    lighting: str = ""
    environment: str = ""
    technical: str = ""
    colors: str = ""
    quality: str = ""
    mood: str = ""
    camera: str = ""
    post_processing: str = ""

class EnhancedImagePromptGenerator:
    """
    Elite AI Image Prompt Generator with cross-platform optimization
    Supports MidJourney, DALL-E 3, Stable Diffusion, Leonardo AI, Firefly, and more
    """
    
    def __init__(self):
        # Platform-specific optimization keywords
        self.platform_keywords = {
            "midjourney": [
                "--ar 16:9", "--style raw", "--stylize 500", 
                "professional photography", "commercial quality",
                "ultra-realistic", "8k uhd", "cinematic"
            ],
            "dalle3": [
                "photorealistic", "high resolution", "detailed",
                "professional", "commercial photography", 
                "studio lighting", "sharp focus"
            ],
            "stable_diffusion": [
                "masterpiece", "best quality", "ultra detailed",
                "8k uhd", "professional photography", "award winning",
                "highly detailed", "realistic"
            ],
            "leonardo": [
                "photorealistic", "ultra detailed", "professional",
                "cinematic", "high quality", "masterpiece"
            ]
        }
        
        # Enhanced quality modifiers for better output
        self.quality_enhancers = [
            "ultra-high resolution", "professional commercial photography",
            "award-winning composition", "masterpiece quality",
            "studio-grade lighting", "editorial excellence",
            "razor-sharp focus", "color-graded perfection",
            "museum-quality detail", "flagship camera quality"
        ]
        
        # Cross-platform compatible style descriptors
        self.style_descriptors = {
            "cinematic": "cinematic photography, movie still quality, dramatic lighting, film grain, color graded, professional cinematography",
            "commercial": "commercial photography, advertising quality, clean professional aesthetic, studio lighting, high-end production value",
            "documentary": "documentary photography style, natural lighting, authentic moments, journalistic approach, candid realism",
            "portrait": "professional portrait photography, studio portrait, headshot quality, perfect skin texture, professional retouching",
            "lifestyle": "lifestyle photography, natural authentic moments, warm inviting atmosphere, everyday beauty, relatable scenarios"
        }
        
        # Advanced lighting setups
        self.lighting_setups = {
            "professional": "three-point lighting setup with key light at 45 degrees, soft fill light, subtle rim lighting",
            "natural": "soft natural window light, golden hour warmth, gentle shadows, organic light fall-off",
            "studio": "professional studio lighting with softboxes, controlled shadows, even illumination, color temperature balanced",
            "dramatic": "dramatic chiaroscuro lighting, strong key light, deep shadows, high contrast, moody atmosphere",
            "soft": "soft diffused lighting, minimal shadows, even illumination, flattering skin tones, gentle contrast"
        }
        
        # Enhanced camera specifications
        self.camera_specs = {
            "professional": "Canon EOS R5, 85mm f/1.4L lens, f/2.8, ISO 200, 1/125s",
            "cinematic": "RED Dragon 6K, Zeiss Master Prime 85mm, T2.1, professional cinema camera",
            "commercial": "Phase One XF IQ4, Schneider 80mm LS f/2.8, medium format quality",
            "portrait": "Nikon D850, 105mm f/1.4E, professional portrait setup",
            "editorial": "Hasselblad X2D 100C, XCD 90mm f/3.2, medium format editorial quality"
        }

    def generate_enhanced_prompt(self, 
                                base_description: str,
                                style: str = "cinematic",
                                mood: str = "professional", 
                                platform: str = "universal",
                                shot_type: str = "medium",
                                lighting: str = "professional",
                                environment: str = "studio") -> str:
        """
        Generate ultra-detailed AI image prompt optimized for all platforms
        """
        
        components = ImagePromptComponents()
        
        # 1. Enhanced Subject Description
        components.subject = self._enhance_subject_description(base_description, shot_type)
        
        # 2. Advanced Style Specification
        components.style = self._get_style_specification(style, platform)
        
        # 3. Professional Composition Details
        components.composition = self._get_composition_details(shot_type)
        
        # 4. Advanced Lighting Setup
        components.lighting = self._get_lighting_specification(lighting, mood)
        
        # 5. Detailed Environment Description
        components.environment = self._get_environment_details(environment, mood)
        
        # 6. Professional Camera Specifications
        components.camera = self._get_camera_specifications(style)
        
        # 7. Color Palette & Mood
        components.colors = self._get_color_specifications(mood, style)
        
        # 8. Advanced Quality Modifiers
        components.quality = self._get_quality_modifiers(platform)
        
        # 9. Technical Specifications
        components.technical = self._get_technical_specifications()
        
        # 10. Post-processing Details
        components.post_processing = self._get_post_processing_details(style)
        
        # Combine all components into ultra-detailed prompt
        enhanced_prompt = self._combine_components(components)
        
        # Add platform-specific optimizations
        if platform != "universal":
            enhanced_prompt = self._add_platform_optimizations(enhanced_prompt, platform)
        
        return enhanced_prompt

    def _enhance_subject_description(self, base_description: str, shot_type: str) -> str:
        """Enhance subject description with ultra-specific details"""
        
        # Base enhancement patterns
        enhancements = []
        
        # Add detailed physical attributes if not present
        if "eyes" not in base_description.lower():
            enhancements.append("expressive eyes with natural catchlight")
        
        if "hair" not in base_description.lower():
            enhancements.append("professionally styled hair")
        
        if "skin" not in base_description.lower():
            enhancements.append("natural healthy skin tone with professional makeup")
        
        # Add posture and expression details
        posture_details = {
            "close_up": "perfect posture, confident expression, direct eye contact",
            "medium": "natural confident pose, engaging body language, approachable demeanor", 
            "wide": "full body composition, dynamic pose, environmental interaction"
        }
        
        enhanced_subject = base_description
        if shot_type in posture_details:
            enhanced_subject += f", {posture_details[shot_type]}"
        
        if enhancements:
            enhanced_subject += f", {', '.join(enhancements)}"
        
        return enhanced_subject

    def _get_style_specification(self, style: str, platform: str) -> str:
        """Get comprehensive style specifications"""
        base_style = self.style_descriptors.get(style, "professional photography style")
        
        # Add platform-specific style keywords
        if platform in self.platform_keywords:
            platform_styles = [kw for kw in self.platform_keywords[platform] if "style" in kw.lower()]
            if platform_styles:
                base_style += f", {', '.join(platform_styles)}"
        
        return base_style

    def _get_composition_details(self, shot_type: str) -> str:
        """Get detailed composition specifications"""
        compositions = {
            "close_up": "tight close-up framing, eyes at upper third intersection, shallow depth of field f/1.4, subject fills 70% of frame, intimate composition",
            "medium": "medium shot composition, rule of thirds positioning, subject from waist up, balanced negative space, professional framing",
            "wide": "wide establishing shot, full body in frame, environmental context, leading lines, balanced composition with foreground and background elements",
            "portrait": "classic portrait composition, eyes at golden ratio intersection, vertical orientation, professional headshot framing"
        }
        
        return compositions.get(shot_type, compositions["medium"])

    def _get_lighting_specification(self, lighting: str, mood: str) -> str:
        """Get advanced lighting specifications"""
        base_lighting = self.lighting_setups.get(lighting, self.lighting_setups["professional"])
        
        # Add mood-specific lighting adjustments
        mood_lighting = {
            "professional": "clean professional lighting, minimal shadows, even skin tones",
            "warm": "warm 3200K color temperature, golden hour quality, soft shadows",
            "dramatic": "high contrast lighting, dramatic shadows, moody atmosphere",
            "bright": "bright even illumination, minimal shadows, high-key lighting",
            "intimate": "soft romantic lighting, warm tones, gentle shadows"
        }
        
        if mood in mood_lighting:
            base_lighting += f", {mood_lighting[mood]}"
        
        return base_lighting

    def _get_environment_details(self, environment: str, mood: str) -> str:
        """Get detailed environment specifications"""
        environments = {
            "studio": "professional photography studio, seamless white cyclorama background, controlled lighting environment, minimalist setup",
            "office": "modern professional office space, floor-to-ceiling windows, contemporary furniture, clean architectural lines, natural light",
            "outdoor": "natural outdoor setting, beautiful landscape background, organic environment, natural lighting conditions",
            "home": "comfortable home interior, warm inviting atmosphere, natural furnishings, lived-in authenticity",
            "urban": "contemporary urban environment, city backdrop, modern architecture, dynamic urban energy"
        }
        
        base_env = environments.get(environment, environments["studio"])
        
        # Add mood-specific environmental details
        mood_environments = {
            "professional": "clean organized space, professional aesthetics, purposeful elements",
            "warm": "cozy inviting atmosphere, warm textures, comfortable furnishings",
            "modern": "contemporary design elements, sleek surfaces, minimalist aesthetic"
        }
        
        if mood in mood_environments:
            base_env += f", {mood_environments[mood]}"
        
        return base_env

    def _get_camera_specifications(self, style: str) -> str:
        """Get professional camera specifications"""
        return self.camera_specs.get(style, self.camera_specs["professional"])

    def _get_color_specifications(self, mood: str, style: str) -> str:
        """Get detailed color palette specifications"""
        color_palettes = {
            "professional": "professional color palette with navy blues, crisp whites, and silver accents, high contrast, color-graded perfection",
            "warm": "warm inviting color palette with golden tones, cream colors, soft browns, natural wood accents, cozy atmosphere",
            "dramatic": "dramatic high-contrast color palette, deep shadows, bright highlights, cinematic color grading",
            "bright": "bright cheerful color palette with vibrant but natural colors, high saturation, optimistic tones",
            "elegant": "sophisticated color palette with muted tones, elegant neutrals, refined color harmony"
        }
        
        return color_palettes.get(mood, color_palettes["professional"])

    def _get_quality_modifiers(self, platform: str) -> str:
        """Get platform-optimized quality modifiers"""
        base_quality = "ultra-high resolution, masterpiece quality, professional photography, award-winning composition, razor-sharp focus, perfect detail"
        
        if platform in self.platform_keywords:
            platform_quality = [kw for kw in self.platform_keywords[platform] if any(q in kw.lower() for q in ["quality", "detailed", "realistic", "resolution"])]
            if platform_quality:
                base_quality += f", {', '.join(platform_quality)}"
        
        return base_quality

    def _get_technical_specifications(self) -> str:
        """Get advanced technical specifications"""
        return "8K UHD resolution, 16:9 aspect ratio, professional color space, HDR quality, perfect exposure, optimal depth of field"

    def _get_post_processing_details(self, style: str) -> str:
        """Get post-processing specifications"""
        processing = {
            "cinematic": "professional color grading, film-like quality, subtle film grain, cinematic post-processing",
            "commercial": "commercial retouching, perfect skin tone, advertising quality finish, professional post-production",
            "natural": "natural color correction, minimal processing, authentic look, organic feel",
            "dramatic": "enhanced contrast, dramatic post-processing, moody color grading, cinematic effects"
        }
        
        return processing.get(style, processing["commercial"])

    def _combine_components(self, components: ImagePromptComponents) -> str:
        """Combine all components into coherent ultra-detailed prompt"""
        
        # Structure the prompt for maximum effectiveness
        prompt_parts = []
        
        # Start with subject (most important)
        if components.subject:
            prompt_parts.append(components.subject)
        
        # Add style and composition
        if components.style:
            prompt_parts.append(components.style)
        
        if components.composition:
            prompt_parts.append(components.composition)
        
        # Add lighting and environment
        if components.lighting:
            prompt_parts.append(components.lighting)
        
        if components.environment:
            prompt_parts.append(components.environment)
        
        # Add technical specifications
        if components.camera:
            prompt_parts.append(components.camera)
        
        if components.technical:
            prompt_parts.append(components.technical)
        
        # Add colors and mood
        if components.colors:
            prompt_parts.append(components.colors)
        
        if components.post_processing:
            prompt_parts.append(components.post_processing)
        
        # Add quality modifiers at the end
        if components.quality:
            prompt_parts.append(components.quality)
        
        # Join with proper punctuation
        enhanced_prompt = ", ".join([part.strip() for part in prompt_parts if part.strip()])
        
        return enhanced_prompt

    def _add_platform_optimizations(self, prompt: str, platform: str) -> str:
        """Add platform-specific optimizations"""
        if platform not in self.platform_keywords:
            return prompt
        
        # Add platform-specific keywords that aren't already included
        platform_kw = self.platform_keywords[platform]
        
        for keyword in platform_kw:
            if keyword.lower() not in prompt.lower() and not keyword.startswith("--"):
                prompt += f", {keyword}"
        
        # Add MidJourney parameters at the end
        if platform == "midjourney":
            mj_params = [kw for kw in platform_kw if kw.startswith("--")]
            if mj_params:
                prompt += f" {' '.join(mj_params)}"
        
        return prompt

    def optimize_for_platform(self, prompt: str, target_platform: str) -> str:
        """Optimize existing prompt for specific platform"""
        return self._add_platform_optimizations(prompt, target_platform)

    def extract_and_enhance_image_prompts(self, script_text: str) -> str:
        """Extract and enhance all image prompts in a script"""
        
        # Pattern to find AI image prompts in scripts
        pattern = r'\*\*\[([^\]]+)\] AI IMAGE PROMPT:\*\*\s*"([^"]+)"'
        
        def enhance_match(match):
            timestamp = match.group(1)
            original_prompt = match.group(2)
            
            # Enhance the prompt
            enhanced = self.generate_enhanced_prompt(
                base_description=original_prompt,
                style="cinematic",
                mood="professional",
                platform="universal"
            )
            
            return f'**[{timestamp}] AI IMAGE PROMPT:**\n"{enhanced}"'
        
        # Replace all image prompts with enhanced versions
        enhanced_script = re.sub(pattern, enhance_match, script_text)
        
        return enhanced_script