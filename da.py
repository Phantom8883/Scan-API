rfbw = read_file_by_words("file.txt")
print(next(rfbw)) # получаем одно слово
print(rfbw.send(5)) # получаем 5 слов
for word in rfbw:
    print(word)




def iter_words(file_path: str, chunk_size: int = 1024):
    if chunk_size > 1024:
        raise ValueError("chunk_size не может быть больше 1024")

    buffer = ""

    with open(file_path, "r", encoding="utf-8") as file:
        while True:
            chunk = file.read(chunk_size)

            if not chunk:
                break

            buffer += chunk

            parts = buffer.split()

            if buffer[-1].isspace():
                buffer = ""
            else:
                buffer = parts.pop()

            for word in parts:
                yield word

        if buffer:
            yield buffer


