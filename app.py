import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import time
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from io import BytesIO
import os
import uuid


# ============================================================
# GOOGLE SHEETS
# ============================================================

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    dict(st.secrets["gcp_service_account"]),
    scopes=scopes
)

gc = gspread.authorize(credentials)

sheet = gc.open(st.secrets["google_sheet"]["name"])

# ============================================================
# BODY MASSE – GOOGLE SHEETS
# ============================================================

def get_body_worksheet(username):

    worksheet_name = f"Body_{username}"

    try:
        worksheet = sheet.worksheet(worksheet_name)

    except gspread.WorksheetNotFound:

        worksheet = sheet.add_worksheet(
            title=worksheet_name,
            rows=1000,
            cols=30
        )

    return worksheet


def load_body_data(username):

    worksheet = get_body_worksheet(username)

    values = worksheet.get_all_values()

    if not values:
        return pd.DataFrame()

    headers = values[0]

    if not headers:
        return pd.DataFrame()

    rows = values[1:]

    if not rows:
        return pd.DataFrame(columns=headers)

    normalized_rows = []

    for row in rows:

        if len(row) < len(headers):
            row = row + [""] * (len(headers) - len(row))

        normalized_rows.append(
            row[:len(headers)]
        )

    return pd.DataFrame(
        normalized_rows,
        columns=headers
    )


def save_body_data(username, df):

    worksheet = get_body_worksheet(username)

    worksheet.clear()

    if df.empty:
        return

    clean_df = df.copy().fillna("")

    for col in clean_df.columns:

        clean_df[col] = clean_df[col].apply(
            lambda x: x.isoformat()
            if isinstance(x, (date, datetime))
            else x
        )

    data = [
        clean_df.columns.tolist()
    ] + clean_df.astype(str).values.tolist()

    worksheet.update(
        range_name="A1",
        values=data
    )

# ============================================================
# BENUTZER
# ============================================================

USERS = {
    "Tamara": {
        "password": "1010",
        "gender": "female"
    },

    "Can": {
        "password": "1010",
        "gender": "male"
    },

    "Papa": {
        "password": "aramat",
        "gender": "male"
    },

    "Nomi": {
        "password": "thebest",
        "gender": "female"
    },

    "Nemo": {
        "password": "Popeye",
        "gender": "male"
    },

    "Onur": {
        "password": "Popeye",
        "gender": "male"
    }
}

# ============================================================
# ÜBUNGEN
# ============================================================


exercises_by_group = {

    "Rücken": [
        "T row",
        "Lat pull down",
        "Überzüge",
        "Rudern",
        "Iso-Lateral Row",
        "Iso-Lateral D.Y. Row",
        "Face pulls",
        "Delt Fly",
        "Hanging"
    ],

    "Brust": [
        "Push",
        "Incline Chest Press",
        "Butterfly"
    ],

    "Beine": [
        "Leg extension",
        "Leg curl",
        "Leg press",
        "Pendulum Leg Press",
        "Abductor",
        "Adductor",
        "Squat",
        "Calf raises"
    ],

    "Glutes": [
        "Hip Thrust",
        "Bulgarian Split Squats",
        "RDLs",
        "Step ups",
        "Abductor",
        "Squat",
        "Cable kick back",
        "Lunges",
        "Glute hyperextension"
    ],

    "Bizeps": [
        "Hammer curl",
        "Biceps curl"
    ],

    "Trizeps": [
        "Dips",
        "Push down",
        "Overhead Triceps Extension"
    ],

    "Schultern": [
        "Lateral raises",
        "Front raises",
        "Cable Front Raise (Between Legs)",
        "Shoulder Press",
        "Delt Fly"
    ],

    "core": [
        "Dumbbell side bend",
        "Lying Alternating Leg Raise",
        "Lying leg raises",
        "Dead bug",
        "Heel tap crunches",
        "Alternating knee tucks",
        "Russian twist",
        "Over unders beide Richtungen",
        "Ab wheel rollout",
        "Reverse crunch",
        "Hanging crunches",
        "Side plank right",
        "Side plank left",
        "Plank"
    ],

    "Calisthenics": [
        "Push up",
        "Pike Push up",
        "Handstand",
        "Pull up",
        "Chin up",
        "Dips",
        "Australian Rows",
        "Squat",
        "Lunges"
    ],

    "TRX": [
        "TRX Row",
        "TRX Chest Press",
        "TRX Biceps Curl",
        "TRX Triceps Extension",
        "TRX Squat",
        "TRX Lunge",
        "TRX Pike",
        "TRX Plank"
    ]
}

# ============================================================
# MEALPLANS
# ============================================================
# ============================================================
# NÄHRWERTDATENBANK
# Werte gemäss Excel, Stand Oktober 2026
# Standard: pro 100 g, ausser anders angegeben
# ============================================================

FOOD_NUTRITION = {
    # Zusätze
    "Proteinpulver": {"protein": 73.33, "carbs": 9.67, "kcal": 373.33, "fat": 6.20},
    "Isoclear": {"protein": 80, "carbs": 3, "kcal": 346.67, "fat": 0},

    # Frühstück
    "Alpro Joghurt": {"protein": 4, "carbs": 0, "kcal": 42, "fat": 2.3},
    "Walnüsse": {"protein": 15, "carbs": 5, "kcal": 700, "fat": 65},
    "Granola": {"protein": 16, "carbs": 27, "kcal": 553, "fat": None},
    "Mandeln": {"protein": 21, "carbs": 22, "kcal": 576, "fat": 49},
    "Chiasamen": {"protein": 17, "carbs": 42, "kcal": 486, "fat": 31},
    "Starbucks Chilled Coffee": {"protein": 2.9, "carbs": 4.2, "kcal": 35, "fat": 0.9},
    "Haferflocken": {"protein": 13, "carbs": 60, "kcal": 360, "fat": 7},
    "Skyr": {"protein": 11, "carbs": 4, "kcal": 70, "fat": 0.2},
    "Honig": {"protein": 0, "carbs": 80, "kcal": 300, "fat": 0},
    "Erdnussbutter": {"protein": 23, "carbs": 7.1, "kcal": 646, "fat": 47},
    "Reis roh": {"protein": 8, "carbs": 77, "kcal": 340, "fat": 0.7},

    # Proteinquellen
    "Hüttenkäse": {"protein": 13, "carbs": 3, "kcal": 98, "fat": 4},
    "Feta Light": {"protein": 15.7, "carbs": 0.8, "kcal": 273, "fat": 23},
    "Halloumi": {"protein": 21, "carbs": 2, "kcal": 321, "fat": 24.8},
    "Tofu": {"protein": 14, "carbs": 1.4, "kcal": 131, "fat": 8},
    "Garnelen": {"protein": 20, "carbs": 1, "kcal": 100, "fat": 1.7},
    "Poulet": {"protein": 22, "carbs": 1, "kcal": 119, "fat": 2.6},
    "Rindersteak": {"protein": 21, "carbs": 0.8, "kcal": 121, "fat": 4},
    "Rindhack": {"protein": 19, "carbs": 0, "kcal": 194, "fat": 12},
    "Lachs": {"protein": 20.7, "carbs": 0.3, "kcal": 208, "fat": 13},
    "Hummus Reduce": {"protein": 6.5, "carbs": 11, "kcal": 155, "fat": 8.3},
    "Mozzarella": {"protein": 20.5, "carbs": 1.5, "kcal": 165, "fat": 8.5},
    "Tempeh": {"protein": 18, "carbs": 4.9, "kcal": 161, "fat": 9},
    "Käse": {"protein": 25, "carbs": 0, "kcal": 120, "fat": 30},
    "Eiweiss": {"protein": 11, "carbs": 0, "kcal": 50, "fat": 0},
    "Pute": {"protein": 23, "carbs": 0, "kcal": 110, "fat": 1},
    "Greek Joghurt": {"protein": 4.8, "carbs": 3.9, "kcal": 118, "fat": 9},
    "Magerquark": {"protein": 12, "carbs": 4.1, "kcal": 68, "fat": 0.2},
    "Seelachs": {"protein": 17, "carbs": 0, "kcal": 74, "fat": 0.5},
    "Tilapia": {"protein": 20, "carbs": 0, "kcal": 95, "fat": 2},

    # Gemüse und Obst
    "Pilze": {"protein": 3.1, "carbs": 3.3, "kcal": 22, "fat": 0.3},
    "Spinat": {"protein": 2.9, "carbs": 3.6, "kcal": 23, "fat": 0.4},
    "Brokkoli": {"protein": 2.8, "carbs": 6.6, "kcal": 34, "fat": 0.4},
    "Blumenkohl": {"protein": 1.9, "carbs": 4.9, "kcal": 25, "fat": 0.3},
    "Kartoffeln": {"protein": 2, "carbs": 17, "kcal": 77, "fat": 0.1},
    "Avocado": {"protein": 2, "carbs": 1.8, "kcal": 160, "fat": 15},
    "Zucchini": {"protein": 1.6, "carbs": 2.2, "kcal": 16, "fat": 0.3},
    "Peperoni": {"protein": 1, "carbs": 6, "kcal": 26, "fat": 0.3},
    "Aubergine": {"protein": 1, "carbs": 5.9, "kcal": 25, "fat": 0.2},
    "Karotten": {"protein": 0.9, "carbs": 9.6, "kcal": 41, "fat": 0.2},
    "Tomaten": {"protein": 0.9, "carbs": 3.9, "kcal": 18, "fat": 0.2},
    "Gurken": {"protein": 0.7, "carbs": 2, "kcal": 12, "fat": 0.1},
    "Schwarze Bohnen": {"protein": 7.7, "carbs": 21, "kcal": 132, "fat": 0.5},
    "Süsskartoffeln": {"protein": 1.6, "carbs": 20, "kcal": 86, "fat": 0.1},
    "Zwiebel": {"protein": 1.2, "carbs": 4.9, "kcal": 27, "fat": 0.2},
    "Linsen trocken": {"protein": 26, "carbs": 55, "kcal": 350, "fat": 1.1},
    "Apfel": {"protein": 0.3, "carbs": 14, "kcal": 53, "fat": 0.2},
    "Banane": {"protein": 1, "carbs": 20, "kcal": 105, "fat": 0.3},
    "Mixed Berries": {"protein": 1, "carbs": 15, "kcal": 65, "fat": 0.3},
    "Lange Bohnen": {"protein": 2, "carbs": 5, "kcal": 35, "fat": 0.1},
    "Spargeln": {"protein": 2, "carbs": 2, "kcal": 20, "fat": 0.1},
    "Salat": {"protein": 1.5, "carbs": 1, "kcal": 15, "fat": 0.2},
    "Datteln": {"protein": 2.5, "carbs": 75, "kcal": 282, "fat": 0.1},
    "Gemüsemix": {"protein": 4, "carbs": 11, "kcal": 24, "fat": 0.5},
    "Feigen getrocknet": {"protein": 3.2, "carbs": 57, "kcal": 274, "fat": 0.2},

    # Kohlenhydrate
    "Pasta roh": {"protein": 12, "carbs": 71, "kcal": 359, "fat": None},
    "Gnocchi": {"protein": 3, "carbs": 30, "kcal": 145, "fat": None},
    "Gepuffter Reis": {"protein": 6, "carbs": 80, "kcal": 370, "fat": None},
    "Kartoffelstock": {"protein": 2, "carbs": 13, "kcal": 73, "fat": None},

    # Milchprodukte und weitere Zutaten
    "Mandelmilch": {"protein": 0.4, "carbs": 0, "kcal": 13, "fat": 1.1},
    "Entöltes Mandelmehl": {"protein": 45, "carbs": 5, "kcal": 325, "fat": 12},
    "Philadelphia Balance": {"protein": 5.4, "carbs": 4.3, "kcal": 226, "fat": 11},
    "Kokosmilch": {"protein": 1.7, "carbs": 3.4, "kcal": 218, "fat": 21},
    "Olivenöl": {"protein": 0, "carbs": 0, "kcal": 820, "fat": 91},
    "Matcha": {"protein": 22.8, "carbs": 2.9, "kcal": 138, "fat": 4.06},
}

# Lebensmittel, deren Excel-Werte sich auf Stück/Portionen
# statt auf 100 g beziehen.
FOOD_NUTRITION_PER_UNIT = {
    "Linsenwaffel": {"unit": "Stück (7 g)", "protein": 1.8, "carbs": 4.1, "kcal": 26, "fat": 1},
    "Ei": {"unit": "grosses Ei", "protein": 6, "carbs": 0.6, "kcal": 77, "fat": 5.3},
    "Proteinbite": {"unit": "Stück", "protein": 1, "carbs": 4.12, "kcal": 31.6, "fat": None},
    "Wrap": {"unit": "Stück", "protein": 11, "carbs": 24, "kcal": 197, "fat": None},
    "Bagel": {"unit": "Stück", "protein": 27, "carbs": 56, "kcal": 395, "fat": None},
    "Brötchen": {"unit": "Stück", "protein": 16, "carbs": 19, "kcal": 206, "fat": 6},
    "Gyoza Tofu und Gemüse": {"unit": "20 g", "protein": 1, "carbs": 26, "kcal": 155, "fat": None},
}

# Fertige Rezepte – Werte gemäss Excel
# Portionsdefinitionen später bei Bedarf ergänzen.
FOOD_NUTRITION_RECIPES = {
    "Frühstücksporridge": {"protein": 36.24, "carbs": 36.89, "kcal": 523.78, "fat": 22.65},
    "Frühstücksjoghurt Can": {"protein": 53.25, "carbs": 39.01, "kcal": 550.11, "fat": 17.74},
    "Morningshake Can": {"protein": 32.6, "carbs": 53.61, "kcal": 487.6, "fat": 12.56},
    "Apfel-Zimt-Protein-Muffins": {"protein": 8, "carbs": 2.91, "kcal": 65.4, "fat": 0},
    "Milchreis P T": {"protein": 23.1, "carbs": 46.16, "kcal": 418.4, "fat": 13.706},
    "Belegtes Brot": {"protein": 30.88, "carbs": 23.62, "kcal": 530.35, "fat": 28.3},
}

MEAL_PLANS = {


    "Tamara": {

        # ==================================================
        # 2400 KCAL
        # ==================================================

        "2400 kcal": {

            "Frühstück": [
                (1, "Frühstücksporridge")
            ],

            "9i / Nacht": {

                "Milchreis": [
                    (1, "Milchreis PT")
                ],

                "Joghurt": [
                    (200, "Alpro Joghurt"),
                    (20, "Proteinpulver"),
                    (30, "Haferflocken"),
                    (4, "Chiasamen"),
                    (40, "Datteln")
                ],

                "Magerquark": [
                    (250, "Magerquark"),
                    (20, "Proteinpulver"),
                    (20, "Erdnussbutter"),
                    (20, "Datteln")
                ]
            },

            "Mittag / 4i": {

                "Rindhack": [
                    (150, "Rindhack"),
                    (150, "Kartoffeln"),
                    (30, "Reis roh"),
                    (50, "Gemüsemix")
                ],

                "Tofu": [
                    (200, "Tofu"),
                    (100, "Kartoffeln"),
                    (50, "Reis roh"),
                    (10, "Avocado")
                ],

                "Eiweiss": [
                    (250, "Eiweiss"),
                    (200, "Kartoffeln"),
                    (50, "Reis roh"),
                    (50, "Avocado")
                ],

                "Garnelen": [
                    (200, "Garnelen"),
                    (150, "Kartoffeln"),
                    (50, "Reis roh"),
                    (20, "Avocado")
                ],

                "Mozzarella": [
                    (125, "Mozzarella"),
                    (150, "Kartoffeln"),
                    (60, "Reis roh"),
                    (50, "Tomaten")
                ],

                "Poulet": [
                    (200, "Poulet"),
                    (120, "Kartoffeln"),
                    (50, "Reis roh"),
                    (20, "Avocado")
                ]
            }
        },

        # ==================================================
        # 2600 KCAL
        # ==================================================

        "2600 kcal": {

            "Frühstück": [
                (1, "Frühstücksporridge")
            ],

            "9i / Nacht": {

                "Milchreis": [
                    (1, "Milchreis PT")
                ],

                "Joghurt": [
                    (200, "Alpro Joghurt"),
                    (20, "Proteinpulver"),
                    (30, "Haferflocken"),
                    (4, "Chiasamen"),
                    (40, "Datteln")
                ],

                "Magerquark": [
                    (250, "Magerquark"),
                    (20, "Proteinpulver"),
                    (20, "Erdnussbutter"),
                    (20, "Datteln")
                ]
            },

            "Mittag / 4i": {

                "Rindhack": [
                    (150, "Rindhack"),
                    (150, "Kartoffeln"),
                    (60, "Reis roh"),
                    (70, "Gemüsemix")
                ],

                "Tofu": [
                    (200, "Tofu"),
                    (100, "Kartoffeln"),
                    (70, "Reis roh"),
                    (30, "Avocado")
                ],

                "Eiweiss": [
                    (250, "Eiweiss"),
                    (200, "Kartoffeln"),
                    (80, "Reis roh"),
                    (50, "Avocado")
                ],

                "Garnelen": [
                    (200, "Garnelen"),
                    (150, "Kartoffeln"),
                    (80, "Reis roh"),
                    (20, "Avocado")
                ],

                "Mozzarella": [
                    (125, "Mozzarella"),
                    (180, "Kartoffeln"),
                    (80, "Reis roh"),
                    (50, "Tomaten")
                ],

                "Poulet": [
                    (200, "Poulet"),
                    (120, "Kartoffeln"),
                    (80, "Reis roh"),
                    (20, "Avocado")
                ]
            }
        }
    },


            "Can": {

                "3000 kcal": {

                    # ==================================================
                    # FIXE MAHLZEITEN
                    # ==================================================

                    "Fix": {

                        "07:00": [
                            (1, "Morningshake Can")
                        ],

                        "09:00": [
                            (2, "2 belegte Protein Brote")
                        ],

                        "15:00": [
                            (1, "Apfel-Zimt-Protein-Muffins")
                        ],

                        "Nacht": [
                            (10, "Proteinpulver"),
                            (10, "Erdnussbutter"),
                            (250, "Magerquark")
                        ]
                    },


                    # ==================================================
                    # 12:00 / 17:30
                    # frei austauschbare Hauptmahlzeiten
                    # ==================================================

                    "Hauptmahlzeiten": {

                        # SE = Seelachs
                        "SE – Seelachs": [
                            (200, "Seelachs"),
                            (100, "Kartoffeln"),
                            (50, "Reis roh"),
                            (100, "Karotten")
                        ],

                        # PO = Poulet
                        "PO – Poulet": [
                            (150, "Poulet"),
                            (100, "Kartoffeln"),
                            (50, "Reis roh"),
                            (100, "Tomaten")
                        ],

                        # TO = Tofu
                        "TO – Tofu": [
                            (200, "Tofu"),
                            (50, "Reis roh"),
                            (100, "Gemüsemix")
                        ],

                        # TI = Tilapia
                        "TI – Tilapia": [
                            (200, "Tilapia"),
                            (70, "Kartoffeln"),
                            (50, "Reis roh"),
                            (100, "Gemüsemix")
                        ],

                        # GA = Garnelen
                        "GA – Garnelen": [
                            (150, "Garnelen"),
                            (120, "Kartoffeln"),
                            (50, "Reis roh"),
                            (100, "Gemüsemix")
                        ],
                        "RH - Rindhack": [
                            (150, "Rindhack"),
                            (50, "Kartoffeln"),
                            (30, "Reis roh"),
                            (100, "Gemüsemix")
                        ],

                        "RS - Rindersteak": [
                            (150, "Rindersteak"),
                            (100, "Kartoffeln"),
                            (50, "Reis roh"),
                            (100, "Gemüsemix")
                        ]
                    },

                    # ==================================================
                    # 19:00
                    # ==================================================

                    "19:00": {

                        # EI = Eiweiss
                        "EI – Eiweiss": [
                            (100, "Eiweiss"),
                            (100, "Kartoffeln"),
                            (100, "Avocado")
                        ],

                        # MO = Mozzarella
                        "MO – Mozzarella": [
                            (125, "Mozzarella"),
                            (100, "Kartoffeln"),
                            (50, "Avocado")
                        ]
                    }
                },

            "3500 kcal": {

                # ==================================================
                # FIXE MAHLZEITEN
                # ==================================================

                "Fix": {

                    "07:00": [
                        (1, "Morningshake Can")
                    ],

                    "09:00": [
                        (2, "2 belegte Protein Brote")
                    ],

                    "15:00": [
                        (1, "Apfel-Zimt-Protein-Muffins")
                    ],

                    "Nacht": [
                        (10, "Proteinpulver"),
                        (10, "Erdnussbutter"),
                        (250, "Magerquark")
                    ]
                },


                # ==================================================
                # 12:00 / 17:30
                # austauschbare Hauptmahlzeiten ~580 kcal
                # ==================================================

                "Hauptmahlzeiten": {

                    "SE – Seelachs": [
                        (200, "Seelachs"),
                        (100, "Kartoffeln"),
                        (90, "Reis roh"),
                        (100, "Karotten")
                    ],

                    "PO – Poulet": [
                        (150, "Poulet"),
                        (100, "Kartoffeln"),
                        (90, "Reis roh"),
                        (100, "Tomaten")
                    ],

                    "TO – Tofu": [
                        (200, "Tofu"),
                        (100, "Kartoffeln"),
                        (60, "Reis roh"),
                        (100, "Tomaten")
                    ],

                    "GA – Garnelen": [
                        (150, "Garnelen"),
                        (120, "Kartoffeln"),
                        (90, "Reis roh"),
                        (100, "Gemüsemix")
                    ],

                    "TI – Tilapia": [
                        (200, "Tilapia"),
                        (110, "Kartoffeln"),
                        (80, "Reis roh"),
                        (100, "Gemüsemix")
                    ]
                },


                # ==================================================
                # 19:00
                # ==================================================

                "19:00": {

                    "EI – Eiweiss": [
                        (100, "Eiweiss"),
                        (100, "Kartoffeln"),
                        (50, "Reis roh"),
                        (100, "Avocado")
                    ],

                    "MO – Mozzarella": [
                        (125, "Mozzarella"),
                        (100, "Kartoffeln"),
                        (30, "Reis roh"),
                        (50, "Avocado")
                    ]
                }
            }
        }
    }

# Benutzer, die den Mealplan-Tab sehen dürfen
MEALPLAN_USERS = ["Tamara", "Can", "Nemo", "Onur"]

def format_meal_amount(amount, food):
    """
    Bereitet Mengen für die Anzeige vor.

    Kartoffeln:
    Im Mealplan ist das Rohgewicht gespeichert.
    Für die Anzeige wird automatisch mit 0.8 multipliziert,
    damit das gekochte Gewicht angezeigt wird.
    """

    if food.lower() == "kartoffeln":
        amount = amount * 0.8
        return f"{amount:g} g {food} (gekocht)"

    return f"{amount:g} g {food}"

# ============================================================
# GOOGLE SHEETS FUNKTIONEN
# ============================================================

def get_user_worksheet(username):
    """
    Jeder Benutzer bekommt innerhalb der Gym Notes Database
    ein eigenes Tabellenblatt.
    """

    try:
        worksheet = sheet.worksheet(username)

    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(
            title=username,
            rows=2000,
            cols=50
        )

    return worksheet

def load_data(username):

    worksheet = get_user_worksheet(username)

    values = worksheet.get_all_values()

    if not values:
        return pd.DataFrame()

    headers = values[0]

    if not headers:
        return pd.DataFrame()

    rows = values[1:]

    if not rows:
        return pd.DataFrame(columns=headers)

    # Zeilen auf gleiche Länge bringen
    normalized_rows = []

    for row in rows:
        if len(row) < len(headers):
            row = row + [""] * (len(headers) - len(row))

        normalized_rows.append(row[:len(headers)])

    df = pd.DataFrame(normalized_rows, columns=headers)

    return df

def save_data(username, df):

    worksheet = get_user_worksheet(username)

    clean_df = df.copy().fillna("")

    for col in clean_df.columns:
        clean_df[col] = clean_df[col].apply(
            lambda x: x.isoformat()
            if isinstance(x, (date, datetime))
            else x
        )

    data = [
        clean_df.columns.tolist()
    ] + clean_df.astype(str).values.tolist()

    if not data[0]:
        raise ValueError(
            "Speichern abgebrochen: Keine Spalten vorhanden."
        )

    existing_values = worksheet.get_all_values()

    # Bestehende Zeilen nicht unbeabsichtigt entfernen
    if len(data) < len(existing_values):
        raise ValueError(
            "Speichern abgebrochen: Der neue Datenstand "
            "enthält weniger Zeilen als Google Sheets. "
            "Bitte die Änderung überprüfen."
        )

    if len(data[0]) > worksheet.col_count:
        worksheet.add_cols(
            len(data[0]) - worksheet.col_count
        )

    worksheet.update(
        range_name="A1",
        values=data
    )

def find_training_row_by_id(username, training_id):
    df = load_data(username)

    if df.empty or "Training ID" not in df.columns:
        return None

    matches = df.index[
        df["Training ID"].astype(str) == str(training_id)
    ].tolist()

    if len(matches) > 1:
        raise ValueError(
            "Doppelte Training ID gefunden. Speichern abgebrochen."
        )

    return matches[0] if matches else None

def save_training_row(username, entry, training_id=None):
    worksheet = get_user_worksheet(username)
    current_df = load_data(username)

    entry = entry.copy()

    # Neue Übung oder bestehende Übung?
    if training_id is None:
        training_id = str(uuid.uuid4())
        is_new = True
    else:
        is_new = False

    training_id = str(training_id)

    row_index = find_training_row_by_id(
        username, training_id
    )

    # Eine vorhandene ID darf niemals stillschweigend
    # eine neue Übung erzeugen.
    if not is_new and row_index is None:
        raise ValueError(
            "Training ID nicht gefunden. "
            "Speichern abgebrochen, um Duplikate zu verhindern."
        )

    if is_new and row_index is not None:
        raise ValueError(
            "Training ID existiert bereits."
        )

    entry["Training ID"] = training_id

    columns = list(current_df.columns)

    for col in entry:
        if col not in columns:
            columns.append(col)

    if len(columns) > worksheet.col_count:
        worksheet.add_cols(
            len(columns) - worksheet.col_count
        )

    if columns != list(current_df.columns):
        worksheet.update(
            range_name="A1",
            values=[columns]
        )

    def clean_value(value):
        if value is None:
            return ""
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if pd.isna(value):
            return ""
        return str(value)

    if is_new:
        row_data = {
            col: entry.get(col, "")
            for col in columns
        }

        values = [
            clean_value(row_data[col])
            for col in columns
        ]

        worksheet.append_row(
            values,
            value_input_option="RAW"
        )

    else:
        row_data = current_df.iloc[row_index].to_dict()
        row_data.update(entry)

        values = [
            clean_value(row_data.get(col, ""))
            for col in columns
        ]

        # Vor dem Überschreiben nochmals prüfen
        # (Schutz gegen zwischenzeitliche Änderungen)
        latest_df = load_data(username)

        if (
            row_index >= len(latest_df)
            or str(
                latest_df.iloc[row_index].get(
                    "Training ID", ""
                )
            ) != training_id
        ):
            raise ValueError(
                "Die Trainingszeile hat sich verändert. "
                "Speichern abgebrochen."
            )

        worksheet.update(
            range_name=f"A{row_index + 2}",
            values=[values]
        )

    return training_id

def delete_training_day(username, selected_date):
    worksheet = get_user_worksheet(username)
    df = load_data(username)

    if df.empty or "Datum" not in df.columns:
        raise ValueError("Keine Trainingsdaten gefunden.")

    matching_indices = df.index[
        df["Datum"].astype(str) == str(selected_date)
    ].tolist()

    if not matching_indices:
        raise ValueError(
            "Für dieses Datum wurde kein Training gefunden."
        )

    # Google-Sheets-Zeilennummern:
    # Zeile 1 = Überschriften, Zeile 2 = erster Datensatz
    sheet_rows = [int(idx) + 2 for idx in matching_indices]

    # Von unten nach oben löschen, damit sich die
    # Zeilennummern der übrigen Einträge nicht verschieben.
    for sheet_row in sorted(sheet_rows, reverse=True):
        worksheet.delete_rows(sheet_row)

    return len(sheet_rows)

# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def get_available_exercises(muscle_groups):

    available = []

    for group in muscle_groups:
        available.extend(exercises_by_group[group])

    return sorted(set(available))

def safe_float(value, default=0.0):

    try:
        if pd.isna(value) or value == "":
            return default

        return float(value)

    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):

    try:
        if pd.isna(value) or value == "":
            return default

        return int(float(value))

    except (ValueError, TypeError):
        return default

def safe_string(value, default=""):

    if pd.isna(value):
        return default

    return str(value)

def get_latest_body_weight(body_df):
    if body_df.empty:
        return None, None

    if not all(col in body_df.columns for col in ["Datum", "Gewicht kg"]):
        return None, None

    df = body_df.copy()

    df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
    df["Gewicht kg"] = pd.to_numeric(df["Gewicht kg"], errors="coerce")

    df = df.dropna(subset=["Datum", "Gewicht kg"])
    df = df[df["Gewicht kg"] > 0]

    if df.empty:
        return None, None

    latest = df.sort_values("Datum").iloc[-1]

    return float(latest["Gewicht kg"]), latest["Datum"].strftime("%d.%m.%Y")

def body_value_or_empty(value):
    if value is None or value == 0:
        return "Keine Angabe"

    return value

def get_last_set2_weight(saved_df, exercise, machine, griff):

    if saved_df.empty:
        return None

    required_columns = [
        "Datum",
        "Übung",
        "Machine",
        "Griff",
        "Set 2 Gewicht"
    ]

    if not all(col in saved_df.columns for col in required_columns):
        return None

    df = saved_df.copy()

    df["Datum"] = pd.to_datetime(
        df["Datum"],
        errors="coerce"
    )

    matches = df[
        (df["Übung"] == exercise) &
        (df["Machine"] == machine) &
        (df["Griff"] == griff)
    ].sort_values(
        "Datum",
        ascending=False
    )

    if matches.empty:
        return None

    weight = safe_float(
        matches.iloc[0]["Set 2 Gewicht"],
        default=0
    )

    return weight

def get_last_training_weights(saved_df, exercise):
    if saved_df.empty:
        return ""

    df = saved_df.copy()

    df["Datum"] = pd.to_datetime(
        df["Datum"], errors="coerce"
    )

    matches = df[
        df["Übung"] == exercise
    ].sort_values(
        "Datum", ascending=False, kind="stable"
    )

    if matches.empty:
        return ""

    last_training = matches.iloc[0]
    sets = []

    for set_number in range(1, 50):
        weight_col = f"Set {set_number} Gewicht"
        reps_col = f"Set {set_number} Wdh"

        if weight_col not in df.columns:
            continue

        weight = safe_float(
            last_training.get(weight_col, 0),
            default=0
        )

        reps = safe_float(
            last_training.get(reps_col, 0),
            default=0
        )

        if weight > 0 or reps > 0:
            sets.append(
                f"{set_number}. {weight:g} kg × {reps:g}"
            )

    return " · ".join(sets)

def get_last_mode_and_calories(saved_df):

    if saved_df.empty:
        return "Maintaining", 2200

    if "Datum" not in saved_df.columns:
        return "Maintaining", 2200

    df = saved_df.copy()

    df["Datum"] = pd.to_datetime(
        df["Datum"],
        errors="coerce"
    )

    df = df.sort_values(
        "Datum",
        ascending=False
    )

    if df.empty:
        return "Maintaining", 2200

    last_row = df.iloc[0]

    last_mode = last_row.get(
        "Modus",
        "Maintaining"
    )

    if last_mode not in [
        "Maintaining",
        "Bulk",
        "Cut"
    ]:
        last_mode = "Maintaining"

    last_calories = safe_int(
        last_row.get(
            "Kalorienziel",
            2200
        ),
        default=2200
    )

    return last_mode, last_calories

# ============================================================
# TRAININGSFORMULAR
# ============================================================

def training_form(username, saved_df, edit_date=None, edit_row_index=None):
    """Einzelne Sets sicher in einer Google-Sheets-Zeile speichern.

    Benötigt die vorhandenen App-Helfer: get_user_worksheet, load_data,
    load_body_data, get_latest_body_weight, get_last_training_weights,
    get_last_mode_and_calories, get_available_exercises, exercises_by_group,
    USERS, safe_float, safe_int, safe_string sowie st, pd, date, datetime, uuid.
    """
    import uuid
    import re

    def nonempty(value):
        return pd.notna(value) and str(value).strip().lower() not in ("", "nan", "none")

    def clean(value):
        if value is None:
            return ""
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        try:
            if pd.isna(value):
                return ""
        except (TypeError, ValueError):
            pass
        return str(value)

    def read_sheet():
        ws = get_user_worksheet(username)
        values = ws.get_all_values()
        if not values:
            return ws, [], []
        headers = values[0]
        return ws, headers, values[1:]

    def persist_set(entry, training_id, legacy_index=None):
        """Neue Zeile anhängen oder exakt eine bestehende Zeile aktualisieren."""
        ws, headers, rows = read_sheet()
        if headers and len(headers) != len(set(headers)):
            raise ValueError("Doppelte Spaltenüberschriften in Google Sheets.")
        if training_id is None:
            raise ValueError("Eine stabile Training ID fehlt.")
        id_column = headers.index("Training ID") if "Training ID" in headers else None
        matches = ([idx for idx, row in enumerate(rows)
                    if id_column is not None and len(row) > id_column
                    and row[id_column] == training_id])
        if len(matches) > 1:
            raise ValueError("Training ID ist mehrfach vorhanden; Abbruch.")
        if matches:
            target = matches[0]
        elif legacy_index is not None:
            target = int(legacy_index)
            if target < 0 or target >= len(rows):
                raise ValueError("Alte Trainingszeile nicht gefunden.")
            current = dict(zip(headers, rows[target]))
            if nonempty(current.get("Training ID", "")):
                raise ValueError("Die alte Trainingszeile hat inzwischen eine andere ID.")
            if (clean(current.get("Übung")) != clean(entry.get("Übung"))
                    or clean(current.get("Datum")) != clean(entry.get("Datum"))):
                raise ValueError("Alte Trainingszeile hat sich verändert; Abbruch.")
        else:
            target = None

        # Ein neues Training bekommt seine ID vor dem ersten Schreibversuch.
        # Bei unklarem Ergebnis bleibt die ID erhalten, damit ein Retry nicht dupliziert.
        for col in list(entry) + ["Training ID"]:
            if col not in headers:
                headers.append(col)
        if not headers:
            raise ValueError("Keine Spalten vorhanden.")
        if len(headers) > ws.col_count:
            ws.add_cols(len(headers) - ws.col_count)
        original_headers = ws.row_values(1)
        if original_headers != headers:
            ws.update(range_name="A1", values=[headers])

        if target is None:
            data = {col: "" for col in headers}
        else:
            data = dict(zip(headers, rows[target]))
        data.update(entry)
        data["Training ID"] = training_id
        output = [clean(data.get(col, "")) for col in headers]

        if target is None:
            # Nicht per append_row: gspread kann nach einem Timeout trotzdem
            # geschrieben haben. Ein erneuter Klick prüft zuerst dieselbe ID.
            ws.append_row(output, value_input_option="RAW")
        else:
            # Sheet-Zeile = Header + 0-basierter Datenindex + 1
            ws.update(range_name=f"A{target + 2}", values=[output])
        return training_id

    def saved_set_numbers(row):
        result = []
        for col in row.index:
            match = re.fullmatch(r"Set (\d+) (Gewicht|Wdh|Links Gewicht|Links Wdh|Rechts Gewicht|Rechts Wdh|Dauer Sekunden|Notiz)", str(col))
            if match and nonempty(row[col]):
                number = int(match.group(1))
                if number not in result:
                    result.append(number)
        return sorted(result)

    if "gym_editor_version" not in st.session_state:
        st.session_state.gym_editor_version = 0
    if "active_training_id" not in st.session_state:
        st.session_state.active_training_id = None
    if "gym_active_identity" not in st.session_state:
        st.session_state.gym_active_identity = None
    if "gym_edit_row" not in st.session_state:
        st.session_state.gym_edit_row = None
    if "gym_pending_save" not in st.session_state:
        st.session_state.gym_pending_save = False

    version = st.session_state.gym_editor_version
    def key(name):
        return f"gym_{version}_{name}"

    # Das ausgewählte Datum bleibt frei wählbar; keine automatische Datumswiederherstellung.
    selected_day = st.date_input(
        "Datum", value=pd.to_datetime(edit_date).date() if edit_date else date.today(),
        key=key("date"))
    selected_date = str(selected_day)

    # Editierziel wird beim Klick auf ✏️ gesetzt. Externes edit_row_index
    # wird nur verwendet, wenn noch kein internes Ziel gewählt wurde.
    if st.session_state.gym_edit_row is None and edit_row_index is not None:
        st.session_state.gym_edit_row = edit_row_index
    edit_index = st.session_state.gym_edit_row

    latest = load_data(username)
    if latest.empty:
        latest = pd.DataFrame(columns=list(saved_df.columns))
    if "Datum" in latest.columns:
        day_rows = latest[latest["Datum"].astype(str) == selected_date]
    else:
        day_rows = latest.iloc[0:0]

    st.markdown("### ✅ Bereits gespeichert")
    if day_rows.empty:
        st.caption("Für diesen Tag wurde noch keine Übung gespeichert.")
    for row_index, row in day_rows.iterrows():
        title = safe_string(row.get("Übung", "Übung"))
        status = safe_string(row.get("Status", "Abgeschlossen"))
        actual = len(saved_set_numbers(row))
        planned = safe_int(row.get("Anzahl Sets", actual))
        left, right = st.columns([5, 1])
        with left:
            st.markdown(f"**{title}** · {actual}/{planned} Sets · {status}")
        with right:
            if st.button("✏️", key=key(f"edit_{row_index}")):
                if st.session_state.active_training_id is not None:
                    st.warning("Schliesse zuerst deine aktuelle Übung ab.")
                else:
                    st.session_state.gym_edit_row = row_index
                    st.session_state.gym_editor_version += 1
                    st.rerun()

    old_row = None
    legacy_index = None
    if edit_index is not None:
        if edit_index not in latest.index:
            st.error("Die ausgewählte Trainingszeile existiert nicht mehr.")
            st.stop()
        old_row = latest.loc[edit_index]
        legacy_index = edit_index if not nonempty(old_row.get("Training ID", "")) else None
        if st.session_state.active_training_id is None:
            st.session_state.active_training_id = (
                str(old_row["Training ID"]) if legacy_index is None else str(uuid.uuid4()))
        st.info(f"Bearbeitung: {safe_string(old_row.get('Übung', 'Übung'))}")

    # Wenn eine Übung begonnen wurde, laden wir die aktuellen Werte derselben ID.
    active_id = st.session_state.active_training_id
    if active_id and "Training ID" in latest.columns:
        found = latest[latest["Training ID"].astype(str) == str(active_id)]
        if len(found) > 1:
            st.error("Doppelte Training ID. Speichern gestoppt.")
            st.stop()
        if len(found) == 1:
            old_row = found.iloc[0]
            legacy_index = None

    st.subheader("Allgemeine Angaben")
    last_mode, last_calories = get_last_mode_and_calories(latest)
    modes = ["Maintaining", "Bulk", "Cut"]
    default_mode = str(old_row.get("Modus", last_mode)) if old_row is not None else last_mode
    if default_mode not in modes:
        default_mode = "Maintaining"
    default_cal = safe_int(old_row.get("Kalorienziel", last_calories)) if old_row is not None else safe_int(last_calories)
    c1, c2 = st.columns(2)
    with c1:
        mode = st.selectbox("Modus", modes, index=modes.index(default_mode), key=key("mode"))
    with c2:
        calories = st.number_input("Kalorienziel", 0, 10000, int(default_cal), step=50, key=key("calories"))

    period_mode, period_start, period_end = False, "", ""
    if USERS[username]["gender"] == "female":
        old_period = str(old_row.get("Period Mode", "False")).lower() == "true" if old_row is not None else False
        period_mode = st.checkbox("Period Mode", value=old_period, key=key("period"))
        if period_mode:
            p1, p2 = st.columns(2)
            def period_date(col):
                value = old_row.get(col, "") if old_row is not None else ""
                return pd.to_datetime(value).date() if nonempty(value) else selected_day
            with p1:
                period_start = st.date_input("Periode Start", value=period_date("Periode Start"), key=key("period_start"))
            with p2:
                period_end = st.date_input("Periode Ende", value=period_date("Periode Ende"), key=key("period_end"))

    mood_default = safe_int(old_row.get("Stimmung", 3)) if old_row is not None else 3
    mood = st.slider("Stimmung / Gefühl", 1, 5, min(5, max(1, mood_default)),
                     help="1 = super toll, 3 = normal, 5 = dreckig", key=key("mood"))
    pain = ""
    if mood >= 4:
        pain = st.text_input("Gab es Schmerzen? Wenn ja, wo?",
                             value=clean(old_row.get("Schmerzen", "")) if old_row is not None else "",
                             key=key("pain"))

    st.subheader("Cardio")
    cardio_options = ["Kein Cardio", "Laufen", "Fahrrad", "Stepper", "Stairmaster",
                      "Crosstrainer", "Rudern", "Walking", "Anderes"]
    old_cardio = str(old_row.get("Cardio Form", "Kein Cardio")) if old_row is not None else "Kein Cardio"
    if old_cardio not in cardio_options:
        old_cardio = "Kein Cardio"
    cardio_type = st.selectbox("Cardio-Form", cardio_options,
                               index=cardio_options.index(old_cardio), key=key("cardio_type"))
    cardio_time = cardio_distance = cardio_calories = 0.0
    if cardio_type != "Kein Cardio":
        c1, c2, c3 = st.columns(3)
        with c1:
            cardio_time = st.number_input("Cardio Zeit in Minuten", min_value=0.0,
                value=safe_float(old_row.get("Cardio Zeit min", 0)) if old_row is not None else 0.0,
                step=1.0, key=key("cardio_time"))
        with c2:
            cardio_distance = st.number_input("Distanz in km", min_value=0.0,
                value=safe_float(old_row.get("Cardio Distanz km", 0)) if old_row is not None else 0.0,
                step=0.1, key=key("cardio_distance"))
        with c3:
            cardio_calories = st.number_input("Cardio Kalorien", min_value=0.0,
                value=safe_float(old_row.get("Cardio Kalorien", 0)) if old_row is not None else 0.0,
                step=10.0, key=key("cardio_calories"))

    st.subheader("Krafttraining")
    all_groups = ["Rücken", "Brust", "Beine", "Glutes", "Trizeps", "Bizeps",
                  "Schultern", "core", "Calisthenics", "TRX"]
    old_exercise = clean(old_row.get("Übung", "")) if old_row is not None else ""
    defaults = [g for g in all_groups if old_exercise in exercises_by_group.get(g, [])]
    muscle_groups = st.multiselect("Welche Muskelgruppe trainierst du?", all_groups,
                                   default=defaults, key=key("muscle_groups"))
    available_exercises = list(get_available_exercises(muscle_groups))
    if old_exercise and old_exercise not in available_exercises:
        available_exercises.append(old_exercise)
    available_exercises = sorted(set(available_exercises))
    if not available_exercises:
        st.info("Wähle mindestens eine Muskelgruppe aus.")
        return
    exercise = st.selectbox("Übung", available_exercises,
                            index=available_exercises.index(old_exercise) if old_exercise in available_exercises else 0,
                            key=key("exercise"))

    # Nach dem ersten Set ist die Zuordnung fix. Datum und Übung können
    # nicht stillschweigend zu einer anderen gespeicherten Zeile werden.
    identity = (selected_date, exercise)
    if old_row is not None and active_id:
        expected = (clean(old_row.get("Datum")), clean(old_row.get("Übung")))
        if identity != expected:
            st.error(f"Du bearbeitest '{expected[1]}' vom {expected[0]}. "
                     "Wähle dieses Datum und diese Übung, um fortzufahren.")
            return
    if st.session_state.gym_active_identity is not None and active_id:
        if identity != tuple(st.session_state.gym_active_identity):
            st.error("Die laufende Übung darf nicht gewechselt werden. "
                     "Wähle wieder die ursprüngliche Übung und das Datum.")
            return

    execution_options = ["Beidseitig", "Einseitig"]
    old_execution = clean(old_row.get("Ausführung", "Beidseitig")) if old_row is not None else "Beidseitig"
    execution_type = st.segmented_control("Ausführung", options=execution_options,
        default=old_execution if old_execution in execution_options else "Beidseitig",
        selection_mode="single", key=key("execution")) or "Beidseitig"
    default_sets = safe_int(old_row.get("Anzahl Sets", 4)) if old_row is not None else 4
    if default_sets < 1:
        default_sets = max(saved_set_numbers(old_row), default=4) if old_row is not None else 4
    number_of_sets = int(st.number_input("Anzahl Sets", min_value=1,
                                        value=default_sets, step=1, key=key("number_sets")))
    if exercise in exercises_by_group.get("Calisthenics", []) or exercise in exercises_by_group.get("TRX", []) or exercise == "Hanging":
        machine_options = ["Bodyweight"]
    else:
        machine_options = ["Cable", "Freigewicht", "Maschine"]
    old_machine = clean(old_row.get("Machine", "")) if old_row is not None else ""
    machine = st.selectbox("Machine", machine_options,
        index=machine_options.index(old_machine) if old_machine in machine_options else 0,
        key=key("machine"))
    extra_info = ""
    if exercise in exercises_by_group.get("TRX", []):
        extra_options = ["Sehr aufrecht / leicht", "Mittel", "Sehr schräg / schwer"]
        old_extra = clean(old_row.get("Extra Info", "")) if old_row is not None else ""
        extra_info = st.selectbox("Schräge / Schwierigkeit", extra_options,
            index=extra_options.index(old_extra) if old_extra in extra_options else 0, key=key("extra"))
    elif exercise == "Hanging":
        extra_info = st.text_input("Hanging-Variante / Notiz",
            value=clean(old_row.get("Extra Info", "")) if old_row is not None else "", key=key("extra"))
    if exercise in exercises_by_group.get("Beine", []) or exercise in exercises_by_group.get("Glutes", []):
        griff = "Nicht relevant"
    else:
        grip_options = ["Neutral", "Breit", "Eng", "Untergriff", "Obergriff"]
        old_grip = clean(old_row.get("Griff", "Neutral")) if old_row is not None else "Neutral"
        griff = st.selectbox("Griff", grip_options,
            index=grip_options.index(old_grip) if old_grip in grip_options else 0, key=key("grip"))
    note = st.text_input("Notiz zur Übung",
        value=clean(old_row.get("Notiz Übung", "")) if old_row is not None else "", key=key("note"))
    if any(g in muscle_groups for g in ("Rücken", "Schultern")):
        st.warning("⚠️ Schulterblätter nach hinten und runter drücken.")

    if machine == "Bodyweight":
        body_weight, body_day = get_latest_body_weight(load_body_data(username))
        if body_weight is not None:
            st.caption(f"⚖️ Letztes Körpergewicht: {body_weight:g} kg (vom {body_day})")
        else:
            st.caption("Noch kein Körpergewicht unter 'Body Maße' gespeichert.")

    # Letztes Training kompakt anzeigen, ohne das aktuelle Training zu verwenden.
    history = latest.copy()
    if active_id and "Training ID" in history.columns:
        history = history[history["Training ID"].astype(str) != str(active_id)]
    last_weights = get_last_training_weights(history, exercise)
    if last_weights:
        st.caption(f"Letztes Training: {last_weights}")
    weight_cols = [c for c in history.columns if re.fullmatch(r"Set \d+ (Gewicht|Links Gewicht|Rechts Gewicht)", str(c))]
    exercise_history = history[history["Übung"].astype(str) == exercise] if "Übung" in history.columns else history.iloc[0:0]
    max_weight = None
    if weight_cols and not exercise_history.empty:
        weights = pd.to_numeric(exercise_history[weight_cols].stack(), errors="coerce").dropna()
        if not weights.empty:
            max_weight = float(weights.max())
    if max_weight is not None:
        st.caption(f"🏆 Höchstgewicht bisher: {max_weight:g} kg")

    is_time_exercise = exercise in ["Side plank right", "Side plank left", "Plank", "Hanging"]
    uses_weight = machine != "Bodyweight"
    if exercise in exercises_by_group.get("core", []) and not is_time_exercise and machine != "Bodyweight":
        default_weight = any(safe_float(old_row.get(f"Set {n} Gewicht", 0)) > 0
            for n in range(1, number_of_sets + 1)) if old_row is not None else False
        uses_weight = st.checkbox("Mit Gewicht gearbeitet?", value=default_weight, key=key("uses_weight"))

    base_entry = {
        "Benutzer": username, "Datum": selected_day, "Modus": mode,
        "Kalorienziel": calories, "Ausführung": execution_type,
        "Period Mode": period_mode, "Periode Start": period_start,
        "Periode Ende": period_end, "Stimmung": mood, "Schmerzen": pain,
        "Cardio Form": cardio_type, "Cardio Zeit min": cardio_time,
        "Cardio Distanz km": cardio_distance, "Cardio Kalorien": cardio_calories,
        "Übung": exercise, "Machine": machine, "Griff": griff,
        "Extra Info": extra_info, "Notiz Übung": note, "Anzahl Sets": number_of_sets,
        "Status": clean(old_row.get("Status", "In Bearbeitung")) if old_row is not None else "In Bearbeitung"
    }
    if not base_entry["Status"]:
        base_entry["Status"] = "In Bearbeitung"

    st.markdown("### Sets")
    for s in range(number_of_sets):
        n = s + 1
        old = old_row if old_row is not None else {}
        with st.expander(f"Set {n}", expanded=True):
            values = {"weight": 0.0, "reps": 0.0, "duration": 0.0,
                      "left_weight": 0.0, "left_reps": 0.0,
                      "right_weight": 0.0, "right_reps": 0.0}
            if is_time_exercise:
                values["duration"] = st.number_input("Zeit in Sekunden", min_value=0.0,
                    max_value=3600.0, value=safe_float(old.get(f"Set {n} Dauer Sekunden", 0)),
                    step=5.0, key=key(f"duration_{s}"))
            elif execution_type == "Einseitig":
                for side, label in (("Links", "links"), ("Rechts", "rechts")):
                    st.markdown(f"**{side}**")
                    prefix = "left" if side == "Links" else "right"
                    if uses_weight:
                        values[f"{prefix}_weight"] = st.number_input(f"Gewicht {label}", min_value=0.0,
                            max_value=400.0, value=safe_float(old.get(f"Set {n} {side} Gewicht", 0)),
                            step=0.5, key=key(f"{prefix}_weight_{s}"))
                    values[f"{prefix}_reps"] = st.number_input(f"Wdh {label}", min_value=0.0,
                        max_value=1000.0, value=safe_float(old.get(f"Set {n} {side} Wdh", 8), default=8.0),
                        step=0.5, key=key(f"{prefix}_reps_{s}"))
            else:
                if uses_weight:
                    values["weight"] = st.number_input("Gewicht", min_value=0.0,
                        max_value=400.0, value=safe_float(old.get(f"Set {n} Gewicht", 0)),
                        step=0.5, key=key(f"weight_{s}"))
                values["reps"] = st.number_input("Wdh", min_value=0.0,
                    max_value=1000.0, value=safe_float(old.get(f"Set {n} Wdh", 8), default=8.0),
                    step=0.5, key=key(f"reps_{s}"))
            set_note = st.text_input("Set-Notiz", value=clean(old.get(f"Set {n} Notiz", "")),
                                     key=key(f"set_note_{s}"))
            if st.button(f"💾 Set {n} speichern", key=key(f"save_{s}"),
                         disabled=st.session_state.gym_pending_save):
                st.session_state.gym_pending_save = True
                # ID vor dem ersten Google-Sheets-Aufruf merken; Retry bleibt idempotent.
                if st.session_state.active_training_id is None:
                    st.session_state.active_training_id = str(uuid.uuid4())
                training_id = st.session_state.active_training_id
                entry = base_entry.copy()
                entry.update({
                    f"Set {n} Gewicht": values["weight"],
                    f"Set {n} Wdh": values["reps"],
                    f"Set {n} Links Gewicht": values["left_weight"],
                    f"Set {n} Links Wdh": values["left_reps"],
                    f"Set {n} Rechts Gewicht": values["right_weight"],
                    f"Set {n} Rechts Wdh": values["right_reps"],
                    f"Set {n} Dauer Sekunden": values["duration"],
                    f"Set {n} Notiz": set_note
                })
                try:
                    with st.spinner(f"Set {n} wird gespeichert..."):
                        persist_set(entry, training_id, legacy_index=legacy_index)
                    st.session_state.gym_active_identity = identity
                    st.toast(f"Set {n} gespeichert! ✓")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Set {n} konnte nicht gespeichert werden: {exc}")
                finally:
                    st.session_state.gym_pending_save = False

    if st.button("✓ Übung abschliessen", type="primary", key=key("finish"),
                 disabled=st.session_state.gym_pending_save):
        training_id = st.session_state.active_training_id
        if not training_id:
            st.warning("Speichere zuerst mindestens ein Set.")
        else:
            try:
                st.session_state.gym_pending_save = True
                with st.spinner("Übung wird abgeschlossen..."):
                    # Die Originaldaten für Datum und Übung müssen erhalten bleiben.
                    persist_set({"Status": "Abgeschlossen"}, training_id)
                st.session_state.active_training_id = None
                st.session_state.gym_active_identity = None
                st.session_state.gym_edit_row = None
                st.session_state.gym_editor_version += 1
                st.toast("Übung abgeschlossen! ✓")
                st.rerun()
            except Exception as exc:
                st.error(f"Übung konnte nicht abgeschlossen werden: {exc}")
            finally:
                st.session_state.gym_pending_save = False



# ============================================================
# LOGIN
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if "edit_date" not in st.session_state:
    st.session_state.edit_date = None

if "exercise_edit_index" not in st.session_state:
    st.session_state.exercise_edit_index = None

if not st.session_state.logged_in:

    st.title("🔐 Login")

    username_input = st.text_input(
        "Benutzername"
    )

    password = st.text_input(
        "Passwort",
        type="password"
    )


    if st.button("Einloggen"):

        if (
            username_input in USERS
            and USERS[username_input]["password"]
            == password
        ):

            st.session_state.logged_in = True

            st.session_state.username = \
                username_input

            st.session_state.login_time = \
                datetime.now()

            st.rerun()

        else:

            st.error(
                "Benutzername oder Passwort falsch"
            )


    st.stop()


# ============================================================
# SESSION TIMEOUT
# ============================================================

if "login_time" not in st.session_state:

    st.session_state.login_time = \
        datetime.now()


if (
    datetime.now()
    - st.session_state.login_time
    > timedelta(minutes=120)
):

    st.session_state.logged_in = False

    st.session_state.edit_date = None

    st.warning(
        "Session abgelaufen. Bitte neu einloggen."
    )

    st.rerun()


# ============================================================
# DATEN DES BENUTZERS LADEN
# ============================================================

username = \
    st.session_state.username


saved_df = load_data(
    username
)
body_df = load_body_data(
    username
)
# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.success(
    f"Eingeloggt als {username}"
)


if st.sidebar.button(
    "Logout"
):

    st.session_state.logged_in = False

    st.session_state.edit_date = None

    st.rerun()


# ============================================================
# APP
# ============================================================


AVATAR_CONFIG = {
    "Tamara": {
        1: "avatars/Tamara/A1T.png",
        2: "avatars/Tamara/A2T.png",
        3: "avatars/Tamara/A3T.png",
        4: "avatars/Tamara/A4T.png",
        5: "avatars/Tamara/A5T.png",
    },
    "Nemo": {
        1: "avatars/Nemo/A1N.png",
        2: "avatars/Nemo/A2N.png",
        3: "avatars/Nemo/A3N.png",
        4: "avatars/Nemo/A4N.png",
        5: "avatars/Nemo/A5N.png",
    },
    "Can": {
        1: "avatars/Can/A1C.png",
        2: "avatars/Can/A2C.png",
        3: "avatars/Can/A3C.png",
        4: "avatars/Can/A4C.png",
        5: "avatars/Can/A5C.png",
    },
    "Onur": {
            1: "avatars/Onur/A1O.png",
            2: "avatars/Onur/A2O.png",
            3: "avatars/Onur/A3O.png",
            4: "avatars/Onur/A4O.png",
            5: "avatars/Onur/A5O.png",
        }
}


def show_avatar(username, level):

    st.title("🏋️ Gym Notes")

    if username not in AVATAR_CONFIG:
        return

    avatar_path = AVATAR_CONFIG[username].get(level)

    if not avatar_path or not os.path.exists(avatar_path):
        return

    st.markdown(
        '<div id="gym-avatar-marker"></div>',
        unsafe_allow_html=True
    )

    st.image(
        avatar_path,
        width=260
    )

    st.markdown(
        """
        <style>

        /* =====================================================
           AVATAR DESKTOP
           ===================================================== */

        div[data-testid="stElementContainer"]:has(#gym-avatar-marker)
        + div[data-testid="stElementContainer"] {

            position: absolute;
            top: 60px;
            right: 150px;
            width: 320px !important;

            z-index: 0;
            pointer-events: none;
        }

        div[data-testid="stElementContainer"]:has(#gym-avatar-marker) {
            display: none;
        }


        /* =====================================================
           HANDY
           ===================================================== */

        @media (max-width: 768px) {

            /* =========================================
            AVATAR
            ========================================= */

            div[data-testid="stElementContainer"]:has(#gym-avatar-marker)
            + div[data-testid="stElementContainer"] {

                position: absolute !important;

                top: 110px !important;
                right: -10px !important;

                width: 200px !important;

                z-index: 0 !important;
                pointer-events: none !important;
            }

            div[data-testid="stElementContainer"]:has(#gym-avatar-marker)
            + div[data-testid="stElementContainer"] img {

                width: 200px !important;
                max-width: 200px !important;
                height: auto !important;
            }


            /* =========================================
            NUR AVATAR-EINGABEFELDER
            ========================================= */


            /* KALORIENZIEL */
            .st-key-avatar_general [data-testid="stNumberInputContainer"] {
                background-color: color-mix(
                    in srgb,
                    var(--secondary-background-color) 65%,
                    transparent
                ) !important;
            }


            /* =========================================
            DATUM
            ========================================= */

            .st-key-avatar_date [data-testid="stDateInputField"] {
                background-color: color-mix(
                    in srgb,
                    var(--secondary-background-color) 65%,
                    transparent
                ) !important;
            }


            /* =========================================
            MODUS
            ========================================= */

            /* Der Wrapper, der Input + Pfeil enthält */
            .st-key-avatar_general .react-aria-ComboBox div:has(> input[aria-label="Modus"]) {
                background-color: color-mix(
                    in srgb,
                    var(--secondary-background-color) 65%,
                    transparent
                ) !important;
            }

            /* Input selbst transparent + Schrift nach Theme */
            .st-key-avatar_general .react-aria-ComboBox input[aria-label="Modus"] {
                background: transparent !important;
                color: var(--text-color) !important;
                -webkit-text-fill-color: var(--text-color) !important;
            }


            /* =========================================
            TEXT IMMER VORNE + THEME-ABHÄNGIG
            ========================================= */

            .st-key-avatar_date input,
            .st-key-avatar_general input {
                color: var(--text-color) !important;
                -webkit-text-fill-color: var(--text-color) !important;
                opacity: 1 !important;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )

def get_avatar_level(saved_df):

    if saved_df.empty or "Datum" not in saved_df.columns:
        return 1

    df = saved_df.copy()

    df["Datum"] = pd.to_datetime(
        df["Datum"],
        errors="coerce"
    )

    df = df.dropna(subset=["Datum"])

    if df.empty:
        return 1

    # =========================================================
    # EIN TRAININGSTAG ZÄHLT NUR EINMAL
    # =========================================================

    training_dates = (
        df["Datum"]
        .dt.normalize()
        .drop_duplicates()
    )

    # =========================================================
    # TRAININGS PRO KALENDERWOCHE
    # =========================================================

    training_df = pd.DataFrame({
        "Datum": training_dates
    })

    iso = training_df["Datum"].dt.isocalendar()

    training_df["Jahr"] = iso.year.astype(int)
    training_df["Woche"] = iso.week.astype(int)

    weekly_counts = (
        training_df
        .groupby(["Jahr", "Woche"])
        .size()
        .to_dict()
    )

    # =========================================================
    # AVATAR-TABELLE
    #
    # Zeile = mindestens X Trainings pro Woche
    # Spalte = X Wochen am Stück
    # =========================================================

    avatar_table = {
        1: {1: 1, 2: 1, 3: 2, 4: 3, 5: 3},
        2: {1: 1, 2: 2, 3: 3, 4: 3, 5: 4},
        3: {1: 1, 2: 2, 3: 3, 4: 3, 5: 4},
        4: {1: 2, 2: 3, 3: 4, 4: 4, 5: 5},
        5: {1: 2, 2: 3, 3: 4, 4: 5, 5: 5},
    }

    # =========================================================
    # AKTUELLE KALENDERWOCHE
    # =========================================================

    today = pd.Timestamp.today().normalize()

    current_iso = today.isocalendar()

    current_year = int(current_iso.year)
    current_week = int(current_iso.week)

    # =========================================================
    # DIE LETZTEN 5 KALENDERWOCHEN ERZEUGEN
    #
    # Dadurch zählen auch Wochen mit 0 Trainings.
    # =========================================================

    current_monday = (
        today - pd.Timedelta(days=today.weekday())
    )

    weeks = []

    for i in range(5):

        monday = current_monday - pd.Timedelta(
            weeks=i
        )

        iso_week = monday.isocalendar()

        year = int(iso_week.year)
        week = int(iso_week.week)

        count = weekly_counts.get(
            (year, week),
            0
        )

        weeks.append({
            "year": year,
            "week": week,
            "count": count,
            "current": i == 0
        })

    # =========================================================
    # BESTES AVATAR-LEVEL BESTIMMEN
    # =========================================================

    best_level = 1

    for min_trainings in range(1, 6):

        streak = 0

        for week_data in weeks:

            count = week_data["count"]
            is_current_week = week_data["current"]

            # -------------------------------------------------
            # AKTUELLE WOCHE
            #
            # Wenn das Ziel bereits erreicht wurde:
            # → aktuelle Woche zählt zur Streak.
            #
            # Wenn noch nicht:
            # → sie zerstört die vorherige Streak NICHT.
            # -------------------------------------------------

            if is_current_week:

                if count >= min_trainings:
                    streak += 1

                # Noch nicht genug Trainings:
                # einfach zur letzten abgeschlossenen Woche gehen
                continue

            # -------------------------------------------------
            # ABGESCHLOSSENE WOCHEN
            # -------------------------------------------------

            if count >= min_trainings:
                streak += 1

            else:
                break

        # Tabelle geht maximal bis 5 Wochen
        streak = min(streak, 5)

        if streak >= 1:

            level = avatar_table[
                min_trainings
            ][streak]

            best_level = max(
                best_level,
                level
            )

    return best_level

avatar_level = get_avatar_level(saved_df)


# ============================================================
# BEARBEITUNGSMODUS
# ============================================================

if st.session_state.edit_date:

    st.warning(
        f"Bearbeitungsmodus für Training vom "
        f"{st.session_state.edit_date}"
    )


    training_form(
        username,
        saved_df,
        edit_date=st.session_state.edit_date
    )


    if st.button(
        "Bearbeitung abbrechen"
    ):

        st.session_state.edit_date = None

        st.rerun()


# ============================================================
# HAUPTANSICHT
# ============================================================

if username in MEALPLAN_USERS:

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ Neues Training",
        "📖 Gespeicherte Trainings",
        "📊 Statistik",
        "🍽️ Mealplan",
        "📏 Body Maße"
    ])

else:

    tab1, tab2, tab3, tab5 = st.tabs([
        "➕ Neues Training",
        "📖 Gespeicherte Trainings",
        "📊 Statistik",
        "📏 Body Maße"
    ])


    # ========================================================
    # NEUES TRAINING
    # ========================================================

with tab1:
        
        show_avatar(username, avatar_level)
        training_form(
            username,
            saved_df,
            edit_date=st.session_state.edit_date,
            edit_row_index=st.session_state.exercise_edit_index
        )


    # ========================================================
    # GESPEICHERTE TRAININGS
    # ========================================================

with tab2:
        show_avatar(username, avatar_level)
        st.subheader(
            "📖 Gespeicherte Trainings"
        )


        if saved_df.empty:

            st.info(
                "Noch keine gespeicherten Trainings vorhanden."
            )


        elif "Datum" not in saved_df.columns:

            st.warning(
                "Die Tabelle enthält noch keine Datum-Spalte."
            )


        else:

            saved_df["Datum"] = \
                saved_df["Datum"].astype(str)


            available_dates = sorted(
                saved_df[
                    "Datum"
                ].dropna().unique(),
                reverse=True
            )


            date_options = [
                f"🔴 {d}"
                for d in available_dates
            ]


            selected_date_label = \
                st.selectbox(
                    "Trainingstag auswählen",
                    date_options
                )


            selected_date_str = \
                selected_date_label.replace(
                    "🔴 ",
                    ""
                )


            day_df = saved_df[
                saved_df["Datum"]
                == selected_date_str
            ]


            if day_df.empty:

                st.info(
                    "Für dieses Datum gibt es kein gespeichertes Training."
                )


            else:

                # Nur interessante Spalten anzeigen
                display_columns = [
                    col
                    for col in [
                        "Übung",
                        "Machine",
                        "Griff",
                        "Extra Info",
                        "Set 1 Gewicht",
                        "Set 1 Wdh",
                        "Set 1 Dauer Sekunden",
                        "Set 2 Gewicht",
                        "Set 2 Wdh",
                        "Set 2 Dauer Sekunden",
                        "Set 3 Gewicht",
                        "Set 3 Wdh",
                        "Set 3 Dauer Sekunden",
                        "Set 4 Gewicht",
                        "Set 4 Wdh",
                        "Set 4 Dauer Sekunden",
                        "Notiz Übung"
                    ]
                    if col in day_df.columns
                ]


                st.dataframe(
                    day_df[
                        display_columns
                    ],
                    use_container_width=True,
                    hide_index=True
                )


                c1, c2 = st.columns(2)


                with c1:

                    if st.button(
                        "✏️ Dieses Training bearbeiten"
                    ):

                        st.session_state.edit_date = \
                            selected_date_str

                        st.rerun()


                
                with c2:

                    if st.button(
                        "🗑️ Dieses Training löschen"
                    ):
                        st.session_state.confirm_delete_date = (
                            selected_date_str
                        )

                if st.session_state.get(
                    "confirm_delete_date"
                ) == selected_date_str:

                    st.warning(
                        f"Willst du wirklich alle Übungen "
                        f"vom {selected_date_str} löschen?"
                    )

                    confirm_col, cancel_col = st.columns(2)

                    with confirm_col:
                        if st.button(
                            "Ja, endgültig löschen",
                            type="primary"
                        ):
                            try:
                                deleted_count = delete_training_day(
                                    username,
                                    selected_date_str
                                )

                                st.session_state.pop(
                                    "confirm_delete_date", None
                                )

                                st.toast(
                                    f"{deleted_count} Übung(en) gelöscht."
                                )
                                st.rerun()

                            except Exception as e:
                                st.error(
                                    f"Löschen fehlgeschlagen: {e}"
                                )

                    with cancel_col:
                        if st.button("Abbrechen"):
                            st.session_state.pop(
                                "confirm_delete_date", None
                            )
                            st.rerun()


with tab3:
        show_avatar(username, avatar_level)
        st.subheader(
            "📊 Statistik"
        )

        # ====================================================
        # EXPORT
        # ====================================================

        st.subheader(
            "📤 Export"
        )

        csv_data = saved_df.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        st.download_button(
            label="⬇️ CSV exportieren",
            data=csv_data,
            file_name=f"{username}_gym_export.csv",
            mime="text/csv"
        )


        # Excel im Arbeitsspeicher erzeugen
        excel_buffer = BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            saved_df.to_excel(
                writer,
                index=False,
                sheet_name="Gym Notes"
            )


        st.download_button(
            label="⬇️ Excel exportieren",
            data=excel_buffer.getvalue(),
            file_name=f"{username}_gym_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


        # ====================================================
        # STATISTIK
        # ====================================================

        if saved_df.empty:

            st.info(
                "Noch keine Daten für Statistik vorhanden."
            )


        else:

            stats_df = saved_df.copy()


            if "Datum" in stats_df.columns:

                stats_df["Datum"] = \
                    pd.to_datetime(
                        stats_df["Datum"],
                        errors="coerce"
                    )


            # Zahlen-Spalten wieder numerisch machen
            numeric_columns = [
                "Stimmung",
                "Cardio Zeit min",
                "Cardio Distanz km",
                "Cardio Kalorien",
                "Set 1 Gewicht",
                "Set 2 Gewicht",
                "Set 3 Gewicht",
                "Set 4 Gewicht",
                "Set 1 Wdh",
                "Set 2 Wdh",
                "Set 3 Wdh",
                "Set 4 Wdh",
                "Set 1 Dauer Sekunden",
                "Set 2 Dauer Sekunden",
                "Set 3 Dauer Sekunden",
                "Set 4 Dauer Sekunden"
            ]


            for col in numeric_columns:

                if col in stats_df.columns:

                    stats_df[col] = \
                        pd.to_numeric(
                            stats_df[col],
                            errors="coerce"
                        ).fillna(0)


            # ------------------------------------------------
            # KENNZAHLEN
            # ------------------------------------------------

            if "Datum" in stats_df.columns:

                st.metric(
                    "Anzahl Trainings",
                    stats_df[
                        "Datum"
                    ].nunique()
                )


            st.metric(
                "Anzahl Übungen gesamt",
                len(stats_df)
            )


            # ------------------------------------------------
            # ÜBUNGEN
            # ------------------------------------------------

            if "Übung" in stats_df.columns:

                st.subheader(
                    "Trainings pro Übung"
                )


                exercise_counts = \
                    stats_df[
                        "Übung"
                    ].value_counts()


                st.bar_chart(
                    exercise_counts
                )


                # ============================================
                # GEWICHTSENTWICKLUNG
                # ============================================

                exercises = sorted(
                    stats_df[
                        "Übung"
                    ].dropna().unique()
                )


                if exercises:

                    st.subheader(
                        "Gewichtsentwicklung pro Übung"
                    )


                    selected_exercise = \
                        st.selectbox(
                            "Übung für Verlauf auswählen",
                            exercises
                        )


                    progress_df = stats_df[
                        stats_df["Übung"]
                        == selected_exercise
                    ].copy()

                    
                    last_weights = get_last_training_weights(
                        saved_df, selected_exercise
                    )

                    if last_weights:
                        st.caption(f"Letztes Training: {last_weights}")


                    if "Datum" in progress_df.columns:

                        progress_df = \
                            progress_df.sort_values(
                                "Datum"
                            )


                    # ============================================
                    # ALLE VORHANDENEN SETS AUTOMATISCH ERKENNEN
                    # ============================================

                    weight_columns = [
                        col
                        for col in progress_df.columns
                        if col.startswith("Set ")
                        and col.endswith(" Gewicht")
                    ]


                    # Set-Spalten richtig sortieren:
                    # Set 1, Set 2, Set 3 ... Set 10 usw.
                    def get_set_number(column_name):
                        try:
                            return int(column_name.split(" ")[1])
                        except:
                            return 999


                    weight_columns = sorted(
                        weight_columns,
                        key=get_set_number
                    )


                    # ============================================
                    # GEWICHTE NUMERISCH MACHEN
                    # ============================================

                    for col in weight_columns:

                        progress_df[col] = pd.to_numeric(
                            progress_df[col],
                            errors="coerce"
                        )


                    # ============================================
                    # NUR TATSÄCHLICH BENUTZTE SETS ANZEIGEN
                    # ============================================

                    weight_columns = [
                        col
                        for col in weight_columns
                        if progress_df[col].notna().any()
                        and (progress_df[col] > 0).any()
                    ]


                    # ============================================
                    # CHART
                    # ============================================

                    if (
                        weight_columns
                        and "Datum" in progress_df.columns
                    ):

                        chart_df = progress_df[
                            ["Datum"] + weight_columns
                        ].copy()

                        chart_df = chart_df.set_index("Datum")

                        # 0 kg nicht als echte Messung darstellen
                        chart_df = chart_df.replace(0, np.nan)

                        st.line_chart(chart_df)

                    else:

                        st.info(
                            "Für diese Übung sind noch keine Gewichtsdaten vorhanden."
                        )


            # ------------------------------------------------
            # STIMMUNG
            # ------------------------------------------------

            if "Stimmung" in stats_df.columns:

                st.subheader(
                    "Durchschnittliche Stimmung"
                )


                avg_mood = \
                    stats_df[
                        "Stimmung"
                    ].mean()


                st.metric(
                    "Ø Stimmung",
                    round(
                        avg_mood,
                        2
                    )
                )


            # ------------------------------------------------
            # CARDIO
            # ------------------------------------------------

            cardio_columns = [
                "Cardio Zeit min",
                "Cardio Distanz km",
                "Cardio Kalorien"
            ]


            if all(
                col in stats_df.columns
                for col in cardio_columns
            ):

                st.subheader(
                    "Cardio gesamt"
                )


                total_cardio_time = \
                    stats_df[
                        "Cardio Zeit min"
                    ].sum()


                total_cardio_distance = \
                    stats_df[
                        "Cardio Distanz km"
                    ].sum()


                total_cardio_calories = \
                    stats_df[
                        "Cardio Kalorien"
                    ].sum()


                c1, c2, c3 = \
                    st.columns(3)


                c1.metric(
                    "Cardio Minuten",
                    round(
                        total_cardio_time,
                        1
                    )
                )


                c2.metric(
                    "Cardio km",
                    round(
                        total_cardio_distance,
                        1
                    )
                )


                c3.metric(
                    "Cardio kcal",
                    round(
                        total_cardio_calories,
                        0
                    )
                )

    # ========================================================
    # MEALPLAN
    # ========================================================

if username in MEALPLAN_USERS:

        with tab4:

            st.subheader("🍽️ Mealplan")

            # ------------------------------------------------
            # KALORIENPLAN
            # ------------------------------------------------

            if username == "Nemo":
                user_mealplans = MEAL_PLANS["Can"]
            elif username == "Onur":
                user_mealplans = MEAL_PLANS["Can"]
            else:
                user_mealplans = MEAL_PLANS[username]

            calorie_options = list(user_mealplans.keys())

            if username == "Can" and "3500 kcal" in calorie_options:
                default_calorie_index = calorie_options.index("3500 kcal")

            elif username == "Nemo" and "3000 kcal" in calorie_options:
                default_calorie_index = calorie_options.index("3000 kcal")

            elif username == "Tamara" and "2400 kcal" in calorie_options:
                default_calorie_index = calorie_options.index("2400 kcal")

            else:
                default_calorie_index = 0

            calorie_plan = st.selectbox(
                "Kalorienplan",
                calorie_options,
                index=default_calorie_index,
                key="mealplan_calories"
            )

            selected_plan = user_mealplans[calorie_plan]

            # ------------------------------------------------
            # FALLS NOCH KEINE DATEN VORHANDEN SIND
            # ------------------------------------------------

            if not selected_plan:

                st.info(
                    "Für diesen Mealplan sind noch keine Mahlzeiten hinterlegt."
                )

            else:

                # ====================================================
                # MAHLZEIT AUSWÄHLEN
                # ====================================================

                meal_sections = list(selected_plan.keys())

                # ====================================================
                # TAMARA – MAHLZEITENAUSWAHL
                # ====================================================

                if username == "Tamara":

                    meal_time = st.segmented_control(
                        "Mahlzeit",
                        options=[
                            "Frühstück",
                            "9i / Nacht",
                            "Mittag / 4i"
                        ],
                        default="Frühstück",
                        selection_mode="single",
                        key="mealplan_time"
                    )

                    if meal_time is None:
                        meal_time = "Frühstück"

                    # ================================================
                    # FRÜHSTÜCK
                    # ================================================

                    if meal_time == "Frühstück":

                        selected_meal = selected_plan["Frühstück"]

                        meal_title = "Frühstück"

                    # ================================================
                    # 9i / NACHT UND MITTAG / 4i
                    # ================================================

                    else:

                        meal_options = selected_plan[meal_time]

                        option_names = list(meal_options.keys())

                        selected_option = st.segmented_control(
                            "Variante",
                            options=option_names,
                            default=option_names[0],
                            selection_mode="single",
                            key=f"tamara_{meal_time}_option"
                        )

                        if selected_option is None:
                            selected_option = option_names[0]

                        selected_meal = meal_options[selected_option]

                        meal_title = f"{meal_time} – {selected_option}"




                # ====================================================
                # CAN / NEMO
                # ====================================================

                else:

                    meal_day = st.segmented_control(
                        "Mealplan-Tag",
                        options=meal_sections,
                        default=meal_sections[0],
                        selection_mode="single",
                        key="mealplan_day"
                    )

                    if meal_day is None:
                        meal_day = meal_sections[0]

                    selected_day = selected_plan[meal_day]

                    # ------------------------------------------------
                    # FALL 1:
                    # selected_day ist direkt eine Mahlzeit
                    # ------------------------------------------------

                    if isinstance(selected_day, list):

                        selected_meal = selected_day
                        meal_title = meal_day

                    # ------------------------------------------------
                    # FALL 2:
                    # selected_day enthält weitere Auswahlmöglichkeiten
                    # ------------------------------------------------

                    elif isinstance(selected_day, dict):

                        meal_times = list(selected_day.keys())

                        meal_time = st.segmented_control(
                            "Mahlzeit",
                            options=meal_times,
                            default=meal_times[0],
                            selection_mode="single",
                            key="mealplan_time"
                        )

                        if meal_time is None:
                            meal_time = meal_times[0]

                        selected_meal = selected_day[meal_time]

                        meal_title = meal_time

                    else:

                        st.error(
                            "Die Struktur dieses Mealplans konnte nicht gelesen werden."
                        )

                        selected_meal = []
                        meal_title = ""


                # ====================================================
                # AUSGABE
                # ====================================================

                st.divider()

                if meal_title:

                    st.markdown(
                        f"## {meal_title}"
                    )

                    st.caption(
                        f"{calorie_plan}"
                    )


                # ====================================================
                # LEBENSMITTEL
                # ====================================================

                for amount, food in selected_meal:

                    food_lower = food.lower()


                    # ------------------------------------------------
                    # KARTOFFELN
                    # ------------------------------------------------

                    if food_lower == "kartoffeln":

                        cooked_amount = amount * 0.8

                        st.container(border=True).markdown(
                            f"""
                            ### 🥔 Kartoffeln
                            **{cooked_amount:g} g gekocht**

                            :gray[{amount:g} g ungekocht]
                            """
                        )


                    # ------------------------------------------------
                    # REIS
                    # ------------------------------------------------

                    elif food_lower == "reis roh":

                        cooked_amount = amount * 3

                        st.container(border=True).markdown(
                            f"""
                            ### 🍚 Reis
                            **{cooked_amount:g} g gekocht**

                            :gray[{amount:g} g roh]
                            """
                        )


                    # ------------------------------------------------
                    # MANDELMILCH
                    # ------------------------------------------------

                    elif food_lower == "mandelmilch":

                        st.container(border=True).markdown(
                            f"""
                            ### 🥛 Mandelmilch
                            **{amount:g} ml**
                            """
                        )


                    # ------------------------------------------------
                    # MORNING-SHAKE CAN
                    # ------------------------------------------------

                    elif food_lower == "morningshake can":

                        st.container(border=True).markdown(
                            """
                            ### 🥤 Morningshake Can

                            **Inhalt:**
                            - 200 ml Mandelmilch
                            - 1 Banane
                            - 30 g Proteinpulver
                            - 10 g Erdnussbutter
                            - 50 g Haferflocken
                            """
                        )


                    # ------------------------------------------------
                    # MILCHREIS / MILCHREIS PT
                    # ------------------------------------------------

                    elif food_lower in ["milchreis", "milchreis pt"]:

                        st.container(border=True).markdown(
                            """
                            ### 🍚 Milchreis

                            **Portion: 280 g Milchreis**

                            **Grundrezept:**
                            - 2.5 l Mandelmilch
                            - 500 g Reis roh
                            - 180 g Proteinpulver

                            **Dazu:**
                            - 20 g Erdnussbutter
                            - 30 g Mixed Berries

                            :gray[Grundrezept ergibt ca. 2800 g Milchreis]
                            """
                        )


                    # ------------------------------------------------
                    # FRÜHSTÜCKSPORRIDGE TAMARA
                    # ------------------------------------------------

                    elif food_lower == "frühstücksporridge":

                        st.container(border=True).markdown(
                            """
                            ### 🥣 Frühstücksporridge

                            **Inhalt:**
                            - 120 ml Mandelmilch
                            - 40 g Haferflocken
                            - 30 g Proteinpulver
                            - 30 g Mixed Berries
                            - 8 g Chiasamen
                            - 30 g Erdnussbutter
                            """
                        )


                    # ------------------------------------------------
                    # APFEL-ZIMT-PROTEIN-MUFFINS
                    # ------------------------------------------------

                    elif food_lower == "apfel-zimt-protein-muffins":

                        st.container(border=True).markdown(
                            """
                            ### 🧁 Apfel-Zimt-Protein-Muffins
                            """
                        )


                    # ------------------------------------------------
                    # BELEGTES BROT
                    # ------------------------------------------------

                    elif food_lower == "2 belegte protein Brote":

                        st.container(border=True).markdown(
                            f"""
                            ### 🥪 2 belegte Protein Brote
                            **{amount:g} Stück**
                            """
                        )


                    # ------------------------------------------------
                    # NORMALE LEBENSMITTEL
                    # ------------------------------------------------

                    else:

                        st.container(border=True).markdown(
                            f"""
                            ### {food}
                            **{amount:g} g**
                            """
                        )
    # ============================================================
    # BODY MASSE
    # ============================================================

with tab5:
        

        st.subheader("📏 Body Maße")

        st.caption(
            "Für möglichst vergleichbare Ergebnisse am besten "
            "immer unter ähnlichen Bedingungen messen."
        )
        # ========================================================
        # MESSANLEITUNG
        # ========================================================

        with st.expander("📐 Wo muss ich messen?", expanded=False):
            if USERS[username]["gender"] == "female":
                body_filename = "Wbody2.png"
            else:
                body_filename = "Mbody.png"

            body_image = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "Bodymeasurements",
                body_filename
            )

            if os.path.exists(body_image):
                st.image(
                    body_image,
                    use_container_width=True
                )
            else:
                st.warning(
                    f"Bild zur Messanleitung nicht gefunden: {body_image}"
                )

            st.caption(
                "Das Maßband waagerecht um die markierte Stelle legen. "
                "Nicht zu locker und nicht in die Haut einschneiden."
        )


        # ========================================================
        # DATUM UND GEWICHT
        # ========================================================

        body_date = st.date_input(
            "Datum",
            value=date.today(),
            key="body_date"
        )

        body_weight = st.number_input(
            "Körpergewicht (kg)",
            min_value=0.0,
            max_value=300.0,
            value=0.0,
            step=0.1,
            key="body_weight"
        )


        # ========================================================
        # MESSBEDINGUNGEN
        # ========================================================

        st.markdown("### Messbedingungen")

        measurement_time = st.segmented_control(
            "Tageszeit",
            options=[
                "Morgens",
                "Tagsüber",
                "Abends"
            ],
            default="Morgens",
            selection_mode="single",
            key="body_measurement_time"
        )

        training_status = st.segmented_control(
            "Training / Pump",
            options=[
                "Ohne Pump",
                "Nach Training / Pump"
            ],
            default="Ohne Pump",
            selection_mode="single",
            key="body_training_status"
        )

        fasted = st.segmented_control(
            "Nüchterner Magen?",
            options=[
                "Ja",
                "Nein"
            ],
            default="Ja",
            selection_mode="single",
            key="body_fasted"
        )


        # ========================================================
        # KÖRPERMASSE
        # ========================================================

        st.markdown("### Körpermaße")

        st.caption("Alle Angaben in cm.")


        # --------------------------
        # OBERKÖRPER
        # --------------------------

        st.markdown("#### Oberkörper")

        c1, c2 = st.columns(2)

        with c1:
            biceps_left = st.number_input(
                "Bizeps links – entspannt",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="body_biceps_left"
            )

        with c2:
            biceps_right = st.number_input(
                "Bizeps rechts – entspannt",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="body_biceps_right"
            )

        c1, c2 = st.columns(2)

        with c1:
            biceps_flexed_left = st.number_input(
                "Bizeps links – angespannt 💪",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="body_biceps_flexed_left"
            )

        with c2:
            biceps_flexed_right = st.number_input(
                "Bizeps rechts – angespannt 💪",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="body_biceps_flexed_right"
            )

        lat_flexed = st.number_input(
            "Lat – angespannt / Lat Spread",
            min_value=0.0,
            max_value=200.0,
            step=0.1,
            key="body_lat_flexed"
        )

        chest = st.number_input(
            "Brust",
            min_value=0.0,
            max_value=200.0,
            step=0.1,
            key="body_chest"
        )


        # --------------------------
        # MITTE
        # --------------------------

        st.markdown("#### Taille & Hüfte")

        waist = st.number_input(
            "Taille",
            min_value=0.0,
            max_value=200.0,
            step=0.1,
            key="body_waist"
        )

        hips = st.number_input(
            "Hüfte",
            min_value=0.0,
            max_value=200.0,
            step=0.1,
            key="body_hips"
        )

        glutes = st.number_input(
            "Glutes / Po",
            min_value=0.0,
            max_value=200.0,
            step=0.1,
            key="body_glutes"
        )


        # --------------------------
        # BEINE
        # --------------------------

        st.markdown("#### Beine")

        c1, c2 = st.columns(2)

        with c1:

            thigh_left = st.number_input(
                "Oberschenkel links",
                min_value=0.0,
                max_value=150.0,
                step=0.1,
                key="body_thigh_left"
            )

        with c2:

            thigh_right = st.number_input(
                "Oberschenkel rechts",
                min_value=0.0,
                max_value=150.0,
                step=0.1,
                key="body_thigh_right"
            )


        c1, c2 = st.columns(2)

        with c1:

            calf_left = st.number_input(
                "Wade links",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="body_calf_left"
            )

        with c2:

            calf_right = st.number_input(
                "Wade rechts",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="body_calf_right"
            )
        


        # ========================================================
        # NOTIZ
        # ========================================================

        body_note = st.text_input(
            "Notiz",
            key="body_note"
        )


        # ========================================================
        # SPEICHERN
        # ========================================================

        if st.button(
            "📏 Körpermaße speichern",
            key="save_body_measurements"
        ):

            new_body_entry = pd.DataFrame([{

                "Datum": body_date,

                "Gewicht kg": body_value_or_empty(body_weight),

                "Bizeps links cm": body_value_or_empty(biceps_left),
                "Bizeps rechts cm": body_value_or_empty(biceps_right),

                "Brust cm": body_value_or_empty(chest),

                "Taille cm": body_value_or_empty(waist),
                "Hüfte cm": body_value_or_empty(hips),
                "Glutes cm": body_value_or_empty(glutes),

                "Oberschenkel links cm": body_value_or_empty(thigh_left),
                "Oberschenkel rechts cm": body_value_or_empty(thigh_right),

                "Wade links cm": body_value_or_empty(calf_left),
                "Wade rechts cm": body_value_or_empty(calf_right),

                "Lat angespannt cm": body_value_or_empty(lat_flexed),
                "Bizeps links angespannt cm": body_value_or_empty(biceps_flexed_left),
                "Bizeps rechts angespannt cm": body_value_or_empty(biceps_flexed_right),
                "Tageszeit": measurement_time,
                "Training / Pump": training_status,
                "Nüchterner Magen": fasted,

                "Notiz": body_note
            }])


            # Falls für diesen Tag bereits eine Messung existiert:
            # alte Messung ersetzen

            old_body_df = body_df.copy()

            if (
                not old_body_df.empty
                and "Datum" in old_body_df.columns
            ):

                old_body_df = old_body_df[
                    old_body_df["Datum"].astype(str)
                    != str(body_date)
                ]


            full_body_df = pd.concat(
                [
                    old_body_df,
                    new_body_entry
                ],
                ignore_index=True
            )


            save_body_data(
                username,
                full_body_df
            )

            st.success(
                "Körpermaße gespeichert! 📏"
            )

            time.sleep(0.5)

            st.rerun()
          
        # ============================================================
        # BISHERIGE KÖRPERMASSE
        # ============================================================

        st.markdown("---")
        st.subheader("📋 Bisherige Messungen")

        if body_df.empty:

            st.info("Noch keine Körpermaße gespeichert.")

        else:

            body_table = body_df.copy()

            # Neueste Messung zuerst
            if "Datum" in body_table.columns:

                body_table["Datum"] = pd.to_datetime(
                    body_table["Datum"],
                    errors="coerce"
                )

                body_table = body_table.sort_values(
                    "Datum",
                    ascending=False
                )

                body_table["Datum"] = body_table[
                    "Datum"
                ].dt.strftime("%d.%m.%Y")

            st.dataframe(
                body_table,
                use_container_width=True,
                hide_index=True
            )


            # ========================================================
            # BODY STATISTIK
            # ========================================================

            st.markdown("---")
            st.subheader("📈 Entwicklung")

            measurement_columns = [
                "Gewicht kg",
                "Bizeps links cm",
                "Bizeps rechts cm",
                "Bizeps links angespannt cm",
                "Bizeps rechts angespannt cm",
                "Brust cm",
                "Taille cm",
                "Hüfte cm",
                "Glutes cm",
                "Oberschenkel links cm",
                "Oberschenkel rechts cm",
                "Wade links cm",
                "Wade rechts cm",
                "Lat angespannt cm"
            ]

            available_measurements = [
                col
                for col in measurement_columns
                if col in body_df.columns
            ]

            if available_measurements:

                selected_measurement = st.selectbox(
                    "Messwert auswählen",
                    available_measurements,
                    key="body_stat_measurement"
                )

                body_stats = body_df[
                    ["Datum", selected_measurement]
                ].copy()

                # Datum umwandeln
                body_stats["Datum"] = pd.to_datetime(
                    body_stats["Datum"],
                    errors="coerce"
                )

                # "Keine Angabe" wird automatisch NaN
                body_stats[selected_measurement] = pd.to_numeric(
                    body_stats[selected_measurement],
                    errors="coerce"
                )

                # Nur echte Messungen
                body_stats = body_stats.dropna(
                    subset=[
                        "Datum",
                        selected_measurement
                    ]
                )

                # Älteste -> neueste Messung
                body_stats = body_stats.sort_values(
                    "Datum"
                )

                if len(body_stats) >= 2:

                    st.line_chart(
                        body_stats,
                        x="Datum",
                        y=selected_measurement,
                        use_container_width=True
                    )

                elif len(body_stats) == 1:

                    st.info(
                        "Für diesen Messwert gibt es bisher nur "
                        "eine Messung. Ab der zweiten Messung "
                        "kann ein Verlauf angezeigt werden."
                    )

                else:

                    st.info(
                        "Für diesen Messwert wurden noch keine "
                        "Werte gespeichert."
                    )