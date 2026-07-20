def validate_court_decision(text: str):
    """
    Memvalidasi apakah teks merupakan putusan pengadilan
    dan apakah berkaitan dengan perkara pencurian.
    """

    text_lower = text.lower()

    # ---------- Validasi Putusan ----------
    required = [
        "putusan",
        "mengadili",
    ]

    optional = [
        "pengadilan",
        "menimbang",
        "mengingat",
        "terdakwa",
    ]

    required_score = sum(word in text_lower for word in required)
    optional_score = sum(word in text_lower for word in optional)

    if required_score < 2 or optional_score < 2:
        return False, (
            "Dokumen yang diunggah tidak terdeteksi sebagai putusan pengadilan. "
            "Silakan unggah dokumen putusan dalam format PDF atau TXT."
        )

    # ---------- Validasi Kasus Pencurian ----------
    theft_keywords = [
        "pasal 362",
        "pasal 363",
        "pasal 364",
        "pasal 365",
        "pencurian",
    ]

    if not any(word in text_lower for word in theft_keywords):
        return False, (
            "Dokumen berhasil dikenali sebagai putusan pengadilan, "
            "namun bukan merupakan perkara tindak pidana pencurian."
        )

    return True, ""