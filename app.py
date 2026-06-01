import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

USERS = {
    "Tamara": "1010",
    "Can": "1010"
}

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_user_file(username):
    return DATA_DIR / f"{username}_gym_log.csv"
def load_data(user_file):
    if user_file.exists():
        return pd.read_csv(user_file)
    return pd.DataFrame()
def save_data(user_file, df):
    df.to_csv(user_file, index=False)
def get_available_exercises(muscle_groups):
    exercises_by_group = {
        "Rücken": ["T row", "Lat pull down", "Überzüge", "Rudern"],
        "Brust": ["Push", "Butterfly"],
        "Beine": ["Leg extension", "Leg curl", "Leg press", "Abductor", "Adductor", "Squat"],
        "Glutes": ["Hip Thrust", "bulgarian Split Squats", "RDLs", "Step ups", "Abductor", "Squat", "Cable kick back", "Lunges", "Back extension"],
        "Bizeps": ["Hammer curl", "Biceps curl"],
        "Trizeps": ["Dips", "Push down"],
        "Schultern": ["Lateral raises", "Front raises", "Shoulder Press"],
    }

    available = []
    for group in muscle_groups:
        available.extend(exercises_by_group[group])

    return sorted(set(available))
def training_form(username, user_file, saved_df, edit_date=None):
    if edit_date:
        training_date = st.date_input("Datum", value=pd.to_datetime(edit_date).date())
    else:
        training_date = st.date_input("Datum", value=date.today())

    st.subheader("Allgemeine Angaben")

    mode = st.selectbox("Modus", ["Maintaining", "Bulk", "Cut"])

    if mode == "Bulk":
        calories = st.number_input("Kalorienziel", min_value=0, max_value=10000, value=2500, step=50)
    elif mode == "Cut":
        calories = st.number_input("Kalorienziel", min_value=0, max_value=10000, value=1800, step=50)
    else:
        calories = st.number_input("Kalorienziel", min_value=0, max_value=10000, value=2200, step=50)

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

    muscle_groups = st.multiselect(
        "Welche Muskelgruppen hast du trainiert?",
        ["Rücken", "Brust", "Beine", "Glutes", "Trizeps", "Bizeps", "Schultern"]
    )

    available_exercises = get_available_exercises(muscle_groups)

    if not available_exercises:
        st.info("Wähle mindestens eine Muskelgruppe aus.")
        return

    rows = st.number_input(
        "Wie viele Übungen möchtest du eintragen?",
        min_value=1,
        max_value=20,
        value=3
    )

    entries = []

    for i in range(rows):
        st.markdown(f"### Übung {i + 1}")

        exercise = st.selectbox("Übung", available_exercises, key=f"exercise_{i}")
        machine = st.selectbox("Machine", ["Cable", "Freigewicht", "Maschine"], key=f"machine_{i}")
        if exercise in exercises_by_group["Beine"] or exercise in exercises_by_group["Glutes"]:
            griff = "Nicht relevant"
        else:
            griff = st.selectbox(
                "Griff",
                ["Neutral", "Breit", "Eng", "Untergriff", "Obergriff"],
                key=f"grip_{i}"
            )
        note = st.text_input("Notiz zur Übung", key=f"note_{i}")

        if any(group in muscle_groups for group in ["Rücken", "Schultern"]):
            st.warning("⚠️ Schulterblätter nach hinten und runter drücken.")

        last_weight = get_last_set2_weight(saved_df, exercise, machine, griff)

        if last_weight is not None:
            st.info(f"Letztes Mal bei genau dieser Übung: Set 2 = {last_weight} kg")
        else:
            st.caption("Noch kein früherer Eintrag für diese genaue Übung gefunden.")

        cols = st.columns(4)
        sets = []

        for s in range(4):
            with cols[s]:
                st.write(f"Set {s + 1}")

                weight = st.number_input(
                    "Gewicht",
                    min_value=0.0,
                    max_value=400.0,
                    value=0.0,
                    step=0.5,
                    key=f"weight_{i}_{s}"
                )

                reps = st.number_input(
                    "Wdh",
                    min_value=0.0,
                    max_value=50.0,
                    value=8.0,
                    step=0.5,
                    key=f"reps_{i}_{s}"
                )

                note_set = st.text_input("Set-Notiz", key=f"note_set_{i}_{s}")

                sets.append((weight, reps, note_set))

        entries.append({
            "Benutzer": username,
            "Datum": training_date,
            "Modus": mode,
            "Kalorienziel": calories,
            "Stimmung": mood,
            "Schmerzen": pain,

            "Cardio Form": cardio_type,
            "Cardio Zeit min": cardio_time,
            "Cardio Distanz km": cardio_distance,
            "Cardio Kalorien": cardio_calories,

            "Übung": exercise,
            "Machine": machine,
            "Griff": griff,
            "Notiz Übung": note,

            "Set 1 Gewicht": sets[0][0],
            "Set 1 Wdh": sets[0][1],
            "Set 1 Notiz": sets[0][2],

            "Set 2 Gewicht": sets[1][0],
            "Set 2 Wdh": sets[1][1],
            "Set 2 Notiz": sets[1][2],

            "Set 3 Gewicht": sets[2][0],
            "Set 3 Wdh": sets[2][1],
            "Set 3 Notiz": sets[2][2],

            "Set 4 Gewicht": sets[3][0],
            "Set 4 Wdh": sets[3][1],
            "Set 4 Notiz": sets[3][2],
        })

    button_text = "Änderungen speichern" if edit_date else "Training speichern"

    if st.button(button_text):
        new_df = pd.DataFrame(entries)
        old_df = load_data(user_file)

        if edit_date and not old_df.empty:
            old_df = old_df[old_df["Datum"] != str(edit_date)]

        full_df = pd.concat([old_df, new_df], ignore_index=True)
        save_data(user_file, full_df)

        st.success("Gespeichert!")
        st.session_state.edit_date = None
        st.dataframe(new_df, use_container_width=True, hide_index=True)
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
            st.rerun()
        else:
            st.error("Benutzername oder Passwort falsch")

    st.stop()
st.session_state.login_time = datetime.now()
if datetime.now() - st.session_state.login_time > timedelta(minutes=120):
    st.session_state.logged_in = False
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