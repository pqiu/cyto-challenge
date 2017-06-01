"""Check pull requests and score submitted answers."""
import json
import os
from glob import iglob

from pr_validation import validate
from solution_checker import score

SOLUTIONS = {
    '2': ['solutions/challenge2/major13_test_obfuscated.csv'],
    '3': ['solutions/challenge3/rare_events_test_obfuscated.csv'],
    '4': [
        'solutions/challenge4/class_disc_test_obfuscated.csv',
        'solutions/challenge4/rare_events_class_disc_test_obfuscated.csv'],
    'bonus': [
        'solutions/bonus/major13_test_ccv_obfuscated.csv',
        'solutions/bonus/rare_events_test_ccv_obfuscated.csv'],
    'test': ['solutions/test/toy_events_solution.csv']
}

RECALL = 'recall'
PRECISION = 'precision'
F1_SCORE = 'f1_score'
SCORE_FILE = 'scores.json'


def check(commit_range=None, branch_slug=None):
    """Perform checks."""
    env = os.environ.copy()
    if commit_range is None:
        commit_range = env.get('TRAVIS_COMMIT_RANGE')
    if commit_range is None:
        commit_range = 'master..HEAD'
    if branch_slug is None:
        branch_slug = env.get('TRAVIS_PULL_REQUEST_SLUG')
    if branch_slug:
        validate(commit_range, branch_slug, SOLUTIONS.keys())
    else:
        check_scores()


def check_scores():
    """Check scores."""
    with open(SCORE_FILE, 'r+') as score_file:
        scores = json.load(score_file)
        for submitted in iglob('./submissions/*/*.csv'):
            base, _ = os.path.splitext(submitted)
            _, team_challenge = os.path.split(base)
            parts = team_challenge.split('_')
            challenge = str(parts[-1])
            team = str(parts[0:-2])
            solutions = SOLUTIONS[challenge]
            for sol_path in solutions:
                fin_r_score, fin_p_score, fin_f_score = score(
                    submitted, sol_path)
                # FIXME: Handle cases of more than one solution per challenge
                scores.update({team: {challenge: {
                    RECALL: fin_r_score, PRECISION: fin_p_score,
                    F1_SCORE: fin_f_score}}})


def main():
    """Run main."""
    check()


if __name__ == '__main__':
    main()
