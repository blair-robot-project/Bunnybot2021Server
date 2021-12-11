from enum import Enum

from dataconstants import Fields


# Stores and calculates data about a team, and outputs it in the format of the match strategy sheets
class Team:
    partner = True
    ally_header = "team: cross | shots | taken(M/A) |#|  low(M/A) |   high(I/M/A)  |.| spin |#| climb | time |##| hitpart|level|dead(b:h:d)|def(p:a)"
    ally_form = "{team:>4s}:  {auto_move:3d}% |   {auto_target:2s}  | {auto_m:4.1f}/{auto_a:4.1f}  |#| {low_m:4.1f}/{low_a:4.1f} | {high_i:4.1f}/{high_m:4.1f}/{high_a:4.1f} |.|  {spinner:1s}   |#| {climb_success:2d}/{climb_attempts:2d} |  {climb_time:2.0f}  |##|  {hit_partner:3d}%  | {level:3d}%|   {dead_b:1d}:{dead_hd:1d}:{dead_d:1d}   |  {defense_p:1d}:{defense_a:1d}"

    opp_header = (
        "team:  auto |.| spin |  low(M/A) |   high(I/M/A)  |.| climb |##| defense(p:a)"
    )
    opp_form = "{team:>4s}:  {auto_pts:4.1f} |.|   {spinner:1s}  | {low_m:4.1f}/{low_a:4.1f} | {high_i:4.1f}/{high_m:4.1f}/{high_a:4.1f} |.| {climb_success:2d}/{climb_attempts:2d} |##| {defense_p:1d}:{defense_a:1d}"

    quick_form = (
        "\033[7m\033[95m{team:4s}\033[0m SS:{autoh:3d}:{autoc:3d} H:{allhatch:4.1f} C:{allcargo:4.1f} "
        "HI:{height:2s} EG:{success2:3d}:{success3:3d}"
    )

    detail_form = "\033[7m\033[95m{team:4s}\033[0m\n"

    NO_DATA = "No data avalible"

    class Forms(Enum):
        STRAT = "strat"
        QUICK = "quick"
        DETAIL = "detail"

    def __init__(self, team, partner=True):
        self.total = 0

        self.team = team
        (
            self.auto_move,
            self.hit_partner,
            self.auto_intake,
            self.auto_low,
            self.auto_high,
            self.auto_center,
            self.auto_miss,
        ) = (0, 0, 0, 0, 0, 0, 0)
        self.low, self.high, self.center, self.miss = 0, 0, 0, 0
        self.spinner2, self.spinner3 = False, False
        self.climb_attempts, self.climb_success = 0, 0
        self.climb_time = []
        self.level = []
        self.dead = []
        self.defense = []
        self.comments = []

        self.set_partner(partner)

    def set_partner(self, partner):
        self.partner = partner
        if partner:
            self.strat_header, self.strat_form = self.ally_header, self.ally_form
        else:
            self.strat_header, self.strat_form = self.opp_header, self.opp_form

    def get_team(self):
        return self.team

    def get_header(self):
        return self.strat_header

    def get_comments(self):
        return "\n\t".join(self.comments)

    def add_match(self, match):
        self.total += 1

        self.auto_move += match[Fields.AUTO_MOVE]
        self.hit_partner += match[Fields.HIT_PARTNER]
        self.auto_intake += match[Fields.AUTO_INTAKE]
        self.auto_low += match[Fields.AUTO_LOW]
        self.auto_high += match[Fields.AUTO_HIGH]
        self.auto_center += match[Fields.AUTO_CENTER]
        self.auto_miss += match[Fields.AUTO_MISS]

        self.low += match[Fields.LOW]
        self.high += match[Fields.HIGH]
        self.center += match[Fields.CENTER]
        self.miss += match[Fields.MISS]
        self.spinner2 = self.spinner2 or match[Fields.SPINNER_ROT]
        self.spinner3 = self.spinner3 or match[Fields.SPINNER_POS]

        self.climb_attempts += match[Fields.ATTEMPTED_CLIMB] in (1, 2)
        if match[Fields.SOLO_CLIMB_NYF] == 1 or match[Fields.DOUBLE_CLIMB_NYF] == 1:
            self.climb_success += 1
            self.climb_time.append(match[Fields.CLIMB_TIME])
            # self.level.append(match[Fields.LEVEL])

        self.dead.append(match[Fields.DEAD])
        self.defense.append(match[Fields.DEFENSE])

        comment = match[Fields.COMMENTS]
        if comment:
            self.comments.append(comment)

    def calc_values(self):
        return {
            "team": self.team,
            "auto_move": percent(self.avg(self.auto_move)),
            "hit_partner": percent(self.avg(self.auto_move)),
            "auto_intake": percent(self.avg(self.auto_intake)),
            "auto_target": "LH"
            if self.auto_low and (self.auto_high or self.auto_center)
            else "L"
            if self.auto_low
            else "H"
            if self.auto_high or self.auto_center
            else "-",
            "auto_m": self.avg(self.auto_low + self.auto_high + self.auto_center),
            "auto_a": self.avg(
                self.auto_low + self.auto_high + self.auto_center + self.auto_miss
            ),
            "auto_pts": self.avg(
                5 * self.auto_move
                + 2 * self.auto_low
                + 4 * self.auto_high
                + 6 * self.auto_center
            ),
            "low_m": self.avg(self.auto_low),
            "low_a": self.avg(
                self.auto_low
                + (self.miss if self.low and not (self.high or self.center) else 0)
            ),
            "high_i": self.avg(self.center),
            "high_m": self.avg(self.high + self.center),
            "high_a": self.avg(
                self.high
                + self.center
                + (self.miss if self.high or self.center or not self.low else 0)
            ),
            "spinner": "y" if self.spinner2 or self.spinner3 else "n",
            "climb_attempts": self.climb_attempts,
            "climb_success": self.climb_success,
            "climb_time": self.avg(self.climb_time),
            "level": percent(self.avg(self.level)),
            "dead_b": self.dead.count(1),
            "dead_hd": self.dead.count(2),
            "dead_d": self.dead.count(3),
            "defense_p": self.defense.count(1),
            "defense_a": self.defense.count(2),
        }

    def summary(self, form=Forms.STRAT):
        forms = {
            Team.Forms.STRAT: self.strat_form,
            Team.Forms.QUICK: self.quick_form,
            Team.Forms.DETAIL: self.detail_form,
        }
        if self.total > 0:
            return forms[form].format(**self.calc_values())
        return "{0:>4s}: ".format(self.team) + self.NO_DATA

    def avg(self, x, perc=False, itint=True):
        if type(x) in (int, float):
            # Sum average
            r = 0 if not self.total else x / self.total
        else:
            # Iterable average
            r = sum(x) / (1 if len(x) == 0 else len(x))
            if itint:
                r = int(r)
        return r if not perc else percent(r)


def percent(n):
    return int(n * 100)
