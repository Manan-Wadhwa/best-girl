import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import random
import plotly.express as px
import plotly.graph_objects as go

# Configure the page
st.set_page_config(
    page_title="🎭 Ideal Match Predictor", 
    page_icon="💕", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #e91e63;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .scenario-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
    }
    .option-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    .result-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .character-match {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .answer-history {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'assessment_started' not in st.session_state:
        st.session_state.assessment_started = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = None
    if 'scenario_history' not in st.session_state:
        st.session_state.scenario_history = []
    if 'assessment_complete' not in st.session_state:
        st.session_state.assessment_complete = False
    if 'answer_history' not in st.session_state:
        st.session_state.answer_history = []

def reset_assessment():
    """Reset all session state variables to restart the assessment"""
    keys_to_reset = ['assessment_started', 'current_question', 'user_preferences', 
                     'scenario_history', 'assessment_complete', 'answer_history']
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    initialize_session_state()

# Load data
@st.cache_data
def load_data():
    DATA_PATH = "./data.csv"
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        st.error(f"❌ Error: {DATA_PATH} not found. Make sure 'data.csv' is in the same directory.")
        df = pd.DataFrame({'name': ['Dummy'], 'summary': ['Dummy summary'], 'Trait1': [50], 'Trait2': [50]})
    
    trait_cols = df.select_dtypes(include=np.number).columns.tolist()
    
    # Normalize traits
    scaler = MinMaxScaler()
    traits_norm = pd.DataFrame(scaler.fit_transform(df[trait_cols]) - 0.5, columns=trait_cols, index=df.index)
    
    return df, traits_norm, trait_cols

# Load scenario data
@st.cache_data
def get_scenarios():
    """Get fun and engaging PG-13 scenarios covering all personality aspects"""
    return [
        # Adventure & Comedy scenarios
        {
            "scenario_question": "🎮 Your crush challenges you to a video game tournament. Your partner:",
            "option_a": "Accepts immediately and starts trash-talking playfully",
            "option_b": "Studies your gaming habits for weeks before accepting",
            "vector_a": {"Combat Prowess": 1.8, "Impulsiveness": 2.2, "Self-Esteem": 1.7},
            "vector_b": {"Intellect": 2.1, "Discipline": 1.8, "Cynicism": 1.2}
        },
        # Social & Dating scenarios  
        {
            "scenario_question": "💕 On your first date at a fancy restaurant, your partner:",
            "option_a": "Orders the most expensive thing and winks at you",
            "option_b": "Nervously asks what you're ordering first",
            "vector_a": {"Social Acuity": 2.3, "Self-Esteem": 2.0, "Assertiveness": 1.6},
            "vector_b": {"Empathy": 1.9, "Emotional Stability": -0.8, "Nurturance": 1.4}
        },
        # Funny Situation scenarios
        {
            "scenario_question": " You both get caught in the rain without umbrellas. Your partner:",
            "option_a": "Starts dancing in the rain like it's a music video",
            "option_b": "Calculates the exact angle to minimize wetness",
            "vector_a": {"Optimism": 2.4, "Impulsiveness": 1.9, "Social Acuity": 1.5},
            "vector_b": {"Intellect": 2.2, "Discipline": 1.6, "Emotional Stability": 1.3}
        },
        # Creative & Romantic scenarios
        {
            "scenario_question": "🎨 For your anniversary, your partner decides to:",
            "option_a": "Write you a dramatic love song and perform it publicly",
            "option_b": "Create a detailed scrapbook of all your memories together",
            "vector_a": {"Empathy": 2.1, "Impulsiveness": 1.7, "Self-Esteem": 1.8},
            "vector_b": {"Nurturance": 2.3, "Discipline": 1.9, "Perseverance": 1.5}
        },
        # Competition & Fun scenarios
        {
            "scenario_question": "🏃‍♀️ During a friendly race in the park, your partner:",
            "option_a": "Sprints ahead yelling 'Can't catch me!' like a kid",
            "option_b": "Maintains perfect form and pacing like an athlete",
            "vector_a": {"Optimism": 2.0, "Impulsiveness": 2.1, "Social Acuity": 1.4},
            "vector_b": {"Discipline": 2.2, "Ambition": 1.7, "Perseverance": 1.6}
        },
        # Food & Lifestyle scenarios
        {
            "scenario_question": "🍕 At 2 AM, you're both craving pizza. Your partner:",
            "option_a": "Already has three delivery apps open and credit card ready",
            "option_b": "Suggests making homemade pizza because it's healthier",
            "vector_a": {"Impulsiveness": 2.3, "Optimism": 1.8, "Adaptability": 1.5},
            "vector_b": {"Discipline": 2.0, "Intellect": 1.6, "Nurturance": 1.4}
        },
        # Mystery & Adventure scenarios
        {
            "scenario_question": "🕵️ You find a mysterious locked box in the attic. Your partner:",
            "option_a": "Immediately starts picking the lock with a hairpin",
            "option_b": "Researches the box's history before touching it",
            "vector_a": {"Ambition": 2.1, "Impulsiveness": 2.4, "Combat Prowess": 1.3},
            "vector_b": {"Intellect": 2.3, "Discipline": 1.8, "Emotional Stability": 1.2}
        },
        # Emotional & Sweet scenarios
        {
            "scenario_question": "😢 You're having a terrible day and feel like crying. Your partner:",
            "option_a": "Brings ice cream and bad movies for a cuddle session",
            "option_b": "Gives you space but leaves encouraging notes everywhere",
            "vector_a": {"Empathy": 2.4, "Nurturance": 2.2, "Social Acuity": 1.6},
            "vector_b": {"Independence": 1.8, "Nurturance": 2.0, "Discipline": 1.5}
        },
        # Leadership & Social scenarios
        {
            "scenario_question": "🎉 Planning a surprise party for a friend, your partner:",
            "option_a": "Takes charge and assigns everyone specific tasks",
            "option_b": "Quietly handles all the details behind the scenes",
            "vector_a": {"Assertiveness": 2.3, "Social Acuity": 2.0, "Ambition": 1.7},
            "vector_b": {"Nurturance": 2.2, "Discipline": 1.9, "Altruism": 1.8}
        },
        # Drama & Conflict scenarios
        {
            "scenario_question": "💢 Your friend starts spreading rumors about you. Your partner:",
            "option_a": "Confronts them directly at lunch in front of everyone",
            "option_b": "Quietly gathers evidence and plans the perfect comeback",
            "vector_a": {"Assertiveness": 2.4, "Impulsiveness": 2.0, "Loyalty": 1.9},
            "vector_b": {"Intellect": 2.1, "Cynicism": 1.8, "Discipline": 1.7}
        },
        # Romance & Flirting scenarios
        {
            "scenario_question": "😏 When you compliment their new haircut, your partner:",
            "option_a": "Blushes adorably and does a little hair flip",
            "option_b": "Smirks confidently and says 'I know, right?'",
            "vector_a": {"Empathy": 1.6, "Self-Esteem": -0.5, "Nurturance": 1.3},
            "vector_b": {"Self-Esteem": 2.2, "Assertiveness": 1.8, "Social Acuity": 1.5}
        },
        # Adventure & Spontaneity scenarios
        {
            "scenario_question": "🎢 At an amusement park, your partner wants to:",
            "option_a": "Ride the scariest roller coaster five times in a row",
            "option_b": "Win you the biggest stuffed animal from the ring toss",
            "vector_a": {"Combat Prowess": 2.0, "Impulsiveness": 2.2, "Resilience": 1.8},
            "vector_b": {"Nurturance": 2.1, "Perseverance": 2.0, "Ambition": 1.4}
        },
        # Technology & Modern Life scenarios
        {
            "scenario_question": "📱 Your phone dies during a date. Your partner:",
            "option_a": "Says 'Perfect! Now we can actually talk to each other'",
            "option_b": "Immediately offers their portable charger",
            "vector_a": {"Independence": 2.0, "Social Acuity": 1.8, "Optimism": 1.6},
            "vector_b": {"Nurturance": 2.3, "Empathy": 1.9, "Discipline": 1.4}
        },
        # Shopping & Lifestyle scenarios  
        {
            "scenario_question": " During a shopping trip, your partner:",
            "option_a": "Tries on ridiculous outfits to make you laugh",
            "option_b": "Carefully compares prices and reads all the reviews",
            "vector_a": {"Optimism": 2.2, "Social Acuity": 1.9, "Impulsiveness": 1.6},
            "vector_b": {"Intellect": 2.1, "Discipline": 2.0, "Emotional Stability": 1.5}
        },
        # Study & School scenarios
        {
            "scenario_question": "📚 Before a big exam, your partner:",
            "option_a": "Stays up all night cramming with energy drinks",
            "option_b": "Has been studying consistently for weeks with a schedule",
            "vector_a": {"Impulsiveness": 2.3, "Resilience": 1.8, "Ambition": 1.6},
            "vector_b": {"Discipline": 2.4, "Intellect": 2.0, "Perseverance": 2.1}
        },
        # Family & Friends scenarios
        {
            "scenario_question": "👨‍👩‍👧‍👦 Meeting your parents for the first time, your partner:",
            "option_a": "Brings homemade cookies and compliments everything",
            "option_b": "Researches your family's interests and asks thoughtful questions",
            "vector_a": {"Nurturance": 2.2, "Social Acuity": 2.0, "Empathy": 1.8},
            "vector_b": {"Intellect": 2.1, "Discipline": 1.9, "Adaptability": 1.7}
        },
        # Pets & Animals scenarios
        {
            "scenario_question": "🐱 A stray kitten follows you both home. Your partner:",
            "option_a": "Already has it named and is googling pet stores",
            "option_b": "Wants to find its owner or a proper shelter first",
            "vector_a": {"Impulsiveness": 2.4, "Nurturance": 2.3, "Optimism": 1.9},
            "vector_b": {"Discipline": 2.0, "Altruism": 2.1, "Intellect": 1.6}
        },
        # Weather & Seasons scenarios
        {
            "scenario_question": "❄️ On the first snow day, your partner:",
            "option_a": "Immediately starts a snowball fight",
            "option_b": "Makes hot chocolate and suggests staying cozy inside",
            "vector_a": {"Optimism": 2.3, "Impulsiveness": 2.1, "Combat Prowess": 1.5},
            "vector_b": {"Nurturance": 2.2, "Emotional Stability": 1.8, "Empathy": 1.6}
        },
        # Dreams & Goals scenarios
        {
            "scenario_question": "⭐ When you mention your crazy dream career, your partner:",
            "option_a": "Gets super excited and starts planning how to make it happen",
            "option_b": "Listens carefully and asks about backup plans too",
            "vector_a": {"Optimism": 2.4, "Ambition": 2.1, "Impulsiveness": 1.7},
            "vector_b": {"Intellect": 2.0, "Emotional Stability": 1.8, "Discipline": 1.6}
        },
        # Time & Punctuality scenarios
        {
            "scenario_question": "⏰ You're running late for movie night. Your partner:",
            "option_a": "Says 'Fashionably late is the best kind of late!'",
            "option_b": "Has already called ahead to change the showtime",
            "vector_a": {"Adaptability": 2.2, "Optimism": 1.9, "Independence": 1.5},
            "vector_b": {"Discipline": 2.3, "Intellect": 1.8, "Nurturance": 1.7}
        }
        
    ]

def get_character_image(character_name):
    """Get local character image path or fallback to placeholder"""
    from pathlib import Path
    
    images_dir = Path("images")
    safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    
    # Try different extensions
    for ext in ['.jpg', '.png', '.jpeg', '.webp']:
        filename = images_dir / f"{safe_name}{ext}"
        if filename.exists():
            return str(filename)
    
    # Fallback to high-quality placeholder with character info
    fallback_images = {
        "Asuna Yuuki": "https://via.placeholder.com/300x400/FF69B4/FFFFFF?text=Asuna+⚔️",
        "C.C.": "https://via.placeholder.com/300x400/9370DB/FFFFFF?text=C.C.+🔮",
        "Emilia": "https://via.placeholder.com/300x400/87CEEB/FFFFFF?text=Emilia+❄️",
        "Erza Scarlet": "https://via.placeholder.com/300x400/DC143C/FFFFFF?text=Erza+⚔️",
        "Hinata Hyūga": "https://via.placeholder.com/300x400/9370DB/FFFFFF?text=Hinata+👁️",
        "Holo": "https://via.placeholder.com/300x400/DEB887/FFFFFF?text=Holo+🐺",
        "Kurisu Makise": "https://via.placeholder.com/300x400/FF6347/FFFFFF?text=Kurisu+🧪",
        "Mai Sakurajima": "https://via.placeholder.com/300x400/FF1493/FFFFFF?text=Mai+🎭",
        "Maki Zenin": "https://via.placeholder.com/300x400/228B22/FFFFFF?text=Maki+👓",
        "Marin Kitagawa": "https://via.placeholder.com/300x400/FFB6C1/FFFFFF?text=Marin+👗",
        "Mitsuri Kanroji": "https://via.placeholder.com/300x400/FF69B4/FFFFFF?text=Mitsuri+🗾",
        "Nezuko Kamado": "https://via.placeholder.com/300x400/FF69B4/FFFFFF?text=Nezuko+🌸",
        "Nico Robin": "https://via.placeholder.com/300x400/4169E1/FFFFFF?text=Robin+📚",
        "Nobara Kugisaki": "https://via.placeholder.com/300x400/FF4500/FFFFFF?text=Nobara+🔨",
        "Power": "https://via.placeholder.com/300x400/FF6347/FFFFFF?text=Power+🩸",
        "Rem": "https://via.placeholder.com/300x400/87CEEB/FFFFFF?text=Rem+💙",
        "Rias Gremory": "https://via.placeholder.com/300x400/DC143C/FFFFFF?text=Rias+👹",
        "Shinobu Kocho": "https://via.placeholder.com/300x400/9370DB/FFFFFF?text=Shinobu+🦋",
        "Shinobu Oshino": "https://via.placeholder.com/300x400/FFD700/FFFFFF?text=Shinobu+🍩",
        "Tohru": "https://via.placeholder.com/300x400/32CD32/FFFFFF?text=Tohru+🐉",
        "Tsunade": "https://via.placeholder.com/300x400/228B22/FFFFFF?text=Tsunade+🎰",
        "Yor Forger": "https://via.placeholder.com/300x400/DC143C/FFFFFF?text=Yor+🗡️",
        "Yoruichi Shihōin": "https://via.placeholder.com/300x400/9370DB/FFFFFF?text=Yoruichi+⚡",
        "Yukino Yukinoshita": "https://via.placeholder.com/300x400/87CEEB/FFFFFF?text=Yukino+❄️",
        "Zero Two": "https://via.placeholder.com/300x400/FF69B4/FFFFFF?text=Zero+Two+🦄"
    }
    
    return fallback_images.get(character_name, f"https://via.placeholder.com/300x400/808080/FFFFFF?text={character_name.replace(' ', '+')}")

def main():
    initialize_session_state()
    df, traits_norm, trait_cols = load_data()
    scenarios = get_scenarios()
    
    # Header
    st.markdown('<h1 class="main-header">🎭 Ideal Match Predictor</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Discover your perfect anime waifu through personality assessment!</p>', unsafe_allow_html=True)
    
    # Sidebar with controls
    with st.sidebar:
        st.header("🎮 Controls")
        
        if st.button( "Reset Assessment", use_container_width=True):
            reset_assessment()
            st.rerun()
        
        st.header("📊 Progress")
        if st.session_state.assessment_started and not st.session_state.assessment_complete:
            progress = st.session_state.current_question / len(scenarios)
            st.progress(progress)
            st.write(f"Question {st.session_state.current_question + 1} of {len(scenarios)}")
        elif st.session_state.assessment_complete:
            st.success("✅ Assessment Complete!")
        
        st.header("🎯 How it works")
        st.markdown("""
        1. **Answer 20 scenarios** about personality preferences
        2. **See your choices** in real-time
        3. **Get personality profile** based on traits  
        4. **View your matches** with detailed analysis
        5. **Reset anytime** to try again!
        """)
        
        # Show answer history
        if st.session_state.answer_history:
            st.header("📋 Your Answers")
            for i, answer in enumerate(st.session_state.answer_history):
                with st.expander(f"Q{i+1}: {answer['choice'][:30]}...", expanded=False):
                    st.write(f"**Question:** {answer['question']}")
                    st.write(f"**Your Choice:** {answer['choice']}")
    
    # Main content
    if not st.session_state.assessment_started:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="result-card">
                <h2 style="text-align: center;">🌟 Welcome to Your Ideal Match Journey!</h2>
                <p style="text-align: center; font-size: 1.1rem;">
                    Ready to discover your perfect anime character match? 
                    This comprehensive personality assessment will analyze your preferences 
                    across 20 different traits using 20 detailed scenarios to find your ideal waifu!
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Start Assessment", key="start_btn", use_container_width=True):
                st.session_state.assessment_started = True
                st.session_state.user_preferences = pd.Series(0.0, index=trait_cols)
                st.rerun()
    
    elif st.session_state.assessment_complete:
        # Results screen
        st.markdown('<h2 style="text-align: center; color: #e91e63;">🏆 Your Ideal Matches! 🏆</h2>', unsafe_allow_html=True)
        
        # Calculate results
        match_scores = traits_norm.values @ st.session_state.user_preferences.values
        rank_df = pd.DataFrame({
            'name': df['name'],
            'summary': df['summary'],
            'match_score': match_scores
        }).sort_values('match_score', ascending=False).reset_index(drop=True)
        
        # Display top 5 matches
        st.markdown("### 🎯 Your Top 5 Matches")
        
        for i in range(min(5, len(rank_df))):
            row = rank_df.iloc[i]
            # Position-based percentage: 100% for 1st, decreasing by rank
            total_chars = len(rank_df)
            match_percentage = max(20, 100 - (i * (80 / max(total_chars - 1, 1))))
            
            rank_emojis = ["🥇", "🥈", "🥉", "🏅", "🏅"]
            rank_emoji = rank_emojis[min(i, 4)]
            
            # Create character card
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Display character image (local or fallback)
                image_path = get_character_image(row['name'])
                st.image(image_path, width=200)
            
            with col2:
                st.markdown(f"""
                <div class="character-match">
                    <h3>{rank_emoji} #{i+1}: {row['name']}</h3>
                    <h2>💖 Match Score: {match_percentage:.1f}%</h2>
                    <p><strong>About:</strong> {row['summary']}</p>
                    <p><strong>Compatibility Score:</strong> {row['match_score']:+.3f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # Show personality profile
        st.markdown("### 📊 Your Personality Profile")
        significant_prefs = st.session_state.user_preferences[abs(st.session_state.user_preferences) > 0.1]
        
        if len(significant_prefs) > 0:
            # Create radar chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=significant_prefs.values,
                theta=significant_prefs.index,
                fill='toself',
                name='Your Preferences',
                line_color='rgb(233, 30, 99)',
                fillcolor='rgba(233, 30, 99, 0.3)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[-2, 2])
                ),
                showlegend=False,
                title="Your Personality Trait Preferences",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show trait details
            st.markdown("### 🎯 Your Key Personality Traits")
            for trait, score in significant_prefs.abs().nlargest(5).items():
                actual_score = st.session_state.user_preferences[trait]
                direction = "Strong preference" if actual_score > 0 else "Avoids"
                st.write(f"**{trait}**: {direction} (Score: {actual_score:+.2f})")
        
        # Complete rankings
        with st.expander("📋 Complete Rankings (All Characters)", expanded=False):
            for i, row in rank_df.iterrows():
                # Position-based percentage for all characters
                total_chars = len(rank_df)
                match_percentage = max(20, 100 - (i * (80 / max(total_chars - 1, 1))))
                st.write(f"**{i+1:2d}.** {row['name']:<25} | **{match_percentage:5.1f}%** | Score: {row['match_score']:+6.3f}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Take Assessment Again", use_container_width=True):
                reset_assessment()
                st.rerun()
        
        with col2:
            if st.button("📊 View Detailed Analysis", use_container_width=True):
                st.markdown("### 🔍 Detailed Analysis")
                non_zero_prefs = st.session_state.user_preferences[st.session_state.user_preferences != 0]
                st.write(f"• **Active traits**: {len(non_zero_prefs)}/{len(st.session_state.user_preferences)}")
                st.write(f"• **Strongest preference**: {st.session_state.user_preferences.abs().max():.3f}")
                st.write(f"• **Average preference strength**: {st.session_state.user_preferences.abs().mean():.3f}")
                
                st.markdown("**All Your Trait Scores:**")
                trait_df = pd.DataFrame({
                    'Trait': st.session_state.user_preferences.index,
                    'Score': st.session_state.user_preferences.values
                }).sort_values('Score', key=abs, ascending=False)
                
                for _, row in trait_df.iterrows():
                    if abs(row['Score']) > 0.01:
                        st.write(f"• **{row['Trait']}**: {row['Score']:+.3f}")
    
    else:
        # Assessment in progress
        current_scenario = scenarios[st.session_state.current_question]
        
        # Display current question
        st.markdown(f"""
        <div class="scenario-card">
            <h2>Question {st.session_state.current_question + 1} of {len(scenarios)}</h2>
            <h1>{current_scenario['scenario_question']}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Display options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="option-card">
                <h3>Option A</h3>
                <p>{current_scenario['option_a']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="option-card">
                <h3>Option B</h3>
                <p>{current_scenario['option_b']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Choice buttons
        st.markdown("### 🎯 Choose your preference:")
        
        choice_cols = st.columns(5)
        choices = [
            ("🔥 Strongly A", 1.0, "a", f"Strongly prefer: {current_scenario['option_a']}"),
            ("👍 Prefer A", 0.5, "a", f"Prefer: {current_scenario['option_a']}"),
            ("😐 Neutral", 0.0, "neutral", "No strong preference either way"),
            ("👍 Prefer B", 0.5, "b", f"Prefer: {current_scenario['option_b']}"),
            ("🔥 Strongly B", 1.0, "b", f"Strongly prefer: {current_scenario['option_b']}")
        ]
        
        for i, (label, multiplier, choice, description) in enumerate(choices):
            with choice_cols[i]:
                if st.button(label, key=f"choice_{i}", use_container_width=True):
                    # Process choice
                    if multiplier > 0 and choice != "neutral":
                        chosen_vector_key = "vector_a" if choice == "a" else "vector_b"
                        score_vector = current_scenario[chosen_vector_key]
                        
                        for trait, score in score_vector.items():
                            if trait in st.session_state.user_preferences:
                                st.session_state.user_preferences[trait] += score * multiplier
                    
                    # Record answer
                    st.session_state.answer_history.append({
                        'question': current_scenario['scenario_question'],
                        'choice': description,
                        'multiplier': multiplier,
                        'option': choice
                    })
                    
                    # Add to history
                    st.session_state.scenario_history.append(current_scenario['scenario_question'])
                    
                    # Move to next question
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= len(scenarios):
                        st.session_state.assessment_complete = True
                    
                    st.rerun()
        
        # Show previous answers
        if st.session_state.answer_history:
            st.markdown("### 📝 Your Previous Answers")
            for i, answer in enumerate(st.session_state.answer_history[-3:]):  # Show last 3 answers
                st.markdown(f"""
                <div class="answer-history">
                    <strong>Q{len(st.session_state.answer_history)-len(st.session_state.answer_history[-3:])+i+1}:</strong> {answer['question']}<br>
                    <strong>Your choice:</strong> {answer['choice']}
                </div>
                """, unsafe_allow_html=True)
if __name__ == "__main__":
    main()
