from ooppai import Calc, Mod
import sys

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " file.osu")
    exit()

beatmap_path = sys.argv[1]

# ----------------------------
print("\n\nTEST 1 - SIMPLE")

calc = Calc(beatmap_path, disable_cache=True)
diff = calc.calc_diff()
pp = calc.calc_pp()

print("{1.stars} stars\n{0.total} pp".format(pp, diff))

# ----------------------------
print("\n\nTEST 2 - OVERRIDE + MODS")

calc = Calc(beatmap_path, disable_cache=True)
calc.override_beatmap(cs=7, od=10, ar=10)   # override can also be specified as constructor arguments ie. Calc(cs=3, od=7, ar=8)
diff = calc.calc_diff(mods=Mod.HD+Mod.DT)   # can combine mods with + operator, or bitwise | operator
pp = calc.calc_pp()

print("{1.stars} stars\n{0.total} pp".format(pp, diff))

# ----------------------------
print("\n\nTEST 3 - COMBO/ACC")

calc = Calc(beatmap_path, disable_cache=True)
diff = calc.calc_diff(with_awkwardness=True)
# you can specify if you want values like rhythm awkwardness returned from with calc_diff(with_awkwardness=True). see calc_diff method for full list
pp = calc.calc_pp(combo=438, c300=306, c100=8, c50=0, misses=0)
# you can optionally specify acc by percent like so: calc_pp_acc(accuracy=96.5). however this can be less accurate. see issue in ooppai.py

print("{1.stars} stars\n{1.rhythm_awkwardness} rhythm awkwardness\n{0.total} pp".format(pp, diff))

