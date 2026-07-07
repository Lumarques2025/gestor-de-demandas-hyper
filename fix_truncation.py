import re

UPLOADS = '/sessions/eloquent-festive-archimedes/mnt/uploads/index.html'
OUTPUTS = '/sessions/eloquent-festive-archimedes/mnt/outputs/index.html'

with open(UPLOADS, 'r', encoding='utf-8') as f:
    orig = f.read()

with open(OUTPUTS, 'r', encoding='utf-8') as f:
    new_file = f.read()

# The new file ends mid-sentence in chatAnexar function
# Find the exact cutoff point
CUTOFF = "localStorage tem limite de ~5MB. Continuar?`)"
new_cut_pos = new_file.rfind(CUTOFF)
orig_cut_pos = orig.rfind(CUTOFF)

print(f"New file cut pos: {new_cut_pos}")
print(f"Orig cut pos: {orig_cut_pos}")
print(f"New file total: {len(new_file)}")
print(f"Orig file total: {len(orig)}")

# Get the tail from original file (everything after the cutoff point)
orig_tail = orig[orig_cut_pos + len(CUTOFF):]
print(f"Tail to append length: {len(orig_tail)}")
print(f"Tail first 200 chars: {repr(orig_tail[:200])}")
print(f"Tail last 200 chars: {repr(orig_tail[-200:])}")

# The new file needs:
# 1. Everything up to and including the cutoff marker
# 2. The tail from original
# 3. But we need to replace the OLD init section with our new one

# Find the old INIT in orig_tail
old_init = """/* ================================
   INIT
================================ */
autoAvancarProgramadas();
refreshCounts();
render('dashboard');
setTimeout(mostrarBoasVindas, 500);
</script>
</body>
</html>"""

new_init = """/* ================================
   INIT
   A inicializacao real acontece no fbAuth.onAuthStateChanged (acima).
   Aqui apenas garantimos que a tela de login apareca imediatamente
   enquanto o Firebase verifica a sessao.
================================ */
// Mostra tela de login por padrao (Firebase vai esconder se ja logado)
showLoginScreen();
</script>
</body>
</html>"""

if old_init in orig_tail:
    print("Found old INIT in tail - will replace")
    orig_tail = orig_tail.replace(old_init, new_init)
else:
    print("Old INIT NOT found in tail - checking...")
    # Check if it's in the tail at all
    idx = orig_tail.find('autoAvancarProgramadas();')
    print(f"autoAvancarProgramadas in tail at: {idx}")
    idx2 = orig_tail.find('render(\'dashboard\');')
    print(f"render dashboard in tail at: {idx2}")

# Build final file
final = new_file[:new_cut_pos + len(CUTOFF)] + orig_tail

print(f"\nFinal file size: {len(final)}")
print(f"Has </script> at end: {'</script>' in final[-100:]}")
print(f"Has </body> at end: {'</body>' in final[-50:]}")
print(f"Has </html> at end: {'</html>' in final[-20:]}")

with open(OUTPUTS, 'w', encoding='utf-8') as f:
    f.write(final)

print("File written successfully!")
