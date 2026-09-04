import json
import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
try:
    from backend.models import Product
except (ImportError, ModuleNotFoundError):
    from models import Product

SEED_PRODUCTS = [
    {
        "product_id": "HP001",
        "name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
        "brand": "Sony",
        "description": "Industry-leading noise cancellation with 8 mics, Auto NC Optimizer, 30hr battery, LDAC Hi-Res audio, and speak-to-chat.",
        "category": "headphones",
        "price": 24990.0,
        "original_price": 29990.0,
        "discount": 17.0,
        "inventory": 35,
        "rating": 4.9,
        "review_count": 1420,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "Industry Leading Active Noise Cancelling",
            "30-Hour Battery Life",
            "Speak-to-Chat & Quick Attention",
            "Multipoint Bluetooth 5.2"
        ],
        "tags": [
            "headphones",
            "wireless",
            "anc",
            "noise-cancelling",
            "sony",
            "premium",
            "travel",
            "audio"
        ],
        "compatible_products": [
            "ACC001",
            "ACC002"
        ],
        "upsell_products": [
            "HP003"
        ],
        "cross_sell_products": [
            "ACC001",
            "ACC002"
        ],
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "HP002",
        "name": "Bose QuietComfort 45 Bluetooth Wireless Headphones",
        "brand": "Bose",
        "description": "Iconic quiet, comfort, and sound. TriPort acoustic architecture with Quiet and Aware modes, 24hr battery life.",
        "category": "headphones",
        "price": 19990.0,
        "original_price": 24990.0,
        "discount": 20.0,
        "inventory": 28,
        "rating": 4.85,
        "review_count": 980,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "Acoustic Noise Cancelling",
            "Plush Synthetic Leather Cushions",
            "Aware Mode for Transparency",
            "24-Hour Battery with Fast USB-C"
        ],
        "tags": [
            "headphones",
            "wireless",
            "anc",
            "bose",
            "comfort",
            "travel",
            "meetings"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "HP001"
        ],
        "cross_sell_products": [
            "ACC001",
            "ACC004"
        ],
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "HP003",
        "name": "Sennheiser Momentum 4 Wireless Studio Headphones",
        "brand": "Sennheiser",
        "description": "Audiophile-grade 42mm transducer system with 60-hour ultra battery life, adaptive ANC, and customizable sound EQ.",
        "category": "headphones",
        "price": 26990.0,
        "original_price": 34990.0,
        "discount": 23.0,
        "inventory": 22,
        "rating": 4.88,
        "review_count": 760,
        "delivery_days": 1,
        "margin": 0.34,
        "features": [
            "60-Hour Battery Life",
            "42mm Audiophile Transducers",
            "Adaptive Noise Cancellation",
            "aptX Adaptive HD Codec Support"
        ],
        "tags": [
            "headphones",
            "wireless",
            "sennheiser",
            "audiophile",
            "studio",
            "anc",
            "premium"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "HP001"
        ],
        "cross_sell_products": [
            "ACC001",
            "ACC008"
        ],
        "image_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "HP004",
        "name": "Audio-Technica ATH-M50x Professional Studio Headphones",
        "brand": "Audio-Technica",
        "description": "Critically acclaimed sonic performance praised by top audio engineers with 45mm large-aperture drivers.",
        "category": "headphones",
        "price": 13490.0,
        "original_price": 17500.0,
        "discount": 23.0,
        "inventory": 40,
        "rating": 4.92,
        "review_count": 3200,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Proprietary 45mm Large-Aperture Drivers",
            "90\u00b0 Swiveling Earcups",
            "Detachable Cables Included",
            "Sound Isolation in Loud Environments"
        ],
        "tags": [
            "headphones",
            "wired",
            "studio",
            "audio-technica",
            "music production",
            "podcast",
            "editing"
        ],
        "compatible_products": [
            "ACC002"
        ],
        "upsell_products": [
            "HP003"
        ],
        "cross_sell_products": [
            "ACC002",
            "ACC008"
        ],
        "image_url": "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "HP005",
        "name": "JBL Tune 770NC Wireless Over-Ear Active Noise Cancelling Headphones",
        "brand": "JBL",
        "description": "Adaptive Noise Cancelling with Smart Ambient, Pure Bass Sound, 70-hour battery, and speed charge.",
        "category": "headphones",
        "price": 5999.0,
        "original_price": 9999.0,
        "discount": 40.0,
        "inventory": 65,
        "rating": 4.65,
        "review_count": 1850,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "Adaptive Noise Cancelling with Smart Ambient",
            "JBL Pure Bass Sound Architecture",
            "Up to 70 Hours Battery Life",
            "Hands-Free Calls with VoiceAware"
        ],
        "tags": [
            "headphones",
            "wireless",
            "jbl",
            "anc",
            "bass",
            "under 6000",
            "budget anc"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "HP002"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1545127398-14699f92334b?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "HP006",
        "name": "boAt Rockerz 550 Over-Ear Bluetooth Wireless Headphones",
        "brand": "boAt",
        "description": "50mm dynamic drivers, physical noise isolation, 20 hours playback, and plush ergonomic comfort cushions.",
        "category": "headphones",
        "price": 1799.0,
        "original_price": 4999.0,
        "discount": 64.0,
        "inventory": 120,
        "rating": 4.52,
        "review_count": 4500,
        "delivery_days": 1,
        "margin": 0.42,
        "features": [
            "50mm Dynamic Sound Drivers",
            "20-Hour Playback Time",
            "Soft-Cushioned Earcups",
            "Dual Mode: Wireless & AUX Support"
        ],
        "tags": [
            "headphones",
            "wireless",
            "boat",
            "budget",
            "under 2000",
            "bass",
            "gift"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "HP005"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "HP007",
        "name": "Marshall Major IV Wireless Bluetooth On-Ear Headphones",
        "brand": "Marshall",
        "description": "80+ solid hours of wireless playtime, custom-tuned dynamic drivers, wireless charging, and iconic vintage rock design.",
        "category": "headphones",
        "price": 12999.0,
        "original_price": 14999.0,
        "discount": 13.0,
        "inventory": 30,
        "rating": 4.82,
        "review_count": 1100,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "80+ Hours of Wireless Playtime",
            "Custom-Tuned Dynamic Drivers",
            "Wireless Qi Charging Capable",
            "Multi-Directional Control Knob"
        ],
        "tags": [
            "headphones",
            "wireless",
            "marshall",
            "rock",
            "vintage",
            "bass",
            "style"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "HP002"
        ],
        "cross_sell_products": [
            "ACC001",
            "BAG007"
        ],
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "HP008",
        "name": "Beats Studio Pro Premium Wireless Noise Cancelling Headphones",
        "brand": "Beats",
        "description": "Custom acoustic platform delivering rich, immersive sound, Personalized Spatial Audio with dynamic head tracking, and lossless USB-C audio.",
        "category": "headphones",
        "price": 29900.0,
        "original_price": 34900.0,
        "discount": 14.0,
        "inventory": 18,
        "rating": 4.76,
        "review_count": 620,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Personalized Spatial Audio with Head Tracking",
            "Fully Adaptive Active Noise Cancelling",
            "Lossless Audio via USB-C",
            "Up to 40 Hours of Battery Life"
        ],
        "tags": [
            "headphones",
            "wireless",
            "beats",
            "apple",
            "anc",
            "spatial audio",
            "premium"
        ],
        "compatible_products": [
            "ACC001",
            "PH002"
        ],
        "upsell_products": [
            "HP001"
        ],
        "cross_sell_products": [
            "ACC001",
            "BAG001"
        ],
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "HP009",
        "name": "Sony WH-CH520 Lightweight Wireless Bluetooth Headphones",
        "brand": "Sony",
        "description": "Up to 50-hour battery life, DSEE sound upscaling, multipoint connection, and crystal clear hands-free calls.",
        "category": "headphones",
        "price": 3990.0,
        "original_price": 4990.0,
        "discount": 20.0,
        "inventory": 95,
        "rating": 4.7,
        "review_count": 3800,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "50-Hour Mega Battery Life",
            "DSEE High Frequency Audio Restoration",
            "Multipoint Dual Device Pairing",
            "Lightweight 147g Ergonomic Build"
        ],
        "tags": [
            "headphones",
            "wireless",
            "sony",
            "budget",
            "under 5000",
            "work",
            "calling",
            "gift"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "HP005"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "EB001",
        "name": "Apple AirPods Pro (2nd Generation with MagSafe USB-C Case)",
        "brand": "Apple",
        "description": "Up to 2x more Active Noise Cancellation, Adaptive Audio, Transparency mode, and Personalized Spatial Audio with head tracking.",
        "category": "earbuds",
        "price": 20990.0,
        "original_price": 24900.0,
        "discount": 16.0,
        "inventory": 50,
        "rating": 4.92,
        "review_count": 3100,
        "delivery_days": 1,
        "margin": 0.22,
        "features": [
            "H2 Apple Silicon Chip",
            "Adaptive Audio & Transparency",
            "Precision Finding MagSafe Case",
            "IP54 Dust & Sweat Resistant"
        ],
        "tags": [
            "earbuds",
            "headphones",
            "apple",
            "airpods",
            "wireless",
            "anc",
            "premium",
            "iphone"
        ],
        "compatible_products": [
            "PH002",
            "LP001"
        ],
        "upsell_products": [
            "HP001"
        ],
        "cross_sell_products": [
            "ACC001",
            "ACC004"
        ],
        "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "EB002",
        "name": "Sony WF-1000XM5 True Wireless Noise Cancelling Earbuds",
        "brand": "Sony",
        "description": "Best noise canceling with dual processors, dynamic driver X for wide frequency reproduction, and bone conduction sensors.",
        "category": "earbuds",
        "price": 19990.0,
        "original_price": 29990.0,
        "discount": 33.0,
        "inventory": 32,
        "rating": 4.86,
        "review_count": 1250,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Dual Feedback Microphones with Integrated Processor V2",
            "Dynamic Driver X Audio Architecture",
            "AI Noise Reduction Algorithm",
            "IPX4 Water Resistance"
        ],
        "tags": [
            "earbuds",
            "wireless",
            "sony",
            "anc",
            "audiophile",
            "hi-res",
            "travel"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "HP001"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "EB003",
        "name": "Samsung Galaxy Buds2 Pro True Wireless Earbuds with ANC",
        "brand": "Samsung",
        "description": "24-bit Hi-Fi audio sound quality, intelligent 3-mic active noise cancellation, and seamless 360 audio.",
        "category": "earbuds",
        "price": 12999.0,
        "original_price": 17999.0,
        "discount": 28.0,
        "inventory": 45,
        "rating": 4.78,
        "review_count": 1900,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "24-bit Hi-Fi Audio Stream",
            "Intelligent 3-Mic High SNR ANC",
            "360 Audio with Direct Multi-Channel",
            "IPX7 Water Resistance"
        ],
        "tags": [
            "earbuds",
            "wireless",
            "samsung",
            "anc",
            "galaxy",
            "calling",
            "sports"
        ],
        "compatible_products": [
            "PH001",
            "WAT002"
        ],
        "upsell_products": [
            "EB002"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "EB004",
        "name": "OnePlus Nord Buds 2 True Wireless In-Ear Earbuds",
        "brand": "OnePlus",
        "description": "25dB Active Noise Cancellation with BassWave algorithm, 36hr playback, IP55 water resistance, fast charging.",
        "category": "earbuds",
        "price": 2499.0,
        "original_price": 3299.0,
        "discount": 24.0,
        "inventory": 85,
        "rating": 4.65,
        "review_count": 2400,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "25dB Active Noise Cancellation",
            "BassWave Dynamic Enhancement",
            "36-Hour Total Playback",
            "IP55 Water & Sweat Resistance"
        ],
        "tags": [
            "earbuds",
            "headphones",
            "budget",
            "wireless",
            "oneplus",
            "anc",
            "under 3000",
            "under 5000"
        ],
        "compatible_products": [
            "PH004",
            "ACC001"
        ],
        "upsell_products": [
            "EB003"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "EB005",
        "name": "Nothing Ear (2) Hi-Res Audio Dual-Chamber Wireless Earbuds",
        "brand": "Nothing",
        "description": "Iconic transparent design with personalized active noise cancellation up to 40dB, 11.6mm custom driver, and Dual Connection.",
        "category": "earbuds",
        "price": 8999.0,
        "original_price": 12999.0,
        "discount": 31.0,
        "inventory": 40,
        "rating": 4.75,
        "review_count": 1350,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "Personalized Sound Profile & ANC",
            "LHDC 5.0 Hi-Res Audio Certified",
            "Dual Chamber Acoustic Architecture",
            "IP54 Buds / IP55 Case Rating"
        ],
        "tags": [
            "earbuds",
            "wireless",
            "nothing",
            "anc",
            "transparent",
            "design",
            "under 10000"
        ],
        "compatible_products": [
            "PH006",
            "ACC001"
        ],
        "upsell_products": [
            "EB001"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "EB006",
        "name": "Jabra Elite 8 Active Ultra-Rugged Waterproof Sports Earbuds",
        "brand": "Jabra",
        "description": "Tested to military standards for ruggedness with ShakeGrip technology, Adaptive Hybrid ANC, and Dolby Audio.",
        "category": "earbuds",
        "price": 14999.0,
        "original_price": 19999.0,
        "discount": 25.0,
        "inventory": 25,
        "rating": 4.82,
        "review_count": 820,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "IP68 Dustproof and Waterproof Rating",
            "Jabra ShakeGrip Fit Technology",
            "Adaptive Hybrid Active Noise Cancellation",
            "Dolby Spatial Audio Sound"
        ],
        "tags": [
            "earbuds",
            "wireless",
            "jabra",
            "sports",
            "running",
            "gym",
            "waterproof",
            "rugged"
        ],
        "compatible_products": [
            "WAT003",
            "ACC001"
        ],
        "upsell_products": [
            "EB001"
        ],
        "cross_sell_products": [
            "ACC001",
            "SH001"
        ],
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "EB007",
        "name": "Realme Buds Air 5 Pro Dual-Driver 50dB ANC Wireless Earbuds",
        "brand": "Realme",
        "description": "RealBoost dual coaxial drivers (11mm bass + 6mm micro-planar tweeter) with 50dB deep active noise cancellation.",
        "category": "earbuds",
        "price": 4499.0,
        "original_price": 7999.0,
        "discount": 44.0,
        "inventory": 75,
        "rating": 4.68,
        "review_count": 2100,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "50dB Deep Active Noise Cancellation",
            "Dual Coaxial Acoustic Drivers",
            "LDAC Hi-Res Audio Codec",
            "40 Hours Extended Battery Life"
        ],
        "tags": [
            "earbuds",
            "wireless",
            "realme",
            "anc",
            "budget",
            "under 5000",
            "bass"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "EB005"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "EB008",
        "name": "Anker Soundcore Liberty 4 NC Wireless Earbuds with 98.5% Noise Reduction",
        "brand": "Anker",
        "description": "Adaptive ANC 2.0 real-time ear canal calibration, 11mm custom tuned drivers, and wireless charging case.",
        "category": "earbuds",
        "price": 6999.0,
        "original_price": 9999.0,
        "discount": 30.0,
        "inventory": 55,
        "rating": 4.74,
        "review_count": 1600,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "Adaptive ANC 2.0 Noise Isolation",
            "11mm Custom Tuned Drivers",
            "50-Hour Playtime with Case",
            "Wireless Qi Charging Capable"
        ],
        "tags": [
            "earbuds",
            "wireless",
            "anker",
            "soundcore",
            "anc",
            "under 7000",
            "travel"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "EB002"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "EB009",
        "name": "boAt Airdopes 141 True Wireless Bluetooth Earbuds",
        "brand": "boAt",
        "description": "42 hours total playback, ENx environment noise cancellation tech for calls, ASAP fast charge, and IPX4 sweat resistance.",
        "category": "earbuds",
        "price": 1099.0,
        "original_price": 4490.0,
        "discount": 75.0,
        "inventory": 180,
        "rating": 4.45,
        "review_count": 9500,
        "delivery_days": 1,
        "margin": 0.45,
        "features": [
            "42-Hour Total Battery Life",
            "ENx Clear Voice Technology",
            "ASAP Charge: 5 Mins = 75 Mins",
            "IPX4 Sweat and Splash Proof"
        ],
        "tags": [
            "earbuds",
            "wireless",
            "boat",
            "budget",
            "under 1500",
            "calling",
            "gift"
        ],
        "compatible_products": [
            "ACC001"
        ],
        "upsell_products": [
            "EB004"
        ],
        "cross_sell_products": [
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "LP001",
        "name": "Apple MacBook Pro 16\" (M3 Pro 12-Core, 18GB Unified Memory, 512GB SSD, Space Black)",
        "brand": "Apple",
        "description": "Liquid Retina XDR display, up to 22 hours battery life, 1080p FaceTime HD camera, studio-quality three-mic array, six-speaker sound.",
        "category": "laptop",
        "price": 249900.0,
        "original_price": 269900.0,
        "discount": 7.0,
        "inventory": 12,
        "rating": 4.95,
        "review_count": 580,
        "delivery_days": 1,
        "margin": 0.18,
        "features": [
            "Apple M3 Pro 12-Core CPU / 18-Core GPU",
            "16.2-inch Liquid Retina XDR ProMotion 120Hz",
            "18GB Unified High-Speed Memory",
            "22-Hour Battery Life"
        ],
        "tags": [
            "laptop",
            "apple",
            "macbook",
            "coding",
            "developer",
            "m3",
            "premium",
            "creator"
        ],
        "compatible_products": [
            "ACC003",
            "MON001",
            "MS001",
            "BAG001"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "ACC003",
            "MON001",
            "BAG001"
        ],
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "LP002",
        "name": "Dell XPS 15 9530 (13th Gen Intel Core i7-13700H, RTX 4060, 32GB DDR5, 1TB NVMe, OLED 3.5K Touch)",
        "brand": "Dell",
        "description": "Precision crafted with CNC machined aluminum and carbon fiber palm rest, 15.6\" 3.5K OLED InfinityEdge touch display.",
        "category": "laptop",
        "price": 184990.0,
        "original_price": 219990.0,
        "discount": 16.0,
        "inventory": 15,
        "rating": 4.88,
        "review_count": 420,
        "delivery_days": 1,
        "margin": 0.22,
        "features": [
            "Intel Core i7-13700H (14 Cores, 5.0 GHz)",
            "NVIDIA GeForce RTX 4060 8GB GDDR6",
            "15.6-inch 3.5K (3456x2160) OLED Touch",
            "32GB Dual-Channel DDR5 4800MHz"
        ],
        "tags": [
            "laptop",
            "dell",
            "xps",
            "coding",
            "creator",
            "oled",
            "intel",
            "rtx",
            "under 200000"
        ],
        "compatible_products": [
            "ACC003",
            "MON002",
            "MS001",
            "BAG001"
        ],
        "upsell_products": [
            "LP001"
        ],
        "cross_sell_products": [
            "ACC003",
            "MS001",
            "BAG001"
        ],
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "LP003",
        "name": "Lenovo ThinkPad X1 Carbon Gen 11 (Intel Core i7-1365U vPro, 16GB LPDDR5, 512GB PCIe Gen4 SSD)",
        "brand": "Lenovo",
        "description": "Legendary ultra-lightweight carbon fiber chassis weighing just 1.12kg, military-spec MIL-STD-810H durability, and world-class ThinkPad keyboard.",
        "category": "laptop",
        "price": 149990.0,
        "original_price": 185000.0,
        "discount": 19.0,
        "inventory": 20,
        "rating": 4.9,
        "review_count": 610,
        "delivery_days": 1,
        "margin": 0.25,
        "features": [
            "Ultra-Light 1.12kg Carbon Fiber Chassis",
            "Iconic Spill-Resistant ThinkPad Keyboard & TrackPoint",
            "14-inch 2.8K OLED Anti-Glare 400 nits Display",
            "FHD IR Web Camera with Privacy Shutter"
        ],
        "tags": [
            "laptop",
            "lenovo",
            "thinkpad",
            "business",
            "coding",
            "developer",
            "lightweight",
            "under 150000"
        ],
        "compatible_products": [
            "ACC002",
            "KB001",
            "MS001",
            "BAG002"
        ],
        "upsell_products": [
            "LP002"
        ],
        "cross_sell_products": [
            "MS001",
            "BAG002"
        ],
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "LP004",
        "name": "ASUS ROG Zephyrus G14 (AMD Ryzen 9 8945HS, RTX 4070, 32GB LPDDR5X, 1TB SSD, 3K 120Hz OLED)",
        "brand": "ASUS",
        "description": "Unbelievable gaming & AI processing in an ultra-thin 1.59cm CNC aluminum unibody with AniMe Matrix LED lid.",
        "category": "laptop",
        "price": 169990.0,
        "original_price": 199990.0,
        "discount": 15.0,
        "inventory": 18,
        "rating": 4.86,
        "review_count": 390,
        "delivery_days": 1,
        "margin": 0.24,
        "features": [
            "AMD Ryzen 9 8945HS with Ryzen AI Engine",
            "NVIDIA GeForce RTX 4070 8GB GDDR6",
            "14-inch 3K (2880x1800) 120Hz ROG Nebula OLED",
            "32GB High-Speed LPDDR5X Memory"
        ],
        "tags": [
            "laptop",
            "asus",
            "rog",
            "gaming",
            "ai",
            "rtx",
            "oled",
            "compact gaming"
        ],
        "compatible_products": [
            "MS003",
            "KB003",
            "ACC008"
        ],
        "upsell_products": [
            "LP001"
        ],
        "cross_sell_products": [
            "MS003",
            "KB003"
        ],
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "LP005",
        "name": "Apple MacBook Air 13\" (M2 8-Core CPU / 8-Core GPU, 8GB Unified, 256GB SSD, Starlight)",
        "brand": "Apple",
        "description": "Incredibly thin, fanless silent design with 13.6\" Liquid Retina display, MagSafe 3 charging, 1080p FaceTime HD camera, 18hr battery.",
        "category": "laptop",
        "price": 89900.0,
        "original_price": 99900.0,
        "discount": 10.0,
        "inventory": 40,
        "rating": 4.91,
        "review_count": 2800,
        "delivery_days": 1,
        "margin": 0.2,
        "features": [
            "Apple M2 Silicon Chip",
            "Fanless 100% Silent Thermal Architecture",
            "13.6-inch Liquid Retina Display with True Tone",
            "Up to 18 Hours Battery Life"
        ],
        "tags": [
            "laptop",
            "apple",
            "macbook air",
            "student",
            "lightweight",
            "coding",
            "under 90000"
        ],
        "compatible_products": [
            "ACC002",
            "MS001",
            "BAG004"
        ],
        "upsell_products": [
            "LP001"
        ],
        "cross_sell_products": [
            "ACC002",
            "BAG004"
        ],
        "image_url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "LP006",
        "name": "HP Pavilion Plus 14 for Coding & Productivity (Intel Core i5-13500H, 16GB LPDDR5, 512GB SSD)",
        "brand": "HP",
        "description": "Best budget laptop for coding under 60000 featuring a crisp 14-inch 2.2K IPS display, 5MP IR camera with AI noise reduction.",
        "category": "laptop",
        "price": 58990.0,
        "original_price": 74990.0,
        "discount": 21.0,
        "inventory": 60,
        "rating": 4.72,
        "review_count": 1450,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Intel Core i5-13500H (12 Cores, 16 Threads)",
            "14.0-inch 2.2K (2240x1400) IPS Anti-Glare Display",
            "16GB Dual-Channel LPDDR5 5200MHz RAM",
            "Backlit Keyboard & Fingerprint Reader"
        ],
        "tags": [
            "laptop",
            "hp",
            "coding",
            "developer",
            "budget",
            "under 60000",
            "under 60k",
            "best laptop for coding under \u20b960000"
        ],
        "compatible_products": [
            "MS001",
            "ACC002",
            "BAG002"
        ],
        "upsell_products": [
            "LP005"
        ],
        "cross_sell_products": [
            "MS001",
            "BAG002"
        ],
        "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "LP007",
        "name": "ASUS TUF Gaming F15 (Intel Core i5-12500H, RTX 3050, 16GB DDR4, 512GB SSD, 144Hz FHD)",
        "brand": "ASUS",
        "description": "High value gaming and development machine with military-grade toughness, 144Hz IPS display, and dual fans with self-cleaning tech.",
        "category": "laptop",
        "price": 54990.0,
        "original_price": 79990.0,
        "discount": 31.0,
        "inventory": 50,
        "rating": 4.68,
        "review_count": 2100,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "Intel Core i5-12500H (12 Cores)",
            "NVIDIA GeForce RTX 3050 4GB GPU",
            "15.6-inch FHD 144Hz IPS Anti-Glare Display",
            "RGB Backlit Keyboard with Highlighted WASD"
        ],
        "tags": [
            "laptop",
            "asus",
            "tuf",
            "gaming",
            "coding",
            "rtx",
            "budget gaming",
            "under 60000"
        ],
        "compatible_products": [
            "MS002",
            "KB004",
            "BAG002"
        ],
        "upsell_products": [
            "LP004"
        ],
        "cross_sell_products": [
            "MS002",
            "KB004"
        ],
        "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "LP008",
        "name": "Acer Swift Go 14 Thin & Light OLED (Intel Core i5-13500H, 16GB LPDDR5, 512GB SSD, 2.8K 90Hz OLED)",
        "brand": "Acer",
        "description": "Stunning 2.8K OLED display with 100% DCI-P3 color gamut, dual TwinAir fans, and 1440p QHD webcam in an aluminum unibody.",
        "category": "laptop",
        "price": 59990.0,
        "original_price": 79999.0,
        "discount": 25.0,
        "inventory": 42,
        "rating": 4.75,
        "review_count": 1180,
        "delivery_days": 1,
        "margin": 0.26,
        "features": [
            "14.0-inch 2.8K (2880x1800) 90Hz OLED Display",
            "Intel Core i5-13500H Processor",
            "Dual Thunderbolt 4 Type-C Ports",
            "Lightweight 1.25kg Sleek Metal Chassis"
        ],
        "tags": [
            "laptop",
            "acer",
            "oled",
            "coding",
            "creator",
            "under 60000",
            "under 60k",
            "thin light"
        ],
        "compatible_products": [
            "MS001",
            "ACC002",
            "BAG004"
        ],
        "upsell_products": [
            "LP003"
        ],
        "cross_sell_products": [
            "MS001",
            "ACC002"
        ],
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "LP009",
        "name": "Lenovo Legion Pro 5 (AMD Ryzen 7 7745HX, RTX 4070 140W, 32GB DDR5, 1TB SSD, 16\" WQXGA 240Hz)",
        "brand": "Lenovo",
        "description": "Ultimate esports performance with AI Tuning Engine, Legion Coldfront 5.0 thermal technology, and TrueStrike RGB keyboard.",
        "category": "laptop",
        "price": 154990.0,
        "original_price": 189990.0,
        "discount": 18.0,
        "inventory": 14,
        "rating": 4.9,
        "review_count": 480,
        "delivery_days": 1,
        "margin": 0.22,
        "features": [
            "AMD Ryzen 7 7745HX (8 Cores, 16 Threads)",
            "NVIDIA GeForce RTX 4070 8GB GDDR6 140W TGP",
            "16.0-inch WQXGA (2560x1600) 240Hz 500nits IPS",
            "32GB Dual-Channel DDR5 5200MHz RAM"
        ],
        "tags": [
            "laptop",
            "lenovo",
            "legion",
            "gaming",
            "esports",
            "rtx 4070",
            "high performance"
        ],
        "compatible_products": [
            "MS003",
            "KB003",
            "MON003"
        ],
        "upsell_products": [
            "LP001"
        ],
        "cross_sell_products": [
            "MS003",
            "KB003"
        ],
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PH001",
        "name": "Samsung Galaxy S24 Ultra 5G (Titanium Gray, 12GB RAM, 256GB Storage)",
        "brand": "Samsung",
        "description": "Galaxy AI capabilities, built-in S Pen, 200MP camera system with 5x optical zoom, and Snapdragon 8 Gen 3 for Galaxy.",
        "category": "phone",
        "price": 129999.0,
        "original_price": 139999.0,
        "discount": 7.0,
        "inventory": 20,
        "rating": 4.93,
        "review_count": 1850,
        "delivery_days": 1,
        "margin": 0.18,
        "features": [
            "200MP Quad Telephoto Camera System",
            "Galaxy AI: Live Translate & Circle to Search",
            "6.8-inch Dynamic AMOLED 2X 120Hz 2600nits Display",
            "Titanium Frame with Gorilla Glass Armor"
        ],
        "tags": [
            "phone",
            "smartphone",
            "samsung",
            "galaxy",
            "5g",
            "flagship",
            "camera",
            "ai",
            "stylus",
            "s-pen"
        ],
        "compatible_products": [
            "WAT002",
            "EB003",
            "ACC004"
        ],
        "upsell_products": [
            "PH002"
        ],
        "cross_sell_products": [
            "WAT002",
            "EB003"
        ],
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PH002",
        "name": "Apple iPhone 15 Pro (Natural Titanium, 128GB Storage)",
        "brand": "Apple",
        "description": "Forged in aerospace-grade titanium with A17 Pro chip, Action button, customizable 48MP main camera system, and USB-C with USB 3 speeds.",
        "category": "phone",
        "price": 134900.0,
        "original_price": 144900.0,
        "discount": 7.0,
        "inventory": 25,
        "rating": 4.94,
        "review_count": 3200,
        "delivery_days": 1,
        "margin": 0.16,
        "features": [
            "Aerospace-Grade Titanium Design",
            "A17 Pro Chip with 6-Core GPU",
            "48MP Main Camera with 3x Telephoto",
            "Customizable Action Button & USB-C USB 3"
        ],
        "tags": [
            "phone",
            "smartphone",
            "apple",
            "iphone",
            "iphone 15 pro",
            "5g",
            "camera",
            "premium",
            "titanium"
        ],
        "compatible_products": [
            "EB001",
            "WAT001",
            "ACC004"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "EB001",
            "WAT001"
        ],
        "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PH003",
        "name": "Google Pixel 8 Pro (Obsidian, 12GB RAM, 128GB Storage)",
        "brand": "Google",
        "description": "Google Tensor G3 chip with advanced Google AI, best-in-class computational photography with 50MP main and 5x optical telephoto lens.",
        "category": "phone",
        "price": 89999.0,
        "original_price": 106999.0,
        "discount": 16.0,
        "inventory": 30,
        "rating": 4.88,
        "review_count": 1420,
        "delivery_days": 1,
        "margin": 0.22,
        "features": [
            "Google Tensor G3 Silicon with AI Engine",
            "50MP Triple Camera with Best Take & Magic Editor",
            "6.7-inch Super Actua LTPO OLED 120Hz Display",
            "7 Years of Guaranteed OS & Security Updates"
        ],
        "tags": [
            "phone",
            "smartphone",
            "google",
            "pixel",
            "5g",
            "camera",
            "ai",
            "computational photography",
            "good camera",
            "phones with good camera"
        ],
        "compatible_products": [
            "EB002",
            "WAT005",
            "ACC001"
        ],
        "upsell_products": [
            "PH001"
        ],
        "cross_sell_products": [
            "EB002",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PH004",
        "name": "OnePlus 12 5G (Silky Black, 16GB RAM, 512GB Storage)",
        "brand": "OnePlus",
        "description": "Snapdragon 8 Gen 3, 4th Gen Hasselblad Camera for Mobile, 2K 120Hz ProXDR display, 5400mAh battery with 100W SUPERVOOC charging.",
        "category": "phone",
        "price": 69999.0,
        "original_price": 79999.0,
        "discount": 12.0,
        "inventory": 35,
        "rating": 4.84,
        "review_count": 1650,
        "delivery_days": 1,
        "margin": 0.24,
        "features": [
            "Snapdragon 8 Gen 3 Processor",
            "4th Gen Hasselblad Camera System",
            "5400mAh Battery with 100W SUPERVOOC Fast Charge",
            "6.82-inch 2K 120Hz ProXDR Display with Aqua Touch"
        ],
        "tags": [
            "phone",
            "smartphone",
            "oneplus",
            "5g",
            "fast charging",
            "hasselblad",
            "camera",
            "under 70000"
        ],
        "compatible_products": [
            "EB004",
            "WAT008",
            "ACC001"
        ],
        "upsell_products": [
            "PH003"
        ],
        "cross_sell_products": [
            "EB004",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PH005",
        "name": "Xiaomi Redmi Note 13 Pro+ 5G (Fusion Purple, 12GB RAM, 256GB Storage)",
        "brand": "Xiaomi",
        "description": "200MP OIS camera with 4x lossless zoom, 1.5K 120Hz 3D curved AMOLED display, IP68 water resistance, and 120W HyperCharge.",
        "category": "phone",
        "price": 31999.0,
        "original_price": 37999.0,
        "discount": 16.0,
        "inventory": 65,
        "rating": 4.7,
        "review_count": 3400,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "200MP Ultra-Clear OIS Camera",
            "120W HyperCharge (0 to 100% in 19 mins)",
            "1.5K 120Hz 3D Curved AMOLED Display",
            "IP68 Water and Dust Resistance"
        ],
        "tags": [
            "phone",
            "smartphone",
            "xiaomi",
            "redmi",
            "5g",
            "200mp",
            "camera",
            "fast charge",
            "under 35000",
            "good camera"
        ],
        "compatible_products": [
            "EB007",
            "WAT009",
            "ACC001"
        ],
        "upsell_products": [
            "PH004"
        ],
        "cross_sell_products": [
            "EB007",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PH006",
        "name": "Nothing Phone (2) (Dark Grey, 12GB RAM, 256GB Storage)",
        "brand": "Nothing",
        "description": "Glyph Interface with customizable LED lighting sequences, 50MP dual rear camera, Snapdragon 8+ Gen 1, and clean Nothing OS 2.5.",
        "category": "phone",
        "price": 39999.0,
        "original_price": 49999.0,
        "discount": 20.0,
        "inventory": 40,
        "rating": 4.76,
        "review_count": 1950,
        "delivery_days": 1,
        "margin": 0.26,
        "features": [
            "Iconic Glyph LED Interface",
            "Dual 50MP Sony IMX890 Main Camera System",
            "Snapdragon 8+ Gen 1 High Performance Chip",
            "6.7-inch LTPO OLED 120Hz Display"
        ],
        "tags": [
            "phone",
            "smartphone",
            "nothing",
            "glyph",
            "design",
            "5g",
            "under 40000"
        ],
        "compatible_products": [
            "EB005",
            "ACC001"
        ],
        "upsell_products": [
            "PH004"
        ],
        "cross_sell_products": [
            "EB005",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PH007",
        "name": "Vivo X100 Pro 5G with ZEISS APO Telephoto Camera (16GB RAM, 512GB Storage)",
        "brand": "Vivo",
        "description": "World-first ZEISS APO floating telephoto camera with 1-inch Sony IMX989 main sensor and MediaTek Dimensity 9300 flagship processor.",
        "category": "phone",
        "price": 89999.0,
        "original_price": 99999.0,
        "discount": 10.0,
        "inventory": 18,
        "rating": 4.91,
        "review_count": 780,
        "delivery_days": 1,
        "margin": 0.2,
        "features": [
            "ZEISS 1-Inch Main Camera Sensor + ZEISS APO Telephoto",
            "MediaTek Dimensity 9300 Flagship Processor",
            "5400mAh Battery with 100W FlashCharge",
            "V3 Dedicated 6nm Imaging Chip"
        ],
        "tags": [
            "phone",
            "smartphone",
            "vivo",
            "zeiss",
            "camera",
            "portrait",
            "good camera",
            "5g",
            "flagship camera"
        ],
        "compatible_products": [
            "EB002",
            "ACC001"
        ],
        "upsell_products": [
            "PH001"
        ],
        "cross_sell_products": [
            "EB002",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PH008",
        "name": "Motorola Edge 50 Pro 5G with AI Camera (12GB RAM, 256GB Storage, Luxe Lavender)",
        "brand": "Motorola",
        "description": "World's first Pantone validated camera & display, 50MP AI camera with 3x telephoto, 125W TurboPower charging, and IP68 underwater protection.",
        "category": "phone",
        "price": 31999.0,
        "original_price": 36999.0,
        "discount": 14.0,
        "inventory": 50,
        "rating": 4.73,
        "review_count": 2200,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Pantone Validated 50MP AI Camera System",
            "125W TurboPower Fast Charging (100% in 18 mins)",
            "6.7-inch 1.5K 144Hz 3D Curved pOLED Display",
            "IP68 Underwater Protection Rating"
        ],
        "tags": [
            "phone",
            "smartphone",
            "motorola",
            "5g",
            "ai camera",
            "pantone",
            "curved display",
            "under 35000",
            "good camera"
        ],
        "compatible_products": [
            "EB004",
            "ACC001"
        ],
        "upsell_products": [
            "PH004"
        ],
        "cross_sell_products": [
            "EB004",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PH009",
        "name": "Xiaomi Redmi 13C 5G (Starlight Black, 6GB RAM, 128GB Storage)",
        "brand": "Xiaomi",
        "description": "Affordable 5G smartphone with 50MP AI dual camera, MediaTek Dimensity 6100+ processor, and 5000mAh long-lasting battery.",
        "category": "phone",
        "price": 10499.0,
        "original_price": 13999.0,
        "discount": 25.0,
        "inventory": 110,
        "rating": 4.5,
        "review_count": 5600,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "MediaTek Dimensity 6100+ 5G Processor",
            "50MP AI Dual Rear Camera",
            "6.74-inch 90Hz Smooth Display with Gorilla Glass",
            "5000mAh Battery with 18W Fast Charging"
        ],
        "tags": [
            "phone",
            "smartphone",
            "redmi",
            "budget",
            "under 12000",
            "under 15000",
            "5g",
            "gift"
        ],
        "compatible_products": [
            "EB009",
            "ACC001"
        ],
        "upsell_products": [
            "PH005"
        ],
        "cross_sell_products": [
            "EB009",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "KB001",
        "name": "Mechanical Coding Keyboard (Tenkeyless)",
        "brand": "Keychron",
        "description": "Pro mechanical keyboard engineered for software engineers. Hot-swappable tactile switches, RGB per-key backlighting, Mac/Windows layout switch, and sound dampening foam.",
        "category": "keyboard",
        "price": 1499.0,
        "original_price": 2499.0,
        "discount": 40.0,
        "inventory": 85,
        "rating": 4.9,
        "review_count": 1200,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "Gateron Hot-Swappable Switches",
            "Tenkeyless 87-Key Compact Layout",
            "Double-Shot PBT Keycaps",
            "Wireless Bluetooth 5.1 & Type-C"
        ],
        "tags": [
            "keyboard",
            "mechanical",
            "coding",
            "wireless",
            "keychron",
            "tenkeyless",
            "rgb",
            "hot-swap",
            "developer"
        ],
        "compatible_products": [
            "MS001",
            "ACC001"
        ],
        "upsell_products": [
            "KB002"
        ],
        "cross_sell_products": [
            "MS001",
            "ACC001",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "KB002",
        "name": "Logitech MX Keys S Wireless Illuminated Keyboard (Low Profile, Smart Backlighting)",
        "brand": "Logitech",
        "description": "Master series fluid spherically-dished keystrokes, proximity sensors for smart illumination, Easy-Switch for 3 devices, USB-C.",
        "category": "keyboard",
        "price": 10995.0,
        "original_price": 13995.0,
        "discount": 21.0,
        "inventory": 45,
        "rating": 4.9,
        "review_count": 2400,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Spherically Dished Precision Keycaps",
            "Smart Proximity Sensor Backlighting",
            "Multi-Device Easy-Switch for 3 Devices",
            "Smart Actions Automation Macro Support"
        ],
        "tags": [
            "keyboard",
            "wireless",
            "logitech",
            "low profile",
            "silent",
            "coding",
            "office",
            "productivity"
        ],
        "compatible_products": [
            "MS001",
            "ACC007"
        ],
        "upsell_products": [
            "KB001"
        ],
        "cross_sell_products": [
            "MS001",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "KB003",
        "name": "Razer BlackWidow V4 Pro Mechanical Gaming Keyboard (Green Clicky Switches, Underglow)",
        "brand": "Razer",
        "description": "Razer Command Dial, 8 dedicated macro keys, magnetic plush leatherette wrist rest with underglow, Doubleshot ABS keycaps.",
        "category": "keyboard",
        "price": 18999.0,
        "original_price": 24999.0,
        "discount": 24.0,
        "inventory": 18,
        "rating": 4.86,
        "review_count": 640,
        "delivery_days": 1,
        "margin": 0.26,
        "features": [
            "Razer Command Dial with 8 Macro Keys",
            "Razer Green Clicky Mechanical Switches",
            "Magnetic Plush Wrist Rest with Chroma Underglow",
            "8000Hz HyperPolling Technology"
        ],
        "tags": [
            "keyboard",
            "mechanical",
            "razer",
            "gaming",
            "rgb",
            "macro",
            "clicky"
        ],
        "compatible_products": [
            "MS002",
            "ACC007"
        ],
        "upsell_products": [
            "KB001"
        ],
        "cross_sell_products": [
            "MS002",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "KB004",
        "name": "Royal Kludge RK84 Wireless 75% Mechanical Keyboard (Hot Swappable, Red Linear Switches)",
        "brand": "Royal Kludge",
        "description": "Versatile 3-mode connectivity (Bluetooth 5.0, 2.4GHz wireless, USB-C), 3750mAh battery, 2 built-in USB pass-through ports.",
        "category": "keyboard",
        "price": 4999.0,
        "original_price": 7999.0,
        "discount": 38.0,
        "inventory": 70,
        "rating": 4.78,
        "review_count": 1890,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "Triple Mode: 2.4GHz / Bluetooth / Type-C Wired",
            "Hot-Swappable 3-Pin / 5-Pin Switch Sockets",
            "3750mAh Large Capacity Battery",
            "2 Extra USB 2.0 Passthrough Ports"
        ],
        "tags": [
            "keyboard",
            "mechanical",
            "royal kludge",
            "rk84",
            "wireless",
            "budget",
            "under 5000",
            "coding",
            "75 percent"
        ],
        "compatible_products": [
            "MS004",
            "ACC007"
        ],
        "upsell_products": [
            "KB001"
        ],
        "cross_sell_products": [
            "MS004",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "KB005",
        "name": "NuPhy Air75 V2 Ultra-Slim Wireless Mechanical Keyboard (Gateron Low Profile Cowberry Switch)",
        "brand": "NuPhy",
        "description": "Ultra-thin 13.5mm profile, 1000Hz polling rate in 2.4G wireless, QMK/VIA support, PBT dye-sub keycaps, and customizable sidelights.",
        "category": "keyboard",
        "price": 11999.0,
        "original_price": 14999.0,
        "discount": 20.0,
        "inventory": 28,
        "rating": 4.88,
        "review_count": 720,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "Ultra-Slim 13.5mm Low-Profile Form Factor",
            "1000Hz Wireless Polling Rate",
            "Full QMK/VIA Key Mapping Support",
            "Coast PBT Ultra-Thin Dye-Sub Keycaps"
        ],
        "tags": [
            "keyboard",
            "mechanical",
            "nuphy",
            "low profile",
            "wireless",
            "mac",
            "travel",
            "developer"
        ],
        "compatible_products": [
            "MS001",
            "ACC007"
        ],
        "upsell_products": [
            "KB001"
        ],
        "cross_sell_products": [
            "MS001",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "KB006",
        "name": "Epomaker TH80 Pro 75% Hot Swappable RGB Mechanical Keyboard (Gateron Pro Yellow)",
        "brand": "Epomaker",
        "description": "Gasket-like structure with sound absorption EVA foams, rotary metal knob for volume control, programmable RGB backlighting.",
        "category": "keyboard",
        "price": 6999.0,
        "original_price": 9999.0,
        "discount": 30.0,
        "inventory": 45,
        "rating": 4.82,
        "review_count": 1200,
        "delivery_days": 1,
        "margin": 0.33,
        "features": [
            "Multi-Function Metal Media Knob",
            "Pre-Lubed Gateron Pro Yellow Linear Switches",
            "Triple-Layer Sound Absorbing EVA Foam",
            "Hot-Swappable South-Facing RGB PCB"
        ],
        "tags": [
            "keyboard",
            "mechanical",
            "epomaker",
            "th80",
            "rgb",
            "knob",
            "creamy sound",
            "under 7000"
        ],
        "compatible_products": [
            "MS004",
            "ACC007"
        ],
        "upsell_products": [
            "KB001"
        ],
        "cross_sell_products": [
            "MS004",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "KB007",
        "name": "Redragon K552 Kumara Tenkeyless Mechanical Gaming Keyboard (Outemu Blue Clicky Switches)",
        "brand": "Redragon",
        "description": "Compact 87-key space-saving design, solid aircraft-grade metal-ABS construction, rainbow LED backlighting, gold-plated USB.",
        "category": "keyboard",
        "price": 2299.0,
        "original_price": 3999.0,
        "discount": 43.0,
        "inventory": 90,
        "rating": 4.62,
        "review_count": 4100,
        "delivery_days": 1,
        "margin": 0.4,
        "features": [
            "Aircraft-Grade Aluminum & ABS Construction",
            "Dust-Proof Outemu Blue Clicky Switches",
            "Rainbow LED Backlighting Modes",
            "Full 87 Keys Anti-Ghosting 100% Conflict Free"
        ],
        "tags": [
            "keyboard",
            "mechanical",
            "redragon",
            "budget",
            "under 2500",
            "under 3000",
            "clicky",
            "tenkeyless",
            "keyboard under \u20b92k"
        ],
        "compatible_products": [
            "MS005",
            "ACC007"
        ],
        "upsell_products": [
            "KB004"
        ],
        "cross_sell_products": [
            "MS005",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "KB008",
        "name": "Ducky One 3 TKL Pure White Mechanical Keyboard (Cherry MX Silent Red Switches)",
        "brand": "Ducky",
        "description": "QUACK Mechanics design philosophy featuring dual-layer high-grade silicone dampening, authentic Cherry MX switches, and true PBT seamless keycaps.",
        "category": "keyboard",
        "price": 11499.0,
        "original_price": 13999.0,
        "discount": 18.0,
        "inventory": 20,
        "rating": 4.9,
        "review_count": 550,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Ducky QUACK Mechanics Acoustic Architecture",
            "Hot-Swappable with Kailh Yellow Sockets",
            "Cherry MX Silent Red Ultra-Quiet Switches",
            "Dual-Layer High-Grade Silicone Sound Pad"
        ],
        "tags": [
            "keyboard",
            "mechanical",
            "ducky",
            "silent",
            "coding",
            "cherry mx",
            "white aesthetic"
        ],
        "compatible_products": [
            "MS001",
            "ACC007"
        ],
        "upsell_products": [
            "KB001"
        ],
        "cross_sell_products": [
            "MS001",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "KB009",
        "name": "SteelSeries Apex Pro TKL Wireless 2023 (OmniPoint 2.0 Adjustable Actuation Magnetic Switches)",
        "brand": "SteelSeries",
        "description": "World's fastest keyboard with OmniPoint 2.0 magnetic switches adjustable from 0.2mm to 3.8mm actuation, OLED smart display, aircraft aluminum.",
        "category": "keyboard",
        "price": 24999.0,
        "original_price": 29999.0,
        "discount": 17.0,
        "inventory": 15,
        "rating": 4.88,
        "review_count": 490,
        "delivery_days": 1,
        "margin": 0.25,
        "features": [
            "OmniPoint 2.0 Magnetic Hall Effect Switches",
            "Adjustable Actuation from 0.2mm to 3.8mm",
            "OLED Smart Display for Settings & Game Info",
            "Quantum 2.0 Dual Wireless 2.4GHz + BT 5.0"
        ],
        "tags": [
            "keyboard",
            "mechanical",
            "steelseries",
            "rapid trigger",
            "hall effect",
            "esports",
            "gaming",
            "premium"
        ],
        "compatible_products": [
            "MS003",
            "ACC007"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "MS003",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MS001",
        "name": "Logitech MX Master 3S Wireless Performance Ergonomic Mouse (8K DPI, Quiet Clicks)",
        "brand": "Logitech",
        "description": "8,000 DPI track-on-glass optical sensor, MagSpeed electromagnetic scrolling (1,000 lines per second), Quiet Click switches, App-Specific customizations.",
        "category": "mouse",
        "price": 8995.0,
        "original_price": 10995.0,
        "discount": 18.0,
        "inventory": 50,
        "rating": 4.95,
        "review_count": 3400,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "8000 DPI Any-Surface Track-on-Glass Sensor",
            "MagSpeed Electromagnetic Scrolling",
            "90% Quieter Click Switches",
            "Easy-Switch Multi-Device Control (3 Devices)"
        ],
        "tags": [
            "mouse",
            "wireless",
            "logitech",
            "mx master",
            "ergonomic",
            "productivity",
            "coding",
            "developer"
        ],
        "compatible_products": [
            "KB001",
            "KB002",
            "ACC007"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "KB002",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MS002",
        "name": "Razer DeathAdder V3 Pro Ultra-Lightweight Wireless Ergonomic Gaming Mouse",
        "brand": "Razer",
        "description": "Ultra-lightweight 63g ergonomic design, Focus Pro 30K optical sensor, Gen-3 optical mouse switches, up to 90 hours battery life.",
        "category": "mouse",
        "price": 12999.0,
        "original_price": 15999.0,
        "discount": 19.0,
        "inventory": 30,
        "rating": 4.91,
        "review_count": 920,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Ultra-Lightweight 63g Ergonomic Body",
            "Focus Pro 30K Optical Sensor (99.8% Resolution Accuracy)",
            "Razer Optical Mouse Switches Gen-3 (90M Clicks)",
            "Razer HyperSpeed Wireless Connectivity"
        ],
        "tags": [
            "mouse",
            "wireless",
            "razer",
            "gaming",
            "esports",
            "ultra-light",
            "ergonomic"
        ],
        "compatible_products": [
            "KB003",
            "ACC007"
        ],
        "upsell_products": [
            "MS001"
        ],
        "cross_sell_products": [
            "KB003",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MS003",
        "name": "Logitech G PRO X SUPERLIGHT 2 Wireless Gaming Mouse (HERO 2 Sensor, 60g)",
        "brand": "Logitech",
        "description": "Next-gen 60g esports icon featuring HERO 2 sensor with 32,000 DPI and LIGHTFORCE hybrid optical-mechanical switches.",
        "category": "mouse",
        "price": 14995.0,
        "original_price": 16995.0,
        "discount": 12.0,
        "inventory": 22,
        "rating": 4.93,
        "review_count": 810,
        "delivery_days": 1,
        "margin": 0.26,
        "features": [
            "Under 60 Grams Featherweight Design",
            "LIGHTFORCE Hybrid Optical-Mechanical Switches",
            "HERO 2 Precision Sensor with 32K DPI Tracking",
            "95 Hours Continuous Battery Life"
        ],
        "tags": [
            "mouse",
            "wireless",
            "logitech g",
            "superlight",
            "esports",
            "gaming",
            "fps"
        ],
        "compatible_products": [
            "KB009",
            "ACC007"
        ],
        "upsell_products": [
            "MS001"
        ],
        "cross_sell_products": [
            "KB009",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MS004",
        "name": "Pulsar X2V2 Wireless Ultra-Light Gaming Mouse (53g, PixArt PAW3395 Sensor)",
        "brand": "Pulsar",
        "description": "Symmetrical medium shape weighing only 53g without holes, optical micro switches for zero debounce delay, and 4K polling ready.",
        "category": "mouse",
        "price": 8499.0,
        "original_price": 10999.0,
        "discount": 23.0,
        "inventory": 35,
        "rating": 4.85,
        "review_count": 640,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "53g Solid Shell Ultra-Lightweight Build",
            "PixArt PAW3395 Flagship 26K DPI Optical Sensor",
            "Pulsar Optical Switches for Fast Actuation",
            "4K Hz Wireless Polling Rate Compatible"
        ],
        "tags": [
            "mouse",
            "wireless",
            "pulsar",
            "lightweight",
            "esports",
            "clean design",
            "under 10000"
        ],
        "compatible_products": [
            "KB004",
            "ACC007"
        ],
        "upsell_products": [
            "MS003"
        ],
        "cross_sell_products": [
            "KB004",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MS005",
        "name": "Anker Ergonomic 2.4G Wireless Vertical Optical Mouse",
        "brand": "Anker",
        "description": "Scientific ergonomic design promotes healthy neutral 'handshake' wrist and arm positions for smoother movement and less strain.",
        "category": "mouse",
        "price": 1999.0,
        "original_price": 2999.0,
        "discount": 33.0,
        "inventory": 85,
        "rating": 4.68,
        "review_count": 4800,
        "delivery_days": 1,
        "margin": 0.38,
        "features": [
            "Ergonomic Neutral Handshake Wrist Posture",
            "1600 / 1200 / 800 Adjustable Optical DPI",
            "Next/Previous Browser Navigation Buttons",
            "Power-Saving Auto Sleep Mode"
        ],
        "tags": [
            "mouse",
            "wireless",
            "anker",
            "vertical",
            "ergonomic",
            "rsi prevention",
            "budget",
            "under 2000"
        ],
        "compatible_products": [
            "KB007",
            "ACC007"
        ],
        "upsell_products": [
            "MS001"
        ],
        "cross_sell_products": [
            "KB007",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MS006",
        "name": "Glorious Model O Wireless Lightweight RGB Gaming Mouse (69g, BAMF Sensor)",
        "brand": "Glorious",
        "description": "Honeycomb shell structure for strength and comfort, BAMF sensor created in collaboration with PixArt, 71 hours battery.",
        "category": "mouse",
        "price": 6499.0,
        "original_price": 8999.0,
        "discount": 28.0,
        "inventory": 40,
        "rating": 4.77,
        "review_count": 1350,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "Honeycomb Ventilated Shell at 69 Grams",
            "Proprietary BAMF 19K DPI Sensor",
            "71 Hours Long Lasting Battery Life",
            "Pure Virgin PTFE G-Skates for Smooth Glide"
        ],
        "tags": [
            "mouse",
            "wireless",
            "glorious",
            "rgb",
            "honeycomb",
            "lightweight",
            "under 7000"
        ],
        "compatible_products": [
            "KB006",
            "ACC007"
        ],
        "upsell_products": [
            "MS002"
        ],
        "cross_sell_products": [
            "KB006",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MS007",
        "name": "Keychron M3 Wireless Ergonomic Optical Mouse (PAW3395, 79g, 26000 DPI)",
        "brand": "Keychron",
        "description": "Tri-mode connection (Type-C wired, 2.4G, Bluetooth 5.1), Kailh GM 8.0 micro switches, and dedicated external DPI & polling rate buttons.",
        "category": "mouse",
        "price": 4999.0,
        "original_price": 6999.0,
        "discount": 29.0,
        "inventory": 60,
        "rating": 4.8,
        "review_count": 780,
        "delivery_days": 1,
        "margin": 0.34,
        "features": [
            "PixArt PAW3395 26K Sensor",
            "Kailh GM 8.0 Micro Switches (80M Clicks)",
            "Tri-Mode Wireless / Bluetooth / Type-C",
            "Dedicated External Hardware Tuning Buttons"
        ],
        "tags": [
            "mouse",
            "wireless",
            "keychron",
            "coding",
            "productivity",
            "under 5000"
        ],
        "compatible_products": [
            "KB001",
            "KB004",
            "ACC007"
        ],
        "upsell_products": [
            "MS001"
        ],
        "cross_sell_products": [
            "KB001",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MS008",
        "name": "Logitech MX Anywhere 3S Compact Wireless Performance Mouse",
        "brand": "Logitech",
        "description": "Compact portable performance with 8K DPI track-anywhere sensor, Quiet Clicks, and MagSpeed electromagnetic scroll wheel.",
        "category": "mouse",
        "price": 7495.0,
        "original_price": 8995.0,
        "discount": 17.0,
        "inventory": 45,
        "rating": 4.87,
        "review_count": 1650,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "Ultra-Compact Travel Form Factor",
            "8000 DPI Track-on-Glass Any-Surface Sensor",
            "MagSpeed Precision Electromagnetic Wheel",
            "70 Days Battery Life on Single Charge"
        ],
        "tags": [
            "mouse",
            "wireless",
            "logitech",
            "travel",
            "compact",
            "laptop mouse",
            "macbook"
        ],
        "compatible_products": [
            "LP005",
            "KB002",
            "BAG004"
        ],
        "upsell_products": [
            "MS001"
        ],
        "cross_sell_products": [
            "LP005",
            "BAG004"
        ],
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MS009",
        "name": "Razer Basilisk V3 Ergonomic Wired Gaming Mouse with 11 Programmable Buttons",
        "brand": "Razer",
        "description": "Razer HyperScroll tilt wheel with free-spin and tactile modes, 11 programmable buttons, 11 Razer Chroma RGB lighting zones.",
        "category": "mouse",
        "price": 4499.0,
        "original_price": 6999.0,
        "discount": 36.0,
        "inventory": 70,
        "rating": 4.82,
        "review_count": 2900,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "Razer HyperScroll Tilt Wheel with Smart-Reel",
            "11 Programmable Buttons with Multi-Function Trigger",
            "Focus+ 26K DPI Optical Sensor",
            "11 Chroma RGB Underglow Lighting Zones"
        ],
        "tags": [
            "mouse",
            "wired",
            "razer",
            "basilisk",
            "ergonomic",
            "rgb",
            "thumb rest",
            "under 5000"
        ],
        "compatible_products": [
            "KB003",
            "ACC007"
        ],
        "upsell_products": [
            "MS002"
        ],
        "cross_sell_products": [
            "KB003",
            "ACC007"
        ],
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MON001",
        "name": "LG UltraFine 27\" 4K UHD IPS Display with USB-C 90W Power Delivery (27UP850)",
        "brand": "LG",
        "description": "VESA DisplayHDR 400 with 95% DCI-P3 wide color gamut, USB Type-C 90W laptop charging, hardware calibration ready, and ergonomic stand.",
        "category": "monitor",
        "price": 32999.0,
        "original_price": 42000.0,
        "discount": 21.0,
        "inventory": 25,
        "rating": 4.9,
        "review_count": 1450,
        "delivery_days": 1,
        "margin": 0.24,
        "features": [
            "27-inch 4K UHD (3840x2160) IPS Display",
            "USB-C with 90W Laptop Charging & Video",
            "VESA DisplayHDR 400 with DCI-P3 95%",
            "Height / Pivot / Tilt Adjustable Stand"
        ],
        "tags": [
            "monitor",
            "4k",
            "lg",
            "ips",
            "usb-c",
            "coding",
            "developer",
            "4k monitor",
            "hdr",
            "macbook monitor"
        ],
        "compatible_products": [
            "LP001",
            "ACC003",
            "ACC010"
        ],
        "upsell_products": [
            "MON002"
        ],
        "cross_sell_products": [
            "ACC003",
            "ACC010"
        ],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MON002",
        "name": "Dell UltraSharp 32\" 4K USB-C Hub Monitor (U3223QE with IPS Black Technology)",
        "brand": "Dell",
        "description": "World-class 2000:1 contrast ratio with IPS Black, 98% DCI-P3, built-in 90W USB-C hub with RJ45 Ethernet, and KVM switch.",
        "category": "monitor",
        "price": 74990.0,
        "original_price": 92990.0,
        "discount": 19.0,
        "inventory": 15,
        "rating": 4.94,
        "review_count": 680,
        "delivery_days": 1,
        "margin": 0.22,
        "features": [
            "31.5-inch 4K UHD IPS Black (2000:1 Contrast)",
            "Integrated Hub with 90W USB-C, RJ45 LAN & USB 3.2",
            "Built-In Auto KVM Switch for 2 PCs",
            "ComfortView Plus Hardware Low Blue Light"
        ],
        "tags": [
            "monitor",
            "4k",
            "dell",
            "ultrasharp",
            "ips black",
            "kvm",
            "professional",
            "coding",
            "designer"
        ],
        "compatible_products": [
            "LP001",
            "LP002",
            "ACC010"
        ],
        "upsell_products": [
            "MON003"
        ],
        "cross_sell_products": [
            "LP002",
            "ACC010"
        ],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MON003",
        "name": "Samsung Odyssey Neo G9 49\" Dual QHD Curved Gaming Monitor (Mini-LED, 240Hz, 1ms)",
        "brand": "Samsung",
        "description": "Immense 1000R curvature matching the human eye, Quantum Mini-LED technology with HDR2000, 240Hz refresh rate and 1ms response time.",
        "category": "monitor",
        "price": 149990.0,
        "original_price": 185000.0,
        "discount": 19.0,
        "inventory": 8,
        "rating": 4.88,
        "review_count": 310,
        "delivery_days": 1,
        "margin": 0.2,
        "features": [
            "49-inch Dual QHD (5120x1440) 32:9 Super Ultrawide",
            "Quantum Mini-LED with 2048 Local Dimming Zones",
            "240Hz Refresh Rate with 1ms GtG Response Time",
            "CoreSync Rear RGB Ambient Lighting"
        ],
        "tags": [
            "monitor",
            "ultrawide",
            "samsung",
            "odyssey",
            "curved",
            "240hz",
            "gaming",
            "mini-led",
            "super ultrawide"
        ],
        "compatible_products": [
            "LP004",
            "KB009",
            "ACC010"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "KB009",
            "ACC010"
        ],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MON004",
        "name": "BenQ PD2705U 27\" 4K Designer & Developer Monitor (Calman & Pantone Validated, KVM)",
        "brand": "BenQ",
        "description": "AQCOLOR technology covering 99% sRGB/Rec.709 with factory calibration report, USB-C 65W, DualView mode, and Hotkey Puck G2 controller.",
        "category": "monitor",
        "price": 38990.0,
        "original_price": 49990.0,
        "discount": 22.0,
        "inventory": 20,
        "rating": 4.85,
        "review_count": 520,
        "delivery_days": 1,
        "margin": 0.25,
        "features": [
            "27-inch 4K UHD IPS Panel with Delta E \u2264 3",
            "Hotkey Puck G2 Hardware Quick Controller",
            "M-Book Mode for Perfect Mac Color Matching",
            "KVM Switch & Picture-in-Picture / Picture-by-Picture"
        ],
        "tags": [
            "monitor",
            "4k",
            "benq",
            "designer",
            "color accurate",
            "pantone",
            "macbook",
            "coding"
        ],
        "compatible_products": [
            "LP001",
            "ACC010"
        ],
        "upsell_products": [
            "MON002"
        ],
        "cross_sell_products": [
            "ACC003",
            "ACC010"
        ],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MON005",
        "name": "ASUS TUF Gaming 27\" 2K QHD Fast IPS Gaming Monitor (VG27AQ3A, 180Hz, 1ms GtG)",
        "brand": "ASUS",
        "description": "2560x1440 QHD Fast IPS gaming monitor with 180Hz refresh rate, ASUS Extreme Low Motion Blur Sync, and 130% sRGB color gamut.",
        "category": "monitor",
        "price": 21499.0,
        "original_price": 28999.0,
        "discount": 26.0,
        "inventory": 35,
        "rating": 4.82,
        "review_count": 1780,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "27-inch 2K QHD (2560x1440) Fast IPS Panel",
            "180Hz High Refresh Rate & 1ms GtG Response",
            "ELMB Sync with AMD FreeSync Premium",
            "HDR10 Support with Shadow Boost"
        ],
        "tags": [
            "monitor",
            "asus",
            "2k",
            "180hz",
            "gaming",
            "ips",
            "fast ips",
            "under 25000"
        ],
        "compatible_products": [
            "LP007",
            "MS002",
            "ACC010"
        ],
        "upsell_products": [
            "MON001"
        ],
        "cross_sell_products": [
            "MS002",
            "ACC010"
        ],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MON006",
        "name": "Acer Nitro 24\" FHD 180Hz IPS Gaming Monitor (QG241Y, 0.5ms Response Time)",
        "brand": "Acer",
        "description": "Affordable esports display featuring 180Hz refresh rate, 0.5ms response time, AMD FreeSync Premium, and 99% sRGB.",
        "category": "monitor",
        "price": 8999.0,
        "original_price": 13999.0,
        "discount": 36.0,
        "inventory": 75,
        "rating": 4.65,
        "review_count": 3100,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "23.8-inch Full HD (1920x1080) IPS Panel",
            "180Hz High Refresh Rate & 0.5ms Ultra-Fast Response",
            "AMD FreeSync Premium Tear-Free Technology",
            "HDR10 & Acer VisionCare 2.0 Eye Protection"
        ],
        "tags": [
            "monitor",
            "acer",
            "budget",
            "180hz",
            "gaming",
            "fhd",
            "under 10000",
            "under 10k"
        ],
        "compatible_products": [
            "KB007",
            "MS005"
        ],
        "upsell_products": [
            "MON005"
        ],
        "cross_sell_products": [
            "KB007",
            "MS005"
        ],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MON007",
        "name": "MSI Optix MAG342CQR 34\" UWQHD Curved Ultrawide Gaming Monitor (144Hz, 1500R)",
        "brand": "MSI",
        "description": "3440x1440 ultra-wide resolution with 1500R curvature, 144Hz refresh rate, Mystic Light RGB backlighting, and Night Vision enhancer.",
        "category": "monitor",
        "price": 31999.0,
        "original_price": 45000.0,
        "discount": 29.0,
        "inventory": 20,
        "rating": 4.79,
        "review_count": 890,
        "delivery_days": 1,
        "margin": 0.26,
        "features": [
            "34-inch UWQHD (3440x1440) 21:9 Ultrawide",
            "1500R Immersive Gaming Curve",
            "144Hz Refresh Rate with Adaptive Sync",
            "MSI Mystic Light Rear RGB Accent"
        ],
        "tags": [
            "monitor",
            "ultrawide",
            "msi",
            "curved",
            "144hz",
            "coding",
            "productivity",
            "multitasking"
        ],
        "compatible_products": [
            "LP004",
            "ACC010"
        ],
        "upsell_products": [
            "MON003"
        ],
        "cross_sell_products": [
            "ACC003",
            "ACC010"
        ],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MON008",
        "name": "ViewSonic 15.6\" Portable USB-C FHD IPS Monitor (VA1655, Ultra-Light 700g with Stand)",
        "brand": "ViewSonic",
        "description": "Ultra-portable second screen for laptops and phones featuring one-cable USB-C video & power, built-in magnetic cover stand, and dual speakers.",
        "category": "monitor",
        "price": 10999.0,
        "original_price": 16999.0,
        "discount": 35.0,
        "inventory": 40,
        "rating": 4.73,
        "review_count": 920,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "15.6-inch Full HD IPS Anti-Glare Portable Screen",
            "Dual USB-C Ports with 60W Two-Way Power Delivery",
            "Ultra-Lightweight 700 Grams & 9.8mm Slim Profile",
            "Built-In Foldable Multi-Angle Kickstand"
        ],
        "tags": [
            "monitor",
            "portable",
            "viewsonic",
            "usb-c",
            "travel monitor",
            "laptop screen",
            "second display"
        ],
        "compatible_products": [
            "LP005",
            "LP006",
            "BAG001"
        ],
        "upsell_products": [
            "MON001"
        ],
        "cross_sell_products": [
            "BAG001",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "MON009",
        "name": "ASUS ROG Swift OLED 27\" QHD 240Hz Esports Gaming Monitor (PG27AQDM, 0.03ms)",
        "brand": "ASUS",
        "description": "OLED panel with custom heatsink and intelligent voltage optimization for burn-in protection, 240Hz refresh rate, 0.03ms response time.",
        "category": "monitor",
        "price": 89999.0,
        "original_price": 110000.0,
        "discount": 18.0,
        "inventory": 10,
        "rating": 4.93,
        "review_count": 340,
        "delivery_days": 1,
        "margin": 0.2,
        "features": [
            "27-inch 2K QHD (2560x1440) OLED Panel",
            "240Hz Refresh Rate & Ultra-Fast 0.03ms Response Time",
            "Custom Internal Heatsink for Thermal Management",
            "99% DCI-P3 Color Gamut & Delta E < 2"
        ],
        "tags": [
            "monitor",
            "oled",
            "asus",
            "rog",
            "240hz",
            "esports",
            "hdr",
            "premium"
        ],
        "compatible_products": [
            "LP004",
            "KB009",
            "MS003",
            "ACC010"
        ],
        "upsell_products": [
            "MON003"
        ],
        "cross_sell_products": [
            "KB009",
            "ACC010"
        ],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "WAT001",
        "name": "Apple Watch Ultra 2 (GPS + Cellular, 49mm Titanium Case with Ocean Band)",
        "brand": "Apple",
        "description": "Most rugged and capable Apple Watch. S9 SiP with double tap gesture, 3000 nits display, dual-frequency precision GPS, 72-hour low power mode.",
        "category": "smartwatch",
        "price": 89900.0,
        "original_price": 99900.0,
        "discount": 10.0,
        "inventory": 15,
        "rating": 4.96,
        "review_count": 920,
        "delivery_days": 1,
        "margin": 0.18,
        "features": [
            "49mm Aerospace Titanium Case with Sapphire Crystal",
            "3000 nits Brightest Always-On Retina Display",
            "Precision Dual-Frequency GPS (L1 and L5)",
            "100m Water Resistance with Depth Gauge"
        ],
        "tags": [
            "smartwatch",
            "watch",
            "apple",
            "apple watch ultra",
            "titanium",
            "outdoor",
            "fitness",
            "premium"
        ],
        "compatible_products": [
            "PH002",
            "EB001",
            "ACC004"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "PH002",
            "EB001"
        ],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "WAT002",
        "name": "Samsung Galaxy Watch6 Classic 47mm (Bluetooth/LTE, Rotating Bezel, Silver)",
        "brand": "Samsung",
        "description": "Signature physical rotating bezel, sapphire crystal glass, advanced sleep coaching, ECG and blood pressure monitoring, BioActive sensor.",
        "category": "smartwatch",
        "price": 36999.0,
        "original_price": 42999.0,
        "discount": 14.0,
        "inventory": 25,
        "rating": 4.86,
        "review_count": 1420,
        "delivery_days": 1,
        "margin": 0.25,
        "features": [
            "Signature Physical Rotating Bezel Control",
            "Sapphire Crystal Glass 1.5-inch Super AMOLED",
            "Samsung BioActive Sensor (ECG + BP + Body Composition)",
            "Wear OS Powered by Samsung with Google Wallet"
        ],
        "tags": [
            "smartwatch",
            "watch",
            "samsung",
            "galaxy watch",
            "classic",
            "rotating bezel",
            "health",
            "fitness"
        ],
        "compatible_products": [
            "PH001",
            "EB003"
        ],
        "upsell_products": [
            "WAT001"
        ],
        "cross_sell_products": [
            "PH001",
            "EB003"
        ],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "WAT003",
        "name": "Garmin Forerunner 965 Premium GPS Running Smartwatch (Titanium Bezel, AMOLED)",
        "brand": "Garmin",
        "description": "Brilliant 1.4\" AMOLED touchscreen display, built-in full-color maps, advanced training metrics and recovery insights, up to 23 days battery.",
        "category": "smartwatch",
        "price": 67490.0,
        "original_price": 74990.0,
        "discount": 10.0,
        "inventory": 18,
        "rating": 4.94,
        "review_count": 680,
        "delivery_days": 1,
        "margin": 0.22,
        "features": [
            "1.4-inch Vibrant AMOLED Touchscreen with Titanium Bezel",
            "Full-Color TopoActive Maps & Multi-Band GNSS GPS",
            "Training Readiness, HRV Status & Race Widget",
            "Up to 23 Days Battery Life in Smartwatch Mode"
        ],
        "tags": [
            "smartwatch",
            "watch",
            "garmin",
            "running",
            "marathon",
            "triathlon",
            "gps",
            "fitness"
        ],
        "compatible_products": [
            "EB006",
            "SH001",
            "SH004"
        ],
        "upsell_products": [
            "WAT001"
        ],
        "cross_sell_products": [
            "SH001",
            "EB006"
        ],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "WAT004",
        "name": "Garmin Fenix 7 Pro Solar Multisport GPS Smartwatch (Power Glass, Flashlight)",
        "brand": "Garmin",
        "description": "Solar charging lens for weeks of battery life, built-in multi-LED flashlight, endurance score, hill score, and 24/7 health tracking.",
        "category": "smartwatch",
        "price": 81990.0,
        "original_price": 94990.0,
        "discount": 14.0,
        "inventory": 12,
        "rating": 4.95,
        "review_count": 510,
        "delivery_days": 1,
        "margin": 0.2,
        "features": [
            "Power Sapphire Solar Charging Glass Lens",
            "Built-In Variable Intensity LED Flashlight",
            "Multi-Band GPS Satellite Positioning",
            "Up to 37 Days Battery Life in Solar Mode"
        ],
        "tags": [
            "smartwatch",
            "watch",
            "garmin",
            "fenix",
            "solar",
            "outdoor",
            "hiking",
            "expedition",
            "rugged"
        ],
        "compatible_products": [
            "BAG002",
            "BAG009"
        ],
        "upsell_products": [
            "WAT001"
        ],
        "cross_sell_products": [
            "BAG002",
            "BAG009"
        ],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "WAT005",
        "name": "Amazfit GTR 4 Smartwatch with Dual-Band GPS & Alexa (AMOLED, 14-Day Battery)",
        "brand": "Amazfit",
        "description": "Industry-first circularly-polarized GPS antenna, 150+ sports modes, BioTracker 4.0 PPG biometric sensor, Bluetooth phone calls.",
        "category": "smartwatch",
        "price": 16999.0,
        "original_price": 23999.0,
        "discount": 29.0,
        "inventory": 40,
        "rating": 4.76,
        "review_count": 1890,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "Dual-Band Circularly-Polarized GPS Tracking",
            "1.43-inch HD AMOLED Display with Anti-Glare Bezel",
            "14-Day Ultra-Long Battery Life",
            "Bluetooth Phone Calls & Built-In Amazon Alexa"
        ],
        "tags": [
            "smartwatch",
            "watch",
            "amazfit",
            "battery life",
            "gps",
            "under 20000",
            "fitness"
        ],
        "compatible_products": [
            "PH003",
            "EB004"
        ],
        "upsell_products": [
            "WAT002"
        ],
        "cross_sell_products": [
            "EB004",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "WAT006",
        "name": "Fitbit Charge 6 Advanced Fitness & Health Tracker with Google Apps & Heart Rate on Gym Tech",
        "brand": "Fitbit",
        "description": "Built-in GPS, YouTube Music controls, Google Maps directions, ECG app, EDA stress management, and 7-day battery.",
        "category": "smartwatch",
        "price": 14999.0,
        "original_price": 17999.0,
        "discount": 17.0,
        "inventory": 50,
        "rating": 4.7,
        "review_count": 1350,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Built-In GPS & Google Maps Turn-by-Turn",
            "ECG App for Heart Rhythm & EDA Stress Sensor",
            "Connect to Compatible Gym Equipment via Bluetooth",
            "7-Day Continuous Battery Life with Water Resistance 50m"
        ],
        "tags": [
            "smartwatch",
            "fitness band",
            "fitbit",
            "google",
            "health",
            "ecg",
            "compact tracker"
        ],
        "compatible_products": [
            "PH003",
            "EB008"
        ],
        "upsell_products": [
            "WAT002"
        ],
        "cross_sell_products": [
            "EB008",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "WAT007",
        "name": "OnePlus Watch 2 with Dual-Engine Architecture (Wear OS 4 + RTOS, 100-Hour Battery)",
        "brand": "OnePlus",
        "description": "Snapdragon W5 + BES2700 dual chipsets delivering up to 100 hours in Smart Mode, 5ATM + IP68 military standard MIL-STD-810H.",
        "category": "smartwatch",
        "price": 24999.0,
        "original_price": 27999.0,
        "discount": 11.0,
        "inventory": 30,
        "rating": 4.82,
        "review_count": 910,
        "delivery_days": 1,
        "margin": 0.26,
        "features": [
            "Dual-Engine Architecture (Snapdragon W5 + RTOS)",
            "Up to 100 Hours Battery in Full Smart Mode",
            "Dual-Frequency Precision L1+L5 GPS",
            "Stainless Steel Chassis with 2.5D Sapphire Crystal"
        ],
        "tags": [
            "smartwatch",
            "watch",
            "oneplus",
            "wear os",
            "long battery",
            "5g partner",
            "under 25000"
        ],
        "compatible_products": [
            "PH004",
            "EB004"
        ],
        "upsell_products": [
            "WAT002"
        ],
        "cross_sell_products": [
            "PH004",
            "EB004"
        ],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "WAT008",
        "name": "Titan Smart 3 Premium Metallic Calling Smartwatch (1.96\" AMOLED, AI Voice)",
        "brand": "Titan",
        "description": "1.96\" Super AMOLED display with AOD, SingleSync Bluetooth calling with AI voice assistant, nitro-fast processor, 110+ sports modes.",
        "category": "smartwatch",
        "price": 7995.0,
        "original_price": 11995.0,
        "discount": 33.0,
        "inventory": 65,
        "rating": 4.68,
        "review_count": 2800,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "1.96-inch Super AMOLED 410x502 Display",
            "SingleSync Seamless Bluetooth Calling",
            "AI Voice Assistant Integration",
            "Comprehensive Health Suite (SpO2, 24/7 HR, Stress)"
        ],
        "tags": [
            "smartwatch",
            "watch",
            "titan",
            "calling",
            "amoled",
            "budget",
            "under 8000",
            "gift"
        ],
        "compatible_products": [
            "EB007",
            "ACC001"
        ],
        "upsell_products": [
            "WAT005"
        ],
        "cross_sell_products": [
            "EB007",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "WAT009",
        "name": "Noise ColorFit Pro 5 Max Smartwatch with 1.96\" AMOLED Display & VO2 Max Tracking",
        "brand": "Noise",
        "description": "Post-training recovery analysis, rapid health monitoring, Bluetooth calling with Tru Sync, DIY customizable watch faces.",
        "category": "smartwatch",
        "price": 4499.0,
        "original_price": 9999.0,
        "discount": 55.0,
        "inventory": 110,
        "rating": 4.58,
        "review_count": 6200,
        "delivery_days": 1,
        "margin": 0.42,
        "features": [
            "1.96-inch AMOLED Display with 600 nits Brightness",
            "VO2 Max & Post-Workout Recovery Metrics",
            "Tru Sync Bluetooth Calling with Quick Reply",
            "IP68 Water and Sweat Resistance"
        ],
        "tags": [
            "smartwatch",
            "watch",
            "noise",
            "budget",
            "under 5000",
            "calling",
            "amoled",
            "gift"
        ],
        "compatible_products": [
            "EB009",
            "ACC001"
        ],
        "upsell_products": [
            "WAT008"
        ],
        "cross_sell_products": [
            "EB009",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "CAM001",
        "name": "Sony Alpha 7 IV Full-Frame Mirrorless Hybrid Camera (Body Only, 33MP)",
        "brand": "Sony",
        "description": "33MP full-frame Exmor R back-illuminated sensor, BIONZ XR processing engine, 4K 60p 10-bit 4:2:2 video, real-time eye AF for humans/animals/birds.",
        "category": "camera",
        "price": 209990.0,
        "original_price": 242990.0,
        "discount": 14.0,
        "inventory": 10,
        "rating": 4.95,
        "review_count": 480,
        "delivery_days": 1,
        "margin": 0.18,
        "features": [
            "33MP Full-Frame Exmor R CMOS Sensor",
            "BIONZ XR Image Processor with 759 Phase-Detection AF Points",
            "4K 60p 10-bit 4:2:2 All-Intra Recording with S-Cinetone",
            "5-Axis In-Body Optical Image Stabilization (5.5 stops)"
        ],
        "tags": [
            "camera",
            "sony",
            "full frame",
            "mirrorless",
            "4k",
            "professional",
            "cinematography",
            "photography"
        ],
        "compatible_products": [
            "ACC008",
            "BAG001",
            "ACC002"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "ACC008",
            "BAG001"
        ],
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "CAM002",
        "name": "Canon EOS R6 Mark II Mirrorless Camera with 24-105mm Lens Kit",
        "brand": "Canon",
        "description": "24.2MP full-frame CMOS sensor, up to 40 fps electronic shutter, 6K oversampled uncropped 4K 60p video, in-body IS up to 8 stops.",
        "category": "camera",
        "price": 243990.0,
        "original_price": 275000.0,
        "discount": 11.0,
        "inventory": 8,
        "rating": 4.92,
        "review_count": 310,
        "delivery_days": 1,
        "margin": 0.16,
        "features": [
            "24.2MP Full-Frame CMOS Sensor with Dual Pixel CMOS AF II",
            "Up to 40 fps Continuous Shooting with AF/AE Tracking",
            "6K Oversampled 4K 60p 10-bit Movie Recording with Canon Log 3",
            "In-Body Image Stabilization up to 8 Stops of Correction"
        ],
        "tags": [
            "camera",
            "canon",
            "mirrorless",
            "full frame",
            "4k 60p",
            "wildlife",
            "wedding",
            "professional"
        ],
        "compatible_products": [
            "ACC008",
            "BAG001"
        ],
        "upsell_products": [
            "CAM001"
        ],
        "cross_sell_products": [
            "ACC008",
            "BAG001"
        ],
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "CAM003",
        "name": "DJI Osmo Pocket 3 Gimbal Camera (1\" CMOS Sensor, 4K 120fps, Rotating OLED)",
        "brand": "DJI",
        "description": "Pocket-sized 3-axis stabilized gimbal with 1\" CMOS sensor, 4K 120fps recording, 2-inch rotatable OLED touchscreen, and ActiveTrack 6.0.",
        "category": "camera",
        "price": 49990.0,
        "original_price": 56990.0,
        "discount": 12.0,
        "inventory": 25,
        "rating": 4.94,
        "review_count": 1250,
        "delivery_days": 1,
        "margin": 0.22,
        "features": [
            "1-Inch CMOS Sensor for Low-Light Mastery",
            "4K 120fps Slow Motion in 10-Bit D-Log M",
            "2-Inch Rotatable OLED Touchscreen with Fast Switching",
            "3-Axis Mechanical Gimbal Stabilization"
        ],
        "tags": [
            "camera",
            "dji",
            "osmo pocket",
            "gimbal",
            "vlogging",
            "4k",
            "travel camera",
            "creator",
            "youtube"
        ],
        "compatible_products": [
            "ACC008",
            "BAG007"
        ],
        "upsell_products": [
            "CAM001"
        ],
        "cross_sell_products": [
            "ACC008",
            "BAG007"
        ],
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "CAM004",
        "name": "GoPro HERO12 Black Action Camera (5.3K 60fps Video, HyperSmooth 6.0)",
        "brand": "GoPro",
        "description": "Unbelievable image quality with 5.3K video, HDR photo/video, Emmy-winning HyperSmooth 6.0 stabilization, and rugged 10m waterproof build.",
        "category": "camera",
        "price": 37990.0,
        "original_price": 45000.0,
        "discount": 16.0,
        "inventory": 35,
        "rating": 4.86,
        "review_count": 2100,
        "delivery_days": 1,
        "margin": 0.25,
        "features": [
            "5.3K 60fps & 4K 120fps Ultra-High Resolution Video",
            "HyperSmooth 6.0 with 360\u00b0 Horizon Lock",
            "Rugged & Waterproof to 10m (33ft) Without Housing",
            "Wireless Bluetooth Audio Support with AirPods"
        ],
        "tags": [
            "camera",
            "gopro",
            "action camera",
            "waterproof",
            "underwater",
            "sports",
            "biking",
            "travel"
        ],
        "compatible_products": [
            "ACC008",
            "BAG008"
        ],
        "upsell_products": [
            "CAM003"
        ],
        "cross_sell_products": [
            "ACC008",
            "BAG008"
        ],
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "CAM005",
        "name": "Sony ZV-E10 Interchangeable Lens Mirrorless Vlog Camera with 16-50mm Lens",
        "brand": "Sony",
        "description": "Large APS-C sensor for background defocus bokeh, directional 3-capsule mic with windscreen, product showcase setting, 4K HDR.",
        "category": "camera",
        "price": 61490.0,
        "original_price": 69990.0,
        "discount": 12.0,
        "inventory": 20,
        "rating": 4.88,
        "review_count": 1650,
        "delivery_days": 1,
        "margin": 0.24,
        "features": [
            "24.2MP APS-C Exmor CMOS Sensor",
            "Directional 3-Capsule Internal Mic with Windscreen",
            "Product Showcase Setting & Background Defocus Switch",
            "Vari-Angle Side-Opening LCD Touchscreen"
        ],
        "tags": [
            "camera",
            "sony",
            "vlog",
            "youtube",
            "streaming",
            "mirrorless",
            "creator",
            "under 65000"
        ],
        "compatible_products": [
            "ACC008",
            "BAG002"
        ],
        "upsell_products": [
            "CAM001"
        ],
        "cross_sell_products": [
            "ACC008",
            "BAG002"
        ],
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "CAM006",
        "name": "Logitech Brio 4K Ultra HD Pro Webcam with RightLight 3 and HDR",
        "brand": "Logitech",
        "description": "Stream crystal-clear 4K video with HDR, dual omnidirectional noise-cancelling mics, 5x digital zoom, and Windows Hello facial recognition.",
        "category": "camera",
        "price": 17995.0,
        "original_price": 24995.0,
        "discount": 28.0,
        "inventory": 40,
        "rating": 4.84,
        "review_count": 2900,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "Ultra 4K HD Video at 30fps / 1080p at 60fps",
            "RightLight 3 with HDR Auto Light Correction",
            "Dual Omnidirectional Noise-Cancelling Microphones",
            "Windows Hello Infrared Facial Recognition Login"
        ],
        "tags": [
            "camera",
            "webcam",
            "logitech",
            "4k webcam",
            "streaming",
            "zoom",
            "meetings",
            "wfh"
        ],
        "compatible_products": [
            "MON001",
            "ACC002"
        ],
        "upsell_products": [
            "CAM005"
        ],
        "cross_sell_products": [
            "MON001",
            "ACC002"
        ],
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "CAM007",
        "name": "DJI Mini 4 Pro Drone with DJI RC 2 Remote Controller (4K 60fps HDR, Omnidirectional Obstacle Sensing)",
        "brand": "DJI",
        "description": "Under 249g ultra-lightweight folding drone with omnidirectional active obstacle sensing, 4K 60fps HDR true vertical shooting, and 20km FHD video transmission.",
        "category": "camera",
        "price": 99990.0,
        "original_price": 115000.0,
        "discount": 13.0,
        "inventory": 12,
        "rating": 4.93,
        "review_count": 420,
        "delivery_days": 1,
        "margin": 0.2,
        "features": [
            "Under 249g Regulatory-Friendly Ultra-Light Form",
            "Omnidirectional Active Obstacle Sensing System",
            "4K 60fps HDR Video & True Vertical Social Shooting",
            "DJI O4 20km FHD Low-Latency Video Transmission"
        ],
        "tags": [
            "camera",
            "drone",
            "dji",
            "mini 4 pro",
            "aerial photography",
            "4k 60fps",
            "travel"
        ],
        "compatible_products": [
            "BAG001",
            "ACC008"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "BAG001",
            "ACC008"
        ],
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "CAM008",
        "name": "Insta360 X3 Waterproof 360 Action Camera (5.7K 360 Video, 72MP 360 Photo)",
        "brand": "Insta360",
        "description": "Capture 5.7K 360-degree footage with invisible selfie stick effect, 2.29\" tempered glass touchscreen, AI reframing in the app, and FlowState stabilization.",
        "category": "camera",
        "price": 42990.0,
        "original_price": 49990.0,
        "discount": 14.0,
        "inventory": 22,
        "rating": 4.87,
        "review_count": 890,
        "delivery_days": 1,
        "margin": 0.24,
        "features": [
            "5.7K Active HDR 360-Degree Video Recording",
            "72MP Ultra-High Detail 360 Photos",
            "Invisible Selfie Stick Third-Person Perspective",
            "FlowState 6-Axis Stabilization with 360 Horizon Lock"
        ],
        "tags": [
            "camera",
            "insta360",
            "360 camera",
            "action camera",
            "vlog",
            "travel",
            "motorcycle"
        ],
        "compatible_products": [
            "ACC008",
            "BAG008"
        ],
        "upsell_products": [
            "CAM003"
        ],
        "cross_sell_products": [
            "ACC008",
            "BAG008"
        ],
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "CAM009",
        "name": "Elgato Facecam Pro 4K60 True Ultra HD Studio Webcam (Sony STARVIS Sensor, f/2.0)",
        "brand": "Elgato",
        "description": "Studio-grade optical performance capturing uncompressed 4K 60fps video with 21mm equivalent f/2.0 prime lens and Sony STARVIS sensor.",
        "category": "camera",
        "price": 29990.0,
        "original_price": 34990.0,
        "discount": 14.0,
        "inventory": 15,
        "rating": 4.89,
        "review_count": 310,
        "delivery_days": 1,
        "margin": 0.26,
        "features": [
            "True 4K 60fps Uncompressed Video Stream",
            "Sony STARVIS Sensor with 21mm f/2.0 Prime Lens",
            "Camera Hub Pro DSLR-Like Manual ISO/Shutter Controls",
            "High-Speed USB 3.0 Ultra-Low Latency Interface"
        ],
        "tags": [
            "camera",
            "webcam",
            "elgato",
            "streaming",
            "twitch",
            "youtube",
            "studio quality",
            "4k 60fps"
        ],
        "compatible_products": [
            "MON001",
            "ACC002"
        ],
        "upsell_products": [
            "CAM005"
        ],
        "cross_sell_products": [
            "MON001",
            "ACC002"
        ],
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "SH001",
        "name": "Nike Air Zoom Pegasus 40 Road Running Shoes (Black/White)",
        "brand": "Nike",
        "description": "Engineered mesh upper for breathability, dual Zoom Air units for spring in your step, highly responsive React foam midsole.",
        "category": "shoes",
        "price": 9995.0,
        "original_price": 11895.0,
        "discount": 16.0,
        "inventory": 50,
        "rating": 4.88,
        "review_count": 3200,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "Dual Zoom Air Units (Forefoot & Heel)",
            "Nike React Foam Cushioning Technology",
            "Engineered Single-Layer Mesh Breathability",
            "Waffle-Inspired Outsole Traction Pattern"
        ],
        "tags": [
            "shoes",
            "nike",
            "running",
            "sneaker",
            "footwear",
            "pegasus",
            "marathon",
            "gym",
            "find nike running shoes"
        ],
        "compatible_products": [
            "WAT003",
            "EB006"
        ],
        "upsell_products": [
            "SH002"
        ],
        "cross_sell_products": [
            "WAT003",
            "EB006"
        ],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "SH002",
        "name": "Adidas Ultraboost Light Running Shoes (Core Black / Cloud White)",
        "brand": "Adidas",
        "description": "Lightest Boost cushioning ever made with 30% lighter material, Linear Energy Push system, and Primeknit+ breathable textile upper.",
        "category": "shoes",
        "price": 14999.0,
        "original_price": 18999.0,
        "discount": 21.0,
        "inventory": 35,
        "rating": 4.9,
        "review_count": 2100,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "30% Lighter Light BOOST Energy Capsule Midsole",
            "adidas Primeknit+ Adaptive Foot Hugging Upper",
            "Linear Energy Push (LEP) Torsion Stiffness System",
            "Continental Better Rubber All-Weather Traction"
        ],
        "tags": [
            "shoes",
            "adidas",
            "ultraboost",
            "running",
            "sneakers",
            "premium",
            "comfort"
        ],
        "compatible_products": [
            "WAT003",
            "EB006"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "WAT003",
            "EB006"
        ],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "SH003",
        "name": "Puma Velocity Nitro 2 Lightweight Road Running Shoes",
        "brand": "Puma",
        "description": "NITRO FOAM advanced nitrogen-injected technology delivering superior responsiveness and cushioning in a lightweight package.",
        "category": "shoes",
        "price": 6499.0,
        "original_price": 10999.0,
        "discount": 41.0,
        "inventory": 60,
        "rating": 4.75,
        "review_count": 1450,
        "delivery_days": 1,
        "margin": 0.38,
        "features": [
            "NITRO FOAM Nitrogen-Injected Midsole",
            "PUMAGRIP High-Durability Rubber Outsole",
            "Engineered Mesh with Reflective Visibility Accents",
            "TPU Heel Piece for Enhanced Stability"
        ],
        "tags": [
            "shoes",
            "puma",
            "running",
            "nitro",
            "budget running",
            "under 7000",
            "gym"
        ],
        "compatible_products": [
            "WAT005",
            "EB004"
        ],
        "upsell_products": [
            "SH001"
        ],
        "cross_sell_products": [
            "WAT005",
            "EB004"
        ],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "SH004",
        "name": "Asics Gel-Kayano 30 Maximum Stability Long-Distance Running Shoes",
        "brand": "Asics",
        "description": "4D GUIDANCE SYSTEM provides adaptive stability, PureGEL technology in heel for softer landings, and FF BLAST PLUS ECO cushioning.",
        "category": "shoes",
        "price": 13999.0,
        "original_price": 15999.0,
        "discount": 12.0,
        "inventory": 28,
        "rating": 4.92,
        "review_count": 1680,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "4D GUIDANCE SYSTEM Adaptive Stride Stability",
            "PureGEL Technology for 65% Softer Impact",
            "FF BLAST PLUS ECO Lightweight Bio-Based Foam",
            "OrthoLite X-55 Moisture-Wicking Sockliner"
        ],
        "tags": [
            "shoes",
            "asics",
            "gel kayano",
            "stability",
            "marathon",
            "pronation",
            "running"
        ],
        "compatible_products": [
            "WAT003",
            "EB006"
        ],
        "upsell_products": [
            "SH002"
        ],
        "cross_sell_products": [
            "WAT003",
            "EB006"
        ],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "SH005",
        "name": "New Balance Fresh Foam X 1080v13 Plush Cushioning Running Shoes",
        "brand": "New Balance",
        "description": "Signature Fresh Foam X midsole delivers the softest ride with rocker profile for smoother heel-to-toe transitions, engineered breathable mesh.",
        "category": "shoes",
        "price": 14999.0,
        "original_price": 16999.0,
        "discount": 12.0,
        "inventory": 25,
        "rating": 4.9,
        "review_count": 920,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "Fresh Foam X Midsole with 3% Bio-Based Content",
            "Smooth Rocker Profile Transition Geometry",
            "Engineered Breathable Mesh Second-Skin Upper",
            "Ndurance Solid Rubber Outsole in High-Wear Zones"
        ],
        "tags": [
            "shoes",
            "new balance",
            "fresh foam",
            "cushioning",
            "marathon",
            "walking",
            "running"
        ],
        "compatible_products": [
            "WAT003",
            "EB002"
        ],
        "upsell_products": [
            "SH002"
        ],
        "cross_sell_products": [
            "WAT003",
            "EB002"
        ],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "SH006",
        "name": "Skechers Go Walk 6 Slip-On Walking Shoes (Ultra GO Cushioning, Air Cooled Goga Mat)",
        "brand": "Skechers",
        "description": "High-rebound ultra-lightweight Hyper Pillar Technology, breathable athletic mesh upper, machine washable convenience.",
        "category": "shoes",
        "price": 4999.0,
        "original_price": 6499.0,
        "discount": 23.0,
        "inventory": 80,
        "rating": 4.78,
        "review_count": 4200,
        "delivery_days": 1,
        "margin": 0.38,
        "features": [
            "Lightweight Responsive ULTRA GO Cushioning",
            "Air-Cooled Goga Mat Breathable Insole",
            "High-Rebound Hyper Pillar Technology Underfoot",
            "100% Machine Washable Easy Care"
        ],
        "tags": [
            "shoes",
            "skechers",
            "slip-on",
            "walking",
            "comfort",
            "casual",
            "under 5000"
        ],
        "compatible_products": [
            "WAT006",
            "ACC001"
        ],
        "upsell_products": [
            "SH001"
        ],
        "cross_sell_products": [
            "WAT006",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "SH007",
        "name": "Under Armour HOVR Sonic 6 Connected Running Shoes",
        "brand": "Under Armour",
        "description": "UA HOVR zero-gravity feel foam provides energy return, 3D molded sockliner cradles foot, combination carbon rubber outsole.",
        "category": "shoes",
        "price": 7999.0,
        "original_price": 10999.0,
        "discount": 27.0,
        "inventory": 45,
        "rating": 4.74,
        "review_count": 1100,
        "delivery_days": 1,
        "margin": 0.34,
        "features": [
            "Responsive UA HOVR Cushioning System",
            "Engineered Spacer Mesh Upper with Seamless Forefoot",
            "3D-Molded Sockliner for Enhanced Cushioning",
            "High-Abrasion Rubber Heel Pods"
        ],
        "tags": [
            "shoes",
            "under armour",
            "hovr",
            "running",
            "gym",
            "cross training"
        ],
        "compatible_products": [
            "WAT003",
            "EB006"
        ],
        "upsell_products": [
            "SH001"
        ],
        "cross_sell_products": [
            "WAT003",
            "EB006"
        ],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "SH008",
        "name": "Woodland Genuine Leather Rugged Outdoor Casual Boots",
        "brand": "Woodland",
        "description": "Heavy-duty full-grain nubuck leather with rust-proof metal eyelets, grooved rubber lug sole for mountain trails and city streets.",
        "category": "shoes",
        "price": 4495.0,
        "original_price": 5995.0,
        "discount": 25.0,
        "inventory": 55,
        "rating": 4.69,
        "review_count": 3100,
        "delivery_days": 1,
        "margin": 0.36,
        "features": [
            "100% Genuine Full-Grain Nubuck Leather",
            "Deep-Grooved Anti-Skid Rubber Lug Sole",
            "Cushioned Padded Collar & Breathable Lining",
            "Rust-Proof Solid Brass Eyelets"
        ],
        "tags": [
            "shoes",
            "woodland",
            "boots",
            "leather",
            "outdoor",
            "trekking",
            "rugged",
            "under 5000"
        ],
        "compatible_products": [
            "BAG002",
            "WAT004"
        ],
        "upsell_products": [
            "SH009"
        ],
        "cross_sell_products": [
            "BAG002",
            "WAT004"
        ],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "SH009",
        "name": "Clarks Tilden Cap Formal Genuine Leather Oxford Shoes (Black)",
        "brand": "Clarks",
        "description": "Refined dress shoe in rich full-grain leather with cap-toe detailing, OrthoLite footbed with Cushion Soft technology for all-day comfort.",
        "category": "shoes",
        "price": 6999.0,
        "original_price": 8999.0,
        "discount": 22.0,
        "inventory": 35,
        "rating": 4.84,
        "review_count": 890,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "Premium Full-Grain Polished Calfskin Leather",
            "OrthoLite Cushion Soft Impact-Absorbing Insole",
            "Discreet Elastic Gore Inserts for Easy Fit",
            "Durable Non-Marking Flexible TPR Outsole"
        ],
        "tags": [
            "shoes",
            "clarks",
            "formal",
            "leather",
            "oxford",
            "office",
            "business",
            "wedding"
        ],
        "compatible_products": [
            "BAG006",
            "WAT008"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "BAG006",
            "WAT008"
        ],
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "BAG001",
        "name": "Peak Design Everyday Backpack 20L (Weatherproof 400D Nylon, MagLatch)",
        "brand": "Peak Design",
        "description": "Award-winning iconic everyday and photo backpack with configurable FlexFold dividers, dedicated 16\" laptop sleeve, and dual weatherproof side zips.",
        "category": "bag",
        "price": 26999.0,
        "original_price": 31999.0,
        "discount": 16.0,
        "inventory": 18,
        "rating": 4.95,
        "review_count": 680,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "100% Recycled 400D Weatherproof Canvas Shell",
            "Proprietary MagLatch One-Handed Hardware Closure",
            "3 FlexFold Configurable Origami Dividers",
            "Dedicated Padded 16-inch MacBook Sleeve"
        ],
        "tags": [
            "bag",
            "backpack",
            "peak design",
            "camera bag",
            "laptop bag",
            "waterproof",
            "premium",
            "developer"
        ],
        "compatible_products": [
            "LP001",
            "CAM001"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "LP001",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "BAG002",
        "name": "Nomatic Travel Pack 30L (Water Resistant, Expands from 20L to 30L)",
        "brand": "Nomatic",
        "description": "Engineered for 1-3 day trips with 20+ innovative features: magnetic water bottle pockets, RFID safe pocket, TSA checkpoint-friendly 16\" laptop sleeve.",
        "category": "bag",
        "price": 21990.0,
        "original_price": 26990.0,
        "discount": 19.0,
        "inventory": 22,
        "rating": 4.91,
        "review_count": 450,
        "delivery_days": 1,
        "margin": 0.26,
        "features": [
            "Expandable Capacity from 20L to 30L",
            "TSA Checkpoint-Friendly Lay-Flat Laptop Sleeve",
            "Magnetic Snap Water Bottle Pockets",
            "RFID Safe Security Pocket with YKK Zippers"
        ],
        "tags": [
            "bag",
            "backpack",
            "nomatic",
            "travel",
            "laptop backpack",
            "waterproof",
            "expandable"
        ],
        "compatible_products": [
            "LP002",
            "LP003",
            "ACC001"
        ],
        "upsell_products": [
            "BAG001"
        ],
        "cross_sell_products": [
            "LP003",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "BAG003",
        "name": "Bellroy Transit Workpack 20L (Clean Minimalist Laptop Daypack)",
        "brand": "Bellroy",
        "description": "Streamlined commuter bag with separate 16\" laptop compartment, quick-access sunglasses pocket, hidden side stretch pockets, and contoured back panel.",
        "category": "bag",
        "price": 16499.0,
        "original_price": 19999.0,
        "discount": 18.0,
        "inventory": 25,
        "rating": 4.88,
        "review_count": 520,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "Separate Padded 16-inch Laptop Section",
            "Soft-Lined Quick-Access Sunglasses Pouch",
            "Contoured Breathable Foam Back Panel",
            "Durable Water-Resistant Recycled Woven Fabric"
        ],
        "tags": [
            "bag",
            "backpack",
            "bellroy",
            "commute",
            "office",
            "minimalist",
            "laptop"
        ],
        "compatible_products": [
            "LP005",
            "ACC001"
        ],
        "upsell_products": [
            "BAG001"
        ],
        "cross_sell_products": [
            "LP005",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1546938576-6e6a64f317cc?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "BAG004",
        "name": "Mokobara The Transit Backpack with Dedicated 15.6\" Tech Sleeve",
        "brand": "Mokobara",
        "description": "Sleek modern commuter backpack with vegan leather accents, luggage pass-through strap, waterproof zippers, and hidden passport pocket.",
        "category": "bag",
        "price": 5499.0,
        "original_price": 7999.0,
        "discount": 31.0,
        "inventory": 65,
        "rating": 4.8,
        "review_count": 2100,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "Dedicated Padded 15.6-inch Laptop Compartment",
            "Premium Water-Resistant Fabric & Vegan Leather",
            "Luggage Trolley Pass-Through Sleeve",
            "Magnetic Snap Key Leash & Quick Pockets"
        ],
        "tags": [
            "bag",
            "backpack",
            "mokobara",
            "laptop backpack",
            "office",
            "travel",
            "under 6000"
        ],
        "compatible_products": [
            "LP006",
            "ACC001"
        ],
        "upsell_products": [
            "BAG003"
        ],
        "cross_sell_products": [
            "LP006",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1577733966973-d680bffd2e80?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "BAG005",
        "name": "Herschel Little America Classic Mountaineering Backpack (25L, Navy/Tan)",
        "brand": "Herschel",
        "description": "Timeless mountaineering silhouette with magnetic pin-clip strap closures, signature striped fabric liner, fleece-lined 15\" laptop sleeve.",
        "category": "bag",
        "price": 9999.0,
        "original_price": 12999.0,
        "discount": 23.0,
        "inventory": 35,
        "rating": 4.82,
        "review_count": 1800,
        "delivery_days": 1,
        "margin": 0.32,
        "features": [
            "Signature Striped Fabric Interior Liner",
            "Padded Fleece-Lined 15-inch Laptop Sleeve",
            "Magnetic Strap Closures with Metal Pin Clips",
            "Air Mesh Back Padding & Contoured Straps"
        ],
        "tags": [
            "bag",
            "backpack",
            "herschel",
            "classic",
            "style",
            "college",
            "laptop"
        ],
        "compatible_products": [
            "LP005",
            "ACC001"
        ],
        "upsell_products": [
            "BAG003"
        ],
        "cross_sell_products": [
            "LP005",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1581605405669-fcdf81165afa?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "BAG006",
        "name": "Samsonite Xenon 3.0 Slim Briefcase for 15.6\" Laptops (Ballistic Poly)",
        "brand": "Samsonite",
        "description": "Professional 1680D ballistic polyester business briefcase with padded tablet pocket, smart sleeve for luggage handle, and organize-it-all front panel.",
        "category": "bag",
        "price": 4990.0,
        "original_price": 7500.0,
        "discount": 33.0,
        "inventory": 50,
        "rating": 4.74,
        "review_count": 1400,
        "delivery_days": 1,
        "margin": 0.36,
        "features": [
            "Rugged 1680D Ballistic Polyester Weave",
            "SmartSleeve Slides Over Upright Luggage Handles",
            "Padded 15.6-inch Laptop & Tablet Protection",
            "Neoprene-Padded Top Carry Handles"
        ],
        "tags": [
            "bag",
            "briefcase",
            "samsonite",
            "laptop bag",
            "business",
            "formal",
            "office",
            "under 5000"
        ],
        "compatible_products": [
            "LP003",
            "SH009"
        ],
        "upsell_products": [
            "BAG004"
        ],
        "cross_sell_products": [
            "LP003",
            "SH009"
        ],
        "image_url": "https://images.unsplash.com/photo-1509762774605-f07235a08f1f?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "BAG007",
        "name": "Tomtoc Compact EDC Sling Bag for iPad Mini / Nintendo Switch (Water Resistant)",
        "brand": "Tomtoc",
        "description": "Ergonomic single-strap sling with Cordura ballistic nylon, Duraflex buckles, YKK waterproof zippers, and multi-compartment tech organization.",
        "category": "bag",
        "price": 3499.0,
        "original_price": 4999.0,
        "discount": 30.0,
        "inventory": 80,
        "rating": 4.86,
        "review_count": 3100,
        "delivery_days": 1,
        "margin": 0.4,
        "features": [
            "Military-Grade Cordura Ballistic Fabric",
            "YKK Waterproof Smooth Zippers & Duraflex Buckle",
            "Dedicated Padded Sleeve for iPad Mini / Kindle",
            "Minimalist Lightweight EDC Crossbody Design"
        ],
        "tags": [
            "bag",
            "sling",
            "tomtoc",
            "edc",
            "crossbody",
            "travel",
            "waterproof",
            "under 4000",
            "gift"
        ],
        "compatible_products": [
            "PH002",
            "EB001"
        ],
        "upsell_products": [
            "BAG004"
        ],
        "cross_sell_products": [
            "EB001",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "BAG008",
        "name": "Aer Travel Sling 2 Waterproof Crossbody Bag (Cordura Ballistic Nylon, 12L)",
        "brand": "Aer",
        "description": "Designed for streamlined city travel with padded 13\" laptop pocket, self-healing YKK AquaGuard zippers, and Fidlock magnetic quick-release strap.",
        "category": "bag",
        "price": 11999.0,
        "original_price": 14999.0,
        "discount": 20.0,
        "inventory": 20,
        "rating": 4.9,
        "review_count": 410,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "1680D Cordura Ballistic Nylon Exterior",
            "Fidlock Quick-Release Magnetic Shoulder Buckle",
            "Padded 13-inch MacBook Laptop Pocket",
            "YKK AquaGuard Weatherproof Exterior Zips"
        ],
        "tags": [
            "bag",
            "sling",
            "aer",
            "travel sling",
            "laptop sling",
            "cordura",
            "premium"
        ],
        "compatible_products": [
            "LP005",
            "ACC001"
        ],
        "upsell_products": [
            "BAG002"
        ],
        "cross_sell_products": [
            "LP005",
            "ACC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "BAG009",
        "name": "Wildcraft 45L Rucksack for Trekking & Outdoor Adventure (Rain Cover Included)",
        "brand": "Wildcraft",
        "description": "Ergonomic top-loading rucksack with internal aluminum frame support, ventilated back panel, hydration bladder sleeve, and attached rain cover.",
        "category": "bag",
        "price": 3299.0,
        "original_price": 5499.0,
        "discount": 40.0,
        "inventory": 90,
        "rating": 4.66,
        "review_count": 4800,
        "delivery_days": 1,
        "margin": 0.42,
        "features": [
            "45-Liter High Capacity Top-Loading Design",
            "Internal Aluminum Frame with Ergonomic Lumbar Pad",
            "Integrated High-Visibility Rain Cover",
            "Trekking Pole Loops & Hydration Bladder Port"
        ],
        "tags": [
            "bag",
            "rucksack",
            "wildcraft",
            "trekking",
            "hiking",
            "camping",
            "travel",
            "budget",
            "under 3500"
        ],
        "compatible_products": [
            "WAT004",
            "SH008"
        ],
        "upsell_products": [
            "BAG002"
        ],
        "cross_sell_products": [
            "WAT004",
            "SH008"
        ],
        "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC001",
        "name": "Anker Prime 100W GaN 3-Port Fast Wall Charger (2x USB-C, 1x USB-A, Foldable)",
        "brand": "Anker",
        "description": "Ultra-compact GaNPrime fast charger powering 3 devices simultaneously with ActiveShield 2.0 real-time temperature monitoring.",
        "category": "accessories",
        "price": 5999.0,
        "original_price": 7999.0,
        "discount": 25.0,
        "inventory": 80,
        "rating": 4.93,
        "review_count": 2900,
        "delivery_days": 1,
        "margin": 0.38,
        "features": [
            "100W Max Fast USB-C Power Delivery",
            "Power 3 Devices Simultaneously (2C + 1A)",
            "ActiveShield 2.0 Real-Time Thermal Guard",
            "43% Smaller than Original 96W MacBook Charger"
        ],
        "tags": [
            "accessories",
            "charger",
            "anker",
            "gan",
            "100w",
            "usb-c",
            "fast charging",
            "macbook charger",
            "iphone charger"
        ],
        "compatible_products": [
            "LP001",
            "LP005",
            "PH002",
            "EB001"
        ],
        "upsell_products": [
            "ACC003"
        ],
        "cross_sell_products": [
            "LP001",
            "PH002"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC002",
        "name": "Satechi 9-in-1 USB-C Multiport Adapter Hub (4K HDMI, Gigabit Ethernet, 100W PD)",
        "brand": "Satechi",
        "description": "Sleek aluminum hub featuring 4K 60Hz HDMI, gigabit Ethernet, USB-C 100W PD charging, SD/microSD slots, and 3x USB 3.0 ports.",
        "category": "accessories",
        "price": 6999.0,
        "original_price": 8999.0,
        "discount": 22.0,
        "inventory": 65,
        "rating": 4.88,
        "review_count": 1800,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "4K 60Hz HDMI Video Output",
            "Gigabit Ethernet RJ45 High-Speed Port",
            "100W USB-C Power Delivery Passthrough",
            "Micro/SD Card Readers & 3x USB-A 5Gbps"
        ],
        "tags": [
            "accessories",
            "hub",
            "satechi",
            "usb-c",
            "dock",
            "macbook",
            "laptop dongle",
            "hdmi 4k"
        ],
        "compatible_products": [
            "LP001",
            "LP003",
            "LP005"
        ],
        "upsell_products": [
            "ACC003"
        ],
        "cross_sell_products": [
            "LP005",
            "MON001"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC003",
        "name": "CalDigit TS4 Thunderbolt 4 Dock (18 Ports, 98W Charging, 8K Display Support)",
        "brand": "CalDigit",
        "description": "The ultimate workstation docking station with 18 ports, 98W host charging, 2.5GbE Ethernet, UHS-II SD/microSD, and dual 6K displays.",
        "category": "accessories",
        "price": 39990.0,
        "original_price": 45990.0,
        "discount": 13.0,
        "inventory": 15,
        "rating": 4.96,
        "review_count": 620,
        "delivery_days": 1,
        "margin": 0.25,
        "features": [
            "18 Comprehensive Workstation Ports",
            "Thunderbolt 4 / USB4 40Gbps High Bandwidth",
            "98W Power Delivery Host Laptop Fast Charging",
            "2.5 Gigabit High-Speed Ethernet Networking"
        ],
        "tags": [
            "accessories",
            "dock",
            "thunderbolt 4",
            "caldigit",
            "workstation",
            "coding",
            "developer setup",
            "premium"
        ],
        "compatible_products": [
            "LP001",
            "LP002",
            "MON001",
            "MON002"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "LP001",
            "MON002"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC004",
        "name": "Belkin BoostCharge Pro 3-in-1 MagSafe Wireless Charging Stand (15W Fast Charge)",
        "brand": "Belkin",
        "description": "Official Made for MagSafe 15W wireless charging stand for iPhone 15/14, fast charging for Apple Watch Ultra, and dedicated AirPods tray.",
        "category": "accessories",
        "price": 13999.0,
        "original_price": 15999.0,
        "discount": 12.0,
        "inventory": 35,
        "rating": 4.92,
        "review_count": 1420,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "Official Apple Made for MagSafe 15W Fast Charging",
            "Fast Wireless Charger for Apple Watch Series & Ultra",
            "Base Tray Wireless Pad for AirPods / Earbuds",
            "Architectural Stainless Steel Tree Design"
        ],
        "tags": [
            "accessories",
            "charger",
            "belkin",
            "magsafe",
            "wireless charger",
            "3-in-1",
            "apple stand",
            "desk setup"
        ],
        "compatible_products": [
            "PH002",
            "WAT001",
            "EB001"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "PH002",
            "WAT001",
            "EB001"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC005",
        "name": "Spigen Tough Armor Magnetic Case for iPhone 15 Pro (Air Cushion Drop Protection)",
        "brand": "Spigen",
        "description": "Mil-grade certified drop protection with Air Cushion Technology, built-in magnetic ring for full MagSafe compatibility, and reinforced kickstand.",
        "category": "accessories",
        "price": 2499.0,
        "original_price": 3999.0,
        "discount": 37.0,
        "inventory": 120,
        "rating": 4.88,
        "review_count": 5800,
        "delivery_days": 1,
        "margin": 0.45,
        "features": [
            "Extreme Dual-Layer TPU & Polycarbonate Protection",
            "Air Cushion Technology at All 4 Corners",
            "Integrated Magnetic MagSafe Compatibility Ring",
            "Reinforced Hands-Free Viewing Kickstand"
        ],
        "tags": [
            "accessories",
            "case",
            "spigen",
            "iphone case",
            "magsafe",
            "drop protection",
            "gift",
            "under 2500"
        ],
        "compatible_products": [
            "PH002"
        ],
        "upsell_products": [
            "ACC004"
        ],
        "cross_sell_products": [
            "PH002"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC006",
        "name": "MOFT Invisible Snap-On Ergonomic Laptop Stand with Dual Angle Adjustment",
        "brand": "MOFT",
        "description": "Ultra-thin 3mm adhesive stand holding up to 8kg, folds flat against laptop bottom, provides 25\u00b0 and 15\u00b0 healthy ergonomic viewing angles.",
        "category": "accessories",
        "price": 1999.0,
        "original_price": 2999.0,
        "discount": 33.0,
        "inventory": 90,
        "rating": 4.8,
        "review_count": 2800,
        "delivery_days": 1,
        "margin": 0.42,
        "features": [
            "Ultra-Thin 3mm Featherweight Profile",
            "Dual Height Elevation Angles: 25\u00b0 (3in) / 15\u00b0 (2in)",
            "Custom Removable Clean Adhesive Leaves Zero Residue",
            "Supports Heavy Laptops up to 8kg (17.4 lbs)"
        ],
        "tags": [
            "accessories",
            "stand",
            "moft",
            "laptop stand",
            "ergonomic",
            "macbook",
            "portable",
            "under 2000"
        ],
        "compatible_products": [
            "LP001",
            "LP005",
            "LP006"
        ],
        "upsell_products": [
            "ACC002"
        ],
        "cross_sell_products": [
            "LP005",
            "MS001"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC007",
        "name": "Orbitkey Premium Vegan Leather Desk Mat with Magnetic Cable Organizer (Large, Black)",
        "brand": "Orbitkey",
        "description": "Document hideaway underlayer for storing papers, magnetic cable holder to keep cords in place, water-resistant vegan leather surface.",
        "category": "accessories",
        "price": 5499.0,
        "original_price": 6999.0,
        "discount": 21.0,
        "inventory": 55,
        "rating": 4.9,
        "review_count": 1100,
        "delivery_days": 1,
        "margin": 0.35,
        "features": [
            "Water-Resistant Premium Vegan Leather Top",
            "Document Hideaway Underlayer Storage",
            "Magnetic Zinc Alloy Cable Holder Organizer",
            "Felt Base Protects Desk from Scratches"
        ],
        "tags": [
            "accessories",
            "desk mat",
            "orbitkey",
            "leather pad",
            "desk setup",
            "workspace",
            "keyboard pad",
            "mouse pad"
        ],
        "compatible_products": [
            "KB001",
            "KB002",
            "MS001"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "KB001",
            "MS001"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC008",
        "name": "SanDisk Extreme 1TB Portable External SSD (USB 3.2 Gen 2, Up to 1050MB/s, IP55)",
        "brand": "SanDisk",
        "description": "High-speed NVMe solid state performance with 1050MB/s read speeds, 2-meter drop protection, IP55 water and dust resistance, carabiner loop.",
        "category": "accessories",
        "price": 9499.0,
        "original_price": 14999.0,
        "discount": 37.0,
        "inventory": 70,
        "rating": 4.88,
        "review_count": 4200,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "Up to 1050MB/s Read & 1000MB/s Write Speed",
            "IP55 Water and Dust Resistance Rating",
            "Rugged Silicone Shell with 2-Meter Drop Protection",
            "Carabiner Loop for Easy Travel Attachment"
        ],
        "tags": [
            "accessories",
            "ssd",
            "sandisk",
            "storage",
            "portable ssd",
            "nvme",
            "backup",
            "camera storage",
            "fast storage"
        ],
        "compatible_products": [
            "LP001",
            "CAM001",
            "CAM003"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "LP001",
            "CAM001"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC009",
        "name": "Anker 737 Power Bank PowerCore 24K (24,000mAh 140W Ultra-Fast 3-Port Portable Charger)",
        "brand": "Anker",
        "description": "Equipped with Power Delivery 3.1 and bi-directional 140W fast charging, smart digital display showing power output/input and health.",
        "category": "accessories",
        "price": 12999.0,
        "original_price": 16999.0,
        "discount": 23.0,
        "inventory": 30,
        "rating": 4.93,
        "review_count": 1650,
        "delivery_days": 1,
        "margin": 0.28,
        "features": [
            "140W Ultra-Powerful Two-Way Fast Charging",
            "Smart Digital Display Shows Power & Recharging Time",
            "Massive 24,000mAh Capacity Charges iPhone 5 Times",
            "ActiveShield 2.0 Thermal Temperature Protection"
        ],
        "tags": [
            "accessories",
            "power bank",
            "anker",
            "140w",
            "portable charger",
            "laptop power bank",
            "travel"
        ],
        "compatible_products": [
            "LP001",
            "PH002",
            "WAT001"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "LP001",
            "PH002"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "ACC010",
        "name": "BenQ ScreenBar Halo Wireless Controller LED Monitor Light Bar",
        "brand": "BenQ",
        "description": "Patented optical design illuminates desk space without screen glare, smart wireless dial controller, back ambient light, auto-dimming.",
        "category": "accessories",
        "price": 15990.0,
        "original_price": 18990.0,
        "discount": 15.0,
        "inventory": 25,
        "rating": 4.91,
        "review_count": 780,
        "delivery_days": 1,
        "margin": 0.3,
        "features": [
            "Asymmetric Optical Design Ensures Zero Screen Glare",
            "Wireless Desktop Rotary Dial Controller",
            "Front Light + Rear Backlight Dual Illumination",
            "Built-In Ambient Light Sensor for Auto-Dimming"
        ],
        "tags": [
            "accessories",
            "light",
            "benq",
            "screenbar",
            "monitor light",
            "desk setup",
            "eye care",
            "wfh"
        ],
        "compatible_products": [
            "MON001",
            "MON002",
            "MON004"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "MON001",
            "KB001"
        ],
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "DEC001",
        "name": "Metallic Pastel Latex Party Balloons Set (Pack of 100 with Arch Tape & Dual-Action Pump)",
        "brand": "CelebrationsPro",
        "description": "Premium 12-inch durable biodegradable latex balloons in pastel chrome colors, includes 16ft garland arch tape, glue dots, and inflation pump.",
        "category": "decor",
        "price": 399.0,
        "original_price": 999.0,
        "discount": 60.0,
        "inventory": 150,
        "rating": 4.75,
        "review_count": 2800,
        "delivery_days": 1,
        "margin": 0.45,
        "features": [
            "100 Pcs Premium Biodegradable Latex",
            "Pastel Rainbow Metallic Chrome Assortment",
            "16ft Arch Tape & 100 Glue Dots Included",
            "Dual-Action Fast Air Pump Included"
        ],
        "tags": [
            "balloons",
            "decor",
            "party",
            "birthday",
            "celebration",
            "balloon",
            "budget",
            "under 500",
            "arch",
            "gift"
        ],
        "compatible_products": [
            "DEC002"
        ],
        "upsell_products": [
            "DEC002"
        ],
        "cross_sell_products": [
            "DEC002"
        ],
        "image_url": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "DEC002",
        "name": "Happy Birthday Golden Foil Helium Balloons & Fairy String Lights Combo",
        "brand": "PartyGlow",
        "description": "16-inch golden 3D alphabet foil banner, 20 LED warm fairy string lights, star and heart foil accents for birthday celebrations.",
        "category": "decor",
        "price": 499.0,
        "original_price": 1299.0,
        "discount": 61.0,
        "inventory": 120,
        "rating": 4.82,
        "review_count": 1950,
        "delivery_days": 1,
        "margin": 0.48,
        "features": [
            "13 Pcs 16-inch Golden Foil Letters",
            "20 LED Warm White Fairy Lights (3 Meters)",
            "2 Foil Star Balloons + 2 Foil Heart Balloons",
            "Reusable Self-Sealing Valve Technology"
        ],
        "tags": [
            "balloons",
            "decor",
            "party",
            "birthday",
            "lights",
            "celebration",
            "golden foil",
            "under 500",
            "gift"
        ],
        "compatible_products": [
            "DEC001"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "DEC001"
        ],
        "image_url": "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "APP001",
        "name": "LG 8.0 Kg 5 Star AI Direct Drive Front Loading Washing Machine with Steam (FHP1208Z5W)",
        "brand": "LG",
        "description": "AI DD technology detects fabric softness and optimal wash motions, 6 Motion Direct Drive, Steam allergy care removes 99.9% allergens.",
        "category": "appliances",
        "price": 34990.0,
        "original_price": 44990.0,
        "discount": 22.0,
        "inventory": 20,
        "rating": 4.88,
        "review_count": 1420,
        "delivery_days": 2,
        "margin": 0.25,
        "features": [
            "AI Direct Drive Intelligent Fabric Care",
            "Steam Allergy Care 99.9% Allergen Reduction",
            "6 Motion Direct Drive Drum Technology",
            "5 Star Energy Rating with 10-Year Motor Warranty"
        ],
        "tags": [
            "washing machine",
            "appliances",
            "lg",
            "front load",
            "ai direct drive",
            "home appliances",
            "steam wash",
            "laundry"
        ],
        "compatible_products": [
            "APP003"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "APP003"
        ],
        "image_url": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "APP002",
        "name": "Samsung 7.0 Kg EcoBubble Top Load Washing Machine with Hygiene Steam (WA70BG4441YY)",
        "brand": "Samsung",
        "description": "EcoBubble technology turns detergent into bubbles for faster fabric penetration, Digital Inverter motor with 20-year warranty, Super Speed wash.",
        "category": "appliances",
        "price": 18490.0,
        "original_price": 24500.0,
        "discount": 24.0,
        "inventory": 30,
        "rating": 4.76,
        "review_count": 2100,
        "delivery_days": 2,
        "margin": 0.28,
        "features": [
            "EcoBubble Technology for Gentle Clean",
            "Hygiene Steam Cycle Eliminates Bacteria",
            "Digital Inverter Technology with 20-Yr Warranty",
            "Magic Filter Traps Fluff and Lint"
        ],
        "tags": [
            "washing machine",
            "appliances",
            "samsung",
            "top load",
            "ecobubble",
            "budget washer",
            "under 20000"
        ],
        "compatible_products": [
            "APP003"
        ],
        "upsell_products": [
            "APP001"
        ],
        "cross_sell_products": [
            "APP003"
        ],
        "image_url": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "APP003",
        "name": "LG 242L 3 Star Smart Inverter Double Door Frost-Free Refrigerator",
        "brand": "LG",
        "description": "Smart Inverter Compressor for quiet energy efficiency, Multi Air Flow cooling, Toughened Glass shelves, and Moist 'N' Fresh lattice vegetable box.",
        "category": "appliances",
        "price": 25990.0,
        "original_price": 31990.0,
        "discount": 18.0,
        "inventory": 25,
        "rating": 4.82,
        "review_count": 1800,
        "delivery_days": 2,
        "margin": 0.26,
        "features": [
            "Smart Inverter Compressor Energy Efficient",
            "Multi Air Flow Vents at Every Level",
            "Toughened Glass Spill-Proof Shelves",
            "Smart Diagnosis Troubleshooting Feature"
        ],
        "tags": [
            "appliances",
            "fridge",
            "refrigerator",
            "lg",
            "double door",
            "frost free",
            "home appliances"
        ],
        "compatible_products": [
            "APP001"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "APP001"
        ],
        "image_url": "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "APP004",
        "name": "Daikin 1.5 Ton 5 Star Inverter Split Air Conditioner with PM 2.5 Filter",
        "brand": "Daikin",
        "description": "Triple Display with Power Chill operation, Copper Condenser with Anti-Corrosion Treatment, Dew Clean technology, PM 2.5 air purification.",
        "category": "appliances",
        "price": 44990.0,
        "original_price": 54990.0,
        "discount": 18.0,
        "inventory": 18,
        "rating": 4.86,
        "review_count": 1250,
        "delivery_days": 2,
        "margin": 0.24,
        "features": [
            "Neo Swing Inverter Compressor Technology",
            "Dew Clean Technology Cleans Evaporator Coil",
            "PM 2.5 Microscopic Air Filtration",
            "5 Star Highest ISEER Energy Rating"
        ],
        "tags": [
            "appliances",
            "ac",
            "air conditioner",
            "daikin",
            "inverter ac",
            "5 star",
            "cooling"
        ],
        "compatible_products": [],
        "upsell_products": [],
        "cross_sell_products": [
            "APP001"
        ],
        "image_url": "https://images.unsplash.com/photo-1614633833026-0820552978b6?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PIN001",
        "name": "Stainless Steel Premium Safety Pins Set (Pack of 100 Assorted Sizes)",
        "brand": "CraftPro",
        "description": "Heavy duty nickel-plated rust-resistant safety pins in 4 versatile sizes with safety clasp locks for fabric, sewing, garments, and daily tailoring.",
        "category": "stationery",
        "price": 149.0,
        "original_price": 299.0,
        "discount": 50.0,
        "inventory": 200,
        "rating": 4.88,
        "review_count": 3420,
        "delivery_days": 1,
        "margin": 0.45,
        "features": [
            "Rust Resistant Nickel Plated Finish",
            "4 Assorted Standard Sizes Included",
            "Safe Protective Clasp Lock Design",
            "Durable Spring Tension Retention"
        ],
        "tags": [
            "pin",
            "pins",
            "safety pin",
            "safety pins",
            "stationery",
            "tailoring",
            "craft",
            "household"
        ],
        "compatible_products": [
            "PIN002"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "PIN002"
        ],
        "image_url": "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PIN002",
        "name": "Multi-Color Thumb Push Pins & Notice Board Pins (Box of 100)",
        "brand": "OfficeMaster",
        "description": "Sharp steel point colored head push pins for bulletin boards, cork notice boards, map marking, photo hanging, and office organization.",
        "category": "stationery",
        "price": 129.0,
        "original_price": 249.0,
        "discount": 48.0,
        "inventory": 150,
        "rating": 4.82,
        "review_count": 1890,
        "delivery_days": 1,
        "margin": 0.42,
        "features": [
            "Hardened Steel Sharp Point",
            "Vibrant Multi-Color Grip Heads",
            "Transparent Storage Box Included",
            "Firm Cork Board Grip Hold"
        ],
        "tags": [
            "pin",
            "pins",
            "push pin",
            "board pin",
            "thumb pin",
            "stationery",
            "office"
        ],
        "compatible_products": [
            "PIN001"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "PIN001"
        ],
        "image_url": "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?w=600&auto=format&fit=crop&q=70"
    },
    {
        "product_id": "PIN003",
        "name": "Designer Metallic Hair Bobby Pins & Clips (Pack of 48)",
        "brand": "GlamStyling",
        "description": "Non-slip grip curved hair pins with protective rounded ball tips to prevent scalp scratching. Perfect for bridal styling, buns, and everyday hair holding.",
        "category": "accessories",
        "price": 199.0,
        "original_price": 399.0,
        "discount": 50.0,
        "inventory": 120,
        "rating": 4.9,
        "review_count": 2410,
        "delivery_days": 1,
        "margin": 0.48,
        "features": [
            "Rounded Protective Ball Tip Ends",
            "Reinforced Spring Holding Grip",
            "Electroplated Metallic Gloss Finish",
            "Pack of 48 in Travel Compact Box"
        ],
        "tags": [
            "pin",
            "pins",
            "hair pin",
            "hair pins",
            "bobby pin",
            "clips",
            "accessories",
            "women styling"
        ],
        "compatible_products": [
            "PIN001"
        ],
        "upsell_products": [],
        "cross_sell_products": [
            "PIN001"
        ],
        "image_url": "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?w=600&auto=format&fit=crop&q=70"
    }
]

def get_image_for_query(query: str) -> str:
    ql = query.lower()
    if any(w in ql for w in ["sketch", "sketching", "sketch pen", "sketch pens", "crayons", "drawing", "art pencil"]):
        return "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["pencil", "pencils", "lead pencil", "wooden pencil"]):
        return "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["eraser", "sharpener", "dust free eraser"]):
        return "https://images.unsplash.com/photo-1588072432836-e10032774350?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["pen", "pens", "ball pen", "gel pen", "marker", "highlighter", "kalam"]):
        return "https://images.unsplash.com/photo-1569683795645-b62e50fbf103?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["notebook", "spiral notebook", "diary", "register", "copy", "book", "kitab", "pustak"]):
        return "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["soap", "bathing soap", "shampoo", "body wash", "handwash", "sabun"]):
        return "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["toothbrush", "toothpaste", "comb", "hair brush"]):
        return "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["chocolate", "candy", "biscuit", "biscuits", "maggi", "noodles", "chips", "snack"]):
        return "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["basket", "baskets", "storage basket", "wicker basket", "laundry basket", "fruit basket"]):
        return "https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["football", "soccer", "volleyball", "basketball", "ball"]):
        return "https://images.unsplash.com/photo-1614632537423-1e6c2e7e0aab?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["cricket", "bat", "badminton", "racket", "shuttlecock"]):
        return "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["drill", "tools", "hammer", "screwdriver", "wrench", "toolkit", "hardware"]):
        return "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["helmet", "bike helmet", "riding helmet"]):
        return "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["carpet", "rug", "mat", "floor mat"]):
        return "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["teddy bear", "soft toy", "doll", "plushie", "gudiya"]):
        return "https://images.unsplash.com/photo-1559454403-b8fb88521f11?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["mango", "fruit", "fruits", "banana", "apple fruit", "orange", "vegetables", "grocery", "aam", "seb", "kela"]):
        return "https://images.unsplash.com/photo-1553279768-865429fa0078?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["drone", "quadcopter"]):
        return "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["safety pin", "hair pin", "bobby pin", "paper clip", "board pin", "brooch", "lapel pin", "pin", "pins"]):
        return "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["stationery", "stapler", "scissors", "tape", "glue", "geometry box", "compass", "scale"]):
        return "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["bottle", "water bottle", "flask", "sipper", "thermos", "tumbler", "shaker"]):
        return "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["mug", "cup", "coffee mug", "tea cup", "glass", "cups"]):
        return "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["plate", "bowl", "spoon", "fork", "cutlery", "dinner set", "crockery", "knife", "utensil", "bartan", "thali", "katori", "chammach"]):
        return "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["fan", "ceiling fan", "table fan", "exhaust fan", "pedestal fan", "pankha"]):
        return "https://images.unsplash.com/photo-1618941716939-553df3c6c278?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["bulb", "lamp", "light", "led light", "night lamp", "lantern", "tubelight", "strip light"]):
        return "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["pillow", "cushion", "bedsheet", "blanket", "comforter", "curtain", "mattress cover", "bedsheet set"]):
        return "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["mirror", "wall mirror", "makeup mirror", "vanity mirror"]):
        return "https://images.unsplash.com/photo-1618220179428-22790b461013?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["umbrella", "raincoat", "windcheater", "chhatri"]):
        return "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["towel", "bath towel", "hand towel", "bathrobe", "face towel"]):
        return "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["comb", "hair brush", "hair oil", "shampoo", "conditioner", "soap", "body wash", "face wash"]):
        return "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["wallet", "purse", "belt", "leather belt", "card holder"]):
        return "https://images.unsplash.com/photo-1627123424574-724758594e93?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["sunglasses", "goggles", "spectacles", "eyewear", "aviator", "chashma", "chashme"]):
        return "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["plant", "flower", "indoor plant", "pot", "planter", "seeds", "succulent", "vase"]):
        return "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["clock", "wall clock", "alarm clock", "digital clock", "timer"]):
        return "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["balloon", "balloons", "party", "birthday", "arch", "decor", "celebration", "candle"]):
        return "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["washing machine", "washer", "dryer", "laundry", "front load", "top load"]):
        return "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["iphone", "apple phone", "ios", "iphone 15", "iphone 16"]):
        return "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["phone", "smartphone", "galaxy", "samsung", "pixel", "mobile", "5g", "oneplus", "redmi", "xiaomi"]):
        return "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["earbuds", "airpods", "tws", "in-ear", "buds", "earphones"]):
        return "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["headphone", "headphones", "anc", "audio", "headset", "studio monitor"]):
        return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["laptop", "macbook", "notebook", "computer", "pc", "thinkpad", "gaming laptop", "asus", "dell"]):
        return "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["keyboard", "mechanical", "keycaps", "switches", "tenkeyless", "rgb keyboard"]):
        return "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["mouse", "trackpad", "vertical mouse", "gaming mouse", "ergonomic mouse"]):
        return "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["monitor", "display", "screen", "4k", "ultrawide", "oled"]):
        return "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["watch", "smartwatch", "fitness band", "garmin", "apple watch", "galaxy watch", "ghadi"]):
        return "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["camera", "dslr", "mirrorless", "gimbal", "webcam", "gopro", "drone", "tripod"]):
        return "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["shoe", "shoes", "sneaker", "sneakers", "boots", "running", "footwear", "pegasus", "ultraboost", "nike", "adidas", "jhootha", "jhoota", "joota", "joote", "juta", "jute", "chappal", "sandals", "slippers", "mojdi"]):
        return "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["bag", "backpack", "duffel", "luggage", "tote", "sling", "briefcase", "travel bag"]):
        return "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["charger", "hub", "dock", "cable", "pad", "mat", "desk mat", "accessory", "accessories", "stand", "power bank"]):
        return "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["fridge", "refrigerator", "deep freezer"]):
        return "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["lipstick", "lip balm", "lip gloss"]):
        return "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["makeup", "cosmetics", "eyeliner", "mascara", "foundation", "blush", "eyeshadow", "beauty"]):
        return "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["perfume", "fragrance", "cologne", "scent", "deodorant"]):
        return "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["skincare", "serum", "lotion", "cream", "moisturizer", "sunscreen"]):
        return "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["chocolate", "candy", "snacks", "biscuit", "cookie", "chocolates"]):
        return "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["dress", "saree", "kurti", "gown", "maxi", "skirt", "lehenga", "women wear", "top", "kapda", "kapde", "vastra", "shirt", "tshirt"]):
        return "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["hair dryer", "trimmer", "shaver", "grooming"]):
        return "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["toy", "toys", "lego", "puzzle", "board game", "action figure", "doll", "remote control"]):
        return "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["chair", "office chair", "sofa", "furniture", "desk", "table", "bed", "mattress", "wardrobe"]):
        return "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["ring", "diamond", "gold", "necklace", "earrings", "jewelry", "bracelet", "pendant"]):
        return "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["guitar", "piano", "drums", "violin", "musical", "synthesizer", "ukulele"]):
        return "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["cycle", "bicycle", "treadmill", "gym", "fitness", "dumbbells", "yoga", "protein"]):
        return "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["book", "novel", "diary", "pen", "stationery", "notebook", "art"]):
        return "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=70"
    elif any(w in ql for w in ["tv", "television", "smart tv", "led tv", "qled"]):
        return "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=600&auto=format&fit=crop&q=70"
    else:
        return "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&auto=format&fit=crop&q=70"

class ProductCatalogue:
    """Agent-Readable High-Converting Storefront Product Catalogue (114+ SKUs)."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {p["product_id"]: p for p in SEED_PRODUCTS}

    def seed_db(self, db: Session):
        for sp in SEED_PRODUCTS:
            existing = db.query(Product).filter(Product.product_id == sp["product_id"]).first()
            if not existing:
                p = Product(
                    product_id=sp["product_id"],
                    name=sp["name"],
                    description=sp["description"],
                    category=sp["category"],
                    price=sp["price"],
                    discount=sp.get("discount", 0.0),
                    inventory=sp.get("inventory", 50),
                    rating=sp.get("rating", 4.8),
                    margin=sp.get("margin", 0.25),
                    features=sp.get("features", []),
                    tags=sp.get("tags", []),
                    compatible_products=sp.get("compatible_products", []),
                    upsell_products=sp.get("upsell_products", []),
                    cross_sell_products=sp.get("cross_sell_products", []),
                    image_url=sp.get("image_url"),
                    is_active=True
                )
                db.add(p)
            else:
                existing.name = sp["name"]
                existing.description = sp["description"]
                existing.category = sp["category"]
                existing.price = sp["price"]
                existing.discount = sp.get("discount", 0.0)
                existing.inventory = sp.get("inventory", 50)
                existing.rating = sp.get("rating", 4.8)
                existing.margin = sp.get("margin", 0.25)
                existing.features = sp.get("features", [])
                existing.tags = sp.get("tags", [])
                existing.compatible_products = sp.get("compatible_products", [])
                existing.upsell_products = sp.get("upsell_products", [])
                existing.cross_sell_products = sp.get("cross_sell_products", [])
                existing.image_url = sp.get("image_url")
        db.commit()

    def get_all_products(self, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        if db:
            db_prods = db.query(Product).filter(Product.is_active == True).all()
            if db_prods:
                res = []
                for p in db_prods:
                    seed = self._cache.get(p.product_id, {})
                    orig = seed.get("original_price", round(p.price / max(0.01, 1 - (p.discount or 0)/100), 2))
                    res.append({
                        "id": p.product_id,
                        "product_id": p.product_id,
                        "name": p.name,
                        "brand": seed.get("brand", "ProTech"),
                        "description": p.description,
                        "category": p.category,
                        "price": p.price,
                        "original_price": orig,
                        "discount": p.discount,
                        "inventory": p.inventory,
                        "stock": p.inventory,
                        "rating": p.rating,
                        "review_count": seed.get("review_count", 120),
                        "delivery_days": seed.get("delivery_days", 1),
                        "margin": p.margin,
                        "specifications": p.features or [],
                        "features": p.features or [],
                        "tags": p.tags or [],
                        "compatible_products": p.compatible_products or [],
                        "upsell_products": p.upsell_products or [],
                        "cross_sell_products": p.cross_sell_products or [],
                        "image": p.image_url,
                        "image_url": p.image_url,
                        "is_active": p.is_active
                    })
                return res
        res = []
        for p in self._cache.values():
            orig = p.get("original_price", round(p["price"] / max(0.01, 1 - (p.get("discount", 0)/100)), 2))
            res.append({
                "id": p["product_id"],
                "product_id": p["product_id"],
                "name": p["name"],
                "brand": p.get("brand", "ProTech"),
                "description": p["description"],
                "category": p["category"],
                "price": p["price"],
                "original_price": orig,
                "discount": p.get("discount", 0.0),
                "inventory": p.get("inventory", 50),
                "stock": p.get("inventory", 50),
                "rating": p.get("rating", 4.8),
                "review_count": p.get("review_count", 120),
                "delivery_days": p.get("delivery_days", 1),
                "margin": p.get("margin", 0.25),
                "specifications": p.get("features", []),
                "features": p.get("features", []),
                "tags": p.get("tags", []),
                "compatible_products": p.get("compatible_products", []),
                "upsell_products": p.get("upsell_products", []),
                "cross_sell_products": p.get("cross_sell_products", []),
                "image": p.get("image_url"),
                "image_url": p.get("image_url"),
                "is_active": p.get("is_active", True)
            })
        return res

    def get_product(self, product_id: str, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        seed = self._cache.get(product_id, {})
        if db:
            p = db.query(Product).filter(Product.product_id == product_id).first()
            if p:
                orig = seed.get("original_price", round(p.price / max(0.01, 1 - (p.discount or 0)/100), 2))
                return {
                    "id": p.product_id,
                    "product_id": p.product_id,
                    "name": p.name,
                    "brand": seed.get("brand", "ProTech"),
                    "description": p.description,
                    "category": p.category,
                    "price": p.price,
                    "original_price": orig,
                    "discount": p.discount,
                    "inventory": p.inventory,
                    "stock": p.inventory,
                    "rating": p.rating,
                    "review_count": seed.get("review_count", 120),
                    "delivery_days": seed.get("delivery_days", 1),
                    "margin": p.margin,
                    "specifications": p.features or [],
                    "features": p.features or [],
                    "tags": p.tags or [],
                    "compatible_products": p.compatible_products or [],
                    "upsell_products": p.upsell_products or [],
                    "cross_sell_products": p.cross_sell_products or [],
                    "image": p.image_url,
                    "image_url": p.image_url,
                    "is_active": p.is_active
                }
        if product_id in self._cache:
            p = self._cache[product_id]
            orig = p.get("original_price", round(p["price"] / max(0.01, 1 - (p.get("discount", 0)/100)), 2))
            return {
                "id": p["product_id"],
                "product_id": p["product_id"],
                "name": p["name"],
                "brand": p.get("brand", "ProTech"),
                "description": p["description"],
                "category": p["category"],
                "price": p["price"],
                "original_price": orig,
                "discount": p.get("discount", 0.0),
                "inventory": p.get("inventory", 50),
                "stock": p.get("inventory", 50),
                "rating": p.get("rating", 4.8),
                "review_count": p.get("review_count", 120),
                "delivery_days": p.get("delivery_days", 1),
                "margin": p.get("margin", 0.25),
                "specifications": p.get("features", []),
                "features": p.get("features", []),
                "tags": p.get("tags", []),
                "compatible_products": p.get("compatible_products", []),
                "upsell_products": p.get("upsell_products", []),
                "cross_sell_products": p.get("cross_sell_products", []),
                "image": p.get("image_url"),
                "image_url": p.get("image_url"),
                "is_active": p.get("is_active", True)
            }
        return None

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        brand: Optional[str] = None,
        min_rating: Optional[float] = None,
        tag: Optional[str] = None,
        in_stock_only: bool = False,
        sort_by: Optional[str] = None,
        db: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        products = self.get_all_products(db)
        results = []

        query_tokens = [q.lower().strip() for q in query.split() if len(q) > 1] if query else []

        for p in products:
            if in_stock_only and p.get("inventory", 0) <= 0:
                continue

            if category and category.lower() not in ("all", ""):
                cat_l = category.lower()
                prod_cat = p.get("category", "").lower()
                # Category aliases
                if cat_l in ("keyboard", "keyboards") and prod_cat != "keyboard":
                    continue
                elif cat_l in ("mouse", "mice") and prod_cat != "mouse":
                    continue
                elif cat_l in ("headphones", "headphone", "audio") and prod_cat not in ("headphones", "earbuds"):
                    continue
                elif cat_l in ("earbuds", "earbud") and prod_cat != "earbuds":
                    continue
                elif cat_l in ("laptop", "laptops") and prod_cat != "laptop":
                    continue
                elif cat_l in ("phone", "phones", "smartphones", "smartphone") and prod_cat != "phone":
                    continue
                elif cat_l in ("monitor", "monitors", "display") and prod_cat != "monitor":
                    continue
                elif cat_l in ("smartwatch", "smartwatches", "watch", "watches") and prod_cat != "smartwatch":
                    continue
                elif cat_l in ("camera", "cameras") and prod_cat != "camera":
                    continue
                elif cat_l in ("shoes", "shoe", "footwear") and prod_cat != "shoes":
                    continue
                elif cat_l in ("bag", "bags", "backpack") and prod_cat != "bag":
                    continue
                elif cat_l in ("accessories", "accessory") and prod_cat != "accessories":
                    continue
                elif cat_l in ("decor", "balloon", "balloons") and prod_cat != "decor":
                    continue
                elif cat_l in ("appliances", "appliance", "washing machine") and prod_cat != "appliances":
                    continue

            if max_price is not None and p["price"] > max_price:
                continue

            if min_price is not None and p["price"] < min_price:
                continue

            if brand and brand.lower() not in p.get("brand", "").lower():
                continue

            if min_rating is not None and p.get("rating", 0) < min_rating:
                continue

            if tag and tag.lower() not in [t.lower() for t in p.get("tags", [])]:
                continue

            if query_tokens:
                combined_text = f"{p['name']} {p.get('brand', '')} {p['description']} {' '.join(p.get('tags', []))} {p['category']}".lower()
                matches = 0
                for tok in query_tokens:
                    if len(tok) <= 3:
                        if re.search(r'' + re.escape(tok) + r'', combined_text):
                            matches += 1
                    else:
                        if tok in combined_text:
                            matches += 1
                min_required = len(query_tokens)
                if matches < min_required:
                    continue

            results.append(p)

        # Dynamic fallback if no exact items match the open-ended search query
        if not results and query:
            words = [w for w in re.findall(r'[a-zA-Z0-9]+', query) if w.lower() not in ("under", "show", "need", "i", "want", "for", "best", "find", "good", "cheap", "premium", "please", "can", "you", "me")]
            dedup_words = []
            for w in words:
                if not dedup_words or w.lower() != dedup_words[-1].lower():
                    dedup_words.append(w.title())
            clean_q = " ".join(dedup_words) or query.strip().title()
            ql = query.lower()
            img_url = get_image_for_query(query)
            
            # Determine realistic base price by category
            if any(w in ql for w in ["pencil", "pencils", "lead pencil", "wooden pencil"]):
                base_p = 10.0
            elif any(w in ql for w in ["safety pin", "pin", "pins", "paper clip", "clips", "rubber band", "eraser", "sharpener"]):
                base_p = 10.0
            elif any(w in ql for w in ["sketch", "sketch pen", "sketch pens", "sketchbook", "drawing pencil", "crayons", "color pencil"]):
                base_p = 49.0
            elif any(w in ql for w in ["pen", "ball pen", "gel pen", "marker", "highlighter", "ruler", "scale", "glue", "fevicol", "tape"]):
                base_p = 20.0
            elif any(w in ql for w in ["soap", "shampoo sachet", "matchbox", "biscuit", "biscuits", "parle-g", "maggi", "maggie", "noodles"]):
                base_p = 20.0
            elif any(w in ql for w in ["notebook", "spiral notebook", "copy", "register", "chart paper", "scissors", "fevistick"]):
                base_p = 45.0
            elif any(w in ql for w in ["chocolate", "dairy milk", "kitkat", "snickers", "chips", "lays", "kurkure", "namkeen", "tea", "coffee"]):
                base_p = 50.0
            elif any(w in ql for w in ["comb", "toothbrush", "toothpaste", "hand sanitizer", "mask"]):
                base_p = 40.0
            elif any(w in ql for w in ["water bottle", "bottle", "mug", "cup", "plate", "spoon", "fork", "knife", "towel", "socks"]):
                base_p = 149.0
            elif any(w in ql for w in ["basket", "baskets", "storage basket", "mango", "fruit", "fruits", "vegetables"]):
                base_p = 199.0
            elif any(w in ql for w in ["lipstick", "lip balm", "eyeliner", "kajal", "nail polish", "compact powder"]):
                base_p = 249.0
            elif any(w in ql for w in ["t-shirt", "tshirt", "shirt", "cap", "belt", "wallet", "pillow", "cushion", "umbrella"]):
                base_p = 399.0
            elif any(w in ql for w in ["football", "ball", "soft toy", "teddy bear", "badminton racket"]):
                base_p = 499.0
            elif any(w in ql for w in ["cricket bat", "bat", "helmet", "carpet", "rug", "curtain", "bedsheet"]):
                base_p = 899.0
            elif any(w in ql for w in ["shoes", "sneakers", "jhootha", "jhoota", "joota", "joote", "juta", "jute", "chappal", "sandals", "bag", "backpack", "perfume", "dress", "saree", "jeans", "jacket"]):
                base_p = 999.0
            elif any(w in ql for w in ["earbuds", "headphones", "smartwatch", "hair dryer", "trimmer"]):
                base_p = 1499.0
            elif any(w in ql for w in ["keyboard", "mouse", "mixer", "grinder", "cooker", "pan", "air fryer"]):
                base_p = 1999.0
            elif any(w in ql for w in ["drill", "power drill", "tools", "toolkit", "camera", "drone"]):
                base_p = 2499.0
            elif any(w in ql for w in ["monitor", "display", "tv", "television"]):
                base_p = 9999.0
            elif any(w in ql for w in ["washing machine", "refrigerator", "fridge", "ac", "air conditioner"]):
                base_p = 24990.0
            elif any(w in ql for w in ["phone", "smartphone", "mobile"]):
                base_p = 14999.0
            elif any(w in ql for w in ["laptop", "macbook", "computer"]):
                base_p = 49990.0
            elif any(w in ql for w in ["iphone", "apple"]):
                base_p = 79900.0
            else:
                base_p = 299.0

            if max_price:
                base_p = min(base_p, max_price * 0.95)

            if base_p <= 20:
                p1 = base_p
                p2 = round(base_p * 1.5)
                p3 = round(base_p * 3.0)
                p4 = round(base_p * 5.0)
            elif base_p <= 100:
                p1 = base_p
                p2 = round(base_p * 0.8)
                p3 = round(base_p * 1.5)
                p4 = round(base_p * 2.0)
            elif base_p <= 1000:
                p1 = round(base_p, -1)
                p2 = round(base_p * 0.75, -1)
                p3 = round(base_p * 1.4, -1)
                p4 = round(base_p * 0.50, -1)
            else:
                p1 = round(base_p, -2)
                p2 = round(base_p * 0.8, -2)
                p3 = round(base_p * 1.3, -2)
                p4 = round(base_p * 0.6, -2)

            results = [
                {
                    "id": f"DYN_{abs(hash(query)) % 100000}",
                    "product_id": f"DYN_{abs(hash(query)) % 100000}",
                    "name": f"Top-Rated {clean_q} (Pro Edition)",
                    "brand": "ProSelect",
                    "description": f"Top rated {clean_q} featuring verified 1-day express delivery, 1-year brand warranty, and 5-star customer ratings.",
                    "category": "store",
                    "price": p1,
                    "original_price": round(p1 * 1.30, 2),
                    "discount": 23.0,
                    "inventory": 50,
                    "stock": 50,
                    "rating": 4.92,
                    "review_count": 2180,
                    "delivery_days": 1,
                    "margin": 0.35,
                    "specifications": ["Top Verified Quality", "100% Genuine Brand Assurance", "1-Day Fast Express SLA", "Easy 7-Day Replacement"],
                    "features": ["Top Verified Quality", "100% Genuine Brand Assurance", "1-Day Fast Express SLA", "Easy 7-Day Replacement"],
                    "tags": [query.lower(), "trending", "bestseller", "top-rated"],
                    "compatible_products": ["ACC001"],
                    "upsell_products": [],
                    "cross_sell_products": ["ACC001"],
                    "image": img_url,
                    "image_url": img_url,
                    "is_active": True
                },
                {
                    "id": f"DYN_{(abs(hash(query)) + 1) % 100000}",
                    "product_id": f"DYN_{(abs(hash(query)) + 1) % 100000}",
                    "name": f"Essential {clean_q} (Value Pack)",
                    "brand": "SmartChoice",
                    "description": f"Best-value {clean_q} with high durability, tested quality, and thousands of 5-star customer reviews.",
                    "category": "store",
                    "price": p2,
                    "original_price": round(p2 * 1.25, 2),
                    "discount": 20.0,
                    "inventory": 85,
                    "stock": 85,
                    "rating": 4.78,
                    "review_count": 1420,
                    "delivery_days": 1,
                    "margin": 0.40,
                    "specifications": ["Best Value For Money", "Durable Lightweight Design", "Cash on Delivery Available"],
                    "features": ["Best Value For Money", "Durable Lightweight Design", "Cash on Delivery Available"],
                    "tags": [query.lower(), "value", "budget", "popular"],
                    "compatible_products": ["ACC001"],
                    "upsell_products": [],
                    "cross_sell_products": ["ACC001"],
                    "image": img_url,
                    "image_url": img_url,
                    "is_active": True
                },
                {
                    "id": f"DYN_{(abs(hash(query)) + 2) % 100000}",
                    "product_id": f"DYN_{(abs(hash(query)) + 2) % 100000}",
                    "name": f"Ultra-Premium {clean_q} (Flagship Series)",
                    "brand": "UltraCraft",
                    "description": f"Luxury flagship {clean_q} engineered with aircraft-grade materials, precision performance, and VIP concierge warranty.",
                    "category": "store",
                    "price": p3,
                    "original_price": round(p3 * 1.22, 2),
                    "discount": 18.0,
                    "inventory": 30,
                    "stock": 30,
                    "rating": 4.96,
                    "review_count": 890,
                    "delivery_days": 1,
                    "margin": 0.30,
                    "specifications": ["Flagship Grade Engineering", "Extended 2-Year Full Coverage", "Priority Dispatch Express"],
                    "features": ["Flagship Grade Engineering", "Extended 2-Year Full Coverage", "Priority Dispatch Express"],
                    "tags": [query.lower(), "premium", "luxury", "flagship"],
                    "compatible_products": ["ACC001"],
                    "upsell_products": [],
                    "cross_sell_products": ["ACC001"],
                    "image": img_url,
                    "image_url": img_url,
                    "is_active": True
                },
                {
                    "id": f"DYN_{(abs(hash(query)) + 3) % 100000}",
                    "product_id": f"DYN_{(abs(hash(query)) + 3) % 100000}",
                    "name": f"Next-Gen {clean_q} (Smart Edition)",
                    "brand": "NextGen",
                    "description": f"Smart modern {clean_q} with intelligent design, eco-friendly construction, and instant dispatch.",
                    "category": "store",
                    "price": p4,
                    "original_price": round(p4 * 1.35, 2),
                    "discount": 26.0,
                    "inventory": 110,
                    "stock": 110,
                    "rating": 4.70,
                    "review_count": 3100,
                    "delivery_days": 1,
                    "margin": 0.42,
                    "specifications": ["Smart Compact Form", "Energy Efficient & Eco-Friendly", "All-India Fast Shipping"],
                    "features": ["Smart Compact Form", "Energy Efficient & Eco-Friendly", "All-India Fast Shipping"],
                    "tags": [query.lower(), "budget", "smart", "eco"],
                    "compatible_products": ["ACC001"],
                    "upsell_products": [],
                    "cross_sell_products": ["ACC001"],
                    "image": img_url,
                    "image_url": img_url,
                    "is_active": True
                }
            ]

        # Sorting
        if sort_by == "price_asc":
            results.sort(key=lambda x: x["price"])
        elif sort_by == "price_desc":
            results.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda x: x.get("rating", 0), reverse=True)
        elif sort_by == "discount":
            results.sort(key=lambda x: x.get("discount", 0.0), reverse=True)

        return results

catalogue_engine = ProductCatalogue()
