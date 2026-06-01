import streamlit as st

st.title("🏋️ Gym Notes")
st.write("test2")

st.text_input("Day", key="date")
uebung_col, set1, set2, set3, set4, note = st.columns(6)

with uebung_col:
    splitday = st.selectbox(
        "Muskelgruppe",
        ["Rücken", "Brust", "Beine", "Glutes", "Trizeps", "Bizeps", "Schultern"]
    )

    exercises = {
        "Rücken": ["T row", "Lat pull down", "Überzüge", "Rudern"],
        "Brust": ["Push", "Butterfly"],
        "Beine": ["Leg extension", "Leg curl", "Leg press", "Abductor", "Adductor", "Squat"],
        "Glutes": ["Hip Thrust", "RDLs", "Step ups", "Abductor", "Squat", "Cable kick back", "Lunges", "Back extension"],
        "Bizeps": ["Hammer curl", "Biceps curl"],
        "Trizeps": ["Dips", "Push down"],
        "Schultern": ["Lateral raises", "Front raises", "Shoulder Press"],
    }

    exercise = st.selectbox("Übung", exercises[splitday])
    machine = st.selectbox("Machine", ["Cable", "Freigewicht", "Maschine"])

with set1:
    gewicht1 = st.number_input("Gewicht Set 1", 0, 400, 20, key="gewicht1")
    wdh1 = st.number_input("Wdh Set 1", 0, 30, 8, key="wdh1")

with set2:
    gewicht2 = st.number_input("Gewicht Set 2", 0, 400, 20, key="gewicht2")
    wdh2 = st.number_input("Wdh Set 2", 0, 30, 8, key="wdh2")

with set3:
    gewicht3 = st.number_input("Gewicht Set 3", 0, 400, 20, key="gewicht3")
    wdh3 = st.number_input("Wdh Set 3", 0, 30, 8, key="wdh3")

with set4:
    gewicht4 = st.number_input("Gewicht Set 4", 0, 400, 20, key="gewicht4")
    wdh4 = st.number_input("Wdh Set 4", 0, 30, 8, key="wdh4")

with note:
    st.text_input("Note", key="note")

