import streamlit as st
import openai
import anthropic
import google.generativeai as genai
from typing import Dict, Any
import json
import sys
import warnings
from datetime import datetime, date, time
import requests
from io import BytesIO
import base64

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure page
st.set_page_config(
    page_title="Social Media Post Generator",
    page_icon="📱",
    layout="wide"
)


class AIProviders:
    @staticmethod
    def openai_generate(api_key: str, prompt: str) -> str:
        """Generate content using OpenAI GPT"""
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error with OpenAI: {str(e)}"

    @staticmethod
    def openai_generate_image(api_key: str, prompt: str) -> str:
        """Generate image using OpenAI DALL-E"""
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            return f"Error generating image with OpenAI: {str(e)}"

    @staticmethod
    def claude_generate(api_key: str, prompt: str) -> str:
        """Generate content using Anthropic Claude"""
        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error with Claude: {str(e)}"

    @staticmethod
    def gemini_generate(api_key: str, prompt: str) -> str:
        """Generate content using Google Gemini"""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error with Gemini: {str(e)}"


def create_image_prompt(event_name: str, event_description: str, venue: str) -> str:
    """Create prompt for image generation"""
    prompt = f"""
    Create a professional, eye-catching image for a social media post about:
    Event: {event_name}
    Description: {event_description}
    Venue: {venue}

    Style: Modern, clean, professional social media graphics with vibrant colors.
    Include: Event theme elements, professional typography space for text overlay.
    Avoid: Specific text, faces, or copyrighted content.
    """
    return prompt


def create_prompt(event_name: str, event_description: str, tone: str, platform: str,
                  event_date: str, event_time: str, venue: str) -> str:
    """Create platform-specific prompts with event details"""

    platform_specs = {
        "LinkedIn": {
            "limit": "700 characters",
            "style": "professional networking post with business language",
            "features": "Include relevant hashtags, professional call-to-action, and networking angle"
        },
        "Twitter": {
            "limit": "280 characters",
            "style": "concise and engaging tweet",
            "features": "Include relevant hashtags, mentions, and compelling hook"
        },
        "WhatsApp": {
            "limit": "500 characters",
            "style": "casual and personal message",
            "features": "Use emojis, friendly tone, and personal invitation style"
        }
    }

    spec = platform_specs[platform]

    prompt = f"""
    Create a {platform} post about the following event:

    Event Name: {event_name}
    Event Description: {event_description}
    Date: {event_date}
    Time: {event_time}
    Venue: {venue}
    Tone: {tone}

    Requirements:
    - Maximum {spec['limit']}
    - Style: {spec['style']}
    - {spec['features']}
    - Tone should be {tone}
    - MUST include date, time, and venue information
    - Make it engaging and action-oriented

    Generate only the post content, no additional explanation.
    """

    return prompt


def format_datetime_display(event_date, event_time):
    """Format date and time for display"""
    try:
        # Format date
        if isinstance(event_date, date):
            formatted_date = event_date.strftime("%B %d, %Y")
        else:
            formatted_date = str(event_date)

        # Format time
        if isinstance(event_time, time):
            formatted_time = event_time.strftime("%I:%M %p")
        else:
            formatted_time = str(event_time)

        return f"{formatted_date} at {formatted_time}"
    except:
        return f"{event_date} at {event_time}"


def main():
    st.title("📱 Social Media Post Generator with Images")
    st.markdown("Generate engaging posts for LinkedIn, Twitter, and WhatsApp using AI with relevant images")

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # AI Provider selection
        ai_providers = {
            "OpenAI (GPT + DALL-E)": "openai",
            "Anthropic (Claude)": "claude",
            "Google (Gemini)": "gemini"
        }

        selected_provider = st.selectbox(
            "Select AI Provider:",
            options=list(ai_providers.keys()),
            help="Choose your preferred AI provider. OpenAI includes image generation."
        )

        # API Key input
        api_key = st.text_input(
            "API Key:",
            type="password",
            help="Enter your API key for the selected provider"
        )

        # Tone selection
        tones = [
            "Professional",
            "Casual",
            "Enthusiastic",
            "Sarcastic",
            "Humorous",
            "Inspirational",
            "Urgent",
            "Friendly"
        ]

        selected_tone = st.selectbox(
            "Select Tone:",
            options=tones,
            help="Choose the tone for your posts"
        )

        # Image generation option
        generate_images = st.checkbox(
            "Generate Images (OpenAI only)",
            value=True,
            help="Generate relevant images for posts (requires OpenAI API)"
        )

    # Main content area
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("📝 Event Details")

        event_name = st.text_input(
            "Event Name:",
            placeholder="e.g., Annual Tech Conference 2024"
        )

        event_description = st.text_area(
            "Event Description:",
            height=100,
            placeholder="Describe your event in detail..."
        )

        # Date and Time inputs
        col_date, col_time = st.columns(2)

        with col_date:
            event_date = st.date_input(
                "Event Date:",
                value=datetime.now().date()
            )

        with col_time:
            event_time = st.time_input(
                "Event Time:",
                value=datetime.now().time()
            )

        venue = st.text_input(
            "Venue:",
            placeholder="e.g., Convention Center, Virtual Event, etc."
        )

        # Additional event details
        with st.expander("📋 Additional Details (Optional)"):
            registration_link = st.text_input(
                "Registration Link:",
                placeholder="https://your-event-registration.com"
            )

            contact_info = st.text_input(
                "Contact Information:",
                placeholder="contact@yourcompany.com"
            )

        generate_button = st.button(
            "🚀 Generate Posts & Images",
            type="primary",
            use_container_width=True
        )

    with col2:
        st.header("📱 Generated Content")

        if generate_button:
            if not all([event_name, event_description, venue]):
                st.error("Please fill in event name, description, and venue.")
            elif not api_key:
                st.error("Please enter your API key.")
            else:
                # Get the provider function
                provider_key = ai_providers[selected_provider]

                if provider_key == "openai":
                    generate_func = AIProviders.openai_generate
                elif provider_key == "claude":
                    generate_func = AIProviders.claude_generate
                elif provider_key == "gemini":
                    generate_func = AIProviders.gemini_generate

                # Format datetime for display
                datetime_str = format_datetime_display(event_date, event_time)

                # Generate image if OpenAI is selected and option is enabled
                generated_image_url = None
                if generate_images and provider_key == "openai":
                    with st.spinner("Generating event image..."):
                        image_prompt = create_image_prompt(event_name, event_description, venue)
                        generated_image_url = AIProviders.openai_generate_image(api_key, image_prompt)

                        if not generated_image_url.startswith("Error"):
                            st.subheader("🎨 Generated Event Image")
                            st.image(generated_image_url, caption="AI Generated Event Image", use_container_width=True)
                        else:
                            st.warning(f"Image generation failed: {generated_image_url}")

                # Generate posts for each platform
                platforms = ["LinkedIn", "Twitter", "WhatsApp"]

                with st.spinner("Generating posts..."):
                    for platform in platforms:
                        with st.expander(f"📊 {platform} Post", expanded=True):
                            prompt = create_prompt(
                                event_name,
                                event_description,
                                selected_tone.lower(),
                                platform,
                                datetime_str,
                                str(event_time),
                                venue
                            )

                            # Generate content
                            content = generate_func(api_key, prompt)

                            # Display event summary
                            st.write("**📅 Event Summary:**")
                            st.info(f"**{event_name}**\n📅 {datetime_str}\n📍 {venue}")

                            # Display the generated post
                            st.write("**Generated Post:**")
                            st.success(content)

                            # Character count
                            char_count = len(content)

                            # Platform-specific limits
                            limits = {"LinkedIn": 700, "Twitter": 280, "WhatsApp": 500}
                            limit = limits[platform]

                            if char_count <= limit:
                                st.success(f"✅ Character count: {char_count}/{limit}")
                            else:
                                st.warning(f"⚠️ Character count: {char_count}/{limit} (exceeds limit)")

                            # Show image for this platform if available
                            if generated_image_url and not generated_image_url.startswith("Error"):
                                st.write("**🖼️ Suggested Image:**")
                                st.image(generated_image_url, width=300)

                            # Additional options
                            col_copy, col_edit = st.columns(2)

                            with col_copy:
                                if st.button(f"📋 Copy {platform} Post", key=f"copy_{platform}"):
                                    st.success(f"{platform} post ready to copy!")

                            with col_edit:
                                if st.button(f"✏️ Edit {platform} Post", key=f"edit_{platform}"):
                                    st.info("Click to customize this post further...")

                # Additional resources section
                st.subheader("📚 Additional Resources")

                col_res1, col_res2 = st.columns(2)

                with col_res1:
                    st.write("**📋 Event Details Summary:**")
                    summary_text = f"""
**Event:** {event_name}
**Date:** {datetime_str}
**Venue:** {venue}
**Description:** {event_description[:100]}...
                    """
                    st.code(summary_text)

                with col_res2:
                    st.write("**💡 Tips for Better Engagement:**")
                    tips = [
                        "Post at optimal times for each platform",
                        "Use platform-specific hashtags",
                        "Engage with comments promptly",
                        "Share behind-the-scenes content",
                        "Create countdown posts leading to the event"
                    ]
                    for tip in tips:
                        st.write(f"• {tip}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit | Support for OpenAI (with DALL-E), Anthropic, and Google AI</p>
        <p>🎨 Image generation available with OpenAI • 📱 Optimized for LinkedIn, Twitter & WhatsApp</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")