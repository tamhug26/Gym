import streamlit as st
import pandas as pd
from datetime import date
#st.set_page_config(layout="wide")

st.title("🏋️ Gym Notes")

# Datum auswählen
training_date = st.date_input("Datum", value=date.today())

# Muskelgruppen auswählen
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

# Übungen aus den gewählten Gruppen sammeln
available_exercises = []
for group in muscle_groups:
    available_exercises.extend(exercises_by_group[group])

available_exercises = sorted(set(available_exercises))

st.subheader("Training eintragen")

if not available_exercises:
    st.info("Wähle zuerst mindestens eine Muskelgruppe aus.")
else:
    rows = st.number_input("Wie viele Übungen möchtest du eintragen?", min_value=1, max_value=20, value=3)

    entries = []

    for i in range(rows):
        st.markdown(f"### Übung {i + 1}")

        exercise = st.selectbox(
            "Übung",
            available_exercises,
            key=f"exercise_{i}"
        )
        machine = st.selectbox(
            "Machine",
            ["Cable", "Freigewicht", "Maschine"],
            key=f"machine_{i}"
        )
        griff = st.selectbox(
            "Griff",
            ["Neutral", "Breit", "Eng", "Untergriff", "Obergriff"],
            key=f"grip_{i}"
        )

        note = st.text_input("Notiz", key=f"note_{i}")

        cols = st.columns(4)

        sets = []

        for s in range(4):
            with cols[s]:
                st.write(f"Set {s+1}")

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

                note_set = st.text_input(
                    "Notiz",
                    key=f"note_{i}_{s}"
                )

                sets.append((weight, reps, note_set))

    entries.append({
        "Datum": training_date,
        "Übung": exercise,
        "Machine": machine,
        "Griff": griff,

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
        df = pd.DataFrame(entries)
        st.success("Training gespeichert!")
        st.dataframe(df, use_container_width=True)
    