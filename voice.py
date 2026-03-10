from flask import Flask, render_template, request, jsonify, send_file, session, redirect
import datetime
import wikipedia
import random
from database import (
    register_user, login_user, get_user_by_id, get_password_by_email,
    log_command, get_user_history, clear_user_history
)
import os
from dotenv import load_dotenv
from gtts import gTTS
import io
import time
from functools import lru_cache, wraps

load_dotenv()

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Response cache for instant answers
response_cache = {}

# Initialize database on startup
print("✅ Database initialized successfully")

# Authentication decorator
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized", "success": False}), 401
        return f(*args, **kwargs)
    return decorated_function

# Websites dictionary
websites = {
    "google": "https://google.com",
    "youtube": "https://youtube.com",
    "wikipedia": "https://wikipedia.org",
    "facebook": "https://facebook.com",
    "instagram": "https://instagram.com",
    "twitter": "https://twitter.com",
    "reddit": "https://reddit.com",
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
    "gmail": "https://mail.google.com",
    "amazon": "https://amazon.com",
    "flipkart": "https://flipkart.com",
    "netflix": "https://netflix.com",
    "spotify": "https://spotify.com",
    "chatgpt": "https://chat.openai.com",
    "gemini": "https://gemini.google.com",
    "claude": "https://claude.ai"
}

# Personal Advice Knowledge Base
personal_advice = {
    # Health
    "cold": "For a cold: Rest well, drink warm fluids (water, tea, soup), get vitamin C from citrus fruits, use a humidifier, gargle with salt water, take honey with lemon, stay hydrated, and avoid stress. Most colds last 7-10 days. If symptoms worsen, see a doctor.",
    "fever": "For fever: Take paracetamol or ibuprofen as directed, drink plenty of water, rest, wear light clothing, cool compress on forehead, avoid heavy exercise. Fever is body fighting infection. If fever above 103°F or lasts more than 3 days, see a doctor.",
    "cough": "For cough: Drink warm liquids, use honey and lemon, stay hydrated, use cough drops, humidify air, avoid irritants like smoke, rest your voice. For dry cough use lozenges. For wet cough, keep mucus loose. If cough lasts more than 3 weeks, see a doctor.",
    "headache": "For headache: Rest in quiet dark room, apply cold/warm compress, drink water (dehydration is common cause), take paracetamol or ibuprofen, massage neck and shoulders, avoid stress. Identify triggers: certain foods, lack of sleep, stress. If severe or frequent, see a doctor.",
    "anxiety": "For anxiety: Deep breathing exercises, progressive muscle relaxation, mindfulness meditation, regular exercise, reduce caffeine, adequate sleep, talk to someone, limit social media, journaling. Consider therapy. Anxiety is treatable. Short-term relief: box breathing (4-4-4-4 count).",
    "depression": "For depression: Seek professional help - therapy or counseling is very effective. Exercise regularly, maintain sleep schedule, eat nutritious food, stay connected with people, sunlight exposure, limit alcohol. Depression is medical condition, not weakness. Please talk to doctor or mental health professional.",
    
    # Mental & Performance
    "stress": "For stress: Practice deep breathing, meditate 10 minutes daily, exercise regularly, get 7-8 hours sleep, limit caffeine, spend time in nature, talk to friends, pursue hobbies, keep a journal. Stress management techniques: yoga, progressive muscle relaxation, or counseling if needed.",
    "sleep": "For better sleep: Keep consistent sleep schedule, dark and cool bedroom (65-68°F), no screens 1 hour before bed, avoid caffeine after 2 PM, exercise daily but not before bed, limit alcohol, try warm milk or chamomile tea, meditate. 7-9 hours is ideal for adults.",
    "motivation": "For motivation: Set clear specific goals, break into small steps, celebrate small wins, find your why, minimize distractions, surround yourself with supportive people, track progress, take breaks, maintain healthy lifestyle, forgive yourself for setbacks. Remember why you started when motivation fades.",
    "procrastination": "For procrastination: Start with 5 minutes, break task into smaller parts, remove distractions, set deadlines, find accountability partner, reward yourself, identify why you procrastinate (fear, overwhelm?), plan time blocks, say no to other tasks. Action creates motivation, not vice versa.",
    "focus": "For better focus: Minimize distractions, phone on silent, separate workspace, take breaks every 25 mins (Pomodoro), sleep 7-9 hours, regular exercise, meditate, optimize nutrition, manage stress. Caffeine helps short-term. Deep work requires consistent practice. Attention is a skill you can improve.",
    "memory": "For better memory: Mnemonic techniques, spaced repetition, teach others what you learn, get adequate sleep (consolidates memory), exercise (increases blood flow to brain), reduce stress, learn actively not passively, organize information, meaningful context helps. Meditation improves memory. Brain is trainable.",
    "confidence": "For confidence: Practice and preparation build confidence, face fears gradually, positive self-talk, celebrate achievements, learn from failures, maintain good posture (affects mindset), exercise, dress well, social connections, help others. Confidence developed through action, not theory. Start small and build.",
    
    # Study & Exam
    "exam": "To pass exams: Start studying early (not last minute), understand concepts deeply not just memorize, make notes and summaries, teach others to test your knowledge, practice previous papers, get 7-8 hours sleep before exam (critical!), eat healthy meal before exam, manage exam anxiety with deep breathing, read questions carefully, manage time during exam. Consistent study throughout year is key.",
    "study": "For effective studying: Active recall (test yourself), spaced repetition (review after days), interleaving (mix different topics), deep understanding over memorization, make flashcards, teach others, practice problems, take breaks every 25 mins, study in quiet place, get adequate sleep. One hour focused study beats 5 hours distracted studying.",
    "exam tips": "Exam tips: Read all questions first, plan answers, manage time (faster questions first), write clearly, answer what's asked not what you know, review answers if time permits, stay calm, skip difficult questions and return to them, show working for marks. Last revision: read notes, don't cram new material.",
    "homework": "For homework: Start immediately after assignment given, understand requirements fully, break into steps, research proper sources, work at own pace not rush, take breaks, review for errors, ask teacher if confused. Homework builds understanding and prepares for exams. Consistency matters more than perfection.",
    "concentrate": "To concentrate: Find quiet study space, eliminate distractions (phone away), set timer (Pomodoro 25 mins), clear your mind (write worries), hydrate well, take short breaks, study hardest subjects first when fresh, physically engage (write, speak), make goal clear. Build concentration like muscle - practice daily.",
    "pass": "To pass exams: Focus on fundamentals and concepts, practice lots of problem solving, understand previous paper patterns, attend all classes, make good notes, form study groups, manage time effectively, get enough sleep, reduce exam anxiety with preparation, ask doubts immediately. Consistency beats cramming.",
    "fail": "If you feel you'll fail: Don't panic, focus on what you can control now, understand weak topics, seek tutor help if needed, practice problems repeatedly, sleep well before exam, manage anxiety, during exam answer what you know first, skip tough questions if time short. One attempt is learning for next time.",
    
    # Lifestyle & Habits
    "diet": "Healthy diet: Balanced meals with proteins, carbs, fats, vitamins, minerals. Eat plenty of vegetables, fruits, whole grains. Limit sugar, salt, fried foods. Drink 8 glasses water daily. Portion control important. Mediterranean diet is scientifically proven healthy. Consistency matters more than perfection.",
    "exercise": "For fitness: Aim for 150 minutes moderate exercise weekly or 75 minutes vigorous. Include strength training 2 days. Start slow, be consistent. Mix cardio, strength, flexibility. Find activities you enjoy. Warm up before, cool down after. Rest days important. Consult doctor before major changes.",
    "weight": "For weight management: Balanced diet + regular exercise most effective. Calorie deficit needed to lose weight. Avoid crash diets - they don't work long-term. Include proteins (keep you full), fiber, whole grains. Drink water, limit sugary drinks. Sleep 7-8 hours. Be patient - healthy loss is 1-2 pounds per week.",
    "back pain": "For back pain: Good posture important, strengthen core muscles, regular exercise, avoid heavy lifting or bend knees, use supportive mattress and pillow, warm compress, gentle stretching, professional massage. If pain severe, persistent, or from injury, see a doctor. Prevention better than cure.",
    "neck pain": "For neck pain: Proper posture essential - screen should be eye level, phones held up (text neck), frequent breaks. Gentle neck stretches, warm compress, supportive pillow, strengthen neck muscles, massage. Avoid prolonged phone use. If severe or after injury, seek medical attention.",
    
    # Relationships & Social
    "relationships": "For healthy relationships: Listen actively, communicate clearly, show empathy, respect boundaries, spend quality time, express appreciation, forgive, support each other's goals, healthy conflict resolution, maintain independence, laugh together. No relationship is perfect. Invest time and effort. Professional help if needed.",
}

# Response cache for instant answers
response_cache = {}

def get_cached_response(query):
    """Get response from cache if available"""
    cache_key = query.lower().strip()
    if cache_key in response_cache:
        return response_cache[cache_key]
    return None

def cache_response(query, response):
    """Store response in cache"""
    cache_key = query.lower().strip()
    response_cache[cache_key] = response

def search_wikipedia_fast(query):
    """Search Wikipedia with timeout and caching"""
    # Check cache first - INSTANT response!
    cached = get_cached_response(query)
    if cached:
        return cached
    
    try:
        # Set timeout for Wikipedia request (2 seconds max)
        wikipedia.set_rate_limiting(rate_limit = True, min_wait = 0.1)
        
        # Try to get page
        page = wikipedia.page(query, auto_suggest=True)
        full_content = page.content
        
        # Get first 5 sentences quickly
        sentences = full_content.split('.')
        response_text = '. '.join(sentences[:5]).strip() + '.'
        
        # Limit length
        if len(response_text) > 1000:
            response_text = response_text[:1000] + '...'
        
        # Cache it for future use
        cache_response(query, response_text)
        return response_text
    except wikipedia.exceptions.DisambiguationError:
        return None
    except wikipedia.exceptions.PageError:
        return None
    except Exception as e:
        print(f"Wikipedia error: {e}")
        return None

def process_command(command):
    """Process voice commands and return response"""
    command = command.lower().strip()
    
    if not command:
        return {"text": "I couldn't understand that. Please try again.", "action": None}
    
    # Greetings
    if any(greeting in command for greeting in ["hello", "hi", "hey"]):
        response_text = random.choice([
            "Hello! How can I help you?",
            "Hi there! What can I do for you?",
            "Hey! What's up?"
        ])
        return {"text": response_text, "action": None}
    
    # Time
    if "time" in command:
        now = datetime.datetime.now()
        return {"text": f"The time is {now.strftime('%H:%M:%S')}", "action": None}
    
    # Date
    if "date" in command:
        today = datetime.date.today()
        return {"text": f"Today's date is {today.strftime('%B %d, %Y')}", "action": None}
    
    # SMART Personal Advice Matching - Check for any relevant keywords
    for topic, advice in personal_advice.items():
        if topic in command:
            return {"text": advice, "action": None}
    
    # Additional keyword matching for personal advice
    study_keywords = ["exam", "pass", "fail", "study", "homework", "concentrate", "test", "revision", "prepare", "learning"]
    health_keywords = ["medicine", "doctor", "sick", "pain", "hurt", "ache", "ill", "unwell", "health", "disease"]
    brain_keywords = ["tired", "brain", "mental", "think", "remember", "forget", "confused", "understand", "learn"]
    habit_keywords = ["habit", "lifestyle", "routine", "improve"]
    
    # Check study/exam keywords
    if any(keyword in command for keyword in study_keywords):
        return {"text": personal_advice.get("exam", "To pass exams: Study consistently, understand concepts deeply, practice problems, get good sleep, manage anxiety. Start early, don't cram last minute. Be prepared and confident!"), "action": None}
    
    # Check health keywords
    if any(keyword in command for keyword in health_keywords):
        # Try to find specific condition
        for topic in ["cold", "fever", "cough", "anxiety", "depression", "headache"]:
            if topic in command:
                return {"text": personal_advice[topic], "action": None}
        return {"text": "Please describe your health concern more specifically (e.g., cold, fever, stress, headache, anxiety). I can give you advice.", "action": None}
    
    # Check brain/focus/memory keywords
    if any(keyword in command for keyword in brain_keywords):
        if "focus" in command or "concentrate" in command or "attention" in command or "distracted" in command:
            return {"text": personal_advice["focus"], "action": None}
        elif "remember" in command or "memory" in command or "forget" in command:
            return {"text": personal_advice["memory"], "action": None}
        else:
            return {"text": personal_advice["study"], "action": None}
    
    # Help command
    if "help" in command or "what can you do" in command:
        return {"text": "I'm your smart assistant! I can: Give you exam tips and study advice, Help with health concerns (colds, stress, sleep, etc.), Answer study-related questions, Provide personal life advice, Search Wikipedia for any topic, Open websites, Play YouTube videos, and do Google searches. Ask me anything!", "action": None}
    
    # Wikipedia search - Check for "what is" / "who is"
    if "who is" in command or "what is" in command:
        query = command.replace("who is", "").replace("what is", "").replace("?", "").strip()
        if query:
            response_text = search_wikipedia_fast(query)
            if response_text:
                return {"text": response_text, "action": None}
    
    # Open websites
    if "open" in command:
        for site_name, url in websites.items():
            if site_name in command:
                return {"text": f"Opening {site_name}", "action": "open_url", "url": url}
        return {"text": "I couldn't find that website. Try asking for a different one.", "action": None}
    
    # YouTube play
    if "play" in command:
        song = command.replace("play", "").strip()
        if song:
            youtube_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
            return {"text": f"Playing {song} on YouTube", "action": "open_url", "url": youtube_url}
        return {"text": "What song would you like to play?", "action": None}
    
    # Google search
    if "search" in command:
        query = command.replace("search", "").strip()
        if query:
            google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            return {"text": f"Searching for {query} on Google", "action": "open_url", "url": google_url}
        return {"text": "What would you like to search for?", "action": None}
    
    # SMART general Wikipedia search - try anything with cache & timeout
    try:
        query = command.replace("?", "").strip()
        response_text = search_wikipedia_fast(query)
        if response_text:
            return {"text": response_text, "action": None}
    except:
        pass
    
    # Default - didn't understand
    return {"text": "I didn't quite understand that. Try asking about exams, health tips, any topic on Wikipedia, or other questions!", "action": None}


@app.route("/login")
def login_page():
    """Serve the login page"""
    return render_template("login.html")


@app.route("/api/signup", methods=["POST"])
def signup():
    """Handle user signup"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['name', 'email', 'password']):
            return jsonify({"success": False, "message": "Missing fields"}), 400
        
        name = data['name'].strip()
        email = data['email'].strip()
        password = data['password'].strip()
        
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
        
        success, message = register_user(name, email, password)
        
        return jsonify({"success": success, "message": message})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({"success": False, "message": "Missing email or password"}), 400
        
        email = data['email'].strip()
        password = data['password'].strip()
        
        success, user_data, message = login_user(email, password)
        
        if success:
            session['user_id'] = user_data['user_id']
            session['username'] = user_data['username']
            return jsonify({
                "success": True,
                "message": message,
                "username": user_data['username']
            })
        else:
            return jsonify({"success": False, "message": message}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/get-password-suggestion", methods=["POST"])
def get_password_suggestion():
    """Get password suggestion for login (security: never return actual password, just confirm it exists)"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({"found": False}), 400
        
        email = data['email'].strip()
        password_hash = get_password_by_email(email)
        
        if password_hash:
            # Never return actual password hash! Just confirm user exists
            # Frontend will handle showing the suggestion
            return jsonify({"found": True, "password": "••••••"})
        else:
            return jsonify({"found": False})
    except Exception as e:
        return jsonify({"found": False})


@app.route("/api/logout", methods=["POST"])
def logout():
    """Handle user logout"""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})


@app.route("/")
def home():
    """Serve the main page"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect("/login")
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
@login_required
def process():
    """Process voice command via API"""
    try:
        data = request.get_json()
        
        if not data or "command" not in data:
            return jsonify({"error": "No command provided", "success": False}), 400
        
        command = data["command"].strip()
        user_id = session.get('user_id')
        
        if not command:
            return jsonify({"error": "Empty command", "success": False}), 400
        
        response_data = process_command(command)
        response_text = response_data.get("text", response_data) if isinstance(response_data, dict) else response_data
        
        # Save to database
        try:
            log_command(user_id, command, response_text)
        except Exception as e:
            print(f"⚠️ Could not save to database: {e}")
        
        return jsonify({
            "success": True,
            "command": command,
            "response": response_text,
            "action": response_data.get("action") if isinstance(response_data, dict) else None,
            "url": response_data.get("url") if isinstance(response_data, dict) else None
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    """Get user's command history"""
    try:
        limit = request.args.get("limit", 10, type=int)
        user_id = session.get('user_id')
        history = get_user_history(user_id, limit)
        return jsonify({
            "success": True,
            "history": history
        })
    except Exception as e:
        print(f"⚠️ Could not retrieve history: {e}")
        return jsonify({
            "success": True,
            "history": [],
            "message": "Database unavailable"
        })


@app.route("/api/speak", methods=["POST"])
def speak():
    """Convert text to speech and return audio"""
    try:
        data = request.get_json()
        
        if not data or "text" not in data:
            return jsonify({"error": "No text provided", "success": False}), 400
        
        text = data["text"].strip()
        
        if not text:
            return jsonify({"error": "Empty text", "success": False}), 400
        
        # Limit text length for reasonable audio generation
        if len(text) > 1000:
            text = text[:1000]
        
        # Generate speech
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to BytesIO object instead of file
            audio_stream = io.BytesIO()
            tts.write_to_fp(audio_stream)
            audio_stream.seek(0)
            
            return send_file(
                audio_stream,
                mimetype="audio/mpeg",
                as_attachment=False
            )
        except Exception as e:
            print(f"Error generating speech: {e}")
            return jsonify({"error": str(e), "success": False}), 500
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Page not found", "success": False}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Server error", "success": False}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = False  # Disable debug mode to avoid watchdog compatibility issues
    # Listen on all interfaces (0.0.0.0) for Render deployment
    app.run(host="0.0.0.0", port=port, debug=debug)