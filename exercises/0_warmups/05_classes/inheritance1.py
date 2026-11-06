"""Warm-up inheritance1: super(), abstract base classes

Make Animal abstract, fix Dog's __init__, and make Puppy reuse Dog.speak().

Run:   python3 -m pylings
Or:    python3 exercises/0_warmups/05_classes/inheritance1.py
"""
import unittest
from abc import ABC, abstractmethod
from unittest import mock

# ---------------------------------------------------------------------------
# Your code: make the tests below pass.
# ---------------------------------------------------------------------------


class Animal:
    """Base class. It must be abstract: Animal("x") raises TypeError.
    Subclasses must implement speak()."""

    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

    def describe(self):
        return f"{self.name} says {self.speak()}"


class Dog(Animal):
    def __init__(self, name, breed):
        self.breed = breed

    def speak(self):
        return "woof"


class Puppy(Dog):
    """Speaks like a Dog with "yip! " in front ("yip! woof"). Reuse Dog.speak()."""

    def speak(self):
        return "yip! woof"


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
