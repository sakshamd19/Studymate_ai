"""Multi-language support for StudyMate AI."""
from enum import Enum
from typing import Dict, Any
from functools import lru_cache

class Language(Enum):
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    KANNADA = "kn"

class LanguageManager:
    """Manages translations for all supported languages."""
    
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        "en": {
            # Common UI
            "app_title": "StudyMate AI",
            "app_subtitle": "Tell us about your studies — 6 AI agents will build your personalised plan",
            "your_name": "Your name",
            "privacy_caption": "Your data is processed locally and never stored or shared.",
            "analyze": "Analyze",
            "run_analysis": "Run analysis",
            "loading": "Processing with AI agents...",
            "error": "Error",
            "success": "Success",
            
            # Weakness Analysis
            "weakness_analysis": "Weakness Analysis",
            "overall_average": "Overall Average",
            "weak_subjects": "Weak Subjects",
            "subject_breakdown": "Subject Breakdown",
            "days_left": "days left",
            "critical": "CRITICAL",
            "high": "HIGH",
            "moderate": "MODERATE",
            "good": "GOOD",
            
            # Risk Assessment
            "risk_assessment": "Risk Assessment",
            "overall_risk": "Overall Risk",
            "confidence": "Confidence",
            "verdict": "Verdict",
            "most_at_risk": "Most At Risk",
            "low_risk": "Low Risk",
            "medium_risk": "Medium Risk",
            "high_risk": "High Risk",
            "critical_risk": "Critical Risk",
            
            # Study Plan
            "study_plan": "Study Plan",
            "duration": "Duration",
            "total_hours": "Total Hours",
            "avg_daily_hours": "Avg Daily Hours",
            
            # Career Readiness
            "career_readiness": "Career Readiness",
            "top_career_path": "Top Career Path",
            "salary_range": "Salary Range",
            "free_certs": "Free Certifications",
            "required_skills": "Required Skills",
            "placement_tips": "Placement Tips",
        },
        "hi": {
            # Common UI
            "app_title": "स्टडीमेट एआई",
            "app_subtitle": "अपनी पढ़ाई के बारे में बताएं — 6 AI एजेंट आपकी व्यक्तिगत योजना बनाएंगे",
            "your_name": "आपका नाम",
            "privacy_caption": "आपका डेटा स्थानीय रूप से संसाधित होता है और कभी संग्रहीत नहीं होता।",
            "analyze": "विश्लेषण करें",
            "run_analysis": "विश्लेषण चलाएं",
            "loading": "एआई एजेंट प्रोसेस कर रहे हैं...",
            "error": "त्रुटि",
            "success": "सफल",
            
            # Weakness Analysis
            "weakness_analysis": "कमजोरी विश्लेषण",
            "overall_average": "कुल औसत",
            "weak_subjects": "कमजोर विषय",
            "subject_breakdown": "विषय विवरण",
            "days_left": "दिन बचे",
            "critical": "गंभीर",
            "high": "उच्च",
            "moderate": "मध्यम",
            "good": "अच्छा",
            
            # Risk Assessment
            "risk_assessment": "जोखिम मूल्यांकन",
            "overall_risk": "कुल जोखिम",
            "confidence": "आत्मविश्वास",
            "verdict": "निर्णय",
            "most_at_risk": "सबसे अधिक जोखिम में",
            "low_risk": "कम जोखिम",
            "medium_risk": "मध्यम जोखिम",
            "high_risk": "उच्च जोखिम",
            "critical_risk": "गंभीर जोखिम",
            
            # Study Plan
            "study_plan": "पढ़ाई की योजना",
            "duration": "अवधि",
            "total_hours": "कुल घंटे",
            "avg_daily_hours": "दैनिक औसत घंटे",
            
            # Career Readiness
            "career_readiness": "करियर तैयारी",
            "top_career_path": "शीर्ष करियर पथ",
            "salary_range": "वेतन सीमा",
            "free_certs": "मुफ्त प्रमाणपत्र",
            "required_skills": "आवश्यक कौशल",
            "placement_tips": "प्लेसमेंट सुझाव",
        },
        "ta": {
            # Common UI
            "app_title": "ஸ்டாடிமேட் AI",
            "app_subtitle": "உங்கள் படிப்பைப் பற்றி சொல்லுங்கள் — 6 AI முகவர்கள் தனிப்பயன் திட்டத்தை உருவாக்குவார்கள்",
            "your_name": "உங்கள் பெயர்",
            "privacy_caption": "உங்கள் தரவு உள்ளூரில் செயலாக்கப்படுகிறது; சேமிக்கப்படாது.",
            "analyze": "பகுப்பாய்வு செய்",
            "run_analysis": "பகுப்பாய்வு இயக்கு",
            "loading": "AI ஏஜெண்டுகள் செயல்படுகின்றன...",
            "error": "பிழை",
            "success": "வெற்றி",
            
            # Weakness Analysis
            "weakness_analysis": "பலவீனத்தின் பகுப்பாய்வு",
            "overall_average": "மொத்த சராசரி",
            "weak_subjects": "பலவீனமான பாடங்கள்",
            "subject_breakdown": "பாடங்கள் விரிவு",
            "days_left": "நாட்கள் இருக்கின்றன",
            "critical": "முக்கியமான",
            "high": "அதிக",
            "moderate": "மிதமான",
            "good": "நல்ல",
            
            # Risk Assessment
            "risk_assessment": "ஆபத்து மதிப்பீடு",
            "overall_risk": "மொத்த ஆபத்து",
            "confidence": "நம்பிக்கை",
            "verdict": "தீர்ப்பு",
            "most_at_risk": "மிகவும் ஆபத்தில் உள்ள",
            "low_risk": "குறைந்த ஆபத்து",
            "medium_risk": "மிதமான ஆபத்து",
            "high_risk": "அதிக ஆபத்து",
            "critical_risk": "முக்கிய ஆபத்து",
            
            # Study Plan
            "study_plan": "படிப்பு திட்டம்",
            "duration": "காலம்",
            "total_hours": "மொத்த மணிநேரம்",
            "avg_daily_hours": "சராசரி தினசரி மணிநேரம்",
            
            # Career Readiness
            "career_readiness": "க்யாரியர் தயாரிப்பு",
            "top_career_path": "சிறந்த ொழில் பாதை",
            "salary_range": "சம்பள வரம்பு",
            "free_certs": "இலவச சான்றிதழ்கள்",
            "required_skills": "தேவையான திறன்கள்",
            "placement_tips": "வேலை உதவிக்குறிப்புகள்",
        },
        "kn": {
            # Common UI
            "app_title": "ಸ್ಟಡಿಮೇಟ್ AI",
            "app_subtitle": "ನಿಮ್ಮ ಅಧ್ಯಯನದ ಬಗ್ಗೆ ಹೇಳಿ — 6 AI ಏಜೆಂಟ್‌ಗಳು ವೈಯಕ್ತಿಕ ಯೋಜನೆ ನಿರ್ಮಿಸುತ್ತವೆ",
            "your_name": "ನಿಮ್ಮ ಹೆಸರು",
            "privacy_caption": "ನಿಮ್ಮ ಡೇಟಾ ಸ್ಥಳೀಯವಾಗಿ ಪ್ರಕ್ರಿಯೆಗೊಳ್ಳುತ್ತದೆ; ಶೇಖರಿಸಲಾಗುವುದಿಲ್ಲ.",
            "analyze": "ವಿಶ್ಲೇಷಣೆ ಮಾಡಿ",
            "run_analysis": "ವಿಶ್ಲೇಷಣೆ ಚಲಾಯಿಸಿ",
            "loading": "AI ಏಜೆಂಟ್‌ಗಳು ಪ್ರಕ್ರಿಯೆ ಮಾಡುತ್ತಿವೆ...",
            "error": "ದೋಷ",
            "success": "ಯಶಸ್ಸು",
            
            # Weakness Analysis
            "weakness_analysis": "ದುರ್ಬಲತೆಯ ವಿಶ್ಲೇಷಣೆ",
            "overall_average": "ಒಟ್ಟು ಸರಾಸರಿ",
            "weak_subjects": "ದುರ್ಬಲ ವಿಷಯಗಳು",
            "subject_breakdown": "ವಿಷಯ ವಿವರಣೆ",
            "days_left": "ದಿನಗಳು ಉಳಿದಿವೆ",
            "critical": "ನಿರ್ಣಾಯಕ",
            "high": "ಹೆಚ್ಚು",
            "moderate": "ಮಧ್ಯಮ",
            "good": "ಉತ್ತಮ",
            
            # Risk Assessment
            "risk_assessment": "ಝುಂಬು ಮೌಲ್ಯಮಾಪನ",
            "overall_risk": "ಒಟ್ಟು ಝುಂಬು",
            "confidence": "ಆತ್ಮವಿಶ್ವಾಸ",
            "verdict": "ತೀರ್ಪು",
            "most_at_risk": "ಹೆಚ್ಚು ಝುಂಬುದಲ್ಲಿವೆ",
            "low_risk": "ಕಡಿಮೆ ಝುಂಬು",
            "medium_risk": "ಮಧ್ಯಮ ಝುಂಬು",
            "high_risk": "ಹೆಚ್ಚು ಝುಂಬು",
            "critical_risk": "ನಿರ್ಣಾಯಕ ಝುಂಬು",
            
            # Study Plan
            "study_plan": "ಅಧ್ಯಯನ ಯೋಜನೆ",
            "duration": "ಅವಧಿ",
            "total_hours": "ಒಟ್ಟು ಗಂಟೆಗಳು",
            "avg_daily_hours": "ಪ್ರತಿದಿನ ಸರಾಸರಿ ಗಂಟೆಗಳು",
            
            # Career Readiness
            "career_readiness": "ವೃತ್ತಿ ಸಿದ್ಧತೆ",
            "top_career_path": "ಉನ್ನತ ವೃತ್ತಿ ಮಾರ್ಗ",
            "salary_range": "ವೇತನ ವ್ಯಾಪ್ತಿ",
            "free_certs": "ಉಚಿತ ಪ್ರಮಾಣಪತ್ರಗಳು",
            "required_skills": "ಅಗತ್ಯ ಕೌಶಲ್ಯಗಳು",
            "placement_tips": "ನೇಮಕಾತಿ ಸಲಹೆಗಳು",
        }
    }
    
    def __init__(self, language: Language = Language.ENGLISH):
        self.current_language = language
    
    def set_language(self, language: Language):
        """Set the current language."""
        self.current_language = language
        self.translate.cache_clear()
    
    def get_language_name(self, language: Language) -> str:
        """Get human-readable language name."""
        names = {
            Language.ENGLISH: "English",
            Language.HINDI: "हिंदी (Hindi)",
            Language.TAMIL: "தமிழ் (Tamil)",
            Language.KANNADA: "ಕನ್ನಡ (Kannada)"
        }
        return names.get(language, "English")
    
    @lru_cache(maxsize=256)
    def translate(self, key: str, language: Language = None) -> str:
        """
        Translate a key to the specified language.
        Falls back to English if translation not found.
        """
        lang = language or self.current_language
        lang_code = lang.value
        
        if lang_code in self.TRANSLATIONS and key in self.TRANSLATIONS[lang_code]:
            return self.TRANSLATIONS[lang_code][key]
        
        # Fallback to English
        if key in self.TRANSLATIONS["en"]:
            return self.TRANSLATIONS["en"][key]
        
        return key  # Return key itself if no translation found
    
    def translate_dict(self, data: Dict[str, Any], language: Language = None) -> Dict[str, Any]:
        """
        Recursively translate dictionary values that are translation keys.
        Assumes keys starting with underscore are translation keys.
        """
        translated = {}
        for key, value in data.items():
            if isinstance(value, str) and key.startswith("_"):
                # This is a translation key
                translated[key] = self.translate(value, language)
            elif isinstance(value, dict):
                translated[key] = self.translate_dict(value, language)
            elif isinstance(value, list):
                translated[key] = [
                    self.translate_dict(item, language) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                translated[key] = value
        return translated
    
    def get_all_available_languages(self):
        """Return all available languages."""
        return [
            {"code": lang.value, "name": self.get_language_name(lang)}
            for lang in Language
        ]


# Global language manager instance
_language_manager = None

def get_language_manager() -> LanguageManager:
    """Get or create the global language manager."""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager(Language.ENGLISH)
    return _language_manager

def set_global_language(language: Language):
    """Set the global language."""
    get_language_manager().set_language(language)

def t(key: str) -> str:
    """Convenience function for translation."""
    return get_language_manager().translate(key)
