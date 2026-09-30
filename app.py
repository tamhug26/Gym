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
    "Tamara": "1010",
    "Can": "1010",
    "Papa": "aramat",
    "Nomi": "thebest"
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

def training_form(
    username,
    saved_df,
    edit_date=None
):

    edit_df = pd.DataFrame()

    # --------------------------------------------------------
    # DATUM
    # --------------------------------------------------------

    if edit_date and not saved_df.empty:

        edit_df = saved_df[
            saved_df["Datum"].astype(str)
            == str(edit_date)
        ].copy()

        training_date = st.date_input(
            "Datum",
            value=pd.to_datetime(
                edit_date
            ).date()
        )

    else:

        training_date = st.date_input(
            "Datum",
            value=date.today()
        )


    # ========================================================
    # ALLGEMEINE ANGABEN
    # ========================================================

    st.subheader("Allgemeine Angaben")

    last_mode, last_calories = \
        get_last_mode_and_calories(saved_df)

    mode_options = [
        "Maintaining",
        "Bulk",
        "Cut"
    ]

    # Beim Bearbeiten alte Werte verwenden
    if edit_date and not edit_df.empty:

        old_general = edit_df.iloc[0]

        edit_mode = safe_string(
            old_general.get(
                "Modus",
                last_mode
            )
        )

        if edit_mode in mode_options:
            last_mode = edit_mode

        last_calories = safe_int(
            old_general.get(
                "Kalorienziel",
                last_calories
            ),
            last_calories
        )


    col1, col2 = st.columns(2)

    with col1:

        mode = st.selectbox(
            "Modus",
            mode_options,
            index=mode_options.index(
                last_mode
            )
        )

    with col2:

        calories = st.number_input(
            "Kalorienziel",
            min_value=0,
            max_value=10000,
            value=last_calories,
            step=50
        )


    # --------------------------------------------------------
    # PERIOD MODE
    # --------------------------------------------------------

    old_period_mode = False

    if edit_date and not edit_df.empty:

        old_value = str(
            edit_df.iloc[0].get(
                "Period Mode",
                ""
            )
        ).lower()

        old_period_mode = old_value in [
            "true",
            "1",
            "yes"
        ]

    period_mode = st.checkbox(
        "Period Mode",
        value=old_period_mode
    )

    period_start = ""
    period_end = ""

    if period_mode:

        default_start = training_date
        default_end = training_date

        if edit_date and not edit_df.empty:

            old_start = edit_df.iloc[0].get(
                "Periode Start",
                ""
            )

            old_end = edit_df.iloc[0].get(
                "Periode Ende",
                ""
            )

            if old_start:
                try:
                    default_start = \
                        pd.to_datetime(
                            old_start
                        ).date()
                except:
                    pass

            if old_end:
                try:
                    default_end = \
                        pd.to_datetime(
                            old_end
                        ).date()
                except:
                    pass

        p1, p2 = st.columns(2)

        with p1:

            period_start = st.date_input(
                "Periode Start",
                value=default_start
            )

        with p2:

            period_end = st.date_input(
                "Periode Ende",
                value=default_end
            )


    # --------------------------------------------------------
    # STIMMUNG
    # --------------------------------------------------------

    default_mood = 3

    if edit_date and not edit_df.empty:

        default_mood = safe_int(
            edit_df.iloc[0].get(
                "Stimmung",
                3
            ),
            3
        )

        default_mood = max(
            1,
            min(5, default_mood)
        )

    mood = st.slider(
        "Stimmung / Gefühl",
        min_value=1,
        max_value=5,
        value=default_mood,
        help="1 = super toll, 3 = normal, 5 = dreckig"
    )


    pain = ""

    if mood >= 4:

        old_pain = ""

        if edit_date and not edit_df.empty:

            old_pain = safe_string(
                edit_df.iloc[0].get(
                    "Schmerzen",
                    ""
                )
            )

        pain = st.text_input(
            "Gab es Schmerzen? Wenn ja, wo?",
            value=old_pain
        )


    # ========================================================
    # CARDIO
    # ========================================================

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

    old_cardio = "Kein Cardio"

    if edit_date and not edit_df.empty:

        old_cardio = safe_string(
            edit_df.iloc[0].get(
                "Cardio Form",
                "Kein Cardio"
            )
        )

    if old_cardio not in cardio_options:
        old_cardio = "Kein Cardio"

    cardio_type = st.selectbox(
        "Cardio-Form",
        cardio_options,
        index=cardio_options.index(
            old_cardio
        )
    )


    cardio_time = 0.0
    cardio_distance = 0.0
    cardio_calories = 0.0


    if cardio_type != "Kein Cardio":

        if edit_date and not edit_df.empty:

            cardio_time = safe_float(
                edit_df.iloc[0].get(
                    "Cardio Zeit min",
                    0
                )
            )

            cardio_distance = safe_float(
                edit_df.iloc[0].get(
                    "Cardio Distanz km",
                    0
                )
            )

            cardio_calories = safe_float(
                edit_df.iloc[0].get(
                    "Cardio Kalorien",
                    0
                )
            )

        c1, c2, c3 = st.columns(3)

        with c1:

            cardio_time = st.number_input(
                "Cardio Zeit in Minuten",
                min_value=0.0,
                max_value=500.0,
                value=float(cardio_time),
                step=1.0
            )

        with c2:

            cardio_distance = st.number_input(
                "Distanz in km",
                min_value=0.0,
                max_value=200.0,
                value=float(cardio_distance),
                step=0.1
            )

        with c3:

            cardio_calories = st.number_input(
                "Cardio Kalorien",
                min_value=0.0,
                max_value=3000.0,
                value=float(cardio_calories),
                step=10.0
            )


    # ========================================================
    # KRAFTTRAINING
    # ========================================================

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
            edit_df[
                "Übung"
            ].dropna().unique()
        )

        muscle_groups = st.multiselect(
            "Welche Muskelgruppen hast du trainiert?",
            all_groups,
            default=all_groups
        )

        available_exercises = sorted(
            set(
                get_available_exercises(
                    muscle_groups
                )
                + old_exercises
            )
        )

    else:

        muscle_groups = st.multiselect(
            "Welche Muskelgruppen hast du trainiert?",
            all_groups
        )

        available_exercises = \
            get_available_exercises(
                muscle_groups
            )


    if not available_exercises:

        st.info(
            "Wähle mindestens eine Muskelgruppe aus."
        )

        return


    default_rows = (
        len(edit_df)
        if edit_date and not edit_df.empty
        else 3
    )


    rows = st.number_input(
        "Wie viele Übungen möchtest du eintragen?",
        min_value=1,
        max_value=20,
        value=int(default_rows)
    )


    entries = []


    # ========================================================
    # EINZELNE ÜBUNGEN
    # ========================================================

    for i in range(int(rows)):

        old_row = None

        if (
            edit_date
            and not edit_df.empty
            and i < len(edit_df)
        ):
            old_row = edit_df.iloc[i]


        st.markdown(
            f"### Übung {i + 1}"
        )


        # ----------------------------------------------------
        # ÜBUNG
        # ----------------------------------------------------

        if old_row is not None:

            old_exercise = safe_string(
                old_row.get(
                    "Übung",
                    available_exercises[0]
                )
            )

        else:

            old_exercise = \
                available_exercises[0]


        exercise_index = (
            available_exercises.index(
                old_exercise
            )
            if old_exercise
            in available_exercises
            else 0
        )


        exercise = st.selectbox(
            "Übung",
            available_exercises,
            index=exercise_index,
            key=f"exercise_{i}"
        )


        # ----------------------------------------------------
        # MACHINE
        # ----------------------------------------------------

        if (
            exercise
            in exercises_by_group["Calisthenics"]
            or exercise
            in exercises_by_group["TRX"]
            or exercise == "Hanging"
        ):

            machine_options = [
                "Bodyweight"
            ]

        else:

            machine_options = [
                "Cable",
                "Freigewicht",
                "Maschine"
            ]


        if old_row is not None:

            old_machine = safe_string(
                old_row.get(
                    "Machine",
                    machine_options[0]
                )
            )

        else:

            old_machine = \
                machine_options[0]


        machine_index = (
            machine_options.index(
                old_machine
            )
            if old_machine
            in machine_options
            else 0
        )


        machine = st.selectbox(
            "Machine",
            machine_options,
            index=machine_index,
            key=f"machine_{i}"
        )


        # ----------------------------------------------------
        # EXTRA INFO
        # ----------------------------------------------------

        extra_info = ""

        old_extra = ""

        if old_row is not None:

            old_extra = safe_string(
                old_row.get(
                    "Extra Info",
                    ""
                )
            )


        if exercise in exercises_by_group["TRX"]:

            trx_options = [
                "Sehr aufrecht / leicht",
                "Mittel",
                "Sehr schräg / schwer"
            ]

            trx_index = (
                trx_options.index(old_extra)
                if old_extra in trx_options
                else 1
            )

            extra_info = st.selectbox(
                "Schräge / Schwierigkeit",
                trx_options,
                index=trx_index,
                key=f"extra_{i}"
            )


        elif exercise == "Hanging":

            extra_info = st.text_input(
                "Hanging-Variante / Notiz",
                value=old_extra,
                key=f"extra_{i}"
            )


        # ----------------------------------------------------
        # GRIFF
        # ----------------------------------------------------

        if (
            exercise
            in exercises_by_group["Beine"]
            or exercise
            in exercises_by_group["Glutes"]
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

                old_griff = safe_string(
                    old_row.get(
                        "Griff",
                        "Neutral"
                    )
                )

            else:

                old_griff = "Neutral"


            grip_index = (
                grip_options.index(
                    old_griff
                )
                if old_griff
                in grip_options
                else 0
            )


            griff = st.selectbox(
                "Griff",
                grip_options,
                index=grip_index,
                key=f"grip_{i}"
            )


        # ----------------------------------------------------
        # NOTIZ
        # ----------------------------------------------------

        old_note = ""

        if old_row is not None:

            old_note = safe_string(
                old_row.get(
                    "Notiz Übung",
                    ""
                )
            )


        note = st.text_input(
            "Notiz zur Übung",
            value=old_note,
            key=f"note_{i}"
        )


        # ----------------------------------------------------
        # ERINNERUNG
        # ----------------------------------------------------

        if any(
            group in muscle_groups
            for group in [
                "Rücken",
                "Schultern"
            ]
        ):

            st.warning(
                "⚠️ Schulterblätter nach hinten und runter drücken."
            )


        # ----------------------------------------------------
        # LETZTES GEWICHT
        # ----------------------------------------------------

        last_weight = get_last_set2_weight(
            saved_df,
            exercise,
            machine,
            griff
        )


        if last_weight is not None:

            st.info(
                f"Letztes Mal bei genau dieser Übung: "
                f"Set 2 = {last_weight:g} kg"
            )

        else:

            st.caption(
                "Noch kein früherer Eintrag für diese genaue Übung gefunden."
            )


        # ====================================================
        # SETS
        # ====================================================

        sets = []


        is_core = (
            exercise
            in exercises_by_group["core"]
        )


        is_time_exercise = exercise in [
            "Side plank right",
            "Side plank left",
            "Plank",
            "Hanging",
            "Handstand",
            "TRX Plank"
        ]


        uses_weight = True


        if is_core and not is_time_exercise:

            old_uses_weight = False

            if old_row is not None:

                old_uses_weight = any(
                    safe_float(
                        old_row.get(
                            f"Set {x} Gewicht",
                            0
                        )
                    ) > 0
                    for x in range(1, 5)
                )

            uses_weight = st.checkbox(
                "Mit Gewicht gearbeitet?",
                value=old_uses_weight,
                key=f"uses_weight_{i}"
            )


        # ----------------------------------------------------
        # 4 SETS
        # ----------------------------------------------------

        for s in range(4):

            set_number = s + 1

            with st.expander(
                f"Set {set_number}",
                expanded=True
            ):


                # ZEITÜBUNG
                if is_time_exercise:

                    old_duration = 0.0

                    if old_row is not None:

                        old_duration = safe_float(
                            old_row.get(
                                f"Set {set_number} Dauer Sekunden",
                                0
                            )
                        )

                    duration = st.number_input(
                        "Zeit in Sekunden",
                        min_value=0.0,
                        max_value=600.0,
                        value=float(old_duration),
                        step=5.0,
                        key=f"duration_{i}_{s}"
                    )

                    weight = 0.0
                    reps = 0.0


                # NORMALE ÜBUNG
                else:

                    if uses_weight:

                        old_weight = 0.0

                        if old_row is not None:

                            old_weight = safe_float(
                                old_row.get(
                                    f"Set {set_number} Gewicht",
                                    0
                                )
                            )

                        weight = st.number_input(
                            "Gewicht",
                            min_value=0.0,
                            max_value=400.0,
                            value=float(old_weight),
                            step=0.5,
                            key=f"weight_{i}_{s}"
                        )

                    else:

                        weight = 0.0


                    old_reps = 8.0

                    if old_row is not None:

                        old_reps = safe_float(
                            old_row.get(
                                f"Set {set_number} Wdh",
                                8
                            ),
                            8
                        )


                    reps = st.number_input(
                        "Wdh",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(old_reps),
                        step=0.5,
                        key=f"reps_{i}_{s}"
                    )

                    duration = 0.0


                # SET NOTIZ
                old_set_note = ""

                if old_row is not None:

                    old_set_note = safe_string(
                        old_row.get(
                            f"Set {set_number} Notiz",
                            ""
                        )
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


        # ====================================================
        # DATENSATZ DER ÜBUNG
        # ====================================================

        entries.append({

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

            "Set 1 Gewicht": sets[0][0],
            "Set 1 Wdh": sets[0][1],
            "Set 1 Dauer Sekunden": sets[0][2],
            "Set 1 Notiz": sets[0][3],

            "Set 2 Gewicht": sets[1][0],
            "Set 2 Wdh": sets[1][1],
            "Set 2 Dauer Sekunden": sets[1][2],
            "Set 2 Notiz": sets[1][3],

            "Set 3 Gewicht": sets[2][0],
            "Set 3 Wdh": sets[2][1],
            "Set 3 Dauer Sekunden": sets[2][2],
            "Set 3 Notiz": sets[2][3],

            "Set 4 Gewicht": sets[3][0],
            "Set 4 Wdh": sets[3][1],
            "Set 4 Dauer Sekunden": sets[3][2],
            "Set 4 Notiz": sets[3][3]
        })


    # ========================================================
    # SPEICHERN
    # ========================================================

    button_text = (
        "Änderungen speichern"
        if edit_date
        else "Training speichern"
    )


    if st.button(
        button_text,
        type="primary"
    ):

        new_df = pd.DataFrame(
            entries
        )

        old_df = load_data(
            username
        )


        # Wenn Training bearbeitet wird:
        # alte Version dieses Tages entfernen
        if (
            edit_date
            and not old_df.empty
            and "Datum" in old_df.columns
        ):

            old_df = old_df[
                old_df["Datum"].astype(str)
                != str(edit_date)
            ]


        full_df = pd.concat(
            [
                old_df,
                new_df
            ],
            ignore_index=True
        )


        save_data(
            username,
            full_df
        )


        st.success(
            "Training gespeichert! Zurück zur Hauptseite..."
        )

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
            and USERS[username_input]
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

st.title("🏋️ Gym Notes")


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
            saved_df
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


                    weight_columns = [
                        col
                        for col in [
                            "Set 1 Gewicht",
                            "Set 2 Gewicht",
                            "Set 3 Gewicht",
                            "Set 4 Gewicht"
                        ]
                        if col
                        in progress_df.columns
                    ]


                    if (
                        weight_columns
                        and "Datum"
                        in progress_df.columns
                    ):

                        chart_df = \
                            progress_df[
                                ["Datum"]
                                + weight_columns
                            ].set_index(
                                "Datum"
                            )


                        st.line_chart(
                            chart_df
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