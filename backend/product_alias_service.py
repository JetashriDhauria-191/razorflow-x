import re
from typing import Dict, List, Optional, Tuple

class ProductAliasService:
    """
    Multilingual Product Semantic Alias Engine.
    Maps native words, scripts, transliterations, and local slang across 28 categories
    into canonical product category intents.
    """
    CANONICAL_CATEGORIES = {
        "headphones": "Over-Ear & Wireless Headphones",
        "earbuds": "True Wireless & In-Ear Buds",
        "laptop": "Laptops & Ultrabooks",
        "phone": "Smartphones & 5G Mobiles",
        "smartwatch": "Smartwatches & Fitness Bands",
        "keyboard": "Mechanical & Ergonomic Keyboards",
        "mouse": "Gaming & Productivity Mice",
        "monitor": "Monitors & Professional Displays",
        "camera": "Cameras & Vlogging Equipment",
        "gaming": "Gaming Consoles & Accessories",
        "shoes": "Footwear & Running Shoes",
        "sandals": "Sandals, Slides & Chappals",
        "clothing": "Men's & Women's Apparel",
        "women_clothing": "Women's Ethnic & Western Wear",
        "bag": "Backpacks, Travel & Luggage",
        "jewellery": "Fashion Jewellery & Accessories",
        "kitchen": "Cookware & Kitchen Utensils",
        "appliances": "Home & Kitchen Large Appliances",
        "furniture": "Office & Home Furniture",
        "decor": "Home Decor & Ambient Lighting",
        "beauty": "Personal Care, Skincare & Grooming",
        "sports": "Fitness Equipment & Outdoor Gear",
        "stationery": "Stationery & Notebooks",
        "toys": "Toys, Building Sets & Baby Products",
        "accessories": "Fast Chargers, Cables & Auto Gear",
        "groceries": "Pet Care & Gourmet Packaged Foods"
    }

    CATEGORY_ALIASES = {
        "shoes": [
            "shoes", "shoe", "footwear", "sneakers", "sneaker", "snekaers", "shose", "soes", "running shoes", "boots", "loafers", "trainers", "slippers",
            "joota", "jootay", "juta", "jute", "joote", "jhoota", "jhootha", "jutha", "jotha", "jootaa", "chappal", "chappals", "seruppu", "seruppugal", "cheppulu", "seppu", "mojdi", "bata", "crocs",
            "காலணி", "காலணிகள்", "ஷூ", "செருப்பு", "செருப்புகள்", "ஷூக்கள்", "பாதரட்சை",
            "जूता", "जूते", "चप्पल", "स्नीकर्स", "पादत्राण", "जूतियाँ", "बूट",
            "పాదరక్షలు", "షూస్", "చెప్పులు", "బూట్లు", "జోళ్ళు",
            "ഷൂസ്", "ചെരുപ്പുകൾ", "ചെരുപ്പ്", "പാദരക്ഷകൾ",
            "ಶೂಗಳು", "ಚಪ್ಪಲಿ", "ಪಾದರಕ್ಷೆಗಳು",
            "জুতো", "জুতা", "চটি", "স্নিকার্স",
            "zapatos", "zapatillas", "calzado", "chaussures", "baskets", "schuhe"
        ],
        "headphones": [
            "headphone", "headphones", "headphons", "headphne", "earphone", "earphones", "headset", "audio", "hedfone", "headfon", "hedphone",
            "ஹெட்போன்", "ஹெட்போன்கள்", "இயர்போன்", "ஹெட்செட்", "காதுகேளான்", "ஒலிபெருக்கி", "ஹெட்போன்ஸ்",
            "हेडफोन", "हेडफ़ोन", "इयरफ़ोन", "इयरफोन", "हेडसेट", "ईयरफोन", "हेडफोन्स",
            "హెడ్ఫోన్స్", "హెడ్ఫోన్", "ఇయర్ఫోన్స్", "చెవిలో పెట్టుకునేవి", "ఇయర్ఫోన్",
            "ഹെഡ്ഫോൺ", "ഹെഡ്ഫോണുകൾ", "ഇയർഫോൺ", "ഹെഡ്സെറ്റ്",
            "ಹೆಡ್ಫೋನ್", "ಹೆಡ್ಫೋನ್ಗಳು", "ಇಯರ್ಫೋನ್", "হেডফোন", "ইয়ারফোন",
            "auriculares", "audifonos", "cascos", "écouteurs", "casque", "kopfhörer"
        ],
        "earbuds": [
            "earbud", "earbuds", "tws", "airpods", "airpod", "air pods", "wireless buds", "buds", "in-ear buds",
            "இயர்பட்ஸ்", "இயர்பட்", "ஏர்பாட்ஸ்", "ఇయర్బడ్స్", "ഇയർബഡ്സ്", "ಇಯರ್ಬಡ್ಸ್", "ইয়ারবাডস",
            "auriculares inalámbricos", "écouteurs sans fil", "ohrstöpsel"
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
            "வாட்ச்", "கைக்கடிகாரம்", "ஸ்மார்ட்வாட்ச்", "घड़ी", "स्मार्टवॉच", "వాచ్", "గడియారం",
            "സ്മാർട്ട്വാച്ച്", "ಘಡಿಯಾರ", "ঘড়ি", "reloj", "montre", "uhr"
        ],
        "keyboard": [
            "keyboard", "keyboards", "keybord", "mechanical keyboard", "keeb", "typing keys",
            "விசைப்பலகை", "கீபோர்டு", "कीबोर्ड", "కీబోర్డ్", "കീബോർഡ്", "ಕೀಬೋರ್ಡ್", "কীবোর্ড",
            "teclado", "clavier", "tastatur"
        ],
        "mouse": [
            "mouse", "mice", "gaming mouse", "trackpad", "optical mouse",
            "மவுஸ்", "சுட்டி", "माउस", "మౌస్", "മൗസ്", "ಮೌಸ್", "মাউস", "ratón", "souris", "maus"
        ],
        "monitor": [
            "monitor", "monitors", "display", "screen", "4k display", "curved display",
            "மானிட்டர்", "திரை", "मॉनिटर", "स्क्रीन", "డిస్ప్లే", "മോണിറ്റർ", "ಡಿಸ್ಪ್ಲೇ", "মনিটর",
            "pantalla", "écran", "bildschirm"
        ],
        "camera": [
            "camera", "cameras", "dslr", "mirrorless", "action cam", "gopro", "drone",
            "கேமரா", "புகைப்படக்கருவி", "कैमरा", "కెమెరా", "ക്യാമറ", "ಕ್ಯಾಮೆರಾ", "ক্যামেরা",
            "cámara", "appareil photo", "kamera"
        ],
        "bag": [
            "bag", "bags", "backpack", "backpacks", "rucksack", "handbag", "basta", "jhola", "thela",
            "பை", "பேக்", "பேக்பேக்", "கைப்பை", "बैग", "थैला", "बैकपैक", "झोला", "बस्ता",
            "బ్యాగ్", "సంచి", "ബാഗ്", "തോൾസഞ്ചി", "ಬ್ಯಾಗ್", "ব্যাগ", "bolso", "mochila", "sac"
        ],
        "clothing": [
            "clothing", "shirt", "t-shirt", "tshirt", "dress", "saree", "kurta", "kurti", "apparel", "kapda", "kapde", "thuni", "sattai", "satttai", "kamij", "chokka", "battalu",
            "துணி", "ஆடை", "சட்டை", "சேலை", "कपड़ा", "कपड़े", "शर्ट", "साड़ी", "कुर्ता",
            "బట్టలు", "చొక్కా", "చీర", "వస్త్రം", "ഷർട്ട്", "ಬಟ್ಟೆ", "কাপড়", "ropa", "camisa", "vêtements"
        ],
        "kitchen": [
            "kitchen", "cooker", "pressure cooker", "pan", "kadhai", "utensils", "cookware", "bartan", "thali", "mixer", "grinder",
            "சமையல்", "குக்கர்", "பாத்திரம்", "மிக்ஸி", "कुकवेयर", "कुकर", "कढ़ाई", "बर्तन", "मिक्सर",
            "వంట పాత్రలు", "కుక్కర్", "പാത്രങ്ങൾ", "കുക്കർ", "ಅಡುಗೆ ಪಾತ್ರೆ", "cocina", "cuisine"
        ],
        "appliances": [
            "appliances", "fan", "ceiling fan", "vacuum", "washing machine", "dryer", "fridge", "refrigerator", "ac", "air conditioner", "pankha",
            "மின்விசிறி", "ஃபேன்", "குளிரூட்டி", "पंखा", "पंखे", "वॉशिंग मशीन", "फ्रिज", "एसी",
            "వాషింగ్ మెషిన్", "ഫാൻ", "ಫ್ಯಾನ್", "ventilador", "ventilateur"
        ],
        "beauty": [
            "beauty", "trimmer", "grooming", "hair dryer", "perfume", "soap", "facewash", "shampoo", "lipstick", "makeup", "sabun", "skincare",
            "அழகு", "ட்ரிம்மர்", "சோப்பு", "साबुन", "ट्रिमर", "परफ्यूम", "मेकअप", "சబ్బు", "സോപ്പ്",
            "belleza", "parfum", "savon"
        ],
        "toys": [
            "toy", "toys", "lego", "plush", "kids", "doll", "game", "hot wheels", "puzzle", "khilona", "khilone", "gudiya",
            "பொம்மை", "விளையாட்டு பொருள்", "खिलौना", "खिलौने", "गुड़िया", "బొమ్మ", "കളിപ്പാട്ടം", "খেলনা",
            "juguete", "jouet", "spielzeug"
        ],
        "furniture": [
            "furniture", "chair", "office chair", "desk", "standing desk", "table", "bookshelf", "sofa", "kursi",
            "நாற்காலி", "மேசை", "மரச்சாமான்கள்", "कुर्सी", "मेज", "सोफा", "ఫర్నిచర్", "കസേര", "ಮೇಜು",
            "muebles", "silla", "chaise"
        ],
        "sports": [
            "sports", "fitness", "yoga", "gym", "dumbbell", "badminton", "racket", "football", "cricket", "exercise",
            "உடற்பயிற்சி", "விளையாட்டு", "कसरत", "जिम", "వ్యాయామం", "കായിക", "deportes", "sport"
        ],
        "accessories": [
            "accessories", "charger", "gan charger", "hub", "dock", "usb-c dock", "desk mat", "mousepad", "power bank", "sunglasses", "chashma", "chasma", "kannadi", "kannaadi", "kallajodu",
            "சார்ஜர்", "கண்ணாடி", "चश्मा", "पावर बैंक", "चार्जर", "సన్గ్లాసెస్", "కళ్లద్దాలు", "കണ്ണട", "cargador", "chargeur"
        ],
        "decor": [
            "decor", "balloon", "balloons", "arch kit", "party decor", "birthday decoration", "lights", "led strip", "fairy lights", "lamp", "diya",
            "பலூன்", "அலங்காரம்", "விளக்கு", "गुब्बारा", "सजावट", "लाइट्स", "दीया", "బెలూన్", "അലങ്കാരം", "decoración"
        ],
        "groceries": [
            "groceries", "grocery", "pet food", "dog food", "cat food", "tea", "coffee", "oats", "chai", "biscuit",
            "மளிகை", "தேநீர்", "काफी", "चाय", "दाल", "कॉफी", "চা", "comida para mascotas"
        ]
    }

    def resolve_category(self, query: str) -> Optional[str]:
        q_clean = query.lower().strip()
        for cat, aliases in self.CATEGORY_ALIASES.items():
            if any(alias in q_clean for alias in aliases):
                return cat
        return None

    def get_canonical_name(self, category: str) -> str:
        return self.CANONICAL_CATEGORIES.get(category.lower(), category.title())

product_alias_service = ProductAliasService()
