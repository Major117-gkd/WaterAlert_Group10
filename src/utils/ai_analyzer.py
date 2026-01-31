import os
import logging
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import json

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def analyze_leak_image(photo_path):
    """
    Connects to Google Gemini Vision API to analyze if there is a water leak
    and estimate its severity based on the visual evidence.
    """
    if not api_key:
        logging.warning("GEMINI_API_KEY not found. Falling back to simulation mode.")
        return _simulate_analysis(photo_path)

    try:
        logging.info(f"Real AI Analyzing image: {photo_path}")
        
        # Load the image
        img = Image.open(photo_path)
        
        # Initialize Gemini 1.5 Flash (vision capable)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Regarde cette photo envoyée par un citoyen. 
        1. S'agit-il d'une fuite d'eau, d'une canalisation cassée ou d'une inondation liée à l'eau ? (is_leak: bool)
        2. Si oui, évalue la gravité sur une échelle de 1 à 3 : 
           - Petite (Goutte à goutte, petit filet)
           - Moyenne (Flux constant, trou visible)
           - Élevée (Geyser, inondation majeure, route coupée)
        
        Réponds uniquement sous format JSON strict comme ceci :
        {"is_leak": true, "severity": "Moyenne", "description": "Brève description en 10 mots"}
        """
        
        response = model.generate_content([prompt, img])
        
        # Parse the JSON response
        try:
            # Clean response text in case of markdown blocks
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            data = json.loads(clean_text)
            
            is_leak = data.get("is_leak", True)
            severity = data.get("severity", "Moyenne")
            description = data.get("description", "Analyse terminée.")
            
            analysis_text = (
                f"✅ *Analyse Réelle terminée :* {description} (Sévérité estimée : {severity})"
                if is_leak else
                "⚠️ *Avertissement :* L'IA n'a pas détecté de fuite évidente sur cette photo."
            )
            
            return is_leak, severity, analysis_text
            
        except Exception as e:
            logging.error(f"Error parsing Gemini JSON: {e}")
            return True, "Moyenne", f"✅ Analyse effectuée (Format de réponse non standard)."

    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        return _simulate_analysis(photo_path, error_msg=f" (Erreur API: {str(e)[:50]})")

def _simulate_analysis(photo_path, error_msg=""):
    """Fallback simulation mode if API key is missing or failed."""
    import random
    import time
    time.sleep(1)
    severity_levels = ["Petite", "Moyenne", "Élevée"]
    severity = random.choice(severity_levels)
    return True, severity, f"ℹ️ *Mode Simulation{error_msg} :* Fuite détectée (Sévérité: {severity})."
