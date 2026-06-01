import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

st.set_page_config(layout="wide")

USERS = {
    "tamara": "1010",
    "Can": "1010"
}

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_user_file(username):
    return DATA_DIR / f"{username}_gym_log.csv"


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")

    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    if st.button("Einloggen"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Benutzername oder Passwort falsch")

    st.stop()


username = st.session_state.username
user_file = get_user_file(username)

st.sidebar.success(f"Eingeloggt als {username}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()


st.title("🏋️ Gym Notes")

training_date = st.date_input("Datum", value=date.today())

muscle_groups = st.multiselect(
    "Welche Muskelgruppen hast du trainiert?",
    ["Rücken", "Brust", "Beine", "Glutes", "Trizeps", "Bizeps", "Schultern"]
)

exercises_by_group = {
    "Rücken": ["T row", "Lat pull down", "Überzüge", "Rudern"],
    "Brust": ["Push", "Butterfly"],
    "Beine": ["Leg extension", "Leg curl", "Leg press", "Abductor", "Adductor", "Squat"],
    "Glutes": ["Hip Thrust", "RDLs", "Step ups", "Abductor", "Squat", "Cable kick back", "Lunges", "Back extension"],
    "Bizeps": ["Hammer curl", "Biceps curl"],
    "Trizeps": ["Dips", "Push down"],
    "Schultern": ["Lateral raises", "Front raises", "Shoulder Press"],
}

available_exercises = []
for group in muscle_groups:
    available_exercises.extend(exercises_by_group[group])

available_exercises = sorted(set(available_exercises))

st.subheader("Training eintragen")

if not available_exercises:
    st.info("Wähle zuerst mindestens eine Muskelgruppe aus.")
else:
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
        griff = st.selectbox("Griff", ["Neutral", "Breit", "Eng", "Untergriff", "Obergriff"], key=f"grip_{i}")
        note = st.text_input("Notiz zur Übung", key=f"note_{i}")

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
                    value=0.0,
                    step=0.5,
                    key=f"reps_{i}_{s}"
                )

                note_set = st.text_input("Set-Notiz", key=f"note_set_{i}_{s}")

                sets.append((weight, reps, note_set))

        entries.append({
            "Benutzer": username,
            "Datum": training_date,
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

    if st.button("Training speichern"):
        new_df = pd.DataFrame(entries)

        if user_file.exists():
            old_df = pd.read_csv(user_file)
            full_df = pd.concat([old_df, new_df], ignore_index=True)
        else:
            full_df = new_df

        full_df.to_csv(user_file, index=False)

        st.success("Training gespeichert!")
        st.dataframe(new_df, use_container_width=True, hide_index=True)


st.subheader("📖 Meine gespeicherten Trainings")

if user_file.exists():
    saved_df = pd.read_csv(user_file)
    st.dataframe(saved_df, use_container_width=True, hide_index=True)
else:
    st.info("Noch keine gespeicherten Trainings vorhanden.")