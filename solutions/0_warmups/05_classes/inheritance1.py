"""Solution: inheritance1 — super(), abstract base classes

Why: An overridden `__init__` replaces the parent's; call
`super().__init__(...)` to run it. `ABC` + `@abstractmethod` makes
instantiating the base class an error. `super().speak()` reuses the parent's
behaviour instead of copying it.
"""
import unittest
from abc import ABC, abstractmethod
from unittest import mock

# ---------------------------------------------------------------------------
# Reference solution
# ---------------------------------------------------------------------------


class Animal(ABC):
    """Base class. It must be abstract: Animal("x") raises TypeError.
    Subclasses must implement speak()."""

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def speak(self): ...

    def describe(self):
        return f"{self.name} says {self.speak()}"


class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # without this, self.name is never set
        self.breed = breed

    def speak(self):
        return "woof"


class Puppy(Dog):
    """Speaks like a Dog with "yip! " in front ("yip! woof"). Reuse Dog.speak()."""

    def speak(self):
        return "yip! " + super().speak()


# ---------------------------------------------------------------------------
# Tests: don't change anything below this line.
# ---------------------------------------------------------------------------


class Test(unittest.TestCase):
    def test_animal_is_abstract(self):
        with self.assertRaises(TypeError):
            Animal("generic")

    def test_dog(self):
        dog = Dog("rex", "lab")
        self.assertEqual(dog.breed, "lab")
        self.assertEqual(dog.describe(), "rex says woof")

    def test_puppy_reuses_dog_speak(self):
        self.assertEqual(Puppy("bit", "pug").speak(), "yip! woof")
        with mock.patch.object(Dog, "speak", return_value="WOOF"):
            self.assertEqual(Puppy("bit", "pug").speak(), "yip! WOOF")


if __name__ == "__main__":
    unittest.main()
