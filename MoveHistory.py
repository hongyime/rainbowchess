from copy import deepcopy


class MoveHistory:
    """A bounded stack whose snapshots own their mutable piece state."""

    def __init__(self, size: int):
        if type(size) is not int:
            raise TypeError('history size must be an integer')
        if size <= 0:
            raise ValueError('history size must be positive')
        self.size = size
        self.clear()

    def clear(self):
        self.data = [None] * self.size
        self.head = None
        self._count = 0

    def isempty(self) -> bool:
        return self._count == 0

    def push(self, move):
        snapshot = deepcopy(move)
        self.head = 0 if self.head is None else (self.head + 1) % self.size
        self.data[self.head] = snapshot
        self._count = min(self._count + 1, self.size)

    def pop(self):
        if self.isempty():
            return None
        move = self.data[self.head]
        self.data[self.head] = None
        self._count -= 1
        self.head = (self.head - 1) % self.size if self._count else None
        return move

# The circular storage retains at most `size` complete game snapshots for undo.
