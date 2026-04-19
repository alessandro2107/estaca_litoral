import hashlib

def sha256_3_passes(text):
    result = text.encode('utf-8')
    for i in range(3):
        result = hashlib.sha256(result).digest()
        result = result.hex().encode('utf-8')  # converte para hex string antes do proximo passe
    return result.decode('utf-8')

phrase = input("Digite uma frase: ")
print(sha256_3_passes(phrase))

