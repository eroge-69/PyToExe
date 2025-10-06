# Multilingual Crop Advisory CLI with Detailed Recommendations

def get_crop_info(crop, language):
    # Crop information dictionary
    crop_data = {
        "wheat": {
            "en": {
                "temperature": "10-25°C",
                "soil": "Loamy, well-drained soil",
                "weather": "Cool and dry climate",
                "fertilizer": "Apply NPK (20:20:0) during sowing and top dress nitrogen after 4 weeks",
                "irrigation": "Irrigate at crown root initiation, tillering, and grain filling stage"
            },
            "hi": {
                "temperature": "10-25°C",
                "soil": "दोमट, अच्छी तरह से निथरी मिट्टी",
                "weather": "ठंडा और शुष्क मौसम",
                "fertilizer": "बुवाई के समय NPK (20:20:0) डालें और 4 सप्ताह बाद नाइट्रोजन की टॉप ड्रेसिंग करें",
                "irrigation": "क्राउन रूट इनिशिएशन, तिलरिंग और अनाज भरने के समय सिंचाई करें"
            },
            "pa": {
                "temperature": "10-25°C",
                "soil": "ਦੋਮਟ, ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ ਮਿੱਟੀ",
                "weather": "ਠੰਢਾ ਅਤੇ ਸੁੱਕਾ ਮੌਸਮ",
                "fertilizer": "ਬੋਵਾਈ ਸਮੇਂ NPK (20:20:0) ਲਗਾਓ ਅਤੇ 4 ਹਫ਼ਤੇ ਬਾਅਦ ਨਾਈਟ੍ਰੋਜਨ ਦੀ ਟਾਪ ਡ੍ਰੈਸਿੰਗ ਕਰੋ",
                "irrigation": "ਕਰਾਊਨ ਰੂਟ ਇਨੀਸ਼ੀਏਸ਼ਨ, ਟਿੱਲਰਿੰਗ ਅਤੇ ਅਨਾਜ ਭਰਨ ਵੇਲੇ ਸਿੰਚਾਈ ਕਰੋ"
            }
        },

        "rice": {
            "en": {
                "temperature": "20-35°C",
                "soil": "Clayey or loamy soil with good water retention",
                "weather": "Warm and humid climate",
                "fertilizer": "Use NPK (10:20:20) at transplanting; top dress urea after 30 days",
                "irrigation": "Keep fields flooded until flowering, then reduce water"
            },
            "hi": {
                "temperature": "20-35°C",
                "soil": "मिट्टी की चिकनी या दोमट मिट्टी जिसमें पानी बनी रहे",
                "weather": "गर्म और नम जलवायु",
                "fertilizer": "रोपण के समय NPK (10:20:20) का प्रयोग करें; 30 दिन बाद यूरिया की टॉप ड्रेसिंग करें",
                "irrigation": "फूल आने तक खेतों को भरा रखें, फिर पानी कम करें"
            },
            "pa": {
                "temperature": "20-35°C",
                "soil": "ਮਿੱਟੀ ਦੀ ਚਿਕਨੀ ਜਾਂ ਦੋਮਟ ਮਿੱਟੀ ਜਿਸ ਵਿੱਚ ਪਾਣੀ ਬਰਕਰਾਰ ਰਹੇ",
                "weather": "ਗਰਮ ਅਤੇ ਨਮੀ ਵਾਲਾ ਮੌਸਮ",
                "fertilizer": "ਰੋਪਣ ਸਮੇਂ NPK (10:20:20) ਵਰਤੋਂ; 30 ਦਿਨ ਬਾਅਦ ਯੂਰੀਆ ਦੀ ਟਾਪ ਡ੍ਰੈਸਿੰਗ ਕਰੋ",
                "irrigation": "ਫੁੱਲ ਆਉਣ ਤੱਕ ਖੇਤ ਭਰੇ ਰੱਖੋ, ਫਿਰ ਪਾਣੀ ਘਟਾਓ"
            }
        },

        "maize": {
            "en": {
                "temperature": "18-27°C",
                "soil": "Fertile, well-drained loamy soil",
                "weather": "Warm and sunny climate",
                "fertilizer": "Apply 100kg N, 60kg P2O5 and 40kg K2O per hectare",
                "irrigation": "Irrigate at sowing, knee high, tasseling and grain filling stage"
            },
            "hi": {
                "temperature": "18-27°C",
                "soil": "उपजाऊ, अच्छी तरह से निथरी दोमट मिट्टी",
                "weather": "गर्म और धूप वाला मौसम",
                "fertilizer": "प्रति हेक्टेयर 100kg N, 60kg P2O5 और 40kg K2O डालें",
                "irrigation": "बुवाई, घुटने ऊँचाई, टैसलिंग और अनाज भरने के समय सिंचाई करें"
            },
            "pa": {
                "temperature": "18-27°C",
                "soil": "ਉਪਜਾਉ, ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ ਦੋਮਟ ਮਿੱਟੀ",
                "weather": "ਗਰਮ ਅਤੇ ਧੁੱਪ ਵਾਲਾ ਮੌਸਮ",
                "fertilizer": "ਹੈਕਟੇਅਰ ਪ੍ਰਤੀ 100kg N, 60kg P2O5 ਅਤੇ 40kg K2O ਲਗਾਓ",
                "irrigation": "ਬੋਵਾਈ, ਘੁੱਟੇ ਉੱਚਾਈ, ਟੈਸਲਿੰਗ ਅਤੇ ਅਨਾਜ ਭਰਨ ਵੇਲੇ ਸਿੰਚਾਈ ਕਰੋ"
            }
        },
    

        "cotton": {
            "en": {"temperature": "25-35°C",
                   "soil": "Well-drained sandy loam",
                   "weather": "Warm and sunny",
                   "fertilizer": "Apply NPK (60:30:30 kg/ha) at sowing and top dress nitrogen",
                   "irrigation": "Irrigate 3-4 times depending on soil moisture"},
            "hi": {"temperature": "25-35°C",
                   "soil": "अच्छी तरह से निथरी रेतीली दोमट मिट्टी",
                   "weather": "गर्म और धूप वाला मौसम",
                   "fertilizer": "बुवाई के समय NPK (60:30:30 kg/ha) डालें और नाइट्रोजन की टॉप ड्रेसिंग करें",
                   "irrigation": "मिट्टी की नमी के अनुसार 3-4 बार सिंचाई करें"},
            "pa": {"temperature": "25-35°C",
                   "soil": "ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ ਰੇਤਲੀ ਦੋਮਟ ਮਿੱਟੀ",
                   "weather": "ਗਰਮ ਅਤੇ ਧੁੱਪ ਵਾਲਾ ਮੌਸਮ",
                   "fertilizer": "ਬੋਵਾਈ ਸਮੇਂ NPK (60:30:30 kg/ha) ਲਗਾਓ ਅਤੇ ਨਾਈਟ੍ਰੋਜਨ ਦੀ ਟਾਪ ਡ੍ਰੈਸਿੰਗ ਕਰੋ",
                   "irrigation": "ਮਿੱਟੀ ਦੀ ਨਮੀ ਦੇ ਅਨੁਸਾਰ 3-4 ਵਾਰੀ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "sugarcane": {
            "en": {"temperature": "20-32°C",
                   "soil": "Deep, well-drained loamy soil",
                   "weather": "Tropical and humid",
                   "fertilizer": "Apply NPK (150:60:60 kg/ha) and top dress nitrogen during growth",
                   "irrigation": "Irrigate every 10-15 days"},
            "hi": {"temperature": "20-32°C",
                   "soil": "गहरी, अच्छी तरह से निथरी दोमट मिट्टी",
                   "weather": "उष्णकटिबंधीय और नम",
                   "fertilizer": "NPK (150:60:60 kg/ha) डालें और विकास के दौरान नाइट्रोजन की टॉप ड्रेसिंग करें",
                   "irrigation": "हर 10-15 दिन सिंचाई करें"},
            "pa": {"temperature": "20-32°C",
                   "soil": "ਗਹਿਰੀ, ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ ਦੋਮਟ ਮਿੱਟੀ",
                   "weather": "ਉषਣਕਟਿਬੰਧੀ ਅਤੇ ਨਮੀ ਵਾਲਾ ਮੌਸਮ",
                   "fertilizer": "NPK (150:60:60 kg/ha) ਲਗਾਓ ਅਤੇ ਵਿਕਾਸ ਦੌਰਾਨ ਨਾਈਟ੍ਰੋਜਨ ਦੀ ਟਾਪ ਡ੍ਰੈਸਿੰਗ ਕਰੋ",
                   "irrigation": "ਹਰ 10-15 ਦਿਨ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "barley": {
            "en": {"temperature": "10-25°C",
                   "soil": "Loamy soil, well-drained",
                   "weather": "Cool and dry",
                   "fertilizer": "Apply NPK (20:20:0) at sowing",
                   "irrigation": "Irrigate at tillering and grain filling"},
            "hi": {"temperature": "10-25°C",
                   "soil": "दोमट मिट्टी, अच्छी तरह से निथरी",
                   "weather": "ठंडा और शुष्क",
                   "fertilizer": "बुवाई के समय NPK (20:20:0) डालें",
                   "irrigation": "तिलरिंग और अनाज भरने पर सिंचाई करें"},
            "pa": {"temperature": "10-25°C",
                   "soil": "ਦੋਮਟ ਮਿੱਟੀ, ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ",
                   "weather": "ਠੰਢਾ ਅਤੇ ਸੁੱਕਾ",
                   "fertilizer": "ਬੋਵਾਈ ਸਮੇਂ NPK (20:20:0) ਲਗਾਓ",
                   "irrigation": "ਟਿੱਲਰਿੰਗ ਅਤੇ ਅਨਾਜ ਭਰਨ ਵੇਲੇ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "jowar": {
            "en": {"temperature": "25-35°C",
                   "soil": "Well-drained loamy soil",
                   "weather": "Warm and semi-arid",
                   "fertilizer": "Apply NPK (60:30:30 kg/ha) at sowing",
                   "irrigation": "Irrigate at flowering and grain filling stages"},
            "hi": {"temperature": "25-35°C",
                   "soil": "अच्छी तरह से निथरी दोमट मिट्टी",
                   "weather": "गर्म और अर्ध-शुष्क",
                   "fertilizer": "बुवाई के समय NPK (60:30:30 kg/ha) डालें",
                   "irrigation": "फूलने और अनाज भरने के समय सिंचाई करें"},
            "pa": {"temperature": "25-35°C",
                   "soil": "ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ ਦੋਮਟ ਮਿੱਟੀ",
                   "weather": "ਗਰਮ ਅਤੇ ਅਰਧ ਸੁੱਕਾ",
                   "fertilizer": "ਬੋਵਾਈ ਸਮੇਂ NPK (60:30:30 kg/ha) ਲਗਾਓ",
                   "irrigation": "ਫੁੱਲਣ ਅਤੇ ਅਨਾਜ ਭਰਨ ਵੇਲੇ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "bajra": {
            "en": {"temperature": "25-35°C",
                   "soil": "Sandy loam, well-drained",
                   "weather": "Warm and dry",
                   "fertilizer": "Apply NPK (40:20:20 kg/ha) at sowing",
                   "irrigation": "Irrigate at critical growth stages"},
            "hi": {"temperature": "25-35°C",
                   "soil": "रेतीली दोमट, अच्छी तरह से निथरी",
                   "weather": "गर्म और शुष्क",
                   "fertilizer": "बुवाई के समय NPK (40:20:20 kg/ha) डालें",
                   "irrigation": "महत्वपूर्ण विकास चरणों पर सिंचाई करें"},
            "pa": {"temperature": "25-35°C",
                   "soil": "ਰੇਤਲੀ ਦੋਮਟ, ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ",
                   "weather": "ਗਰਮ ਅਤੇ ਸੁੱਕਾ",
                   "fertilizer": "ਬੋਵਾਈ ਸਮੇਂ NPK (40:20:20 kg/ha) ਲਗਾਓ",
                   "irrigation": "ਮਹੱਤਵਪੂਰਨ ਵਿਕਾਸ ਚਰਣਾਂ ਤੇ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "oats": {
            "en": {"temperature": "15-25°C",
                   "soil": "Loamy soil, well-drained",
                   "weather": "Cool and moist",
                   "fertilizer": "Apply NPK (20:20:0) at sowing",
                   "irrigation": "Irrigate during vegetative and grain filling stages"},
            "hi": {"temperature": "15-25°C",
                   "soil": "दोमट मिट्टी, अच्छी तरह से निथरी",
                   "weather": "ठंडा और नम",
                   "fertilizer": "बुवाई के समय NPK (20:20:0) डालें",
                   "irrigation": "शाकवाती और अनाज भरने के समय सिंचाई करें"},
            "pa": {"temperature": "15-25°C",
                   "soil": "ਦੋਮਟ ਮਿੱਟੀ, ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ",
                   "weather": "ਠੰਢਾ ਅਤੇ ਨਮੀ ਵਾਲਾ",
                   "fertilizer": "ਬੋਵਾਈ ਸਮੇਂ NPK (20:20:0) ਲਗਾਓ",
                   "irrigation": "ਪੌਧਾ ਅਤੇ ਅਨਾਜ ਭਰਨ ਵੇਲੇ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "jute": {
            "en": {"temperature": "24-35°C",
                   "soil": "Loamy alluvial soil",
                   "weather": "Warm and humid",
                   "fertilizer": "Apply NPK (60:30:30 kg/ha) at sowing",
                   "irrigation": "Irrigate every 5-7 days during growth"},
            "hi": {"temperature": "24-35°C",
                   "soil": "दोमट आवसादी मिट्टी",
                   "weather": "गर्म और नम",
                   "fertilizer": "बुवाई के समय NPK (60:30:30 kg/ha) डालें",
                   "irrigation": "विकास के दौरान हर 5-7 दिन सिंचाई करें"},
            "pa": {"temperature": "24-35°C",
                   "soil": "ਦੋਮਟ ਆਵਸਾਦੀ ਮਿੱਟੀ",
                   "weather": "ਗਰਮ ਅਤੇ ਨਮੀ ਵਾਲਾ",
                   "fertilizer": "ਬੋਵਾਈ ਸਮੇਂ NPK (60:30:30 kg/ha) ਲਗਾਓ",
                   "irrigation": "ਵਿਕਾਸ ਦੌਰਾਨ ਹਰ 5-7 ਦਿਨ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "flax seeds": {
            "en": {"temperature": "18-25°C",
                   "soil": "Loamy soil with good drainage",
                   "weather": "Cool and dry",
                   "fertilizer": "Apply NPK (20:20:0) at sowing",
                   "irrigation": "Irrigate during flowering and seed formation"},
            "hi": {"temperature": "18-25°C",
                   "soil": "दोमट मिट्टी, अच्छी जल निकासी वाली",
                   "weather": "ठंडा और शुष्क",
                   "fertilizer": "बुवाई के समय NPK (20:20:0) डालें",
                   "irrigation": "फूलने और बीज बनने पर सिंचाई करें"},
            "pa": {"temperature": "18-25°C",
                   "soil": "ਦੋਮਟ ਮਿੱਟੀ, ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ",
                   "weather": "ਠੰਢਾ ਅਤੇ ਸੁੱਕਾ",
                   "fertilizer": "ਬੋਵਾਈ ਸਮੇਂ NPK (20:20:0) ਲਗਾਓ",
                   "irrigation": "ਫੁੱਲਣ ਅਤੇ ਬੀਜ ਬਣਨ ਵੇਲੇ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "tea": {
            "en": {"temperature": "18-30°C",
                   "soil": "Acidic, well-drained soil",
                   "weather": "Humid and rainy",
                   "fertilizer": "Use NPK (100:50:50 kg/ha) annually",
                   "irrigation": "Provide irrigation in dry periods"},
            "hi": {"temperature": "18-30°C",
                   "soil": "अम्लीय, अच्छी तरह से निथरी मिट्टी",
                   "weather": "नमी और बारिश वाला",
                   "fertilizer": "सालाना NPK (100:50:50 kg/ha) डालें",
                   "irrigation": "सूखे समय में सिंचाई करें"},
            "pa": {"temperature": "18-30°C",
                   "soil": "ਅਮਲੀ, ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ ਮਿੱਟੀ",
                   "weather": "ਨਮੀ ਅਤੇ ਵਰਖਾਵਾਂ ਵਾਲਾ",
                   "fertilizer": "ਸਾਲਾਨਾ NPK (100:50:50 kg/ha) ਲਗਾਓ",
                   "irrigation": "ਸੁੱਕੇ ਸਮਿਆਂ ਵਿੱਚ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "coffee": {
            "en": {"temperature": "18-28°C",
                   "soil": "Well-drained, fertile loam",
                   "weather": "Humid, moderate rainfall",
                   "fertilizer": "Apply NPK (100:60:60 kg/ha) during growth",
                   "irrigation": "Irrigate in dry seasons"},
            "hi": {"temperature": "18-28°C",
                   "soil": "अच्छी तरह से निथरी उपजाऊ दोमट मिट्टी",
                   "weather": "नमी, मध्यम वर्षा",
                   "fertilizer": "विकास के दौरान NPK (100:60:60 kg/ha) डालें",
                   "irrigation": "सूखे मौसम में सिंचाई करें"},
            "pa": {"temperature": "18-28°C",
                   "soil": "ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ ਉਪਜਾਉ ਦੋਮਟ ਮਿੱਟੀ",
                   "weather": "ਨਮੀ, ਦਰਮਿਆਨਾ ਵਰਖਾ",
                   "fertilizer": "ਵਿਕਾਸ ਦੌਰਾਨ NPK (100:60:60 kg/ha) ਲਗਾਓ",
                   "irrigation": "ਸੁੱਕੇ ਮੌਸਮ ਵਿੱਚ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "rubber": {
            "en": {"temperature": "25-35°C",
                   "soil": "Deep, well-drained loamy soil",
                   "weather": "Humid tropical",
                   "fertilizer": "Apply NPK (100:50:50 kg/ha) annually",
                   "irrigation": "Irrigate during dry months"},
            "hi": {"temperature": "25-35°C",
                   "soil": "गहरी, अच्छी तरह से निथरी दोमट मिट्टी",
                   "weather": "उष्णकटिबंधीय और नम",
                   "fertilizer": "सालाना NPK (100:50:50 kg/ha) डालें",
                   "irrigation": "सूखे महीनों में सिंचाई करें"},
            "pa": {"temperature": "25-35°C",
                   "soil": "ਗਹਿਰੀ, ਵਧੀਆ ਨਿਕਾਸ ਵਾਲੀ ਦੋਮਟ ਮਿੱਟੀ",
                   "weather": "ਉषਣਕਟਿਬੰਧੀ ਅਤੇ ਨਮੀ ਵਾਲਾ",
                   "fertilizer": "ਸਾਲਾਨਾ NPK (100:50:50 kg/ha) ਲਗਾਓ",
                   "irrigation": "ਸੁੱਕੇ ਮਹੀਨਿਆਂ ਵਿੱਚ ਸਿੰਚਾਈ ਕਰੋ"}
        },
        "tobacco": {
            "en": {"temperature": "20-30°C",
                   "soil": "Loamy soil, rich in organic matter",
                   "weather": "Warm and humid",
                   "fertilizer": "Apply NPK (100:50:50 kg/ha) at sowing and side dressing",
                   "irrigation": "Irrigate 3-4 times depending on soil moisture"},
            "hi": {"temperature": "20-30°C",
                   "soil": "दोमट मिट्टी, कार्बनिक पदार्थ में समृद्ध",
                   "weather": "गर्म और नम",
                   "fertilizer": "बुवाई के समय NPK (100:50:50 kg/ha) डालें और साइड ड्रेसिंग करें",
                   "irrigation": "मिट्टी की नमी के अनुसार 3-4 बार सिंचाई करें"},
            "pa": {"temperature": "20-30°C",
                   "soil": "ਦੋਮਟ ਮਿੱਟੀ, ਜੈਵਿਕ ਪਦਾਰਥ ਵਿੱਚ ਧਨਵਾਨ",
                   "weather": "ਗਰਮ ਅਤੇ ਨਮੀ ਵਾਲਾ",
                   "fertilizer": "ਬੋਵਾਈ ਸਮੇਂ NPK (100:50:50 kg/ha) ਲਗਾਓ ਅਤੇ ਸਾਈਡ ਡ੍ਰੈਸਿੰਗ ਕਰੋ",
                   "irrigation": "ਮਿੱਟੀ ਦੀ ਨਮੀ ਦੇ ਅਨੁਸਾਰ 3-4 ਵਾਰੀ ਸਿੰਚਾਈ ਕਰੋ"}
        }
    }

    return crop_data.get(crop.lower(), {}).get(language, None)


def main():
    print("🌱 Multilingual Crop Advisory CLI 🌱\n")
    
    # Language selection
    print("Select Language / भाषा चुनें / ਭਾਸ਼ਾ ਚੁਣੋ:")
    print("1. English")
    print("2. Hindi (हिन्दी)")
    print("3. Punjabi (ਪੰਜਾਬੀ)")
    
    lang_choice = input("Enter choice (1-3): ")
    language_map = {"1": "en", "2": "hi", "3": "pa"}
    language = language_map.get(lang_choice, "en")
    
    # Available crops
    print("\nAvailable Crops: Wheat,Rice,Maize,Cotton, Sugarcane, Barley, Jowar, Bajra, Oats, Jute, Flax seeds, Tea, Coffee, Rubber, Tobacco")
    crop = input("Enter crop name: ").strip()
    
    info = get_crop_info(crop, language)
    
    
    if info:
        print(f"\n Crop Adviosory for{crop.capitalize()}:\n")
        print(f"Temperature: {info['temperature']}")
        print(f"Soil Type:{info['soil']}")
        print(f"Weather Condition:{info['weather']}")
        print(f"Fertilizer: {info['fertilizer']}")
        print(f"Irrigation: {info['irrigation']}\n")
    
    else:
        print("Sorry, crop information not available in selected language.")

if __name__ == "__main__":
    main()
