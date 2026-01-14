import math
from abc import ABC, abstractmethod


class Base(ABC):
    def __init__(self, data, result):
        self.data = data
        self.result = result

    def get_answer(self):
        return [int(x >= 0.5) for x in self.data]

    @abstractmethod
    def get_loss(self):
        """Реализовать в конкретных классах."""
        pass

    def get_score(self):
        """По умолчанию - accuracy, можно переопределить."""
        ans = self.get_answer()
        return sum(int(x == y) for x, y in zip(ans, self.result)) / len(ans)


class A(Base):
    def get_loss(self):
        # MSE loss
        return sum((x - y) ** 2 for x, y in zip(self.data, self.result))


class B(Base):
    def get_loss(self):
        # Log loss
        return -sum(
            y * math.log(x) + (1 - y) * math.log(1 - x)
            for x, y in zip(self.data, self.result)
        )

    def get_pre(self):
        ans = self.get_answer()
        true_positives = sum(int(x == 1 and y == 1) for x, y in zip(ans, self.result))
        predicted_positives = sum(ans)
        return true_positives / predicted_positives if predicted_positives else 0.0

    def get_rec(self):
        ans = self.get_answer()
        true_positives = sum(int(x == 1 and y == 1) for x, y in zip(ans, self.result))
        actual_positives = sum(self.result)
        return true_positives / actual_positives if actual_positives else 0.0

    def get_score(self):
        pre = self.get_pre()
        rec = self.get_rec()
        if pre + rec == 0:
            return 0.0
        return 2 * pre * rec / (pre + rec)


class C(Base):
    def get_loss(self):
        # MAE loss
        return sum(abs(x - y) for x, y in zip(self.data, self.result))
