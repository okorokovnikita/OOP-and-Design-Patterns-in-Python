from abc import ABC, abstractmethod

class ObservableEngine(Engine):
    def __init__(self):
        # Вызываем конструктор родительского класса Engine
        super().__init__()
        self._observers = []  # Список подписчиков
    
    def subscribe(self, observer):
        # Подписываем наблюдателя, если его еще нет в списке
        if observer not in self._observers:
            self._observers.append(observer)
    
    def unsubscribe(self, observer):
        # Отписываем наблюдателя
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, achievement):
        # Уведомляем всех подписанных наблюдателей о новом достижении
        for observer in self._observers:
            observer.update(achievement)


class AbstractObserver(ABC):
    @abstractmethod
    def update(self, achievement):
        # Абстрактный метод для обработки достижения
        pass


class ShortNotificationPrinter(AbstractObserver):
    def __init__(self):
        # Множество названий полученных достижений
        self.achievements = set()
    
    def update(self, achievement):
        # Добавляем название достижения в множество
        # Множество автоматически обеспечивает уникальность
        self.achievements.add(achievement["title"])


class FullNotificationPrinter(AbstractObserver):
    def __init__(self):
        # Список достижений в порядке их получения
        self.achievements = []
    
    def update(self, achievement):
        # Добавляем достижение в список, если его еще нет
        # Проверяем уникальность по названию (title)
        if not any(a["title"] == achievement["title"] for a in self.achievements):
            self.achievements.append(achievement)
