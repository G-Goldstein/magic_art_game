import unittest

class name_matcher_test(unittest.TestCase):
	def setUp(self):
		pass

	def run_tests(self, target_word, valid_alternatives, invalid_alternatives):
		self.assertTrue(match_is_close_enough(target_word, target_word), "{!s} did not match itself".format(target_word))
		for valid_word in valid_alternatives:
			self.assertTrue(match_is_close_enough(target_word, valid_word), "{!s} did not match {!s}".format(valid_word, target_word))
			#self.assertTrue(match_is_close_enough(valid_word, target_word), "{!s} did not match {!s}".format(valid_word, target_word))
		for invalid_word in invalid_alternatives:
			self.assertFalse(match_is_close_enough(target_word, invalid_word), "{!s} matched {!s}".format(invalid_word, target_word))
			#self.assertFalse(match_is_close_enough(invalid_word, target_word), "{!s} matched {!s}".format(invalid_word, target_word))

	def test_convert_to_uppercase_consonants(self):
		self.assertEqual(convert_to_uppercase_consonants('Hello'), 'HLL')
		self.assertEqual(convert_to_uppercase_consonants('What on earth'), 'WHTNRTH')

	def test_serra_angel_variations(self):
		target_word = 'Serra Angel'
		valid_alternatives = [
			'Serra_Angel',
			'serra angle',
			'Sarah Angel',
			'Sirrah Angel',
			'Sorry Angel',
			'Serra Angels',
			'SERRA ANGEL',
			'Serra Angel?!?!?11!',
			'Serra Agnel',
			'Serrra Angel',
			'XSerra Angel',
			'Sera Angel'
		]
		invalid_alternatives = [
			'Hamletback Goliath',
			'All is Dust',
			'Scary Angel',
			'Angel',
			'Serra',
			'Serrra Agnel',
			'Ressa Angel',
			'Lerra Anges'
		]
		self.run_tests(target_word, valid_alternatives, invalid_alternatives)

letters = 'BCDFGHJKLMNPQRSTVWXYZ'

def convert_to_uppercase_consonants(string):
	result_builder = ''
	for c in string.upper():
		if c in letters:
			result_builder += c
	return result_builder

def match_is_close_enough(target, guess):
	def same_length_with_no_more_than_one_difference(stringA, stringB):
		if len(stringA) == len(stringB):
			differences = 0
			for i in range(len(stringA)):
				if guess_consonants[i] != stringB[i]:
					differences += 1
			return (differences <= 1)
		return False

	def same_length_with_two_characters_transposed(stringA, stringB):
		if len(stringA) == len(stringB):
			difference_positions = []
			for i in range(len(stringA)):
				if guess_consonants[i] != stringB[i]:
					difference_positions.append(i)
			return (len(difference_positions) == 2 and
				abs(difference_positions[0] - difference_positions[1]) == 1 and
				stringA[difference_positions[0]] == stringB[difference_positions[1]] and
				stringA[difference_positions[1]] == stringB[difference_positions[0]])
		return False

	def lengths_differ_by_one_but_other_characters_match(stringA, stringB):
		def true_and_first_string_is_the_longer(stringA, stringB):
			differences = 0
			if len(stringA) - 1 == len(stringB):
				for i in range(len(stringB)):
					if stringA[i + differences] != stringB[i]:
						differences += 1
						i -= 1
					if differences > 1:
						return False
				return True
			return False

		return (true_and_first_string_is_the_longer(stringA, stringB) or
			true_and_first_string_is_the_longer(stringB, stringA))

	guess_consonants = convert_to_uppercase_consonants(guess)
	target_consonants = convert_to_uppercase_consonants(target)

	if (same_length_with_no_more_than_one_difference(guess_consonants, target_consonants) or
			same_length_with_two_characters_transposed(guess_consonants, target_consonants) or
			lengths_differ_by_one_but_other_characters_match(guess_consonants, target_consonants)):
		return True
	else:
		return False


if __name__ == '__main__':
	unittest.main()