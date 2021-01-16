import os
import sys
import berserk
from github import Github, InputFileContent, Gist

SEPARATOR = "."


PADDING = {"puzzle": 0, "crazyhouse": 0, "chess960": 0,
           "kingOfTheHill": 0, "threeCheck": 2, "antichess": 0, "atomic": 0, "horde": 0, "racingKings": 0,
           "ultraBullet": 0, "blitz": 1, "classical": 1, "rapid": 0, "bullet": 0, "correspondence": 3}

emojis = {"puzzle": "🧩", "crazyhouse": "🤪", "chess960": "9️⃣6️⃣0️⃣",
          "kingOfTheHill": "👑", "threeCheck": "3️⃣", "antichess": "", "atomic": "⚛", "horde": "🐎", "racingKings": "🏁",
          "ultraBullet": "🚅", "blitz": "⚡", "classical": "🏛", "rapid": "⏰", "bullet": "🚂", "correspondence": "🤼‍♂️"}

ENV_VAR_GIST_ID = "GIST_ID"
ENV_VAR_GITHUB_TOKEN = "GH_TOKEN"
ENV_VAR_LICHESS_USERNAME = "LICHESS_USERNAME"
REQUIRED_ENVS = [
    ENV_VAR_GIST_ID,
    ENV_VAR_GITHUB_TOKEN,
    ENV_VAR_LICHESS_USERNAME
]


def check_vars() -> bool:
    env_vars_absent = [
        env
        for env in REQUIRED_ENVS
        if env not in os.environ or len(os.environ[env]) == 0
    ]
    if env_vars_absent:
        print(
            f"Please define {env_vars_absent} in your github secrets. Aborting...")
        return False

    return True


def init() -> tuple:
    gh_gist = Github(ENV_VAR_GITHUB_TOKEN).get_gist(ENV_VAR_GIST_ID)
    lichess_acc = berserk.Client().users.get_public_data(ENV_VAR_LICHESS_USERNAME)
    return (gh_gist, lichess_acc)


def get_rating(acc: dict) -> list:
    ratings = []
    for key in acc['perfs'].keys():
        prov = '?'
        try:
            acc['perfs'][key]['prov']
        except KeyError:
            prov = ""
        ratings.append((key, acc['perfs'][key]['rating'],
                        prov, acc['perfs'][key]['games']))

    ratings.sort(key=lambda k: k[1], reverse=True)
    return ratings


def fromated_line(variant: str, games: str, rating_prov: str, max_line_length: int) -> str:
    separation = max_line_length - (
        len(variant) + len(games) + len(rating_prov) + 4  # emojis and brackets
    )
    separator = f" {SEPARATOR * separation} "
    return variant + f"({games})" + separator + rating_prov


def update_gist(gist: Gist, text: str) -> bool:
    gist.edit(description="", files={list(gist.files.keys())[0]:
                                     InputFileContent(content=text)})


def main():
    if not check_vars():
        return

    global ENV_VAR_GIST_ID, ENV_VAR_GITHUB_TOKEN, ENV_VAR_LICHESS_USERNAME
    ENV_VAR_GIST_ID = os.environ[ENV_VAR_GIST_ID]
    ENV_VAR_GITHUB_TOKEN = os.environ[ENV_VAR_GITHUB_TOKEN]
    ENV_VAR_LICHESS_USERNAME = os.environ[ENV_VAR_LICHESS_USERNAME]

    gist, lichess_acc = init()
    rating = get_rating(lichess_acc)
    content = [fromated_line((emojis[line[0]] + line[0]), str(line[3]),
                             str(line[1]) + line[2] + " 📈", 52 + PADDING[line[0]]) for line in rating]

    print("\n".join(content))

    update_gist(gist, "\n".join(content))


if __name__ == "__main__":

    # test with python lichess-gist.py test <gist> <github-token> <user>
    if len(sys.argv) > 1:
        os.environ[ENV_VAR_GIST_ID] =  sys.argv[2]
        os.environ[ENV_VAR_GITHUB_TOKEN] = sys.argv[3]
        os.environ[ENV_VAR_LICHESS_USERNAME] = sys.argv[4]
    main()

