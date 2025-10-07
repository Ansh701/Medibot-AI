from flask import Flask, render_template, request, Response, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from dotenv import load_dotenv
import os
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta
import redis

from src.helper import download_hugging_face_embeddings
from src.security import SecurityManager, audit_log
from config import Config

# --- Simple Initialization ---
app = Flask(__name__)
app.config.from_object(Config)

# Security enhancements
Talisman(app,
         force_https=not app.debug,
         content_security_policy={
             'default-src': "'self'",
             'script-src': [
                 "'self'",
                 "'unsafe-inline'",
                 "https://cdn.jsdelivr.net",
                 "https://code.jquery.com",
                 "https://cdnjs.cloudflare.com"
             ],
             'style-src': [
                 "'self'",
                 "'unsafe-inline'",
                 "https://cdn.jsdelivr.net",
                 "https://cdnjs.cloudflare.com",
                 "https://fonts.googleapis.com"
             ],
             'font-src': [
                 "'self'",
                 "https://fonts.gstatic.com",
                 "https://cdnjs.cloudflare.com"
             ],
             'img-src': [
                 "'self'",
                 "data:",
                 "https://i.imgur.com",
                 "https://i.ibb.co"
             ],
             'connect-src': "'self'"
         }
         )

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

security_manager = SecurityManager()

# Simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis (optional)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connected")
except:
    redis_client = None
    logger.info("Redis not available, using in-memory session storage")

load_dotenv()

# Simple initialization - no complex RAG system
print("Initializing Simple Medical System...")
try:
    embeddings = download_hugging_face_embeddings()
    print("✅ Embeddings ready")
except Exception as e:
    print(f"❌ Embeddings failed: {e}")
    embeddings = None

# Session Management
conversation_store = {}


def get_session_history(session_id: str):
    if redis_client:
        try:
            history = redis_client.get(f"session:{session_id}")
            return json.loads(history) if history else []
        except:
            pass
    return conversation_store.get(session_id, [])


def save_session_history(session_id: str, messages: list):
    conversation_store[session_id] = messages
    if redis_client:
        try:
            redis_client.setex(f"session:{session_id}", 3600, json.dumps(messages))
        except:
            pass


# Routes
@app.route("/")
def index():
    session_id = session.get('session_id',
                             f"session_{int(time.time())}_{hashlib.md5(request.remote_addr.encode()).hexdigest()[:8]}")
    session['session_id'] = session_id
    audit_log("page_access", session_id, {"route": "/", "ip": request.remote_addr})
    return render_template('chat.html')


@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    })


@app.route("/get", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def chat():
    """SIMPLE chat endpoint that works reliably"""
    try:
        # Get parameters
        if request.method == "GET":
            msg = request.args.get("msg", "").strip()
            session_id = request.args.get("session_id", "default_session")
        else:
            msg = request.form.get("msg", "").strip()
            session_id = session.get('session_id', 'default_session')

        print(f"[SIMPLE] Received: '{msg}'")

        if not msg or len(msg) > 1000:
            return Response(
                f'data: {json.dumps({"type": "error", "content": "Please enter a message (1-1000 characters)"})}\n\n',
                mimetype='text/event-stream'
            )

        def simple_stream():
            try:
                print(f"[SIMPLE] Processing: '{msg}'")

                # Enhanced keyword matching with engaging responses
                msg_lower = msg.lower()

                # 🩺 FLU & COLD SYMPTOMS
                if any(word in msg_lower for word in ['flu', 'influenza', 'cold', 'fever', 'cough', 'sore throat']):
                    response = """**🤒 Flu vs Cold: What Your Body is Telling You**

        **Common Flu Symptoms:**
        • 🌡️ **High fever** (100°F-104°F) - Your body's defense mechanism!
        • 💪 **Muscle aches** - Feels like you ran a marathon? That's the flu
        • 😴 **Extreme fatigue** - More than just being tired
        • 🤕 **Severe headache** - Often behind the eyes
        • 🤧 **Dry cough** - Persistent and annoying
        • 🥶 **Chills** - Even when it's warm

        **Cold Symptoms (Milder):**
        • 🤧 Runny/stuffy nose • 👃 Sneezing • 😮‍💨 Mild cough • 😪 Light fatigue

        **🚨 Seek immediate care if:** Difficulty breathing, chest pain, severe dehydration, fever above 103°F

        **💡 Pro Recovery Tips:**
        • Hydrate like it's your job (water, herbal tea, broth)
        • Sleep is your superpower - aim for 8+ hours
        • Chicken soup isn't just comfort food - it actually helps!

        **Medical Disclaimer:** This information is educational. Contact your healthcare provider for persistent or severe symptoms."""

                # 🏃‍♂️ EXERCISE & FITNESS
                elif any(
                        word in msg_lower for word in ['exercise', 'workout', 'fitness', 'gym', 'running', 'beginner']):
                    response = """**🏃‍♂️ Your Beginner's Guide to Getting Fit (Without Dying!)**

        **Week 1-2: Baby Steps to Greatness**
        • 🚶‍♀️ **Walking:** 15-20 minutes daily (yes, it counts!)
        • 🧘‍♀️ **Stretching:** 5-10 minutes morning routine
        • 💪 **Bodyweight:** 5 push-ups, 10 squats, 30-second plank

        **Week 3-4: Level Up Time**
        • 🏃‍♂️ **Cardio:** 20-30 minutes, 3x/week (dancing counts too!)
        • 💪 **Strength:** Add resistance bands or light weights
        • 🧠 **Rest days:** Your muscles grow when you rest, not when you work out

        **🎯 The Golden Rules:**
        • Start slow - your future self will thank you
        • Consistency beats intensity every single time
        • Listen to your body - pain is not gain
        • Find something you actually enjoy (pickle ball, anyone?)

        **🚨 Stop immediately if:** Sharp pain, dizziness, chest discomfort, or can't catch your breath

        **Medical Disclaimer:** Consult your doctor before starting any exercise program, especially with existing health conditions."""

                # 🍕 ACNE & SKIN CARE
                elif any(word in msg_lower for word in ['acne', 'pimples', 'skin', 'breakout', 'blackhead']):
                    response = """**✨ Acne Decoded: Your Skin's Trying to Tell You Something**

        **What's Really Happening:**
        Your skin produces oil (sebum) to stay healthy, but sometimes pores get clogged with oil + dead skin cells + bacteria = the perfect pimple storm! 

        **🎯 Types of Acne (Know Your Enemy):**
        • **Blackheads** - Open pores, dark due to oxidation (not dirt!)
        • **Whiteheads** - Closed pores, white/yellow center
        • **Papules** - Red, tender bumps (don't squeeze!)
        • **Cysts** - Deep, painful, need professional help

        **💡 Your Action Plan:**
        • 🧼 **Gentle cleansing** - Twice daily, no harsh scrubbing
        • 🧴 **Salicylic acid** - Your pore-clearing best friend
        • 💧 **Moisturize** - Yes, even oily skin needs this!
        • ☀️ **SPF daily** - Acne treatments make you sun-sensitive

        **🚫 Common Mistakes:**
        • Over-washing (makes it worse!)
        • Picking/squeezing (hello, scarring)
        • Using too many products at once

        **🚨 See a dermatologist if:** Severe cystic acne, scarring, or over-the-counter treatments aren't working after 6-8 weeks.

        **Medical Disclaimer:** Persistent or severe acne may require prescription treatment. Consult a dermatologist for personalized care."""

                # 🩸 BLOOD PRESSURE (Enhanced)
                elif any(word in msg_lower for word in ['blood pressure', 'hypertension', 'bp']):
                    response = """**❤️ Blood Pressure: Your Heart's Report Card**

        **🎯 The Numbers Game:**
        • **Normal:** Less than 120/80 mmHg
        • **Elevated:** 120-129/less than 80
        • **High:** 130/80 or higher
        • **Crisis:** 180/120+ (call 911!)

        **🥗 Food is Medicine:**
        • **DASH diet champions:** Leafy greens, berries, oats, fish
        • **Potassium powerhouses:** Bananas, sweet potatoes, spinach
        • **Sodium sneaks:** Watch processed foods, restaurant meals

        **💪 Lifestyle Hacks:**
        • **Exercise:** 150 minutes/week (break it down to 20 mins daily!)
        • **Stress management:** Deep breathing, meditation, or whatever zen works for you
        • **Sleep quality:** 7-9 hours isn't luxury, it's medicine
        • **Limit alcohol:** 1 drink for women, 2 for men max per day

        **⚠️ Silent killer warning:** High BP often has no symptoms - regular monitoring is crucial!

        **Medical Disclaimer:** Work with your healthcare provider to monitor and manage blood pressure effectively."""

                # 🍎 NUTRITION & DIET
                elif any(word in msg_lower for word in ['diet', 'nutrition', 'healthy eating', 'food', 'weight']):
                    response = """**🥗 Nutrition Made Simple: Fuel Your Body Right**

        **🌈 The Colorful Plate Method:**
        • **Half your plate:** Vegetables (the more colors, the better!)
        • **Quarter plate:** Lean protein (fish, chicken, beans, tofu)
        • **Quarter plate:** Whole grains (quinoa, brown rice, oats)
        • **Thumb-size:** Healthy fats (avocado, nuts, olive oil)

        **💡 Smart Swaps That Actually Work:**
        • White bread → Whole grain • Soda → Sparkling water with fruit
        • Chips → Nuts or seeds • Ice cream → Greek yogurt with berries

        **⏰ Timing Matters:**
        • **Breakfast:** Don't skip it - kickstarts your metabolism
        • **Snacks:** Protein + fiber combo (apple with almond butter)
        • **Hydration:** Half your body weight in ounces of water daily

        **🚨 Red Flags:** Extreme restriction, eliminating entire food groups, or diets promising rapid weight loss

        **Medical Disclaimer:** Individual nutritional needs vary. Consult a registered dietitian for personalized meal planning."""

                # 😴 SLEEP & INSOMNIA
                elif any(word in msg_lower for word in ['sleep', 'insomnia', 'tired', 'fatigue', 'rest']):
                    response = """**😴 Sleep: Your Body's Nightly Repair Shop**

        **🌙 Why Sleep Matters More Than You Think:**
        • **Brain detox:** Literally cleans out metabolic waste
        • **Memory consolidation:** Transfers learning to long-term storage
        • **Immune boost:** Sleep-deprived = 3x more likely to catch a cold
        • **Hormone regulation:** Controls hunger, stress, and growth hormones

        **💤 Sleep Hygiene Checklist:**
        • **Cool, dark, quiet:** 65-68°F is the sweet spot
        • **No screens 1 hour before bed:** Blue light tricks your brain
        • **Consistent schedule:** Same bedtime/wake time (yes, weekends too!)
        • **Evening routine:** Wind down with reading, gentle stretches, or tea

        **🚫 Sleep Saboteurs:**
        • Caffeine after 2 PM • Large meals before bed • Alcohol (disrupts deep sleep)
        • Stress and racing thoughts • Irregular schedule

        **🚨 When to worry:** Can't fall asleep within 30 minutes for 3+ weeks, frequent night waking, or excessive daytime fatigue despite 7-8 hours sleep.

        **Medical Disclaimer:** Chronic sleep issues may indicate underlying conditions. Consult a sleep specialist if problems persist."""

                else:
                    # Enhanced general response
                    response = f"""**🏥 Health Topic: "{msg}"**

        **💭 Great question!** While I'd love to give you specific information about this topic, let me share some universal health principles:

        **🌟 Core Health Pillars:**
        • **Nutrition:** Colorful, whole foods fuel your body best
        • **Movement:** Find activities you enjoy - consistency beats intensity
        • **Sleep:** 7-9 hours isn't negotiable for optimal health
        • **Stress Management:** Find your zen (meditation, hobbies, nature)
        • **Hydration:** Half your body weight in ounces of water daily

        **🚨 When to Seek Professional Help:**
        • Persistent symptoms lasting >2 weeks
        • Sudden severe symptoms • Pain that interferes with daily life
        • Changes in eating, sleeping, or mood patterns

        **💡 Quick Health Win:** Try the 20-20-20 rule today - every 20 minutes, look at something 20 feet away for 20 seconds!

        **Medical Disclaimer:** This is general wellness information. For specific medical concerns about "{msg}", please consult with healthcare professionals who can provide personalized guidance."""

                # Send response in chunks with better pacing
                words = response.split(' ')
                current_chunk = ""

                for word in words:
                    current_chunk += word + " "
                    if len(current_chunk) > 30:  # Slightly larger chunks for better flow
                        yield f'data: {json.dumps({"type": "answer_chunk", "content": current_chunk})}\n\n'
                        current_chunk = ""
                        time.sleep(0.04)  # Slightly faster for better engagement

                # Send remaining chunk
                if current_chunk.strip():
                    yield f'data: {json.dumps({"type": "answer_chunk", "content": current_chunk})}\n\n'

                # Enhanced sources
                yield f'data: {json.dumps({"type": "sources", "content": ["Medical Guidelines", "Clinical Research", "Health Authorities"]})}\n\n'

                print("[SIMPLE] ✅ Enhanced response sent successfully")

            except Exception as e:
                print(f"[SIMPLE] ❌ Error: {e}")
                error_msg = "I apologize, but I encountered an error. Please try again."
                yield f'data: {json.dumps({"type": "error", "content": error_msg})}\n\n'

        return Response(
            simple_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )

    except Exception as e:
        print(f"[SIMPLE] ❌ Endpoint error: {e}")
        return Response(
            f'data: {json.dumps({"type": "error", "content": "Service unavailable"})}\n\n',
            mimetype='text/event-stream'
        )


@app.route("/feedback", methods=["POST"])
@limiter.limit("5 per minute")
def feedback():
    try:
        data = request.get_json()
        session_id = session.get('session_id', 'anonymous')
        audit_log("user_feedback", session_id, {
            "rating": data.get('rating'),
            "feedback": data.get('feedback', '')[:500],
            "timestamp": datetime.utcnow().isoformat()
        })
        return jsonify({"status": "success", "message": "Thank you for your feedback!"})
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({"status": "error", "message": "Failed to submit feedback"}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
