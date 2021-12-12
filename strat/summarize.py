from interface import printing
import dataconstants
from controllers.datactl import load_json_file
from interface.logger import log
from strat.team import Team


# Get the data string to return from the list of teams
def strategy(alliances, dataconsts: dataconstants.DataConstants, side=None):
    if type(alliances) != dict:
        alliances = {"red": alliances[:3], "blue": alliances[3:]}
    if not side:
        side = "blue" if dataconsts.team in alliances["blue"] else "red"

    teams_joined = alliances[side] + alliances["blue" if side == "red" else "red"]

    log("datactl.getdata", "Strategy data request for " + ", ".join(teams_joined))

    opp_mask = slice(len(alliances[side]), None, None)
    teams = _maketeams(teams_joined, dataconsts, opp_mask)

    d = list(map(lambda t: t.summary(), teams))
    log("datactl.getdata", "/".join(d))
    return (
        teams[0].get_header()
        + "\n"
        + "\n".join(d[:3])
        + "\n---\n"
        + teams[3].get_header()
        + "\n"
        + "\n".join(d[3:])
        + "\n===\n"
        + "\n".join([t.get_team() + ": " + t.get_comments() for t in teams])
    )


def _maketeams(team_numbers, dataconsts: dataconstants.DataConstants, opponent_mask=slice(0, 0, None)):
    data = load_json_file(dataconsts)

    teams = [Team(t, dataconsts) for i, t in enumerate(team_numbers)]
    list(map(lambda t: t.set_partner(False), teams[opponent_mask]))

    for device in data.values():
        for match in device.values():
            m = match[max(match.keys(), key=int)]
            t = m[dataconstants.Fields.TEAM]
            if t in team_numbers:
                try:
                    teams[team_numbers.index(t)].add_match(m)
                except IndexError as e:
                    printing.printf(
                        "Incomplete match in data: ",
                        style=printing.ERROR,
                        log=True,
                        logtag="Team.addline.error",
                    )
                    printing.printf(
                        m, style=printing.YELLOW, log=True, logtag="Team.addline.error"
                    )
                    log("Team.addline.error", str(e))
                except Exception as e:
                    printing.printf(
                        "Unknown error in strategy request: ",
                        style=printing.ERROR,
                        log=True,
                        logtag="Team.addline.error",
                    )
                    printing.printf(
                        str(e),
                        style=printing.ERROR,
                        log=True,
                        logtag="Team.addline.error",
                    )
                    printing.printf(
                        "For match: " + str(m),
                        style=printing.YELLOW,
                        log=True,
                        logtag="Team.addline.error",
                    )
    return teams


def detailed_summary(team_numbers, dataconsts: dataconstants.DataConstants):
    teams = _maketeams(team_numbers, dataconsts)
    return [team.summary(form=Team.Forms.DETAIL) for team in teams]


def quick_summary(team_numbers, dataconsts: dataconstants.DataConstants):
    teams = _maketeams(team_numbers, dataconsts)
    return [team.summary(form=Team.Forms.QUICK) for team in teams]
