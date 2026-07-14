
# Day order used throughout the bot (Mon-Fri)
DAYS = ["mon", "tue", "wed", "thu", "fri"]
DAY_LABELS = {
    "mon": "Monday",
    "tue": "Tuesday",
    "wed": "Wednesday",
    "thu": "Thursday",
    "fri": "Friday",
}

# ---------------------------------------------------------------
# BUS SCHEDULE
# ---------------------------------------------------------------
BUS_SCHEDULE = {
    "mon": "🚌 Monday Bus\nDepart: 8:00am\nReturn: 4:10pm",
    "tue": "🚌 Tuesday Bus\nDepart: 8:30am\nReturn: 4:40pm",
    "wed": "🚌 Wednesday Bus\nDepart: 8:00am\nReturn: 4:10pm",
    "thu": "🚌 Thursday Bus\nDepart: 8:30am\nReturn: 6:10pm",
    "fri": (
        "🚌 Friday Bus\n"
        "Depart: 7:30am\n"
        "Return: 11:10am\n"
        "Depart (again): 2:30pm\n"
        "Return: 5:00pm"
    ),
}

# ---------------------------------------------------------------
# CLASS SCHEDULE  (from "SET 9 SCHEDULE" photo, Sem 1)
# NOTE: double-check these times against the original photo -
# some block boundaries were estimated where the image was unclear.
# ---------------------------------------------------------------
CLASS_SCHEDULE = {
    "mon": [
        "9am-11am  Chem Lecture (AUDI)",
        "11am - 1pm  Physics Lecture (AUDI)",
        "1pm - 2pm  Lunch",
        "2pm - 4pm  Bio Lecture (AUDI)",
    ],
    "tue": [
        "9am - 11am  Bio Lecture (AUDI)",
        "11am - 1pm  Chem Lecture (AUDI)",
        "1pm - 2pm  Lunch",
        "2pm - 4pm  Physics Lecture (AUDI)",
    ],
    "wed": [
        "9am - 11am  Statistics (MK1) - Ms Nadiah",
        "11am - 1pm  Logical Reasoning (K3) - Dr Mahirah",
        "1pm - 2pm  Lunch",
        "2pm - 3pm  LLA (MB1) - Ms Athirah",
    ],
    "thu": [
        "9am - 11am  Chem Lab/Tutor (MK2) - Dr Prema",
        "11am - 1pm  Research Skills (BGP) - Ms Farah",
        "1pm - 2pm  Lunch",
        "2pm - 3pm  Physics Lab/Tutor (MF1) - Dr Azah",
        "3pm - 5pm  Bio Lab/Tutor (MB1) - Pn Nisa",
    ],
    "fri": [
        "8am - 10am  Statistics (K4) - Ms Nadiah",
        "10am - 11am  Logical Reasoning (K3)",
        "2pm - 4pm  Jati Diri (AUDI)",
    ],
}

# ---------------------------------------------------------------
# SUBJECTS
# ---------------------------------------------------------------
# Each subject has:
#   label:       button text shown to students
#   chapters:    list of chapters/materials. Each chapter is one of:
#                 - {"label": "...", "type": "file", "path": "materials/xxx/yyy.pdf"}
#                     -> bot sends the file at that path
#                 - {"label": "...", "type": "link", "url": "https://..."}
#                     -> bot sends a clickable link
#                 - {"label": "...", "type": "text", "content": "..."}
#                     -> bot sends plain text (e.g. a quick note)
#   assignments: same three types, shown when "Assignments" is tapped
#
# TO ADD SLIDES: drop the file into the matching materials/<subject>/
# folder and set "path" to "materials/<subject>/<filename>".
# ---------------------------------------------------------------

SUBJECTS = {
    "biology": {
        "label": "🧬 Biology",
        "chapters": [
            {
                "label": "C1.1 - Biochemistry",
                "type": "file",
                "path": "materials/biology/CHAPTER 1 Biochemistry.pdf",
            },
            {
                "label": "C1.2 - Enzymes and Metabolism",
                "type": "file",
                "path": "materials/biology/CHAPTER 1.2 ENZYMES AND METABOLISM.pdf",
            },
            {
                "label": "C2 - The Cell",
                "type": "file",
                "path": "materials/biology/CHAPTER 2 THE CELL.pdf",
            },
            {
                "label": "📆 Jadual Pengajaran",
                "type": "file",
                "path": "materials/biology/Jadual Pengajaran.pdf",
            },
        ],
        "assignments": {
            "type": "text",
            "content": "No assignments added yet.",
        },
    },
    "physics": {
        "label": "⚛️ Physics",
        "chapters": [
            {
                "label": "C1 - Unit, Measurement and Math Review",
                "type": "file",
                "path": "materials/physics/Chapter 1; Unit, Measurement and Math Review.pdf",
            },
            {
                "label": "C2 - Motion in One Dimension",
                "type": "file",
                "path": "materials/physics/Chapter 2; Motion in One Dimension.pdf",
            },{
                "label": "C3 - Motion in Two Dimensions",
                "type": "file",
                "path": "materials/physics/Chapter 3; Motion in Two Dimensions.pdf",
            },
        ],
        "assignments": {
            "type": "text",
            "content": "No assignments added yet.",
        },
    },

    "chemistry": {
        "label": "🧪 Chemistry",
        "chapters": [
            {
                "label": "1A - Matter and Atomic Structure",
                "type": "file",
                "path": "materials/chemistry/CHAPTER 1A MATTER AND ATOMIC STRUCTURE.pdf",
            },{
                "label": "1B - QUANTUM THEORY",
                "type": "file",
                "path": "materials/chemistry/CHAPTER 1B QUANTUM THEORY.pdf",
            },
        ],
        "assignments": [
            {
                "label": "Chapter 1A - Questions",
                "type": "file",
                "path": "materials/chemistry/assignments/C1A/CHAPTER 1A MATTER AND ATOMIC STRUCTURE.pdf",
            },
            {
                "label": "Chapter 1A - Answers",
                "type": "file",
                "path": "materials/chemistry/assignments/C1A/Topic 1A_notes_answer.pdf",
            },
        ],
    },

    "statistics": {
        "label": "📊 Statistics",
        "chapters": [
            {
                "label": "Chapter 1.1",
                "type": "file",
                "path": "materials/statistics/Ch_1_1.1_S.pptx",
            },
            {
                "label": "Chapter 1.2",
                "type": "file",
                "path": "materials/statistics/Ch_1_1.2_S.pptx",
            },
            {
                "label": "Chapter 1.3",
                "type": "file",
                "path": "materials/statistics/Ch_1_1.3_S.pptx",
            },
            {
                "label": "Chapter 2.1",
                "type": "file",
                "path": "materials/statistics/Ch_2_2.1_S.pdf",
            },
            {
                "label": "Chapter 2.2",
                "type": "file",
                "path": "materials/statistics/Ch_2_2.2_S.pdf",
            },
            {
                "label": "Chapter 2.3",
                "type": "file",
                "path": "materials/statistics/Ch_2_2.3_S.pdf",
            },
            {
                "label": "Chapter 2.4",
                "type": "file",
                "path": "materials/statistics/Ch_2_2.4_S.pdf",
            },
        ],
        "assignments": {
            "type": "text",
            "content": "No assignments added yet.",
        },
    },

    "logical_reasoning": {
        "label": "🧩 Logical Reasoning",
        "chapters": [
            {
                "label": "Module",
                "type": "file",
                "path": "materials/logical_reasoning/MODULE_LR.pdf",
            },
            {
                "label": "Course Introduction",
                "type": "file",
                "path": "materials/logical_reasoning/Course Introduction.pdf",
            },
        ],
        "assignments": {
            "type": "text",
            "content": "No assignments added yet.",
        },
    },

    "lla": {
        "label": "🗣️ LLA",
        "chapters": [
            {
                "label": "Drive",
                "type": "text",
                "content": "https://drive.google.com/drive/folders/1JsPDDcnFr704jgxYg5qDN9ncOULAqDVS",
            },
        ],
        "assignments": {
            "type": "text",
            "content": "No assignments added yet.",
        },
    },

    "research_skills": {
        "label": "🔬 Research Skills",
        "chapters": [
            {
                "label": "C1 - (edit me in data.py)",
                "type": "text",
                "content": "Add Chapter 1 content, a link, or a file path here.",
            },
        ],
        "assignments": {
            "type": "text",
            "content": "No assignments added yet.",
        },
    },
    "jati_diri": {
        "label": "🌱 Jati Diri",
        "chapters": [
            {
                "label": "Tugasan",
                "type": "file",
                "path": "materials/jati_diri/TAKLIMAT TUGASAN SUBJEK PEMBANGUNAN JATI DIRI.pptx",
            },
            {
                "label": "Jadual Tugasan",
                "type": "file",
                "path": "materials/jati_diri/JADUAL TUGASAN.pdf",
            },
            {
                "label": "Example Proposal Social Experiment",
                "type": "file",
                "path": "materials/jati_diri/PROPOSAL_EKSPERIMENT.pdf",
            },
            {
                "label": "Rubrik Permakahan",
                "type": "file",
                "path": "materials/jati_diri/RUBRIK PEMARKAHAN DAN PENTAKSIRAN.pdf",
            },
        ],
        "assignments": {
            "type": "text",
            "content": "No assignments added yet.",
        },
    },
}
