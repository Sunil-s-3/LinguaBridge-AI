"""Clickable English examples with Kannada and Hindi references.

Hindi first-person sentences use the conventional textbook masculine form.
These references are human-written sample translations for BLEU practice.
They are not model output.
"""

from __future__ import annotations

EXAMPLES: list[dict[str, str]] = [
    {
        "en": "What is your name?",
        "kn": "ನಿಮ್ಮ ಹೆಸರು ಏನು?",
        "hi": "आपका नाम क्या है?",
    },
    {
        "en": "How are you?",
        "kn": "ನೀವು ಹೇಗಿದ್ದೀರಿ?",
        "hi": "आप कैसे हैं?",
    },
    {
        "en": "Where are you going?",
        "kn": "ನೀವು ಎಲ್ಲಿಗೆ ಹೋಗುತ್ತಿದ್ದೀರಿ?",
        "hi": "आप कहाँ जा रहे हैं?",
    },
    {
        "en": "Good morning!",
        "kn": "ಶುಭೋದಯ!",
        "hi": "सुप्रभात!",
    },
    {
        "en": "I am feeling happy today.",
        "kn": "ನಾನು ಇಂದು ಸಂತೋಷವಾಗಿದ್ದೇನೆ.",
        "hi": "मैं आज खुश महसूस कर रहा हूँ।",
    },
    {
        "en": "Can you help me?",
        "kn": "ನೀವು ನನಗೆ ಸಹಾಯ ಮಾಡಬಹುದೇ?",
        "hi": "क्या आप मेरी मदद कर सकते हैं?",
    },
    {
        "en": "This is my book.",
        "kn": "ಇದು ನನ್ನ ಪುಸ್ತಕ.",
        "hi": "यह मेरी किताब है।",
    },
    {
        "en": "I am learning English.",
        "kn": "ನಾನು ಇಂಗ್ಲಿಷ್ ಕಲಿಯುತ್ತಿದ್ದೇನೆ.",
        "hi": "मैं अंग्रेज़ी सीख रहा हूँ।",
    },
    {
        "en": "Where do you live?",
        "kn": "ನೀವು ಎಲ್ಲಿ ವಾಸಿಸುತ್ತೀರಿ?",
        "hi": "आप कहाँ रहते हैं?",
    },
    {
        "en": "Thank you very much.",
        "kn": "ತುಂಬಾ ಧನ್ಯವಾದಗಳು.",
        "hi": "आपका बहुत धन्यवाद।",
    },
    {
        "en": "Please come here.",
        "kn": "ದಯವಿಟ್ಟು ಇಲ್ಲಿಗೆ ಬನ್ನಿ.",
        "hi": "कृपया यहाँ आइए।",
    },
    {
        "en": "Have a nice day.",
        "kn": "ನಿಮ್ಮ ದಿನ ಶುಭವಾಗಲಿ.",
        "hi": "आपका दिन शुभ हो।",
    },
]
