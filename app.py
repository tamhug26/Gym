import streamlit as st

st.title("🏋️ Gym Notes")

st.write("test2")

st.text_input(
        "Day",
        key="Date",
    )

Übung, set1, set2, set3, set4, note =st.columns(6)
with Übung:
    Splitday = st.multiselect(
        "Übung",
        ["Rücken", "Brust", "Beine", "Glutes", "Trizeps", "Bizeps", "Schultern"]
    )

    if Splitday == "Rücken":
        st.selectbox(
        "Übung",
        ["T row", "Lat pull down", "Überzüge", "Rudern"]
    )
        st.selectbox(
        "Machine",
        ["cable", "Freigewicht", "Maschine"]
    )
        
    if Splitday == "Brust":
        st.selectbox(
        "Übung",
        ["Push", "Butterfly"]
    )
        st.selectbox(
        "Richtung",
        ["down", "up", "Straight"]
    )
        st.selectbox(
        "Machine",
        ["cable", "Freigewicht", "Maschine"]
    )
    
    if Splitday == "Beine":
        st.selectbox(
        "Übung",
        ["Leg extension", "Leg curl", "Leg press", "Abductor", "Adductor", "Squat"]
        )
        st.selectbox(
            "Machine",
            ["cable", "Freigewicht", "Maschine"]
        )
    
    if Splitday == "Glutes":
        st.selectbox(
        "Übung",
        ["Hip Thrust", "RDLs", "Step ups", "Abductor", "Squat", "cable kick back", "lunges", "back extension"]
        )
        st.selectbox(
            "Machine",
            ["cable", "Freigewicht", "Maschine"]
        )

    if Splitday == "Biceps":
        st.selectbox(
        "Übung",
        ["Hammer curl", "Biceps curl"]
        )
        st.selectbox(
            "Machine",
            ["cable", "Freigewicht", "Maschine"]
        )
    if Splitday == "Triceps":
        st.selectbox(
        "Übung",
        ["Dips", "Push down"  ]
        )
        st.selectbox(
            "Machine",
            ["cable", "Freigewicht", "Maschine"]
        )

    if Splitday == "Shoulders":
        st.selectbox(
            "Übung",
            ["Lateral raises", "front raises", "Shoulder Press"]
        )
        st.selectbox(
            "Machine",
            ["cable", "Freigewicht", "Maschine"]
        )

with set1:
    Gewicht = st.number_input("Gewicht", 0, 400, 20)
    Wdh = st.number_input("Wiederholungen", 0, 30, 8)
with set2:
    Gewicht = st.number_input("Gewicht", 0, 400, 20)
    Wdh = st.number_input("Wiederholungen", 0, 30, 8)
with set3:
    Gewicht = st.number_input("Gewicht", 0, 400, 20)
    Wdh = st.number_input("Wiederholungen", 0, 30, 8)
with set4:
    Gewicht = st.number_input("Gewicht", 0, 400, 20)
    Wdh = st.number_input("Wiederholungen", 0, 30, 8)
with note:
    st.text_input(
        "Note",
        key="Note",
    )

