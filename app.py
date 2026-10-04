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
        "Face pulls",
        "Delt Fly",
        "Hanging"
    ],

    "Brust": [
        "Push",
        "Butterfly"
    ],

    "Beine": [
        "Leg extension",
        "Leg curl",
        "Leg press",
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
        "Push down"
    ],

    "Schultern": [
        "Lateral raises",
        "Front raises",
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

MEAL_PLANS = {

    "Tamara": {

        # Tamara – 2400 kcal

        "2400 kcal": {

                # FIX
                "Frühstück": [
                    (1, "Frühstücksporridge")
                ],

                # FIX
                "9i": [
                    (30, "Proteinpulver"),
                    (200, "Mandelmilch"),
                    (1, "Milchreis PT")
                ],

                # AUSWAHL – für Mittag UND 4i
                "Hauptmahlzeiten": {

                    "RH": [
                        (150, "Rindhack"),
                        (150, "Kartoffeln"),
                        (30, "Reis roh"),
                        (50, "Gemüsemix")
                    ],

                    "TU": [
                        (200, "Tofu"),
                        (50, "Reis roh"),
                        (10, "Avocado"),
                        (100, "Kartoffeln")
                    ],

                    "EI": [
                        (250, "Eiweiss"),
                        (50, "Avocado"),
                        (50, "Reis roh"),
                        (200, "Kartoffeln")
                    ],

                    "GA": [
                        (200, "Garnelen"),
                        (50, "Reis roh"),
                        (20, "Avocado"),
                        (150, "Kartoffeln")
                    ],

                    "MO": [
                        (125, "Mozzarella"),
                        (150, "Kartoffeln"),
                        (60, "Reis roh"),
                        (50, "Tomaten")
                    ],

                    "PO": [
                        (200, "Poulet"),
                        (50, "Reis roh"),
                        (20, "Avocado"),
                        (120, "Kartoffeln")
                    ]
                },

                # FIX – nur noch Magerquark, kein Skyr
                "Abend": [
                    (10, "Proteinpulver"),
                    (20, "Erdnussbutter"),
                    (250, "Magerquark")
                ]
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

    worksheet.clear()

    if df.empty:
        return

    clean_df = df.copy()

    clean_df = clean_df.fillna("")

    # Datumswerte und andere Objekte sauber in Strings umwandeln
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

def training_form(username, saved_df, edit_date=None):
    edit_df = pd.DataFrame()

    # ============================================================
    # DATUM / BEARBEITUNG
    # ============================================================

    if edit_date and not saved_df.empty:
        edit_df = saved_df[
            saved_df["Datum"].astype(str) == str(edit_date)
        ].copy()


    # ============================================================
    # DATUM – NUR LINKE SPALTE
    # ============================================================

    date_col, empty_col = st.columns(2)

    with date_col:

        if edit_date and not saved_df.empty:

            training_date = st.date_input(
                "Datum",
                value=pd.to_datetime(edit_date).date()
            )

        else:

            training_date = st.date_input(
                "Datum",
                value=date.today()
            )

    # ============================================================
    # ALLGEMEINE ANGABEN
    # ============================================================

    st.subheader("Allgemeine Angaben")

    last_mode, last_calories = get_last_mode_and_calories(saved_df)

    mode_options = ["Maintaining", "Bulk", "Cut"]

    if last_mode not in mode_options:
        last_mode = "Maintaining"

    # Beim Bearbeiten alte Werte laden
    if edit_date and not edit_df.empty:
        first_old_row = edit_df.iloc[0]

        old_mode = first_old_row.get("Modus", last_mode)
        if old_mode in mode_options:
            last_mode = old_mode

        old_calories = first_old_row.get("Kalorienziel", last_calories)

        if pd.notna(old_calories):
            last_calories = int(old_calories)

    col1, col2 = st.columns(2)

    with col1:
        mode = st.selectbox(
            "Modus",
            mode_options,
            index=mode_options.index(last_mode),
            key="training_mode"
        )

    with col2:
        calories = st.number_input(
            "Kalorienziel",
            min_value=0,
            max_value=10000,
            value=int(last_calories),
            step=50,
            key="training_calories"
        )

   # ============================================================
    # PERIOD MODE – NUR FÜR FRAUEN
    # ============================================================

    period_mode = False
    period_start = ""
    period_end = ""

    # Period Mode nur anzeigen, wenn der Benutzer als female
    # hinterlegt wurde
    if USERS[username]["gender"] == "female":

        default_period_mode = False

        if edit_date and not edit_df.empty:
            old_period = edit_df.iloc[0].get("Period Mode", False)

            if pd.notna(old_period):
                if isinstance(old_period, str):
                    default_period_mode = old_period.lower() == "true"
                else:
                    default_period_mode = bool(old_period)

        period_mode = st.checkbox(
            "Period Mode",
            value=default_period_mode,
            key="period_mode"
        )

        if period_mode:

            old_period_start = training_date
            old_period_end = training_date

            if edit_date and not edit_df.empty:

                value = edit_df.iloc[0].get("Periode Start", "")

                if pd.notna(value) and str(value) not in ["", "nan"]:
                    old_period_start = pd.to_datetime(value).date()

                value = edit_df.iloc[0].get("Periode Ende", "")

                if pd.notna(value) and str(value) not in ["", "nan"]:
                    old_period_end = pd.to_datetime(value).date()

            p1, p2 = st.columns(2)

            with p1:
                period_start = st.date_input(
                    "Periode Start",
                    value=old_period_start,
                    key="period_start"
                )

            with p2:
                period_end = st.date_input(
                    "Periode Ende",
                    value=old_period_end,
                    key="period_end"
                )

    # ============================================================
    # STIMMUNG
    # ============================================================

    default_mood = 3

    if edit_date and not edit_df.empty:
        old_mood = edit_df.iloc[0].get("Stimmung", 3)

        if pd.notna(old_mood):
            default_mood = int(old_mood)

    mood = st.slider(
        "Stimmung / Gefühl",
        min_value=1,
        max_value=5,
        value=default_mood,
        help="1 = super toll, 3 = normal, 5 = dreckig",
        key="training_mood"
    )

    pain = ""

    if mood >= 4:

        old_pain = ""

        if edit_date and not edit_df.empty:
            value = edit_df.iloc[0].get("Schmerzen", "")

            if pd.notna(value):
                old_pain = str(value)

        pain = st.text_input(
            "Gab es Schmerzen? Wenn ja, wo?",
            value=old_pain,
            key="training_pain"
        )

    # ============================================================
    # CARDIO
    # ============================================================

    st.subheader("Cardio")

    cardio_options = [
        "Kein Cardio",
        "Laufen",
        "Fahrrad",
        "Stepper",
        "Stairmaster",
        "Crosstrainer",
        "Rudern",
        "Walking",
        "Anderes"
    ]

    old_cardio_type = "Kein Cardio"

    if edit_date and not edit_df.empty:
        value = edit_df.iloc[0].get("Cardio Form", "Kein Cardio")

        if pd.notna(value) and value in cardio_options:
            old_cardio_type = value

    cardio_type = st.selectbox(
        "Cardio-Form",
        cardio_options,
        index=cardio_options.index(old_cardio_type),
        key="cardio_type"
    )

    cardio_time = 0.0
    cardio_distance = 0.0
    cardio_calories = 0.0

    if cardio_type != "Kein Cardio":

        if edit_date and not edit_df.empty:

            old_time = edit_df.iloc[0].get("Cardio Zeit min", 0)
            old_distance = edit_df.iloc[0].get("Cardio Distanz km", 0)
            old_cardio_calories = edit_df.iloc[0].get("Cardio Kalorien", 0)

            cardio_time = float(old_time) if pd.notna(old_time) else 0.0
            cardio_distance = float(old_distance) if pd.notna(old_distance) else 0.0
            cardio_calories = float(old_cardio_calories) if pd.notna(old_cardio_calories) else 0.0

        c1, c2, c3 = st.columns(3)

        with c1:
            cardio_time = st.number_input(
                "Cardio Zeit in Minuten",
                min_value=0.0,
                value=cardio_time,
                step=1.0,
                key="cardio_time"
            )

        with c2:
            cardio_distance = st.number_input(
                "Distanz in km",
                min_value=0.0,
                value=cardio_distance,
                step=0.1,
                key="cardio_distance"
            )

        with c3:
            cardio_calories = st.number_input(
                "Cardio Kalorien",
                min_value=0.0,
                value=cardio_calories,
                step=10.0,
                key="cardio_calories"
            )

    # ============================================================
    # KRAFTTRAINING
    # ============================================================

    st.subheader("Krafttraining")

    all_groups = [
        "Rücken",
        "Brust",
        "Beine",
        "Glutes",
        "Trizeps",
        "Bizeps",
        "Schultern",
        "core",
        "Calisthenics",
        "TRX"
    ]

    if edit_date and not edit_df.empty:

        old_exercises = sorted(
            edit_df["Übung"].dropna().unique()
        )

        muscle_groups = st.multiselect(
            "Welche Muskelgruppen hast du trainiert?",
            all_groups,
            default=all_groups,
            key="muscle_groups"
        )

        available_exercises = sorted(
            set(
                get_available_exercises(muscle_groups)
                + old_exercises
            )
        )

    else:

        muscle_groups = st.multiselect(
            "Welche Muskelgruppen hast du trainiert?",
            all_groups,
            key="muscle_groups"
        )

        available_exercises = get_available_exercises(
            muscle_groups
        )

    if not available_exercises:
        st.info("Wähle mindestens eine Muskelgruppe aus.")
        return

    # ============================================================
    # ANZAHL ÜBUNGEN
    # ============================================================

    default_rows = (
        len(edit_df)
        if edit_date and not edit_df.empty
        else 3
    )

    rows = st.number_input(
        "Wie viele Übungen möchtest du eintragen?",
        min_value=1,
        value=int(default_rows),
        step=1,
        key="exercise_count"
    )

    rows = int(rows)

    entries = []

    # ============================================================
    # ÜBUNGEN
    # ============================================================

    for i in range(rows):

        old_row = None

        if (
            edit_date
            and not edit_df.empty
            and i < len(edit_df)
        ):
            old_row = edit_df.iloc[i]

        st.markdown("---")
        st.markdown(f"### Übung {i + 1}")

        # --------------------------------------------------------
        # ÜBUNG
        # --------------------------------------------------------

        if old_row is not None:
            old_exercise = old_row.get(
                "Übung",
                available_exercises[0]
            )
        else:
            old_exercise = available_exercises[0]

        if old_exercise in available_exercises:
            exercise_index = available_exercises.index(
                old_exercise
            )
        else:
            exercise_index = 0

        exercise = st.selectbox(
            "Übung",
            available_exercises,
            index=exercise_index,
            key=f"exercise_{i}"
        )

        # ========================================================
        # VARIABLE ANZAHL SETS
        # ========================================================

        default_sets = 4

        if old_row is not None:

            # Neue Trainings haben die Spalte Anzahl Sets
            if (
                "Anzahl Sets" in old_row.index
                and pd.notna(old_row["Anzahl Sets"])
            ):

                default_sets = int(
                    old_row["Anzahl Sets"]
                )

            # Alte Trainings hatten diese Spalte noch nicht.
            # Dann schauen wir, wie viele Set-Spalten Daten enthalten.
            else:

                detected_sets = 0

                for old_s in range(1, 50):

                    weight_col = f"Set {old_s} Gewicht"
                    reps_col = f"Set {old_s} Wdh"
                    duration_col = f"Set {old_s} Dauer Sekunden"

                    found_data = False

                    if weight_col in old_row.index:
                        if pd.notna(old_row[weight_col]):
                            found_data = True

                    if reps_col in old_row.index:
                        if pd.notna(old_row[reps_col]):
                            found_data = True

                    if duration_col in old_row.index:
                        if pd.notna(old_row[duration_col]):
                            found_data = True

                    if found_data:
                        detected_sets = old_s

                if detected_sets > 0:
                    default_sets = detected_sets

        number_of_sets = st.number_input(
            "Anzahl Sets",
            min_value=1,
            value=int(default_sets),
            step=1,
            key=f"number_sets_{i}"
        )

        number_of_sets = int(number_of_sets)

        # --------------------------------------------------------
        # MACHINE
        # --------------------------------------------------------

        if (
            exercise in exercises_by_group["Calisthenics"]
            or exercise in exercises_by_group["TRX"]
            or exercise == "Hanging"
        ):

            machine_options = ["Bodyweight"]

        else:

            machine_options = [
                "Cable",
                "Freigewicht",
                "Maschine"
            ]

        if old_row is not None:
            old_machine = old_row.get(
                "Machine",
                machine_options[0]
            )
        else:
            old_machine = machine_options[0]

        if old_machine in machine_options:
            machine_index = machine_options.index(
                old_machine
            )
        else:
            machine_index = 0

        machine = st.selectbox(
            "Machine",
            machine_options,
            index=machine_index,
            key=f"machine_{i}"
        )

        # --------------------------------------------------------
        # TRX / HANGING EXTRA
        # --------------------------------------------------------

        extra_info = ""

        if exercise in exercises_by_group["TRX"]:

            extra_info = st.selectbox(
                "Schräge / Schwierigkeit",
                [
                    "Sehr aufrecht / leicht",
                    "Mittel",
                    "Sehr schräg / schwer"
                ],
                key=f"extra_{i}"
            )

        elif exercise == "Hanging":

            extra_info = st.text_input(
                "Hanging-Variante / Notiz",
                key=f"extra_{i}"
            )

        # --------------------------------------------------------
        # GRIFF
        # --------------------------------------------------------

        if (
            exercise in exercises_by_group["Beine"]
            or exercise in exercises_by_group["Glutes"]
        ):

            griff = "Nicht relevant"

        else:

            grip_options = [
                "Neutral",
                "Breit",
                "Eng",
                "Untergriff",
                "Obergriff"
            ]

            if old_row is not None:
                old_griff = old_row.get(
                    "Griff",
                    "Neutral"
                )
            else:
                old_griff = "Neutral"

            if old_griff in grip_options:
                grip_index = grip_options.index(
                    old_griff
                )
            else:
                grip_index = 0

            griff = st.selectbox(
                "Griff",
                grip_options,
                index=grip_index,
                key=f"grip_{i}"
            )

        # --------------------------------------------------------
        # ÜBUNGSNOTIZ
        # --------------------------------------------------------

        old_note = ""

        if old_row is not None:
            value = old_row.get(
                "Notiz Übung",
                ""
            )

            if pd.notna(value):
                old_note = str(value)

        note = st.text_input(
            "Notiz zur Übung",
            value=old_note,
            key=f"note_{i}"
        )

        # --------------------------------------------------------
        # SCHULTER WARNUNG
        # --------------------------------------------------------

        if any(
            group in muscle_groups
            for group in ["Rücken", "Schultern"]
        ):
            st.warning(
                "⚠️ Schulterblätter nach hinten und runter drücken."
            )

        # --------------------------------------------------------
        # LETZTES GEWICHT
        # --------------------------------------------------------

        last_weight = get_last_set2_weight(
            saved_df,
            exercise,
            machine,
            griff
        )

        if last_weight is not None:

            st.info(
                f"Letztes Mal bei genau dieser Übung: "
                f"Set 2 = {last_weight} kg"
            )

        else:

            st.caption(
                "Noch kein früherer Eintrag für diese genaue Übung gefunden."
            )

        # ========================================================
        # SETS
        # ========================================================

        sets = []

        is_core = (
            exercise in exercises_by_group["core"]
        )

        is_time_exercise = exercise in [
            "Side plank right",
            "Side plank left",
            "Plank",
            "Hanging"
        ]

        uses_weight = True

        if is_core and not is_time_exercise:

            default_uses_weight = False

            if old_row is not None:

                # Falls Gewicht > 0 gespeichert war,
                # gehen wir davon aus, dass Gewicht benutzt wurde.
                for old_s in range(1, number_of_sets + 1):

                    col = f"Set {old_s} Gewicht"

                    if (
                        col in old_row.index
                        and pd.notna(old_row[col])
                        and float(old_row[col]) > 0
                    ):
                        default_uses_weight = True
                        break

            uses_weight = st.checkbox(
                "Mit Gewicht gearbeitet?",
                value=default_uses_weight,
                key=f"uses_weight_{i}"
            )

        # ========================================================
        # VARIABLE SETS
        # ========================================================

        for s in range(number_of_sets):

            set_number = s + 1

            with st.expander(
                f"Set {set_number}",
                expanded=True
            ):

                # -----------------------------------------------
                # ZEITÜBUNGEN
                # -----------------------------------------------

                if is_time_exercise:

                    old_duration = 0.0

                    if old_row is not None:

                        duration_col = (
                            f"Set {set_number} Dauer Sekunden"
                        )

                        if (
                            duration_col in old_row.index
                            and pd.notna(old_row[duration_col])
                        ):
                            old_duration = float(
                                old_row[duration_col]
                            )

                    duration = st.number_input(
                        "Zeit in Sekunden",
                        min_value=0.0,
                        max_value=3600.0,
                        value=old_duration,
                        step=5.0,
                        key=f"duration_{i}_{s}"
                    )

                    weight = 0.0
                    reps = 0.0

                # -----------------------------------------------
                # NORMALE ÜBUNGEN
                # -----------------------------------------------

                else:

                    old_weight = 0.0

                    weight_col = (
                        f"Set {set_number} Gewicht"
                    )

                    if (
                        old_row is not None
                        and weight_col in old_row.index
                        and pd.notna(old_row[weight_col])
                    ):
                        old_weight = float(
                            old_row[weight_col]
                        )

                    if uses_weight:

                        weight = st.number_input(
                            "Gewicht",
                            min_value=0.0,
                            max_value=400.0,
                            value=old_weight,
                            step=0.5,
                            key=f"weight_{i}_{s}"
                        )

                    else:

                        weight = 0.0

                    # Wiederholungen
                    old_reps = 8.0

                    reps_col = (
                        f"Set {set_number} Wdh"
                    )

                    if (
                        old_row is not None
                        and reps_col in old_row.index
                        and pd.notna(old_row[reps_col])
                    ):
                        old_reps = float(
                            old_row[reps_col]
                        )

                    reps = st.number_input(
                        "Wdh",
                        min_value=0.0,
                        max_value=1000.0,
                        value=old_reps,
                        step=0.5,
                        key=f"reps_{i}_{s}"
                    )

                    duration = 0.0

                # -----------------------------------------------
                # SET NOTIZ
                # -----------------------------------------------

                old_set_note = ""

                note_col = (
                    f"Set {set_number} Notiz"
                )

                if (
                    old_row is not None
                    and note_col in old_row.index
                    and pd.notna(old_row[note_col])
                ):
                    old_set_note = str(
                        old_row[note_col]
                    )

                note_set = st.text_input(
                    "Set-Notiz",
                    value=old_set_note,
                    key=f"note_set_{i}_{s}"
                )

                sets.append(
                    (
                        weight,
                        reps,
                        duration,
                        note_set
                    )
                )

        # ========================================================
        # EINTRAG ERSTELLEN
        # ========================================================

        entry = {
            "Benutzer": username,
            "Datum": training_date,

            "Modus": mode,
            "Kalorienziel": calories,

            "Period Mode": period_mode,
            "Periode Start": period_start,
            "Periode Ende": period_end,

            "Stimmung": mood,
            "Schmerzen": pain,

            "Cardio Form": cardio_type,
            "Cardio Zeit min": cardio_time,
            "Cardio Distanz km": cardio_distance,
            "Cardio Kalorien": cardio_calories,

            "Übung": exercise,
            "Machine": machine,
            "Griff": griff,
            "Extra Info": extra_info,
            "Notiz Übung": note,

            "Anzahl Sets": number_of_sets
        }

        # ========================================================
        # SETS DYNAMISCH SPEICHERN
        # ========================================================

        for s in range(number_of_sets):

            set_number = s + 1

            entry[
                f"Set {set_number} Gewicht"
            ] = sets[s][0]

            entry[
                f"Set {set_number} Wdh"
            ] = sets[s][1]

            entry[
                f"Set {set_number} Dauer Sekunden"
            ] = sets[s][2]

            entry[
                f"Set {set_number} Notiz"
            ] = sets[s][3]

        entries.append(entry)

    # ============================================================
    # SPEICHERN
    # ============================================================

    if edit_date:
        button_text = "Änderungen speichern"
    else:
        button_text = "Training speichern"

    if st.button(button_text):
        new_df = pd.DataFrame(entries)

        # Bereits vorhandene Daten dieses Users
        old_df = saved_df.copy()

        # Beim Bearbeiten: altes Training dieses Datums entfernen
        if edit_date and not old_df.empty:
            old_df = old_df[
                old_df["Datum"].astype(str) != str(edit_date)
            ]

        # Neues / bearbeitetes Training hinzufügen
        full_df = pd.concat(
            [old_df, new_df],
            ignore_index=True
        )

        # In Google Sheets speichern
        save_data(username, full_df)

        st.success("Training gespeichert! 💪")
        time.sleep(1)

        st.session_state.edit_date = None
        st.rerun()

# ============================================================
# LOGIN
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if "edit_date" not in st.session_state:
    st.session_state.edit_date = None


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
            INPUTS VOR DEM AVATAR
            ========================================= */

            [data-testid="stDateInput"],
            [data-testid="stNumberInput"],
            [data-testid="stTextInput"],
            [data-testid="stSelectbox"],
            [data-testid="stMultiSelect"] {

                position: relative !important;
                z-index: 2 !important;
            }


            /* =========================================
            INPUT-TEXT AN STREAMLIT THEME ANPASSEN
            ========================================= */

            [data-testid="stDateInput"] input,
            [data-testid="stNumberInput"] input,
            [data-testid="stTextInput"] input {

                color: var(--text-color) !important;
                -webkit-text-fill-color: var(--text-color) !important;
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

show_avatar(username, avatar_level)
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

else:

    if username in MEALPLAN_USERS:
        tab1, tab2, tab3, tab4 = st.tabs([
            "➕ Neues Training",
            "📖 Gespeicherte Trainings",
            "📊 Statistik",
            "🍽️ Mealplan"
        ])
    else:
        tab1, tab2, tab3 = st.tabs([
            "➕ Neues Training",
            "📖 Gespeicherte Trainings",
            "📊 Statistik"
        ])


    # ========================================================
    # NEUES TRAINING
    # ========================================================

    with tab1:
        training_form(
            username,
            saved_df,
            edit_date=st.session_state.edit_date
        )


    # ========================================================
    # GESPEICHERTE TRAININGS
    # ========================================================

    with tab2:

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

                        remaining_df = saved_df[
                            saved_df["Datum"]
                            != selected_date_str
                        ].copy()


                        save_data(
                            username,
                            remaining_df
                        )


                        st.success(
                            "Training gelöscht."
                        )

                        time.sleep(0.5)

                        st.rerun()


    # ========================================================
    # STATISTIK
    # ========================================================

    with tab3:

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

                # Schöner anzeigen:
                # "Hauptmahlzeiten" wird für Tamara als Mittag / 4i
                # separat behandelt.
                if username == "Tamara" and "Hauptmahlzeiten" in meal_sections:

                    meal_time = st.segmented_control(
                        "Mahlzeit",
                        options=[
                            "Frühstück",
                            "9i",
                            "Mittag",
                            "4i",
                            "Abend"
                        ],
                        default="Frühstück",
                        selection_mode="single",
                        key="mealplan_time"
                    )

                    if meal_time is None:
                        meal_time = "Frühstück"

                    # ------------------------------------------------
                    # MITTAG / 4i
                    # ------------------------------------------------

                    if meal_time in ["Mittag", "4i"]:

                        meal_options = selected_plan["Hauptmahlzeiten"]

                        option_names = list(meal_options.keys())

                        selected_option = st.segmented_control(
                            "Proteinquelle",
                            options=option_names,
                            default=option_names[0],
                            selection_mode="single",
                            key=f"tamara_{meal_time}_protein"
                        )

                        if selected_option is None:
                            selected_option = option_names[0]

                        selected_meal = meal_options[selected_option]

                        meal_title = f"{meal_time} – {selected_option}"

                    # ------------------------------------------------
                    # FIXE MAHLZEITEN
                    # ------------------------------------------------

                    else:

                        selected_meal = selected_plan[meal_time]

                        meal_title = meal_time


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
                            - 10 g Chiasamen
                            - 5 g Erdnussbutter
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