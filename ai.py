import re

from faster_whisper import WhisperModel


print()
print("=" * 55)
print("Loading Faster-Whisper...")
print("=" * 55)

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Faster-Whisper loaded successfully!")
print("=" * 55)


def transcribe_audio(filepath):

    print("Starting transcription...")

    segments, info = model.transcribe(
        filepath,
        beam_size=5,
        vad_filter=True,
        vad_parameters={
            "min_silence_duration_ms": 500
        },
        condition_on_previous_text=False
    )

    transcript_parts = []

    for segment in segments:
        text = segment.text.strip()

        if text:
            transcript_parts.append(text)

    transcript = " ".join(transcript_parts)

    print("Transcription finished.")
    print("Detected language:", info.language)

    return transcript


def split_sentences(text):

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def normalize_text(text):

    return re.sub(
        r"\s+",
        " ",
        text.lower().strip()
    )


def is_negative_sentence(text):

    lower = normalize_text(text)

    negative_words = [
        "not",
        "never",
        "won't",
        "wouldn't",
        "can't",
        "cannot",
        "couldn't",
        "shouldn't",
        "don't",
        "doesn't",
        "didn't",
        "wasn't",
        "weren't",
        "isn't"
    ]

    for word in negative_words:

        if re.search(
            r"\b" + re.escape(word) + r"\b",
            lower
        ):
            return True

    return False


def contains_action(text):

    lower = normalize_text(text)

    action_words = [
        "send",
        "submit",
        "complete",
        "finish",
        "call",
        "email",
        "upload",
        "prepare",
        "bring",
        "buy",
        "book",
        "check",
        "review",
        "create",
        "make",
        "write",
        "share",
        "download",
        "install",
        "pay",
        "attend",
        "join",
        "register",
        "apply",
        "get"
    ]

    for word in action_words:

        if re.search(
            r"\b" + re.escape(word) + r"\b",
            lower
        ):
            return True

    return False


def has_task_intent(text):

    lower = normalize_text(text)

    task_phrases = [
        "i need to",
        "i have to",
        "i must",
        "i should",
        "please",
        "can you",
        "could you",
        "you need to",
        "you have to",
        "don't forget to",
        "remember to",
        "make sure to"
    ]

    for phrase in task_phrases:

        if phrase in lower:
            return True

    return False


def create_summary(text):

    sentences = split_sentences(text)

    if not sentences:
        return "No speech was detected in the audio."

    if len(sentences) == 1:
        return sentences[0]

    important_sentences = []

    for sentence in sentences:

        if has_task_intent(sentence):
            important_sentences.append(sentence)

        elif contains_action(sentence):
            important_sentences.append(sentence)

    if important_sentences:
        return " ".join(
            important_sentences[:2]
        )

    return " ".join(
        sentences[:2]
    )


def extract_key_information(text):

    sentences = split_sentences(text)

    key_information = []

    patterns = {

        "Meeting": [
            r"\bmeeting\b",
            r"\bmeet\b"
        ],

        "Deadline": [
            r"\bdeadline\b",
            r"\bdue\b"
        ],

        "Time": [
            r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b",
            r"\b\d{1,2}\s*(?:am|pm)\b",
            r"\bat\s+\d{1,2}\b",
            r"\bnoon\b",
            r"\bmidnight\b"
        ],

        "Date": [
            r"\btoday\b",
            r"\btomorrow\b",
            r"\byesterday\b",
            r"\bmonday\b",
            r"\btuesday\b",
            r"\bwednesday\b",
            r"\bthursday\b",
            r"\bfriday\b",
            r"\bsaturday\b",
            r"\bsunday\b"
        ],

        "Exam": [
            r"\bexam\b",
            r"\btest\b",
            r"\bquiz\b"
        ],

        "Interview": [
            r"\binterview\b"
        ],

        "Project": [
            r"\bproject\b"
        ],

        "Event": [
            r"\bevent\b",
            r"\bfunction\b",
            r"\bparty\b"
        ],

        "Appointment": [
            r"\bappointment\b",
            r"\bdoctor\b"
        ]
    }

    for sentence in sentences:

        lower_sentence = normalize_text(
            sentence
        )

        for label, regex_list in patterns.items():

            found = False

            for pattern in regex_list:

                if re.search(
                    pattern,
                    lower_sentence
                ):
                    found = True
                    break

            if found:

                exists = any(
                    item["value"] == sentence
                    for item in key_information
                )

                if not exists:

                    key_information.append({
                        "label": label,
                        "value": sentence
                    })

                break

    return key_information[:8]


def extract_deadline(text):

    lower = normalize_text(text)

    deadline_patterns = [

        r"\btoday\b",

        r"\btomorrow\b",

        r"\btonight\b",

        r"\bthis morning\b",

        r"\bthis afternoon\b",

        r"\bthis evening\b",

        r"\bbefore\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b",

        r"\bby\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b",

        r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b",

        r"\b\d{1,2}\s*(?:am|pm)\b",

        r"\bmonday\b",

        r"\btuesday\b",

        r"\bwednesday\b",

        r"\bthursday\b",

        r"\bfriday\b",

        r"\bsaturday\b",

        r"\bsunday\b"
    ]

    for pattern in deadline_patterns:

        match = re.search(
            pattern,
            lower
        )

        if match:
            return match.group(0)

    return "No deadline mentioned"


def clean_task_title(sentence):

    title = sentence.strip()

    prefixes = [
        "please ",
        "can you ",
        "could you ",
        "i need to ",
        "i have to ",
        "i must ",
        "i should ",
        "you need to ",
        "you have to ",
        "don't forget to ",
        "remember to ",
        "make sure to "
    ]

    lower_title = title.lower()

    for prefix in prefixes:

        if lower_title.startswith(prefix):

            title = title[
                len(prefix):
            ]

            break

    return title.strip()


def extract_tasks(text):

    sentences = split_sentences(text)

    tasks = []

    for sentence in sentences:

        lower = normalize_text(
            sentence
        )

        # Don't turn completed/negative statements into tasks.
        completed_phrases = [
            "i've done",
            "i have done",
            "i already did",
            "already completed",
            "already finished",
            "i finished",
            "i'm not doing",
            "i am not doing",
            "i'm not going to",
            "i am not going to"
        ]

        completed = False

        for phrase in completed_phrases:

            if phrase in lower:
                completed = True
                break

        if completed:
            continue

        if is_negative_sentence(sentence):
            continue

        explicit_task = has_task_intent(sentence)

        action = contains_action(sentence)

        if not explicit_task and not action:
            continue

        deadline = extract_deadline(
            sentence
        )

        title = clean_task_title(
            sentence
        )

        tasks.append({
            "title": title,
            "deadline": deadline,
            "source": sentence
        })

    return tasks[:10]


def process_audio(filepath):

    print()
    print("=" * 55)
    print("PROCESSING AUDIO")
    print("=" * 55)

    transcript = transcribe_audio(
        filepath
    )

    if not transcript.strip():

        return {
            "transcript": "",
            "summary": "No speech was detected.",
            "key_information": [],
            "tasks": []
        }

    summary = create_summary(
        transcript
    )

    key_information = extract_key_information(
        transcript
    )

    tasks = extract_tasks(
        transcript
    )

    result = {
        "transcript": transcript,
        "summary": summary,
        "key_information": key_information,
        "tasks": tasks
    }

    print()
    print("Processing completed!")
    print("Tasks found:", len(tasks))
    print("Key information found:", len(key_information))
    print("=" * 55)

    return result