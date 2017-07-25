# OOppai is an object oriented wrapper for the pyoppai binding of oppai
# Created for ease of use and a more pythonic interface
# - Syrin

# Issues:
# 
# If map changing mods are passed to diff_calc, and then new
#   map changing mods are passed to diff_calc, then pp_calc
#   will return unexpected results.
#   This happens even when the map is reparsed so it appears
#   to be a problem rooten in the oppai context

import os
from collections import namedtuple
from enum import IntEnum

try:
    import pyoppai
except (ImportError, ModuleNotFoundError) as e:
    raise e("The pyoppai module could not be found")
    

BUFSIZE = 2000000   # BUFSIZE 2000000 is sometimes too small, but currently the
                    # osu site has a bug that truncates files to 1MB regardless,
                    # so this is a non issue at the moment

# Data containers

Beatmap = namedtuple("Diff", "cs od ar hp artist title version creator num_objects num_circles num_sliders num_spinners max_combo")
Diff = namedtuple("Diff", "stars aim_stars speed_stars rhythm_awkwardness num_aim_singles num_timing_singles num_threshold_singles")
Pp = namedtuple("PP", "total aim speed acc")

# Mods enum
class Mod(IntEnum):
    NOMOD = 0
    NF = 1
    EZ = 2
    HD = 8
    HR = 16
    DT = 64
    HT = 256
    NC = 512
    FL = 1024
    SO = 4096

# Exception for any errors resulting from pyoppai.err(context)
class OppaiError(Exception):
    pass

# Calculator class
class Calc:
    def __init__(self, beatmap_path, cs=None, od=None, ar=None, disable_cache=False):
        # Initalise context, buffer and parse beatmap
        self._context = pyoppai.new_ctx()
        self._beatmap = pyoppai.new_beatmap(self._context)
        self._buffer = pyoppai.new_buffer(BUFSIZE)

        self._mods = Mod.NOMOD
        self._disable_cache = disable_cache
        self._beatmap_path = beatmap_path
        self.__parse_beatmap(cs, od, ar)

        self.__check()

    def __check(self):
        # Check for error and raise
        err = pyoppai.err(self._context)

        if err:
            raise OppaiError(err)

    def __parse_beatmap(self, cs=None, od=None, ar=None):
        pyoppai.parse(self._beatmap_path, self._beatmap, self._buffer, BUFSIZE, self._disable_cache, os.path.dirname(os.path.realpath(__file__)))

        if cs:
            pyoppai.set_cs(self._beatmap, cs)
        if od:
            pyoppai.set_od(self._beatmap, od)
        if ar:
            pyoppai.set_ar(self._beatmap, ar)

        self._beatmap_data = Beatmap(
            *pyoppai.stats(self._beatmap),
            pyoppai.artist(self._beatmap),
            pyoppai.title(self._beatmap),
            pyoppai.version(self._beatmap),
            pyoppai.creator(self._beatmap),
            pyoppai.num_objects(self._beatmap),
            pyoppai.num_circles(self._beatmap),
            pyoppai.num_sliders(self._beatmap),
            pyoppai.num_spinners(self._beatmap),
            pyoppai.max_combo(self._beatmap)
        )

        self.__check()

    # Beatmap altering methods
    def override_beatmap(self, cs=None, od=None, ar=None):
        # Override beatmap cs/od/ar

        if cs:
            pyoppai.set_cs(self._beatmap, cs)
        if od:
            pyoppai.set_od(self._beatmap, od)
        if ar:
            pyoppai.set_ar(self._beatmap, ar)

        self._beatmap_data = Beatmap(cs, od, ar, *self._beatmap_data[3:])  # [3:] because we are redefining cs, od and ar

        self.__check()
        return self._beatmap_data

    # Diff calc
    def calc_diff(self, mods=Mod.NOMOD, with_awkwardness=False, with_aim_singles=False, with_timing_singles=False, with_threshold_singles=False, singletap_threshold=125):
        if not hasattr(self, "_diff_context"):
            self._diff_context = pyoppai.new_d_calc_ctx(self._context)

        if (mods & (Mod.EZ|Mod.HR|Mod.DT|Mod.HT) or mods == Mod.NOMOD) and self._mods & (Mod.EZ|Mod.HR|Mod.DT|Mod.HT):
            self.__parse_beatmap()
        pyoppai.apply_mods(self._beatmap, mods)
        self._mods = mods

        settings = (
            with_awkwardness,
            with_aim_singles,
            with_timing_singles,
            with_threshold_singles,
            singletap_threshold
        )

        diff_result = pyoppai.d_calc(self._diff_context, self._beatmap, *settings)
        self._diff = Diff(*diff_result)

        self.__check()
        return self._diff

    # PP Calc
    def calc_pp(self, combo=0xFFFF, c300=0xFFFF, c100=0, c50=0, misses=0, score_version=1):
        if not hasattr(self, "_diff"):
            self.calc_diff()

        pp_result = pyoppai.pp_calc(self._context, self._diff.aim_stars, self._diff.speed_stars, self._beatmap, self._mods, combo, misses, c300, c100, c50, score_version)
        self._pp = Pp(*pp_result[1:])   # [1:] because we dont need the acc_pct return value, as it is an input

        self.__check()
        return self._pp

    # PP Calc
    def calc_pp_acc(self, accuracy=100, combo=0xFFFF, misses=0, score_version=1):
        if not hasattr(self, "_diff"):
            self.calc_diff()

        pp_result = pyoppai.pp_calc_acc(self._context, self._diff.aim_stars, self._diff.speed_stars, self._beatmap, accuracy, self._mods, combo, misses, score_version)
        self._pp = Pp(*pp_result[1:])   # [1:] because we dont need the acc_pct return value, as it is an input

        self.__check()
        return self._pp

    def __str__(self):
        try:
            return "{0.artist} - {0.title} [{0.version}] ({0.creator})".format(self._beatmap_data)
        except:
            return "Empty Calc object"

