from lattice_core import Lattice

lattice = Lattice()

print("Lattice CLI")
print("Commands:")
print("  signal <text>")
print("  vault_export")
print("  exit")

while True:
    cmd = input(">>> ")

    if cmd.startswith("signal "):
        signal = cmd.replace("signal ", "")
        result = lattice.process(signal)
        print(result)

    elif cmd == "vault_export":
        lattice.vault.export()
        print("Vault exported to vault.json")

    elif cmd == "exit":
        break

    else:
        print("Unknown command")