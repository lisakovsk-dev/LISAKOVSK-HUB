import qanot

print("Доступные атрибуты в пакете qanot:")
for attr in dir(qanot):
    if not attr.startswith("_"):
        print(f"- {attr}")