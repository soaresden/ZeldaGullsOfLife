"""Change les options de Gulls of Life dans une ROM déjà compilée, sans recompiler.

Les options sont des octets de la banque 0, juste après la signature « GULLSOPT » ($3fe0, voir
oracles-disasm/code/ages/balladeOptions.s) ; 0 = comme d'habitude.

Usage :
  python tools/options.py ROM                          affiche les options
  python tools/options.py ROM hud=bas [SORTIE]         barre d'état en bas (hud=haut : en haut)

Sans SORTIE, la ROM est modifiée sur place. Le patch BPS se fait ensuite comme d'habitude
(tools/make_patch.py), à partir de la ROM obtenue.
"""
import sys

SIGNATURE = b'GULLSOPT'
OPTIONS = {
    # nom : (écart depuis la signature, {valeur écrite : octet})
    'hud': (0x10, {'haut': 0, 'bas': 1}),
}


def find_table(rom):
    at = rom.find(SIGNATURE, 0, 0x4000)
    if at < 0:
        sys.exit('Pas de table d\'options (signature GULLSOPT) : ROM trop ancienne ?')
    return at


def fix_global_checksum(rom):
    total = (sum(rom) - rom[0x14e] - rom[0x14f]) & 0xffff
    rom[0x14e] = total >> 8
    rom[0x14f] = total & 0xff


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    rom = bytearray(open(path, 'rb').read())
    table = find_table(rom)
    changes = [a for a in sys.argv[2:] if '=' in a]
    others = [a for a in sys.argv[2:] if '=' not in a]
    out = others[0] if others else path
    for change in changes:
        name, value = change.split('=', 1)
        if name not in OPTIONS or value not in OPTIONS[name][1]:
            sys.exit('Option inconnue : %s (possibles : %s)' % (change, ', '.join(
                '%s=%s' % (n, v) for n, (_, vals) in OPTIONS.items() for v in vals)))
        offset, values = OPTIONS[name]
        rom[table + offset] = values[value]
    for name, (offset, values) in OPTIONS.items():
        byte = rom[table + offset]
        shown = [v for v, b in values.items() if b == byte]
        print('%s=%s' % (name, shown[0] if shown else '$%02x' % byte))
    if changes:
        fix_global_checksum(rom)
        open(out, 'wb').write(rom)
        print('->', out)


main()
