from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from .db import (
    init_db,
    add_ticket, get_tickets, close_ticket,
    user_exists, create_user, get_user
)

# ✅ NY: import for e-postvarsling (endring 1)
from .email_service import send_ticket_created_email, notify_support_new_ticket

bp = Blueprint("main", __name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def current_user():
    return session.get("user")

def current_role():
    return session.get("role")

@bp.before_app_request
def ensure_db():
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

@bp.route("/")
def home():
    if not current_user():
        return redirect(url_for("main.login"))
    return redirect(url_for("main.kb"))

@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                error = "Brukernavn og passord er påkrevd."
            else:
                u = get_user(username)
                if u and check_password_hash(u["pw_hash"], password):
                    session["user"] = u["username"]
                    session["role"] = u["role"]
                    logger.info(f"User logged in: {username}")
                    return redirect(url_for("main.kb"))
                error = "Feil brukernavn eller passord."
        except Exception as e:
            logger.error(f"Login error: {e}")
            error = "En feil oppstod. Prøv igjen senere."
    
    return render_template("login.html", error=error)

@bp.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            password2 = request.form.get("password2", "")

            if len(username) < 3:
                error = "Brukernavn må være minst 3 tegn."
            elif len(password) < 8:
                error = "Passord må være minst 8 tegn."
            elif password != password2:
                error = "Passordene er ikke like."
            elif user_exists(username):
                error = "Brukernavnet er allerede i bruk."
            else:
                pw_hash = generate_password_hash(password, method="pbkdf2:sha256")
                create_user(username=username, pw_hash=pw_hash, role="user")
                logger.info(f"New user registered: {username}")
                flash("Bruker opprettet. Du kan logge inn nå.")
                return redirect(url_for("main.login"))
        except Exception as e:
            logger.error(f"Registration error: {e}")
            error = "En feil oppstod ved registrering. Prøv igjen."

    return render_template("register.html", error=error)

@bp.route("/logout")
def logout():
    user = current_user()
    if user:
        logger.info(f"User logged out: {user}")
    session.clear()
    return redirect(url_for("main.login"))

@bp.route("/kb")
def kb():
    if not current_user():
        return redirect(url_for("main.login"))
    return render_template("kb.html")

@bp.route("/tickets", methods=["GET", "POST"])
def tickets():
    user = current_user()
    if not user:
        return redirect(url_for("main.login"))

    role = current_role()

    if request.method == "POST":
        try:
            title = request.form.get("title", "").strip()
            desc = request.form.get("desc", "").strip()
            category = request.form.get("category", "Annet").strip()
            priority = request.form.get("priority", "Middels").strip()
            device = request.form.get("device", "").strip()

            if not title or not desc:
                flash("Du må fylle ut tittel og beskrivelse.")
            else:
                ticket_id = add_ticket(owner=user, title=title, desc=desc,
                           category=category, priority=priority, device=device)
                logger.info(f"Ticket created: #{ticket_id} by {user}")

                # ✅ NY: bygg ticket-dict + send e-post (endring 2)
                ticket = {
                    "id": ticket_id,
                    "title": title,
                    "owner": session.get("user"),
                    "category": category,
                    "priority": priority,
                    "description": desc,
                }
                send_ticket_created_email(ticket, user_email=None)
                notify_support_new_ticket(ticket)

                flash("Saken er sendt til support. Du finner den i oversikten under.")
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            flash("En feil oppstod ved opprettelse av sak. Prøv igjen.")

        return redirect(url_for("main.tickets"))

    try:
        visible = get_tickets() if role == "support" else get_tickets(owner=user)
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        visible = []
        flash("Kunne ikke hente saker. Prøv igjen senere.")
    
    return render_template("_tickets.html", tickets=visible, role=role)

@bp.route("/tickets/<int:ticket_id>/close", methods=["POST"])
def close_ticket_view(ticket_id):
    user = current_user()
    role = current_role()

    if not user:
        return redirect(url_for("main.login"))
    
    if role != "support":
        flash("Du har ikke tilgang til å lukke saker.")
        return redirect(url_for("main.tickets"))

    try:
        close_ticket(ticket_id)
        logger.info(f"Ticket #{ticket_id} closed by {user}")
        flash(f"Sak #{ticket_id} er lukket.")
    except Exception as e:
        logger.error(f"Error closing ticket {ticket_id}: {e}")
        flash("Kunne ikke lukke saken. Prøv igjen.")
    
    return redirect(url_for("main.tickets"))


# -------------------------------------------------------------------
# Enhanced Chatbot (Advanced AI-powered helpdesk)
# -------------------------------------------------------------------

class HelpdeskBot:
    """Advanced helpdesk chatbot with context awareness and learning"""
    
    def __init__(self):
        self.knowledge_base = self._init_knowledge_base()
        self.troubleshooting_trees = self._init_troubleshooting_trees()
        
    def _init_knowledge_base(self) -> Dict:
        """Comprehensive knowledge base with solutions"""
        return {
            "feide": {
                "keywords": ["feide", "innlogging", "login", "logge inn", "pålogging", "autentisering"],
                "common_errors": {
                    "feil brukernavn": "Kontroller at du bruker riktig format: fornavn.etternavn@skole.no",
                    "timeout": "Feide-tjenesten kan være overbelastet. Prøv igjen om noen minutter.",
                    "ugyldig organisasjon": "Sjekk at du har valgt riktig institusjon i nedtrekksmenyen.",
                    "session expired": "Økten har utløpt. Lukk nettleseren helt og start på nytt."
                },
                "advanced_steps": [
                    "Kontroller at klokken på enheten er synkronisert (viktig for autentisering)",
                    "Sjekk om du har VPN aktivert som kan blokkere Feide",
                    "Test med mobil data hvis du er på Wi-Fi (isolerer nettverksproblemer)",
                    "Sjekk status.feide.no for kjente driftsproblemer"
                ]
            },
            "wifi": {
                "keywords": ["wifi", "wi-fi", "nett", "internett", "nettverk", "tilkobling", "trådløst"],
                "common_errors": {
                    "ingen internett": "Tilkoblet nettverk, men ingen internett-tilgang",
                    "begrensad tilkobling": "Nettverket er tilkoblet men fungerer ikke ordentlig",
                    "kan ikke koble til": "Enheten finner ikke eller kan ikke koble til nettverket"
                },
                "advanced_steps": [
                    "Kjør nettverksdiagnose: Windows (ipconfig /release && ipconfig /renew)",
                    "Sjekk DNS-innstillinger - prøv 8.8.8.8 (Google DNS) midlertidig",
                    "Kontroller om MAC-filtrering blokkerer enheten",
                    "Test signalstyrke - flytt nærmere aksesspunkt hvis svakt signal"
                ]
            },
            "utskrift": {
                "keywords": ["utskrift", "skriver", "printer", "print", "skrive ut"],
                "common_errors": {
                    "skriver ikke funnet": "Skriveren vises ikke i listen over tilgjengelige skrivere",
                    "utskriftskø": "Dokumenter blir stående i køen uten å skrives ut",
                    "driverproblemer": "Skriverkonfigurasjon eller driver fungerer ikke"
                },
                "advanced_steps": [
                    "Reinstaller skriverdriver - last ned nyeste versjon fra produsentens nettside",
                    "Sjekk om skriverspooler-tjenesten kjører (services.msc på Windows)",
                    "Test direkte IP-tilkobling til skriver hvis nettverksskriver",
                    "Kontroller skriverinnstillinger for papirstørrelse og orientering"
                ]
            },
            "passord": {
                "keywords": ["passord", "glemt", "låst", "reset", "tilbakestill", "password"],
                "common_errors": {
                    "konto låst": "Kontoen er låst etter for mange feilede forsøk",
                    "passord utløpt": "Passordet må byttes regelmessig",
                    "passord ikke godkjent": "Det nye passordet oppfyller ikke sikkerhetskrav"
                },
                "advanced_steps": [
                    "Vent 30 minutter hvis kontoen er låst (automatisk opplåsing)",
                    "Bruk selvbetjeningsportal for passordbytte hvis tilgjengelig",
                    "Husk passordkrav: min. 12 tegn, store/små bokstaver, tall og spesialtegn",
                    "Vurder passordbehandler for sikker lagring av komplekse passord"
                ]
            },
            "m365": {
                "keywords": ["teams", "office", "word", "excel", "onedrive", "m365", "365", "outlook", "powerpoint"],
                "common_errors": {
                    "synkronisering": "Filer synkroniseres ikke mellom enheter",
                    "tilgang nektet": "Du har ikke tilgang til filen eller mappen",
                    "kan ikke logge inn": "Innlogging til Microsoft 365 feiler"
                },
                "advanced_steps": [
                    "Tilbakestill OneDrive-synkronisering: Høyreklikk OneDrive > Innstillinger > Koble fra",
                    "Sjekk lisensstatus i Microsoft 365 Admin Portal",
                    "Tøm Teams cache: %appdata%\\Microsoft\\Teams og slett mappen",
                    "Bruk Office Repair Tool for å reparere installasjonen"
                ]
            },
            "nettleser": {
                "keywords": ["chrome", "edge", "safari", "firefox", "nettleser", "browser", "cache", "cookies"],
                "common_errors": {
                    "siden laster ikke": "Nettsiden vil ikke laste eller vises feil",
                    "treg ytelse": "Nettleseren er veldig treg",
                    "krasjer": "Nettleseren krasjer eller fryser"
                },
                "advanced_steps": [
                    "Tøm cache grundig: Ctrl+Shift+Del > Velg 'All tid' > Slett alt",
                    "Deaktiver hardware-akselerasjon hvis grafikk-problemer",
                    "Opprett ny nettleserprofil for å utelukke korrupt profil",
                    "Kjør nettleseren i feilsøkingsmodus (safe mode) for testing"
                ]
            }
        }
    
    def _init_troubleshooting_trees(self) -> Dict:
        """Decision trees for systematic troubleshooting"""
        return {
            "feide": {
                "question": "Får du en feilmelding når du prøver å logge inn?",
                "yes": {
                    "question": "Er feilmeldingen relatert til brukernavn/passord?",
                    "yes": "feide_credentials",
                    "no": "feide_technical"
                },
                "no": {
                    "question": "Skjer det ingenting når du trykker 'Logg inn'?",
                    "yes": "feide_browser",
                    "no": "feide_general"
                }
            },
            "wifi": {
                "question": "Kan du se nettverket i listen over tilgjengelige nettverk?",
                "yes": {
                    "question": "Får du koblet til, men ingen internett?",
                    "yes": "wifi_connected_no_internet",
                    "no": "wifi_connection_failed"
                },
                "no": "wifi_not_visible"
            }
        }
    
    def _detect_topic(self, text: str) -> str:
        """Advanced topic detection with confidence scoring"""
        text_lower = text.lower()
        scores = {}
        
        for topic, data in self.knowledge_base.items():
            score = sum(1 for keyword in data["keywords"] if keyword in text_lower)
            if score > 0:
                scores[topic] = score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return "ukjent"
    
    def _extract_context(self, text: str) -> Dict:
        """Enhanced context extraction with pattern matching"""
        ctx = {
            "os": None,
            "browser": None,
            "error": None,
            "device": None,
            "app": None,
            "urgency": "normal"
        }
        
        text_lower = text.lower()
        
        # OS detection
        os_patterns = {
            "Windows": ["windows", "win10", "win11", "pc"],
            "macOS": ["mac", "macos", "osx", "macbook", "imac"],
            "iOS": ["iphone", "ipad", "ios"],
            "Android": ["android", "samsung", "pixel"],
            "Linux": ["linux", "ubuntu", "debian"]
        }
        for os_name, keywords in os_patterns.items():
            if any(k in text_lower for k in keywords):
                ctx["os"] = os_name
                break
        
        # Browser detection
        browser_patterns = {
            "Chrome": ["chrome"],
            "Edge": ["edge"],
            "Safari": ["safari"],
            "Firefox": ["firefox"],
            "Brave": ["brave"],
            "Opera": ["opera"]
        }
        for browser_name, keywords in browser_patterns.items():
            if any(k in text_lower for k in keywords):
                ctx["browser"] = browser_name
                break
        
        # Error message extraction (multiple formats)
        error_patterns = [
            r'"([^"]+)"',  # Text in quotes
            r'feilmelding[:\s]+([^\n\.]+)',  # After "feilmelding:"
            r'error[:\s]+([^\n\.]+)',  # After "error:"
        ]
        for pattern in error_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ctx["error"] = match.group(1).strip()
                break
        
        # Urgency detection
        urgent_keywords = ["haster", "akutt", "kritisk", "nå", "umiddelbart", "viktig møte", "eksamen"]
        if any(k in text_lower for k in urgent_keywords):
            ctx["urgency"] = "high"
        
        # App detection
        app_patterns = {
            "Teams": ["teams", "team"],
            "Outlook": ["outlook", "epost", "e-post", "mail"],
            "Word": ["word"],
            "Excel": ["excel"],
            "OneDrive": ["onedrive"],
            "PowerPoint": ["powerpoint", "ppt"]
        }
        for app_name, keywords in app_patterns.items():
            if any(k in text_lower for k in keywords):
                ctx["app"] = app_name
                break
        
        return ctx
    
    def _find_similar_error(self, error_msg: str, topic: str) -> Optional[str]:
        """Find similar known errors using fuzzy matching"""
        if not error_msg or topic not in self.knowledge_base:
            return None
        
        error_lower = error_msg.lower()
        common_errors = self.knowledge_base[topic].get("common_errors", {})
        
        for known_error, solution in common_errors.items():
            if known_error in error_lower or error_lower in known_error:
                return solution
        
        return None
    
    def _get_progressive_steps(self, topic: str, level: int, ctx: Dict) -> str:
        """Generate progressive troubleshooting steps based on level"""
        if topic not in self.knowledge_base:
            return ""
        
        steps = []
        
        # Level 1: Basic steps
        if level >= 1:
            steps.append("🔍 **Nivå 1 - Grunnleggende sjekk:**")
            if topic == "feide":
                steps.append("1. Kontroller brukernavn og passord (obs Caps Lock)")
                steps.append("2. Velg riktig institusjon i Feide-innlogging")
                steps.append("3. Prøv inkognito-/privat vindu")
                steps.append("4. Tøm nettleserens cache og cookies")
            elif topic == "wifi":
                steps.append("1. Slå Wi-Fi av og på igjen på enheten")
                steps.append("2. Kontroller at du kobler til riktig nettverk")
                steps.append("3. Start enheten på nytt")
                steps.append("4. Flytt nærmere ruter/aksesspunkt")
            elif topic == "utskrift":
                steps.append("1. Sjekk at riktig skriver er valgt")
                steps.append("2. Kontroller papir og toner/blekk")
                steps.append("3. Start skriver og PC på nytt")
                steps.append("4. Sjekk at skriveren er online (ikke i feilmodus)")
            elif topic == "passord":
                steps.append("1. Bruk 'Glemt passord'-funksjonen hvis tilgjengelig")
                steps.append("2. Sjekk Caps Lock og tastaturspråk")
                steps.append("3. Vent 5-10 minutter etter passordbytte (synkronisering)")
                steps.append("4. Prøv å logge inn på en annen enhet")
            elif topic == "m365":
                steps.append("1. Logg helt ut og inn igjen")
                steps.append("2. Sjekk internettforbindelsen")
                steps.append("3. Prøv web-versjonen i nettleser")
                steps.append("4. Start programmet/appen på nytt")
            elif topic == "nettleser":
                steps.append("1. Oppdater siden (Ctrl/Cmd + R)")
                steps.append("2. Prøv inkognito-/privat vindu")
                steps.append("3. Tøm cache og cookies")
                steps.append("4. Test i en annen nettleser")
        
        # Level 2: Intermediate steps
        if level >= 2:
            steps.append("\n🔧 **Nivå 2 - Avansert feilsøking:**")
            advanced = self.knowledge_base[topic].get("advanced_steps", [])
            for i, step in enumerate(advanced[:3], 1):
                steps.append(f"{i}. {step}")
        
        # Level 3: Expert steps
        if level >= 3:
            steps.append("\n⚙️ **Nivå 3 - Ekspert-nivå:**")
            advanced = self.knowledge_base[topic].get("advanced_steps", [])
            for i, step in enumerate(advanced[3:], 1):
                steps.append(f"{i}. {step}")
            steps.append(f"{len(advanced[3:])+1}. Opprett support-sak med detaljert beskrivelse")
        
        return "\n".join(steps)
    
    def _generate_contextual_response(self, topic: str, ctx: Dict, conversation_state: Dict) -> str:
        """Generate intelligent, context-aware response"""
        response_parts = []
        
        # Urgency acknowledgment
        if ctx.get("urgency") == "high":
            response_parts.append("⚡ **Jeg ser dette haster!** La oss løse det raskt.\n")
        
        # Error-specific solution
        if ctx.get("error"):
            similar_solution = self._find_similar_error(ctx["error"], topic)
            if similar_solution:
                response_parts.append(f"💡 **Kjent feilmelding identifisert:**\n{similar_solution}\n")
        
        # Context acknowledgment
        context_info = []
        if ctx.get("os"):
            context_info.append(f"OS: {ctx['os']}")
        if ctx.get("browser"):
            context_info.append(f"Nettleser: {ctx['browser']}")
        if ctx.get("app"):
            context_info.append(f"App: {ctx['app']}")
        
        if context_info:
            response_parts.append(f"📋 **Registrert informasjon:** {', '.join(context_info)}\n")
        
        # Progressive troubleshooting
        level = conversation_state.get("troubleshooting_level", 1)
        steps = self._get_progressive_steps(topic, level, ctx)
        response_parts.append(steps)
        
        # Missing information prompt
        missing = self._identify_missing_info(topic, ctx)
        if missing and level == 1:
            response_parts.append(f"\n❓ **For bedre hjelp, kan du oppgi:**\n{missing}")
        
        # Next steps suggestion
        if level < 3:
            response_parts.append(f"\n💬 Hvis dette ikke løser problemet, skriv 'fortsatt problem' så går vi videre til nivå {level + 1}.")
        else:
            response_parts.append("\n📝 Hvis problemet fortsetter, anbefaler jeg at du oppretter en support-sak så vi kan hjelpe deg direkte.")
        
        return "\n".join(response_parts)
    
    def _identify_missing_info(self, topic: str, ctx: Dict) -> str:
        """Identify what information is missing for better troubleshooting"""
        missing = []
        
        if topic in ["feide", "nettleser", "m365"] and not ctx.get("browser"):
            missing.append("• Hvilken nettleser bruker du?")
        
        if not ctx.get("os"):
            missing.append("• Hvilken enhet/operativsystem (Windows/Mac/iOS/Android)?")
        
        if topic in ["feide", "m365", "nettleser"] and not ctx.get("error"):
            missing.append("• Får du en feilmelding? (skriv den gjerne i anførselstegn)")
        
        return "\n".join(missing) if missing else ""
    
    def process_message(self, user_msg: str, conversation_state: Dict) -> Tuple[str, Dict]:
        """Main processing function with state management"""
        # Detect if user is reporting continued problems
        if any(phrase in user_msg.lower() for phrase in ["fortsatt problem", "fungerer ikke", "virker ikke", "hjelper ikke"]):
            conversation_state["troubleshooting_level"] = conversation_state.get("troubleshooting_level", 1) + 1
            if conversation_state["troubleshooting_level"] > 3:
                conversation_state["troubleshooting_level"] = 3
        
        # Detect topic
        topic = self._detect_topic(user_msg)
        
        # Use previous topic if current detection fails but we have conversation context
        if topic == "ukjent" and conversation_state.get("current_topic"):
            topic = conversation_state["current_topic"]
        else:
            conversation_state["current_topic"] = topic
            if topic != "ukjent":
                conversation_state["troubleshooting_level"] = 1
        
        # Extract context
        ctx = self._extract_context(user_msg)
        
        # Merge with previous context
        previous_ctx = conversation_state.get("context", {})
        for key, value in ctx.items():
            if value:
                previous_ctx[key] = value
        conversation_state["context"] = previous_ctx
        
        # Generate response
        if topic == "ukjent":
            response = self._handle_unknown_topic(user_msg)
        else:
            response = self._generate_contextual_response(topic, previous_ctx, conversation_state)
        
        return response, conversation_state
    
    def _handle_unknown_topic(self, user_msg: str) -> str:
        """Handle messages where topic cannot be determined"""
        return (
            "🤔 Jeg er ikke helt sikker på hva du trenger hjelp med.\n\n"
            "Jeg kan hjelpe deg med:\n"
            "• 🔐 Feide-innlogging og autentisering\n"
            "• 📡 Wi-Fi og nettverksproblemer\n"
            "• 🖨️ Utskriftsproblemer\n"
            "• 🔑 Passord-problemer\n"
            "• 📧 Microsoft 365 (Teams, Outlook, OneDrive, Office)\n"
            "• 🌐 Nettleser-problemer\n\n"
            "Beskriv gjerne problemet ditt mer detaljert, så hjelper jeg deg!"
        )


# Initialize bot instance
_bot_instance = None

def get_bot() -> HelpdeskBot:
    """Get or create bot instance"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = HelpdeskBot()
    return _bot_instance


@bp.route("/chat", methods=["POST"])
def chat():
    """Enhanced chat endpoint with stateful conversation"""
    if not current_user():
        return jsonify({"reply": "Du må være innlogget for å bruke chat."}), 401

    try:
        data = request.get_json(silent=True) or {}
        user_msg = (data.get("message") or "").strip()

        if not user_msg:
            return jsonify({"reply": "Skriv hva du trenger hjelp med."})

        # Get conversation state
        conversation_state = session.get("conversation_state", {})
        
        # Process message
        bot = get_bot()
        reply, updated_state = bot.process_message(user_msg, conversation_state)
        
        # Update session
        session["conversation_state"] = updated_state
        
        # Update history
        history = session.get("chat_history", [])
        history.append({
            "role": "user",
            "content": user_msg,
            "timestamp": datetime.now().isoformat()
        })
        history.append({
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.now().isoformat(),
            "topic": updated_state.get("current_topic"),
            "level": updated_state.get("troubleshooting_level", 1)
        })
        
        # Keep only last 20 messages
        session["chat_history"] = history[-20:]
        
        return jsonify({
            "reply": reply,
            "topic": updated_state.get("current_topic"),
            "level": updated_state.get("troubleshooting_level", 1)
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"reply": "En feil oppstod. Prøv igjen senere."}), 500


@bp.route("/chat/reset", methods=["POST"])
def reset_chat():
    """Reset chat conversation state"""
    if not current_user():
        return jsonify({"status": "error"}), 401
    
    session.pop("conversation_state", None)
    session.pop("chat_history", None)
    session.pop("chat_topic", None)
    
    return jsonify({"status": "ok", "message": "Samtalen er tilbakestilt."})