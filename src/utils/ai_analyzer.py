import random
import time
import logging

def analyze_leak_image(photo_path):
    """
    Simulates an AI analysis of the uploaded photo.
    In a real scenario, this would call Google Gemini Vision or OpenAI GPT-4o.
    """
    logging.info(f"AI Analyzing image: {photo_path}")
    
    # Simulate processing time
    time.sleep(1.5)
    
    # Mock analysis logic
    severity_levels = ["Faible", "Moyenne", "Critique"]
    detected_leaks = [True, True, True, False] # High probability of leak in this app
    
    is_leak = random.choice(detected_leaks)
    severity = random.choice(severity_levels) if is_leak else "N/A"
    
    analysis_text = (
        f"✅ Fuite détectée avec succès. Sévérité estimée : {severity}."
        if is_leak else
        "⚠️ Attention : L'IA n'a pas détecté de fuite évidente sur cette photo."
    )
    
    return is_leak, severity, analysis_text
