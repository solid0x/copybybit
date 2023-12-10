from django.core.cache import cache

from bybit.api import *
from bybit.utils import *
from time import sleep


class PositionDiff:

    def __init__(self):
        self.created: list[Position] = []
        self.edited: list[Position] = []
        self.closed: list[Position] = []


class FollowService:

    def __init__(self, duration: str = DURATION_7D):
        self.api = BybitAPI(use_testnet=False)
        self.duration = duration

        iteration = cache.get('iteration')
        self.iteration = iteration if iteration else 0

        followed_leaders = cache.get('followed_leaders')
        self.followed_leaders: list[str] = followed_leaders if followed_leaders else []

        leader_positions = cache.get('leader_positions')
        self.leader_positions: dict[str, dict[str, Position]] = leader_positions if leader_positions else {}

        followed_positions = cache.get('followed_positions')
        self.followed_positions: dict[str, dict[str, Position]] = followed_positions if followed_positions else {}

    def update_cache(self):
        cache.set('iteration', self.iteration, timeout=None)
        cache.set('followed_leaders', self.followed_leaders, timeout=None)
        cache.set('leader_positions', self.leader_positions, timeout=None)
        cache.set('followed_positions', self.followed_positions, timeout=None)

    def get_recent_positions(self) -> list[Position]:
        result: list[Position] = []
        for _, positions in self.followed_positions.items():
            for _, position in positions.items():
                if (datetime.now() - position.open_at).total_seconds() < 600:
                    result.append(position)
        return result

    @staticmethod
    def compare(old_positions: dict[str, Position], new_positions: dict[str, Position]):
        diff = PositionDiff()
        for new_pos_signature, new_pos in new_positions.items():
            if new_pos_signature not in old_positions:
                diff.created.append(new_pos)
        for old_pos_signature, old_pos in old_positions.items():
            if old_pos_signature not in new_positions:
                diff.closed.append(old_pos)
            else:
                if old_pos != new_positions[old_pos_signature]:
                    diff.edited.append(old_pos)

        return diff

    @staticmethod
    def matches_criteria(position: Position) -> bool:
        if not position.symbol.endswith('USDT'):
            return False

        return True

    def is_first_iteration(self) -> bool:
        return self.iteration == 1

    def load_leaders(self):
        old_followed_leaders = set(self.followed_leaders)
        removed_leaders = set()
        self.followed_leaders = []
        while not self.followed_leaders:
            try:
                leader_list = self.api.get_leader_list(duration=self.duration, count=100)
                new_followed_leaders = set(leader_list)
                removed_leaders = old_followed_leaders - new_followed_leaders
                self.followed_leaders = leader_list
            except Exception as e:
                logging.exception(f'Failed to load leaders: {e}')
                sleep(60)

        for removed_leader in removed_leaders:
            self.followed_positions.pop(removed_leader, None)
            self.leader_positions.pop(removed_leader, None)

    def update_followed_positions(self, leader_mark: str, diff: PositionDiff):
        if leader_mark not in self.followed_positions:
            self.followed_positions[leader_mark] = {}

        for closed_pos in diff.closed:
            if self.followed_positions[leader_mark].pop(signature(closed_pos), None):
                pass
                # remove closed_pos

        if not self.is_first_iteration():
            for new_pos in diff.created:
                if self.matches_criteria(new_pos):
                    self.followed_positions[leader_mark][signature(new_pos)] = new_pos
                    # add new_pos

    def leaders_of_followed_positions(self) -> list[str]:
        return [leader for leader, pos in self.followed_positions.items() if pos]

    def has_followed_positions(self) -> bool:
        return bool(self.leaders_of_followed_positions())

    def check_positions(self):
        self.load_leaders()

        self.iteration += 1
        print(self.iteration)

        for leader_mark in self.followed_leaders:
            leader_positions = self.api.get_leader_positions(leader_mark)
            leader_positions = {signature(p): p for p in leader_positions}
            if leader_mark in self.leader_positions:
                if leader_positions != self.leader_positions[leader_mark]:
                    diff = self.compare(self.leader_positions[leader_mark], leader_positions)
                    self.update_followed_positions(leader_mark, diff)
            self.leader_positions[leader_mark] = leader_positions
            sleep(0.05)

        self.update_cache()
