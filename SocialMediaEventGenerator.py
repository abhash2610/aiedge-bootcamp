import streamlit as st
import openai
import anthropic
import google.generativeai as genai
from typing import Dict, Any
import json


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


def create_prompt(event_name: str, event_description: str, tone: str, platform: str) -> str:
    """Create platform-specific prompts"""

    platform_specs = {
        "LinkedIn": {
            "limit": "700 characters",
            "style": "professional networking post with hashtags",
            "features": "Include relevant hashtags and professional language"
        },
        "Twitter": {
            "limit": "280 characters",
            "style": "concise and engaging tweet",
            "features": "Include relevant hashtags and mentions if appropriate"
        },
        "WhatsApp": {
            "limit": "500 characters",
            "style": "casual and personal message",
            "features": "Use emojis and friendly tone"
        }
    }

    spec = platform_specs[platform]

    prompt = f"""
    Create a {platform} post about the following event:

    Event Name: {event_name}
    Event Description: {event_description}
    Tone: {tone}

    Requirements:
    - Maximum {spec['limit']}
    - Style: {spec['style']}
    - {spec['features']}
    - Tone should be {tone}

    Generate only the post content, no additional explanation.
    """

    return prompt


def main():
    st.title("📱 Social Media Post Generator")
    st.markdown("Generate engaging posts for LinkedIn, Twitter, and WhatsApp using AI")

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # AI Provider selection
        ai_providers = {
            "OpenAI (GPT)": "openai",
            "Anthropic (Claude)": "claude",
            "Google (Gemini)": "gemini"
        }

        selected_provider = st.selectbox(
            "Select AI Provider:",
            options=list(ai_providers.keys()),
            help="Choose your preferred AI provider"
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
            height=150,
            placeholder="Describe your event in detail..."
        )

        generate_button = st.button(
            "🚀 Generate Posts",
            type="primary",
            use_container_width=True
        )

    with col2:
        st.header("📱 Generated Posts")

        if generate_button:
            if not event_name or not event_description:
                st.error("Please fill in both event name and description.")
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

                # Generate posts for each platform
                platforms = ["LinkedIn", "Twitter", "WhatsApp"]

                with st.spinner("Generating posts..."):
                    for platform in platforms:
                        with st.expander(f"📊 {platform} Post", expanded=True):
                            prompt = create_prompt(
                                event_name,
                                event_description,
                                selected_tone.lower(),
                                platform
                            )

                            # Generate content
                            content = generate_func(api_key, prompt)

                            # Display the generated post
                            st.write("**Generated Post:**")
                            st.info(content)

                            # Character count
                            char_count = len(content)

                            # Platform-specific limits
                            limits = {"LinkedIn": 700, "Twitter": 280, "WhatsApp": 500}
                            limit = limits[platform]

                            if char_count <= limit:
                                st.success(f"✅ Character count: {char_count}/{limit}")
                            else:
                                st.warning(f"⚠️ Character count: {char_count}/{limit} (exceeds limit)")

                            # Copy button simulation
                            if st.button(f"📋 Copy {platform} Post", key=f"copy_{platform}"):
                                st.success(f"{platform} post copied to clipboard!")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit | Support for OpenAI, Anthropic, and Google AI</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()