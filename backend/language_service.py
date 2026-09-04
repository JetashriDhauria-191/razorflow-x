import re
import math
from typing import Dict, List, Any, Optional, Tuple

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates classic Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def calculate_similarity(s1: str, s2: str) -> float:
    """Returns normalized similarity ratio [0.0 to 1.0]."""
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    dist = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    return max(0.0, 1.0 - (dist / max_len))

class LanguageService:
    """
    Universal Multilingual & Query Intelligence Service for RazorFlow X.
    Supports script detection, transliterations (Hinglish/Tanglish/Roman Telugu),
    phonetic sound-alike matching, typo-tolerant Levenshtein recovery,
    and transparent search intelligence extraction.
    """

    SUPPORTED_LANGUAGES = {
        "en": {"code": "en", "bcp47": "en-IN", "name": "English", "native": "English", "script": "Latn"},
        "ta": {"code": "ta", "bcp47": "ta-IN", "name": "Tamil", "native": "தமிழ்", "script": "Taml"},
        "hi": {"code": "hi", "bcp47": "hi-IN", "name": "Hindi", "native": "हिन्दी", "script": "Deva"},
        "te": {"code": "te", "bcp47": "te-IN", "name": "Telugu", "native": "తెలుగు", "script": "Telu"},
        "ml": {"code": "ml", "bcp47": "ml-IN", "name": "Malayalam", "native": "മലയാളം", "script": "Mlym"},
        "kn": {"code": "kn", "bcp47": "kn-IN", "name": "Kannada", "native": "ಕನ್ನಡ", "script": "Knda"},
        "bn": {"code": "bn", "bcp47": "bn-IN", "name": "Bengali", "native": "বাংলা", "script": "Beng"},
        "mr": {"code": "mr", "bcp47": "mr-IN", "name": "Marathi", "native": "मराठी", "script": "Deva"},
        "gu": {"code": "gu", "bcp47": "gu-IN", "name": "Gujarati", "native": "ગુજરાતી", "script": "Gujr"},
        "pa": {"code": "pa", "bcp47": "pa-IN", "name": "Punjabi", "native": "ਪੰਜਾਬੀ", "script": "Guru"},
        "ur": {"code": "ur", "bcp47": "ur-IN", "name": "Urdu", "native": "اردو", "script": "Arab"},
        "es": {"code": "es", "bcp47": "es-ES", "name": "Spanish", "native": "Español", "script": "Latn"},
        "fr": {"code": "fr", "bcp47": "fr-FR", "name": "French", "native": "Français", "script": "Latn"},
        "de": {"code": "de", "bcp47": "de-DE", "name": "German", "native": "Deutsch", "script": "Latn"}
    }

    CANONICAL_NAMES = {
        "headphones": "Over-Ear & Wireless Headphones",
        "earbuds": "True Wireless & In-Ear Buds",
        "shoes": "Footwear & Running Shoes",
        "sandals": "Sandals, Slides & Chappals",
        "laptop": "Laptops & Ultrabooks",
        "phone": "Smartphones & 5G Mobiles",
        "smartwatch": "Smartwatches & Fitness Bands",
        "keyboard": "Mechanical & Ergonomic Keyboards",
        "mouse": "Gaming & Productivity Mice",
        "monitor": "Monitors & Professional Displays",
        "camera": "Cameras & Vlogging Equipment",
        "gaming": "Gaming Consoles & Accessories",
        "bag": "Backpacks, Travel & Luggage",
        "clothing": "Men's & Women's Apparel",
        "women_clothing": "Women's Ethnic & Western Wear",
        "jewellery": "Fashion Jewellery & Accessories",
        "stationery": "Stationery & Notebooks",
        "kitchen": "Cookware & Kitchen Utensils",
        "appliances": "Home & Kitchen Large Appliances",
        "beauty": "Personal Care, Skincare & Grooming",
        "toys": "Toys, Building Sets & Games",
        "furniture": "Office & Home Furniture",
        "sports": "Fitness Equipment & Outdoor Gear",
        "accessories": "Fast Chargers, Cables & Auto Gear",
        "decor": "Home Decor & Ambient Lighting",
        "groceries": "Gourmet Foods & Pet Care"
    }

    # Unicode Range Scripts
    SCRIPT_PATTERNS = [
        (r'[\u0B80-\u0BFF]', 'ta', 'Tamil'),
        (r'[\u0C00-\u0C7F]', 'te', 'Telugu'),
        (r'[\u0D00-\u0D7F]', 'ml', 'Malayalam'),
        (r'[\u0C80-\u0CFF]', 'kn', 'Kannada'),
        (r'[\u0980-\u09FF]', 'bn', 'Bengali'),
        (r'[\u0A80-\u0AFF]', 'gu', 'Gujarati'),
        (r'[\u0A00-\u0A7F]', 'pa', 'Punjabi'),
        (r'[\u0600-\u06FF]', 'ur', 'Urdu'),
        (r'[\u0900-\u097F]', 'hi', 'Hindi')
    ]

    # Multilingual Category Dictionary across all Categories
    CATEGORY_VOCABULARY = {
        "headphones": [
            "headphone", "headphones", "headphons", "headphne", "hedfone", "headfon", "hedphone",
            "earphone", "earphones", "headset", "audio", "wireless headphones", "anc headphones",
            "ஹெட்போன்", "ஹெட்போன்கள்", "இயர்போன்", "ஹெட்செட்", "காதுகேளான்", "ஒலிபெருக்கி", "ஹெட்போன்ஸ்",
            "हेडफोन", "हेडफ़ोन", "इयरफ़ोन", "इयरफोन", "हेडसेट", "ईयरफोन", "हेडफोन्स",
            "హెడ్ఫోన్స్", "హెడ్ఫోన్", "ఇయర్ఫోన్స్", "చెవిలో పెట్టుకునేవి", "ఇయర్ఫోన్",
            "ഹെഡ്ഫോൺ", "ഹെഡ്ഫോണുകൾ", "ഇയർഫോൺ", "ഹെഡ്സെറ്റ്",
            "ಹೆಡ್ಫೋನ್", "ಹೆಡ್ಫೋನ್ಗಳು", "ಇಯರ್ಫೋನ್", "হেডফোন", "ইয়ারফোন",
            "auriculares", "audifonos", "cascos", "écouteurs", "casque", "kopfhörer"
        ],
        "earbuds": [
            "earbud", "earbuds", "erbuds", "tws", "airpods", "airpod", "air pods", "wireless buds", "buds", "in-ear buds",
            "இயர்பட்ஸ்", "இயர்பட்", "ஏர்பாட்ஸ்", "இயர்బడ్స్", "ఇయర్బడ్స్", "ഇയർബഡ്സ്", "ಇಯರ್ಬಡ್ಸ್", "ইয়ারবাডস",
            "auriculares inalámbricos", "écouteurs sans fil", "ohrstöpsel"
        ],
        "shoes": [
            "shoes", "shoe", "sneakers", "sneaker", "snekaers", "shose", "soes", "running shoes", "footwear", "boots", "sandals", "chappal", "chappals", "loafers", "slippers",
            "joota", "jootay", "juta", "jute", "joote", "jhoota", "jhootha", "jutha", "jotha", "jootaa",
            "seruppu", "seruppugal", "cheppulu", "seppu", "mojdi", "bata", "crocs", "trainers",
            "காலணி", "காலணிகள்", "ஷூ", "செருப்பு", "செருப்புகள்", "ஷூக்கள்", "பாதரட்சை",
            "जूता", "जूते", "चप्पल", "स्नीकर्स", "पादत्राण", "जूतियाँ", "बूट",
            "పాదరక్షలు", "షూస్", "చెప్పులు", "బూట్లు", "జోళ్ళు",
            "ഷൂസ്", "ചെരുപ്പുകൾ", "ചെരുപ്പ്", "പാദരക്ഷകൾ",
            "ಶೂಗಳು", "ಚಪ್ಪಲಿ", "ಪಾದರಕ್ಷೆಗಳು",
            "জুতো", "জুতা", "চটি", "স্নিকার্স",
            "zapatos", "zapatillas", "calzado", "chaussures", "baskets", "souliers", "schuhe", "turnschuhe"
        ],
        "laptop": [
            "laptop", "laptops", "laptoop", "laptp", "labtop", "lappi", "notebook", "macbook", "thinkpad", "ultrabook", "computer", "pc",
            "லேப்டாப்", "மடிக்கணினி", "கணினி", "लैपटॉप", "कंप्यूटर", "नोटबुक", "లాప్టాప్", "కంప్యూటర్",
            "ലാപ്ടോപ്പ്", "കമ്പ്യൂട്ടർ", "ಲ್ಯಾಪ್ಟಾಪ್", "লেপটপ", "কম্পিউটার",
            "ordinateur", "portátil", "tragbarer rechner"
        ],
        "phone": [
            "phone", "phones", "smartphone", "smartphones", "mobile", "iphone", "iphne", "iphon", "galaxy", "pixel", "redmi",
            "போன்", "மொபைல்", "ஸ்மார்ட்போன்", "கைபேசி", "செல்பேசி", "தொலைபேசி",
            "फोन", "मोबाइल", "स्मार्टफोन", "सैलफोन",
            "ఫోన్", "మొబైల్", "స్మార్ట్ఫోన్", "సెల్ఫోన్",
            "ഫോൺ", "മൊബൈൽ", "സ്മാർട്ട്ഫോൺ",
            "ಫೋನ್", "ಮೊಬೈಲ್", "ಸ್ಮಾರ್ಟ್ಫೋನ್", "ফোন", "মোবাইল", "স্মার্টফোন",
            "teléfono", "móvil", "celular", "téléphone", "portable", "handy"
        ],
        "smartwatch": [
            "smartwatch", "smartwatches", "samrtwatch", "watch", "watches", "fitness tracker", "fitness band", "ghadi", "ghari",
            "வாட்ச்", "கைக்கடிகாரம்", "ஸ்மார்ட்வாட்ச்",
            "घड़ी", "स्मार्टवॉच", "कलाई घड़ी",
            "వాచ్", "గడియారం", "స్మార్ట్వాచ్",
            "വാച്ച്", "സ്മാർട്ട്വാച്ച്", "കൈഘടികാരം",
            "ಗಡಿಯಾರ", "ಸ್ಮಾರ್ಟ್ವಾಚ್", "ಘಡಿಯಾರ",
            "ঘড়ি", "স্মার্টওয়াচ", "হাতঘড়ি",
            "reloj", "reloj inteligente", "montre", "montre connectée", "uhr"
        ],
        "keyboard": [
            "keyboard", "keyboards", "keybord", "mechanical keyboard", "keeb", "typing keys",
            "விசைப்பலகை", "கீபோர்டு", "कीबोर्ड", "की-बोर्ड", "కీబోర్డ్", "కీబోర్డు", "കീബോർഡ്", "ಕೀಬೋರ್ಡ್", "কীবোর্ড",
            "teclado", "clavier", "tastatur"
        ],
        "mouse": [
            "mouse", "mice", "gaming mouse", "trackpad", "optical mouse",
            "மவுஸ்", "சுட்டி", "माउस", "మౌస్", "മൗസ്", "ಮೌಸ್", "মাউস",
            "ratón", "souris", "maus"
        ],
        "monitor": [
            "monitor", "monitors", "display", "screen", "4k display", "curved display",
            "மானிட்டர்", "திரை", "காட்சித்திரை", "मॉनिटर", "स्क्रीन", "డిస్ప్లే", "స్క్రీన్", "മോണിറ്റർ", "ಡಿಸ್ಪ್ಲೇ", "মনিটর",
            "pantalla", "écran", "moniteur", "bildschirm"
        ],
        "camera": [
            "camera", "cameras", "dslr", "mirrorless", "action cam", "gopro", "drone",
            "கேமரா", "புகைப்படக்கருவி", "कैमरा", "కెమెరా", "ക്യാമറ", "ಕ್ಯಾಮೆರಾ", "ক্যামেরা",
            "cámara", "appareil photo", "kamera"
        ],
        "bag": [
            "bag", "bags", "backpack", "backpacks", "rucksack", "handbag", "basta", "jhola", "thela",
            "பை", "பேக்", "பேக்பேக்", "கைப்பை", "தூக்குப்பை",
            "बैग", "थैला", "बैकपैक", "झोला", "बस्ता",
            "బ్యాగ్", "సంచి", "బ్యాక్ప్యాక్",
            "ബാഗ്", "തോൾസഞ്ചി", "സഞ്ചി",
            "ಬ್ಯಾಗ್", "ಚೀಲ", "ব্যাগ", "ঝোলা",
            "bolso", "mochila", "sac", "sac à dos", "tasche"
        ],
        "clothing": [
            "clothing", "shirt", "t-shirt", "tshirt", "dress", "saree", "kurta", "kurti", "apparel", "kapda", "kapde", "thuni", "sattai", "satttai", "kamij", "chokka", "battalu",
            "துணி", "ஆடை", "சட்டை", "சேலை", "உடை",
            "कपड़ा", "कपड़े", "शर्ट", "साड़ी", "कुर्ता", "कुर्ती", "सूट", "वस्त्र",
            "బట్టలు", "చొక్కా", "చీర", "దుస్తులు",
            "വസ്ത്രം", "ഷർട്ട്", "സാരി", "തുണി",
            "ಬಟ್ಟೆ", "ಸೀರೆ", "ಅಂಗಿ",
            "কাপড়", "শার্ট", "শাড়ি", "পোশাক",
            "ropa", "camisa", "vestido", "vêtements", "chemise", "robe", "kleidung", "hemd"
        ],
        "stationery": [
            "stationery", "pencil", "pencils", "pen", "pens", "notebook", "diary", "kalam", "kitab", "pustak",
            "பேனா", "பென்சில்", "நோட்டுப்புத்தகம்", "புத்தகம்", "எழுதுகோல்",
            "कलम", "पेन", "पेंसिल", "किताब", "कॉपी", "डायरी", "पुस्तक",
            "పెన్", "పెన్సిల్", "పుస్తకం", "నోట్బుక్", "പേന", "പെൻസിൽ", "ಪುಸ್ತಕ", "পেন", "পেন্সিল", "বই",
            "lápiz", "bolígrafo", "stylo", "crayon", "stift", "schreibwaren"
        ],
        "kitchen": [
            "kitchen", "cooker", "pressure cooker", "pan", "kadhai", "utensils", "cookware", "bartan", "thali", "katori", "chammach", "mixer", "grinder",
            "சமையல்", "குக்கர்", "பாத்திரம்", "மிக்ஸி",
            "कुकवेयर", "कुकर", "कढ़ाई", "बर्तन", "मिक्सर", "ग्राइंडर", "रसोई",
            "వంట పాత్రలు", "కుక్కర్", "మిక్సీ",
            "പാത്രങ്ങൾ", "കുക്കർ", "മിക്സി",
            "ಅಡುಗೆ ಪಾತ್ರೆ", "ಕುಕ್ಕರ್", "রান্নাঘর", "কুকার",
            "cocina", "olla", "cuisine", "poêle", "küche", "kochgeschirr"
        ],
        "appliances": [
            "appliances", "fan", "ceiling fan", "vacuum", "washing machine", "dryer", "fridge", "refrigerator", "ac", "air conditioner", "pankha",
            "மின்விசிறி", "ஃபேன்", "குளிரூட்டி", "சலவை இயந்திரம்",
            "पंखा", "पंखे", "वॉशिंग मशीन", "फ्रिज", "एसी",
            "వాషింగ్ మెషిన్", "ఫ్యాన్", "ఫ్రిజ్",
            "ഫാൻ", "ഫ്രിഡ്ജ്", "വാഷിംഗ് മെഷീൻ",
            "ಫ್ಯಾನ್", "ಫ್ರಿಜ್", "পাখা", "ফ্রিজ",
            "ventilador", "ventilateur", "refrigerador", "frigorifique", "kühlschrank"
        ],
        "beauty": [
            "beauty", "trimmer", "grooming", "hair dryer", "perfume", "soap", "facewash", "shampoo", "lipstick", "makeup", "sabun", "tel", "skincare",
            "அழகு", "ட்ரிம்மர்", "சோப்பு", "வாசனை திரவியம்", "சீப்பு",
            "साबुन", "ट्रिमर", "परफ्यूम", "मेकअप", "लिपस्टिक", "फेसवाश", "सौंदर्य",
            "సబ్బు", "ట్రిమ్మర్", "పెర్ఫ్యూమ్", "സോപ്പ്", "ട്രിമ്മർ", "ಸೋಪು", "সাবান",
            "belleza", "afeitadora", "parfum", "savon", "schönheit", "rasierer", "seife"
        ],
        "toys": [
            "toy", "toys", "lego", "plush", "kids", "doll", "game", "hot wheels", "puzzle", "khilona", "khilone", "gudiya",
            "பொம்மை", "விளையாட்டு பொருள்", "குழந்தைகள் பொம்மை",
            "खिलौना", "खिलौने", "गुड़िया", "लेगो", "बच्चों के खिलौने",
            "బొమ్మ", "బొమ్మలు", "കുട്ടികളുടെ കളിപ്പാട്ടങ്ങൾ", "കളിപ്പാട്ടം", "ಆಟಿಕೆ", "খেলনা",
            "juguete", "juguetes", "jouet", "jouets", "spielzeug"
        ],
        "furniture": [
            "furniture", "chair", "office chair", "desk", "standing desk", "table", "bookshelf", "sofa", "kursi", "mej",
            "நாற்காலி", "மேசை", "அலுவலக நாற்காலி", "மரச்சாமான்கள்",
            "कुर्सी", "मेज", "सोफा", "फर्नीचर", "ऑफिस चेयर",
            "కుర్చీ", "టేబుల్", "ఫర్నిచర్", "കസേര", "മേശ", "ಕುರ್ಚಿ", "টেবিল", "চেয়ার",
            "muebles", "silla", "escritorio", "meubles", "chaise", "bureau", "möbel", "stuhl"
        ],
        "sports": [
            "sports", "fitness", "yoga", "gym", "dumbbell", "badminton", "racket", "football", "cricket", "exercise",
            "உடற்பயிற்சி", "விளையாட்டு", "कसरत", "जिम", "వ్యాయామం", "കായിക", "deportes", "sport"
        ],
        "accessories": [
            "accessories", "charger", "gan charger", "hub", "dock", "usb-c dock", "desk mat", "mousepad", "power bank", "sunglasses", "chashma", "chasma", "kannadi", "kannaadi", "kallajodu",
            "சார்ஜர்", "கண்ணாடி", "சூரிய கண்ணாடி", "பவர் பேங்க்",
            "चश्मा", "धूप का चश्मा", "पावर बैंक", "चार्जर", "डक",
            "సన్గ్లాసెస్", "కళ్లద్దాలు", "ఛార్జర్", "കണ്ണട", "ചാർജർ", "ಕನ್ನಡಕ", "সানগ্লাস",
            "accesorios", "cargador", "gafas de sol", "accessoires", "chargeur", "zubehör", "ladegerät"
        ],
        "decor": [
            "decor", "balloon", "balloons", "arch kit", "party decor", "birthday decoration", "lights", "led strip", "fairy lights", "lamp", "diya",
            "பலூன்", "பிறந்தநாள் அலங்காரம்", "அலங்காரம்", "விளக்கு",
            "गुब्बारा", "गुब्बारे", "सजावट", "बर्थडे डेकोरेशन", "लाइट्स", "दीया",
            "బెలూన్", "డెకరేషన్", "లైట్లు", "ബലൂൺ", "അലങ്കാരം", "ಬಲೂನ್", "বেলুন", "সাজসজ্জা",
            "decoración", "globos", "luces", "décoration", "ballons", "lumières", "dekoration", "lichter"
        ]
    }

    # Multilingual Intent Keywords
    INTENT_KEYWORDS = {
        "CHEAPEST": [
            "cheap", "cheapest", "cheaper", "budget", "affordable", "low price", "lowest", "sasta", "kam daam",
            "குறைந்த விலை", "மலிவான", "மலிவு", "குறைந்த", "சுலபமானது", "விலை குறைவான", "பட்ஜெட்",
            "सस्ता", "कम दाम", "किफायती", "कम कीमत", "सस्ते",
            "తక్కువ ధర", "చౌకైన", "తక్కువ రేటు",
            "വിലക്കുറവുള്ള", "കുറഞ്ഞ വില", "ചെലവ് കുറഞ്ഞ",
            "ಕಡಿಮೆ ಬೆಲೆಯ", "ಸ್ವಲ್ಪ ಬೆಲೆಯ",
            "কম দাম", "সস্তা",
            "barato", "económico", "pas cher", "meilleur marché", "günstig", "billig"
        ],
        "PREMIUM": [
            "premium", "luxury", "flagship", "expensive", "best quality", "high end", "top tier", "pro", "ultra",
            "விலை உயர்ந்த", "ஆடம்பர", "உயர் தரம்", "பிரீமியம்", "சிறந்த தரம்",
            "महंगा", "प्रीमियम", "शानदार", "बेहतरीन क्वालिटी", "लक्जरी",
            "ప్రీమియం", "ఖరీదైన", "ఉత్తమ నాణ్యత",
            "പ്രീമിയം", "വിലകൂടിയ", "ഉയർന്ന നിലവാരം",
            "lujo", "caro", "gama alta", "haut de gamme", "luxe", "luxus", "premium"
        ],
        "BEST_RATED": [
            "best rated", "top rated", "highest rated", "most popular", "5 star", "customer favorite", "top review",
            "அதிக மதிப்பீடு", "சிறந்த ரேட்டிங்", "மக்கள் விரும்பிய", "பிரபலமான",
            "टॉप रेटेड", "सबसे अच्छा", "बेस्ट रेटिंग", "5 स्टार", "पॉपुलर",
            "టాప్ రేటెడ్", "మంచి రేటింగ్", "అత్యధిక రేటింగ్",
            "മികച്ച റേറ്റിംഗ്", "കൂടുതൽ ആളുകൾ വാങ്ങിയ",
            "mejor valorado", "más popular", "mieux noté", "bestbewertet"
        ],
        "BEST_VALUE": [
            "best value", "value for money", "best bang for buck", "balanced", "worth it", "recommended",
            "சிறந்த மதிப்பு", "பணத்திற்கான மதிப்பு", "சிறந்தது", "நல்ல", "விருப்பமான",
            "वैल्यू फॉर मनी", "सबसे बढ़िया", "फायदेमंद", "अच्छा",
            "మంచి విలువ", "విలువైన", "ఉత్తమమైన",
            "നല്ല മൂല്യം", "നല്ലത്",
            "mejor relación calidad-precio", "bon rapport qualité-prix", "preis-leistungs-sieger"
        ],
        "COMPARE": [
            "compare", "vs", "versus", "difference", "which is better", "comparison",
            "ஒப்பீடு", "துலா", "வித்தியாசம்", "எது சிறந்தது", "तुलना", "अंतर", "कौन सा अच्छा है", "పోలిక", "ఏది మంచిది",
            "താരതമ്യം", "comparar", "comparer", "vergleichen"
        ]
    }

    # Transliterated Romanized / Hinglish / Tanglish Patterns
    TRANSLITERATION_MAP = {
        "nalla": "good / best", "nalladhu": "good", "sasta": "cheap", "mehnga": "expensive", "accha": "good",
        "chahiye": "need / want", "venum": "need / want", "kavale": "need / want", "venam": "need / want",
        "kaatu": "show", "dikhao": "show", "chupinchu": "show", "kaanikoo": "show", "torisu": "show",
        "rupaye": "rupees", "roobai": "rupees", "rubai": "rupees", "roopayalu": "rupees", "rupa": "rupees",
        "joota": "shoes", "juta": "shoes", "jotha": "shoes", "jutha": "shoes", "jhoota": "shoes", "chappal": "shoes", "seruppu": "shoes", "cheppulu": "shoes",
        "kapda": "clothing", "sattai": "clothing", "chashma": "sunglasses", "kannadi": "sunglasses", "ghadi": "smartwatch",
        "kalam": "pen", "kitab": "notebook", "basta": "bag", "jhola": "bag", "pankha": "fan"
    }

    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detects language code and confidence score (0.0 to 1.0) from input text."""
        if not text or not text.strip():
            return "en", 1.0

        clean_text = text.strip()

        # Check script patterns first (even single script glyph)
        for pattern, code, lang_name in self.SCRIPT_PATTERNS:
            matches = re.findall(pattern, clean_text)
            if matches and len(matches) >= 1:
                ratio = min(1.0, len(matches) / max(1, len(clean_text.replace(" ", ""))))
                confidence = round(max(0.88, ratio), 2)
                return code, confidence

        # Check French, Spanish, German specific words
        lower = clean_text.lower()
        if any(w in lower for w in ["meilleur", "écouteurs", "ordinateur", "montre-moi", "prix", "chaussures"]):
            return "fr", 0.94
        if any(w in lower for w in ["muéstrame", "auriculares", "barato", "zapatos", "precio", "teléfono"]):
            return "es", 0.94
        if any(w in lower for w in ["kopfhörer", "billig", "schuhe", "handy", "zeig mir", "preis"]):
            return "de", 0.94

        # Check Romanized Hinglish/Tanglish/Telugu
        if any(w in lower for w in ["seruppu", "seruppugal", "sattai", "satttai", "thuni", "thunigal", "kannaadi", "kannadi", "kulla", "roobai", "kaatu", "venum", "nalla", "kudukka", "pudavai", "angadi", "vilai", "solunga", "kaadholi", "seppu"]):
            return "ta", 0.92
        if any(w in lower for w in ["joota", "jhoota", "juta", "jutha", "jotha", "jootaa", "joote", "kapda", "kapde", "chashma", "pankha", "ghadi", "chappal", "basta", "jhola", "chahiye", "dikhao", "sasta", "accha", "rupaye", "khol", "batao", "kharido", "daam", "sabun"]):
            return "hi", 0.92
        if any(w in lower for w in ["cheppulu", "chokka", "battalu", "kallajodu", "gadiyaram", "lopu", "lopala", "chupinchu", "kavale", "kavali", "roopayalu", "manchi", "dabbulu", "dhara", "konandi"]):
            return "te", 0.92

        return "en", 0.95

    def get_fuzzy_category_match(self, query: str) -> Tuple[Optional[str], float, Optional[str], Optional[str]]:
        """
        Fuzzy Levenshtein & substring matcher that resolves any misspelled or transliterated token
        into a canonical product category.
        Returns: (matched_category, similarity_score, matched_alias, typo_corrected_term)
        """
        if not query or not query.strip():
            return None, 0.0, None, None

        q_clean = query.lower().strip()
        tokens = re.findall(r'[\w\u0900-\u0D7F]+', q_clean)

        # 1. Direct substring check
        for cat, synonyms in self.CATEGORY_VOCABULARY.items():
            for syn in synonyms:
                syn_low = syn.lower()
                if syn_low in q_clean or any(syn_low == t for t in tokens):
                    return cat, 1.0, syn, syn

        # 2. Token-level fuzzy Levenshtein match
        best_cat = None
        best_score = 0.0
        best_syn = None
        best_token = None

        for cat, synonyms in self.CATEGORY_VOCABULARY.items():
            for syn in synonyms:
                syn_low = syn.lower()
                for token in tokens:
                    if len(token) < 3 and len(syn_low) >= 4:
                        continue
                    sim = calculate_similarity(token, syn_low)
                    if sim > best_score:
                        best_score = sim
                        best_cat = cat
                        best_syn = syn
                        best_token = token

        if best_score >= 0.70 and best_cat:
            typo_str = f"{best_token} ➔ {best_syn}" if best_token != best_syn else best_syn
            return best_cat, round(best_score, 2), best_syn, typo_str

        return None, 0.0, None, None

    def normalize_multilingual_query(self, query: str, active_lang: Optional[str] = None) -> Dict[str, Any]:
        """
        Normalizes a multilingual user query into structured tokens:
        - detected_language, language_name
        - confidence, confidence_score_percent, confidence_tier
        - category, category_canonical, interpreted_intent
        - budget
        - intent_type
        - typo_correction
        - expanded_aliases
        """
        q = (query or "").strip()
        lang_code, lang_conf = self.detect_language(q)
        if active_lang and active_lang != "auto" and active_lang in self.SUPPORTED_LANGUAGES:
            lang_code = active_lang
            lang_conf = 1.0

        lower_q = q.lower()

        # Extract Budget across multilingual number formats
        budget = None
        
        # Regex for Indic/Global budget phrases like 20k, 60k, 5k
        budget_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:k\b|kilo|ஆயிரம்|हजार|వేలు|ആയിരം)", lower_q)
        if budget_match:
            try:
                raw_val = float(budget_match.group(1).replace(",", ""))
                budget = raw_val * 1000.0
            except ValueError:
                pass

        if budget is None:
            # Pattern: under 5000 / 5000 rs / 5000 ரூபாய் / ₹5000
            num_match = re.search(
                r"(?:under|below|less than|within|around|upto|up to|max|budget|₹|rs\.?|inr|ரூபாய்|ரூபாய்க்குள்|रुपये|रुपए|రూపాయలు|రూపాయల|രൂപ|രൂപയ്ക്കുള്ളിൽ|ರೂಪಾಯಿ|টাকা|euros?|€|\$)\s*(\d[\d,.]*)",
                lower_q
            )
            if num_match:
                try:
                    val = float(num_match.group(1).replace(",", ""))
                    if val > 10:
                        budget = val
                except ValueError:
                    pass

        if budget is None:
            # Reverse pattern: 5000 ரூபாய் / 5000 rupees / 5000 ke andar / 5000 budget la / 5000 kulla / ₹5000 குள்ள
            rev_match = re.search(
                r"(?:₹|rs\.?)?\s*(\d[\d,.]*)\s*(?:ரூபாய்|ரூபாய்க்குள்|ரூபாய்க்கு\s*கீழ|குள்ள|kulla|ulla|keela|உள்|रुपये|रुपए|के\s*अंदर|ke\s*andar|andar|mein|me|se\s*kam|tak|lopala|lopu|kinda|budget\s*la|budget|రూపాయలు|రూపాయల|లోపు|രൂപ|രൂപയ്ക്കുള്ളിൽ|ರೂಪಾಯಿ|টাকা|rupees|rs|inr|bucks|euros?|€)",
                lower_q
            )
            if rev_match:
                try:
                    val = float(rev_match.group(1).replace(",", ""))
                    if val > 10:
                        budget = val
                except ValueError:
                    pass

        if budget is None:
            # Standalone 3-6 digit numbers with budget indicators
            if any(w in lower_q for w in ["under", "below", "budget", "andar", "kulla", "lopala", "tak", "mein", "me", "se kam", "₹", "rs", "குள்ள"]):
                num_standalone = re.search(r"\b(\d{3,6})\b", lower_q)
                if num_standalone:
                    try:
                        val = float(num_standalone.group(1))
                        if val >= 100:
                            budget = val
                    except ValueError:
                        pass

        # Detect Category: Exact & Fuzzy Levenshtein
        detected_category, cat_sim, matched_alias, typo_corr = self.get_fuzzy_category_match(q)

        # Detect Intent Type from Multilingual Keywords
        detected_intent = "DISCOVERY"
        for itype, kws in self.INTENT_KEYWORDS.items():
            if any(kw.lower() in lower_q for kw in kws):
                detected_intent = itype
                break

        # Confidence calculation
        overall_conf = round(max(0.60, min(1.0, (lang_conf * 0.4) + (cat_sim * 0.6 if detected_category else 0.5))), 2)
        if overall_conf >= 0.92:
            conf_tier = "HIGH CONFIDENCE"
        elif overall_conf >= 0.75:
            conf_tier = "LIKELY MATCH"
        elif overall_conf >= 0.50:
            conf_tier = "POSSIBLE MATCH"
        else:
            conf_tier = "EXPLORATORY"

        canonical_name = self.CANONICAL_NAMES.get(detected_category or "", (detected_category or "All Categories").title())
        
        # Representative expanded aliases for this category
        expanded_aliases = []
        if detected_category and detected_category in self.CATEGORY_VOCABULARY:
            vocab = self.CATEGORY_VOCABULARY[detected_category]
            # Pick a diverse sample: English, Hindi, Tamil, Telugu
            sample_candidates = [vocab[0]] if vocab else []
            for v in vocab[1:]:
                if any(ord(c) > 127 for c in v) or v in ["sneakers", "joota", "seruppu", "cheppulu", "airpods", "macbook", "iphone"]:
                    if v not in sample_candidates:
                        sample_candidates.append(v)
                if len(sample_candidates) >= 6:
                    break
            expanded_aliases = sample_candidates

        return {
            "original_query": query,
            "detected_language": lang_code,
            "language_name": self.SUPPORTED_LANGUAGES.get(lang_code, {}).get("name", "English"),
            "confidence": overall_conf,
            "confidence_score_percent": int(overall_conf * 100),
            "confidence_tier": conf_tier,
            "category": detected_category,
            "category_canonical": canonical_name,
            "interpreted_intent": canonical_name if detected_category else "Product Discovery",
            "budget": budget,
            "intent_type": detected_intent,
            "matched_alias": matched_alias,
            "typo_correction": typo_corr if (cat_sim < 0.99 and typo_corr) else None,
            "expanded_aliases": expanded_aliases
        }

    def generate_multilingual_insight(
        self,
        lang_code: str,
        products: List[Dict[str, Any]],
        intent: Dict[str, Any]
    ) -> str:
        """Generates an AI Shopping Insight explanation in the user's preferred language."""
        count = len(products)
        if count == 0:
            no_results_map = {
                "ta": "இணைக்கப்பட்ட தயாரிப்பு மூலங்களிலிருந்து பொருந்தக்கூடிய தயாரிப்புகள் எதுவும் கிடைக்கவில்லை. உங்கள் தேடல் சொற்கள் அல்லது பட்ஜெட்டை மாற்றி முயற்சிக்கவும்.",
                "hi": "वर्तमान में जुड़े स्रोतों से कोई उत्पाद नहीं मिला। कृपया अपने बजट या खोज शब्दों को समायोजित करके पुनः प्रयास करें।",
                "te": "కనెక్ట్ చేయబడిన మూలాల నుండి సరిపోలే ఉత్పత్తులు ఏవీ కనుగొనబడలేదు. దయచేసి శోధన పదాలను మార్చండి.",
                "ml": "കണക്റ്റുചെയ്‌ത ഉറവിടങ്ങളിൽ നിന്ന് ഉൽപ്പന്നങ്ങളൊന്നും കണ്ടെത്തിയില്ല. ദയവായി മറ്റ് കീവേഡുകൾ ഉപയോഗിക്കുക.",
                "kn": "ಯಾವುದೇ ಹೊಂದಾಣಿಕೆಯ ಉತ್ಪನ್ನಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಬೇರೆ ಪದಗಳನ್ನು ಬಳಸಿ ಹುಡುಕಿ.",
                "bn": "কোন পণ্য পাওয়া যায়নি। অনুগ্রহ করে অন্য শব্দ দিয়ে অনুসন্ধান করুন।",
                "es": "No se encontraron productos coincidentes de las fuentes conectadas. Intente ajustar su búsqueda.",
                "fr": "Aucun produit correspondant trouvé parmi les sources connectées. Essayez d'ajuster votre recherche.",
                "de": "Keine passenden Produkte aus den verbundenen Quellen gefunden. Bitte Suche anpassen.",
                "en": "No matching products found from currently connected sources. Try adjusting your search or budget."
            }
            return no_results_map.get(lang_code, no_results_map["en"])

        top = products[0]
        top_name = top.get("name", "Product")
        top_price = f"₹{top.get('price', 0):,.0f}"
        top_rating = f"{top.get('rating', 4.8)}★"
        top_days = f"{top.get('delivery_days', 1)}"
        budget_str = f"₹{intent.get('budget', 0):,.0f}" if intent.get("budget") else None

        if lang_code == "ta":
            if budget_str:
                return f"உங்கள் பட்ஜெட்டான {budget_str}-க்குள் {count} சரிபார்க்கப்பட்ட தயாரிப்புகளைக் கண்டறிந்துள்ளேன். இதில் **{top_name}** ({top_price}) மிகச்சிறந்த தேர்வாக பரிந்துரைக்கப்படுகிறது (மதிப்பீடு: {top_rating}, விரைவான {top_days}-நாள் டெலிவரி)."
            return f"உங்கள் தேடலுக்கு {count} தயாரிப்புகள் கிடைத்துள்ளன. **{top_name}** ({top_price}) அதன் சிறந்த {top_rating} மதிப்பீடு மற்றும் தரத்திற்காக முதல் இடத்தில் உள்ளது."

        elif lang_code == "hi":
            if budget_str:
                return f"मुझे आपके {budget_str} के बजट में {count} सत्यापित विकल्प मिले हैं। मेरी शीर्ष अनुशंसा **{top_name}** ({top_price}) है, जिसमें उत्कृष्ट {top_rating} रेटिंग और तेज़ {top_days}-दिन की डिलीवरी उपलब्ध है।"
            return f"कैटलॉग में {count} उत्पाद मिले हैं। **{top_name}** ({top_price}) अपनी उच्च {top_rating} रेटिंग और प्रामाणिकता के लिए #1 रैंक पर है।"

        elif lang_code == "te":
            if budget_str:
                return f"మీ {budget_str} బడ్జెట్లో {count} సరిపోయే ఉత్పత్తులను కనుగొన్నాను. **{top_name}** ({top_price}) ఉత్తమ రేటింగ్ ({top_rating}) మరియు వేగవంతమైన డెలివరీతో అగ్రస్థానంలో ఉంది."
            return f"క్యాటలాగ్‌లో {count} ఉత్పత్తులు లభించాయి. **{top_name}** ({top_price}) అత్యుత్తమ {top_rating} రేటింగ్‌తో మొదటి స్థానంలో ఉంది."

        elif lang_code == "ml":
            if budget_str:
                return f"നിങ്ങളുടെ {budget_str} ബഡ്ജറ്റിൽ {count} മികച്ച ഉൽപ്പന്നങ്ങൾ കണ്ടെത്തി. **{top_name}** ({top_price}) ഉയർന്ന റേറ്റിംഗോടെയും ({top_rating}) വേഗതയേറിയ ഡെലിവറിയോടെയും മുൻപന്തിയിലാണ്."
            return f"തിരഞ്ഞെടുത്തവയിൽ {count} ഉൽപ്പന്നങ്ങൾ ലഭ്യമാണ്. **{top_name}** ({top_price}) ഒന്നാം സ്ഥാനത്ത് ശുപാർശ ചെയ്യുന്നു."

        elif lang_code == "es":
            if budget_str:
                return f"Encontré {count} opciones verificadas dentro de su presupuesto de {budget_str}. La mejor opción es **{top_name}** ({top_price}) con calificación de {top_rating}."
            return f"Se encontraron {count} productos. **{top_name}** ({top_price}) está clasificado #1 por su alta satisfacción ({top_rating})."

        elif lang_code == "fr":
            if budget_str:
                return f"J'ai trouvé {count} options vérifiées correspondant à votre budget de {budget_str}. Mon choix n°1 est **{top_name}** ({top_price}) avec une note de {top_rating}."
            return f"{count} produits trouvés. **{top_name}** ({top_price}) est classé n°1 avec {top_rating} étoiles."

        # Default English
        if budget_str:
            return f"I found {count} verified options matching your budget of {budget_str}. My top recommendation is **{top_name}** at {top_price} with high customer satisfaction ({top_rating}) and {top_days}-day delivery."
        return f"I found {count} matching items in the catalogue. **{top_name}** ({top_price}) is ranked #1 for its strong {top_rating} rating and verified specifications."

    def get_suggestions(self, prefix: str, lang: Optional[str] = None) -> List[str]:
        """Returns multilingual autocomplete search suggestions for a given typed prefix."""
        if not prefix or len(prefix.strip()) < 2:
            return [
                "Headphones under ₹5000",
                "Laptop for coding",
                "Smartphone under ₹30000",
                "Nike running shoes",
                "Best smartwatch for fitness"
            ]

        p = prefix.strip().lower()
        suggestions = []

        # Check vocabulary matches
        for cat, synonyms in self.CATEGORY_VOCABULARY.items():
            for syn in synonyms:
                if syn.lower().startswith(p) or p in syn.lower():
                    suggestions.append(f"{syn.capitalize()} under ₹5,000")
                    suggestions.append(f"Best {syn.lower()}")
                    break

        if not suggestions:
            # Fuzzy match suggestion
            matched_cat, sim, matched_syn, _ = self.get_fuzzy_category_match(p)
            if matched_cat and matched_syn:
                suggestions.append(f"Best {matched_syn}")
                suggestions.append(f"{matched_syn.capitalize()} under ₹5,000")

        if not suggestions:
            suggestions = [
                f"{prefix} under ₹5,000",
                f"Best {prefix}",
                f"{prefix} with top rating",
                f"Cheap {prefix}"
            ]

        return list(dict.fromkeys(suggestions))[:6]

    def get_spelling_correction(self, query: str) -> Optional[str]:
        """Fuzzy spell checking for common misspellings."""
        if not query:
            return None

        q = query.strip().lower()
        common_typos = {
            "hedfone": "Headphones",
            "headfone": "Headphones",
            "headphons": "Headphones",
            "hedphone": "Headphones",
            "earfone": "Earphones",
            "erbuds": "Earbuds",
            "iphon": "iPhone",
            "iphne": "iPhone",
            "laptoop": "Laptop",
            "laptp": "Laptop",
            "labtop": "Laptop",
            "keybord": "Keyboard",
            "shose": "Shoes",
            "soes": "Shoes",
            "snekaers": "Sneakers",
            "samrtwatch": "Smartwatch",
            "watc": "Watch",
            "jotha": "Joota",
            "chasma": "Chashma"
        }

        for typo, fix in common_typos.items():
            if typo in q:
                return q.replace(typo, fix)

        # Fallback to fuzzy category match if typo found
        _, sim, matched_syn, _ = self.get_fuzzy_category_match(q)
        if 0.70 <= sim < 0.98 and matched_syn:
            return matched_syn.capitalize()

        return None

language_service = LanguageService()
