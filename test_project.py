import re
import pytest
from project import get_words
from project import give_hint
from project import select_n_words


def test_get_words():
	assert get_words('words/test_words_file.txt') == ['one', 'two', 'three']


def test_give_hint():
	assert give_hint('test', 1) == 't***'
	assert give_hint('I', 0) == '*'
	assert give_hint('who', 3) == 'who'
	assert give_hint('a fly', 1) == 'a ***'
	assert give_hint('cucumber', 2) == 'cu******'
	
	with pytest.raises(ValueError):
		hint = give_hint('word', -1)


def test_select_n_words():
	words = ['one', 'two', 'three', 'four', 'five']
	
	used_words = ['one', 'five']
	selected_n_words, exceeded = select_n_words(words, used_words, 3)
	assert set(selected_n_words) == set(['two', 'three', 'four'])
	assert exceeded == False
	
	used_words = ['one', 'two', 'three']
	selected_n_words, exceeded = select_n_words(words, used_words, 3)
	assert len(selected_n_words) == 3
	assert 'four' in selected_n_words
	assert 'five' in selected_n_words
	assert 'one' in selected_n_words or 'two' in selected_n_words or 'three' in selected_n_words
	assert exceeded == True
	
	used_words = []
	selected_n_words, exceeded = select_n_words(words, used_words, 5)
	assert set(selected_n_words) == set(words)
	assert exceeded == False
	
	used_words = words[:]
	selected_n_words, exceeded = select_n_words(words, used_words, 2)
	assert len(selected_n_words) == 2
	for word in selected_n_words:
		assert word in words
	assert exceeded == True
