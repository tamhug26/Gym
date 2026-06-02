import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
from datetime import datetime, timedelta
import time

#st.set_page_config(layout="wide")

USERS = {
    "Tamara": "1010",
    "Can": "1010",
    "Papa": "aramat"
}

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

exercises_by_group = {
    "Rücken": ["T row", "Lat pull down", "Überzüge", "Rudern", "Face pulls", "Delt Fly", "Hanging"],
    "Brust": ["Push", "Butterfly"],
    "Beine": ["Leg extension", "Leg curl", "Leg press", "Abductor", "Adductor", "Squat", "Calf raises"],
    "Glutes": ["Hip Thrust", "Bulgarian Split Squats", "RDLs", "Step ups", "Abductor", "Squat", "Cable kick back", "Lunges", "Glute hyperextension"],
    "Bizeps": ["Hammer curl", "Biceps curl"],
    "Trizeps": ["Dips", "Push down"],
    "Schultern": ["Lateral raises", "Front raises", "Shoulder Press", "Delt Fly"],
    "core": ["Dumbbell side bend", "Lying Alternating Leg Raise", "Lying leg raises", "Dead bug", "Heel tap crunches",
             "Alternating knee tucks", "Russian twist", "Over unders beide Richtungen", "Ab wheel rollout",
             "Reverse crunch", "Hanging crunches", "Side plank right", "Side plank left", "Plank"],
    "Calisthenics": ["Push up", "Pike Push up", "Handstand", "Pull up", "Chin up", "Dips", "Australian Rows", "Squat", "Lunges"],
    "TRX": ["TRX Row", "TRX Chest Press", "TRX Biceps Curl", "TRX Triceps Extension", "TRX Squat", "TRX Lunge", "TRX Pike", "TRX Plank"]
}


def get_user_file(username):
    return DATA_DIR / f"{username}_gym_log.csv"
def load_data(user_file):
    if user_file.exists():
        return pd.read_csv(user_file)
    return pd.DataFrame()
def save_data(user_file, df):
    df.to_csv(user_file, index=False)
def get_available_exercises(muscle_groups):
    available = []
    for group in muscle_groups:
        available.extend(exercises_by_group[group])
    return sorted(set(available))
def training_form(username, user_file, saved_df, edit_date=None):
    edit_df = pd.DataFrame()

    if edit_date and not saved_df.empty:
        edit_df = saved_df[saved_df["Datum"].astype(str) == str(edit_date)].copy()
        training_date = st.date_input("Datum", value=pd.to_datetime(edit_date).date())
    else:
        training_date = st.date_input("Datum", value=date.today())

    st.subheader("Allgemeine Angaben")

    last_mode, last_calories = get_last_mode_and_calories(saved_df)

    mode_options = ["Maintaining", "Bulk", "Cut"]

    if last_mode not in mode_options:
        last_mode = "Maintaining"
    
    col1, col2 = st.columns(2)
    with col1:
        mode = st.selectbox(
            "Modus",
            mode_options,
            index=mode_options.index(last_mode)
        )
    with col2: 
        calories = st.number_input(
            "Kalorienziel",
            min_value=0,
            max_value=10000,
            value=last_calories,
            step=50
        )
    period_mode = st.checkbox("Period Mode")

    period_start = ""
    period_end = ""

    if period_mode:
        p1, p2 = st.columns(2)
        with p1:
            period_start = st.date_input("Periode Start", value=training_date)
        with p2:
            period_end = st.date_input("Periode Ende", value=training_date)

    mood = st.slider(
        "Stimmung / Gefühl",
        min_value=1,
        max_value=5,
        value=3,
        help="1 = super toll, 3 = normal, 5 = dreckig"
    )

    pain = ""
    if mood >= 4:
        pain = st.text_input("Gab es Schmerzen? Wenn ja, wo?")

    st.subheader("Cardio")

    cardio_type = st.selectbox(
        "Cardio-Form",
        ["Kein Cardio", "Laufen", "Fahrrad", "Stepper", "Stairmaster", "Crosstrainer", "Rudern", "Walking", "Anderes"]
    )

    cardio_time = 0.0
    cardio_distance = 0.0
    cardio_calories = 0.0

    if cardio_type != "Kein Cardio":
        c1, c2, c3 = st.columns(3)
        with c1:
            cardio_time = st.number_input("Cardio Zeit in Minuten", min_value=0.0, max_value=500.0, value=0.0, step=1.0)
        with c2:
            cardio_distance = st.number_input("Distanz in km", min_value=0.0, max_value=200.0, value=0.0, step=0.1)
        with c3:
            cardio_calories = st.number_input("Cardio Kalorien", min_value=0.0, max_value=3000.0, value=0.0, step=10.0)

    st.subheader("Krafttraining")

    all_groups = ["Rücken", "Brust", "Beine", "Glutes", "Trizeps", "Bizeps", "Schultern", "core", "Calisthenics", "TRX"]

    if edit_date and not edit_df.empty:
        old_exercises = sorted(edit_df["Übung"].dropna().unique())
        muscle_groups = st.multiselect(
            "Welche Muskelgruppen hast du trainiert?",
            all_groups,
            default=all_groups
        )
        available_exercises = sorted(set(get_available_exercises(muscle_groups) + old_exercises))
    else:
        muscle_groups = st.multiselect(
            "Welche Muskelgruppen hast du trainiert?",
            all_groups
        )
        available_exercises = get_available_exercises(muscle_groups)

    if not available_exercises:
        st.info("Wähle mindestens eine Muskelgruppe aus.")
        return

    default_rows = len(edit_df) if edit_date and not edit_df.empty else 3

    rows = st.number_input(
        "Wie viele Übungen möchtest du eintragen?",
        min_value=1,
        max_value=20,
        value=default_rows
    )

    entries = []

    for i in range(rows):
        old_row = None

        if edit_date and not edit_df.empty and i < len(edit_df):
            old_row = edit_df.iloc[i]
        st.markdown(f"### Übung {i + 1}")

        old_exercise = old_row["Übung"] if old_row is not None and "Übung" in old_row else available_exercises[0]
        exercise_index = available_exercises.index(old_exercise) if old_exercise in available_exercises else 0

        exercise = st.selectbox(
            "Übung",
            available_exercises,
            index=exercise_index,
            key=f"exercise_{i}"
        )

        if exercise in exercises_by_group["Calisthenics"] or exercise in exercises_by_group["TRX"] or exercise == "Hanging":
            machine_options = ["Bodyweight"]
        else:
            machine_options = ["Cable", "Freigewicht", "Maschine"]
        old_machine = old_row["Machine"] if old_row is not None and "Machine" in old_row else "Cable"
        machine_index = machine_options.index(old_machine) if old_machine in machine_options else 0

        machine = st.selectbox(
            "Machine",
            machine_options,
            index=machine_index,
            key=f"machine_{i}"
        )

        extra_info = ""

        if exercise in exercises_by_group["TRX"]:
            extra_info = st.selectbox(
                "Schräge / Schwierigkeit",
                ["Sehr aufrecht / leicht", "Mittel", "Sehr schräg / schwer"],
                key=f"extra_{i}"
            )
        elif exercise == "Hanging":
            extra_info = st.text_input("Hanging-Variante / Notiz", key=f"extra_{i}")

        if exercise in exercises_by_group["Beine"] or exercise in exercises_by_group["Glutes"]:
            griff = "Nicht relevant"
        else:
            grip_options = ["Neutral", "Breit", "Eng", "Untergriff", "Obergriff"]
            old_griff = old_row["Griff"] if old_row is not None and "Griff" in old_row else "Neutral"
            grip_index = grip_options.index(old_griff) if old_griff in grip_options else 0

            griff = st.selectbox(
                "Griff",
                grip_options,
                index=grip_index,
                key=f"grip_{i}"
            )

        old_note = old_row["Notiz Übung"] if old_row is not None and "Notiz Übung" in old_row else ""
        note = st.text_input("Notiz zur Übung", value=str(old_note), key=f"note_{i}")

        if any(group in muscle_groups for group in ["Rücken", "Schultern"]):
            st.warning("⚠️ Schulterblätter nach hinten und runter drücken.")

        last_weight = get_last_set2_weight(saved_df, exercise, machine, griff)

        if last_weight is not None:
            st.info(f"Letztes Mal bei genau dieser Übung: Set 2 = {last_weight} kg")
        else:
            st.caption("Noch kein früherer Eintrag für diese genaue Übung gefunden.")

        sets = []

        is_core = exercise in exercises_by_group["core"]
        is_time_exercise = exercise in ["Side plank right", "Side plank left", "Plank", "Hanging"]

        uses_weight = True

        if is_core:
            uses_weight = st.checkbox("Mit Gewicht gearbeitet?", value=False, key=f"uses_weight_{i}")

        for s in range(4):
            with st.expander(f"Set {s + 1}", expanded=True):

                if is_time_exercise:
                    duration = st.number_input(
                        "Zeit in Sekunden",
                        min_value=0.0,
                        max_value=600.0,
                        value=0.0,
                        step=5.0,
                        key=f"duration_{i}_{s}"
                    )
                    weight = 0.0
                    reps = 0.0

                else:
                    if uses_weight:
                        weight = st.number_input(
                            "Gewicht",
                            min_value=0.0,
                            max_value=400.0,
                            value=float(old_row[f"Set {s + 1} Gewicht"]) if old_row is not None and f"Set {s + 1} Gewicht" in old_row else 0.0,
                            step=0.5,
                            key=f"weight_{i}_{s}"
                        )
                    else:
                        weight = 0.0

                    reps = st.number_input(
                        "Wdh",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(old_row[f"Set {s + 1} Wdh"]) if old_row is not None and f"Set {s + 1} Wdh" in old_row else 8.0,
                        step=0.5,
                        key=f"reps_{i}_{s}"
                    )

                    duration = 0.0

                old_set_note = old_row[f"Set {s + 1} Notiz"] if old_row is not None and f"Set {s + 1} Notiz" in old_row else ""

                note_set = st.text_input(
                    "Set-Notiz",
                    value=str(old_set_note),
                    key=f"note_set_{i}_{s}"
                )

                sets.append((weight, reps, duration, note_set))

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
            "Set 4 Notiz": sets[3][3],
        })

    button_text = "Änderungen speichern" if edit_date else "Training speichern"

    if st.button(button_text):
        new_df = pd.DataFrame(entries)
        old_df = load_data(user_file)

        if edit_date and not old_df.empty:
            old_df = old_df[old_df["Datum"] != str(edit_date)]

        full_df = pd.concat([old_df, new_df], ignore_index=True)
        save_data(user_file, full_df)

        st.success("Änderungen gespeichert. Zurück zur Hauptseite...")
        time.sleep(1)
        st.session_state.edit_date = None
        st.rerun()
def get_last_set2_weight(saved_df, exercise, machine, griff):
    if saved_df.empty:
        return None

    df = saved_df.copy()
    df["Datum"] = pd.to_datetime(df["Datum"])

    matches = df[
        (df["Übung"] == exercise) &
        (df["Machine"] == machine) &
        (df["Griff"] == griff)
    ].sort_values("Datum", ascending=False)

    if matches.empty:
        return None

    return matches.iloc[0]["Set 2 Gewicht"]
def get_last_mode_and_calories(saved_df):
    if saved_df.empty:
        return "Maintaining", 2200

    df = saved_df.copy()
    df["Datum"] = pd.to_datetime(df["Datum"])
    df = df.sort_values("Datum", ascending=False)

    last_row = df.iloc[0]

    last_mode = last_row.get("Modus", "Maintaining")
    last_calories = int(last_row.get("Kalorienziel", 2200))

    return last_mode, last_calories


# Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "edit_date" not in st.session_state:
    st.session_state.edit_date = None

if not st.session_state.logged_in:
    st.title("🔐 Login")

    username_input = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    if st.button("Einloggen"):
        if username_input in USERS and USERS[username_input] == password:
            st.session_state.logged_in = True
            st.session_state.username = username_input
            st.session_state.login_time = datetime.now()
            st.rerun()
        else:
            st.error("Benutzername oder Passwort falsch")

    st.stop()
if "login_time" not in st.session_state:
    st.session_state.login_time = datetime.now()

if datetime.now() - st.session_state.login_time > timedelta(minutes=120):
    st.session_state.logged_in = False
    st.session_state.edit_date = None
    st.warning("Session abgelaufen. Bitte neu einloggen.")
    st.rerun()

username = st.session_state.username
user_file = get_user_file(username)
saved_df = load_data(user_file)

st.sidebar.success(f"Eingeloggt als {username}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.edit_date = None
    st.rerun()

#----------------------------------------
st.title("🏋️ Gym Notes")

if st.session_state.edit_date:
    st.warning(f"Bearbeitungsmodus für Training vom {st.session_state.edit_date}")
    training_form(username, user_file, saved_df, edit_date=st.session_state.edit_date)

    if st.button("Bearbeitung abbrechen"):
        st.session_state.edit_date = None
        st.rerun()

else:
    tab1, tab2, tab3 = st.tabs(["➕ Neues Training", "📖 Gespeicherte Trainings", "📊 Statistik"])

    with tab1:
        training_form(username, user_file, saved_df)

    with tab2:
        st.subheader("📖 Gespeicherte Trainings")

        if saved_df.empty:
            st.info("Noch keine gespeicherten Trainings vorhanden.")
        else:
            saved_df["Datum"] = saved_df["Datum"].astype(str)
            available_dates = sorted(saved_df["Datum"].unique(), reverse=True)

            date_options = []
            for d in available_dates:
                date_options.append(f"🔴 {d}")

            selected_date_label = st.selectbox("Trainingstag auswählen", date_options)
            selected_date_str = selected_date_label.replace("🔴 ", "")
            selected_date = pd.to_datetime(selected_date_str).date()

            day_df = saved_df[saved_df["Datum"] == selected_date_str]

            if day_df.empty:
                st.info("Für dieses Datum gibt es kein gespeichertes Training.")
            else:
                st.dataframe(day_df, use_container_width=True, hide_index=True)

                c1, c2 = st.columns(2)

                with c1:
                    if st.button("Dieses Training bearbeiten"):
                        st.session_state.edit_date = selected_date_str
                        st.rerun()

                with c2:
                    if st.button("Dieses Training löschen"):
                        saved_df = saved_df[saved_df["Datum"] != selected_date_str]
                        save_data(user_file, saved_df)
                        st.success("Training gelöscht.")
                        st.rerun()
    with tab3:
        st.subheader("📊 Statistik")

        st.subheader("📤 Export")

        csv_data = saved_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ CSV exportieren",
            data=csv_data,
            file_name=f"{username}_gym_export.csv",
            mime="text/csv"
        )

        excel_buffer = saved_df.to_excel("temp.xlsx", index=False)

        with open("temp.xlsx", "rb") as f:
            st.download_button(
                label="⬇️ Excel exportieren",
                data=f,
                file_name=f"{username}_gym_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        if saved_df.empty:
            st.info("Noch keine Daten für Statistik vorhanden.")
        else:
            stats_df = saved_df.copy()
            stats_df["Datum"] = pd.to_datetime(stats_df["Datum"])

            st.metric("Anzahl Trainings", stats_df["Datum"].nunique())
            st.metric("Anzahl Übungen gesamt", len(stats_df))

            st.subheader("Trainings pro Muskelgruppe / Übung")
            exercise_counts = stats_df["Übung"].value_counts()
            st.bar_chart(exercise_counts)

            st.subheader("Gewichtsentwicklung pro Übung")

            selected_exercise = st.selectbox(
                "Übung für Verlauf auswählen",
                sorted(stats_df["Übung"].dropna().unique())
            )

            progress_df = stats_df[stats_df["Übung"] == selected_exercise].copy()
            progress_df = progress_df.sort_values("Datum")

            chart_df = progress_df[[
                "Datum",
                "Set 1 Gewicht",
                "Set 2 Gewicht",
                "Set 3 Gewicht",
                "Set 4 Gewicht"
            ]].set_index("Datum")

            st.line_chart(chart_df)

            st.subheader("Durchschnittliche Stimmung")
            avg_mood = stats_df["Stimmung"].mean()
            st.metric("Ø Stimmung", round(avg_mood, 2))

            st.subheader("Cardio gesamt")
            total_cardio_time = stats_df["Cardio Zeit min"].sum()
            total_cardio_distance = stats_df["Cardio Distanz km"].sum()
            total_cardio_calories = stats_df["Cardio Kalorien"].sum()

            c1, c2, c3 = st.columns(3)
            c1.metric("Cardio Minuten", round(total_cardio_time, 1))
            c2.metric("Cardio km", round(total_cardio_distance, 1))
            c3.metric("Cardio kcal", round(total_cardio_calories, 0))    