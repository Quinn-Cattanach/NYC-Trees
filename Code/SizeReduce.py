import re
def patchFilename(
    filename: str,
    expectedExtension: str
):
    pattern = r"[a-zA-Z\_\(\)0-9]+\." + expectedExtension

    if not re.fullmatch(pattern, filename):
        filename = re.sub(
            r"\s",
            "_",
            filename
        )
        filename = re.sub(
            r"\W",
            "?",
            filename
        )
        filename = re.sub(
            r"\.",
            ":",
            filename
        )
        filename += "." + expectedExtension
    
    return filename

print(patchFilename(" scbjhksb dbhjbs jkchbasd clisudbvk.flop", "csv"))

print(patchFilename("abc123.csv", "csv"))
