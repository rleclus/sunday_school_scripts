import tkinter as tk
import random

# Simple words for 6-year-olds
WORDS = [
	"cat", "dog", "sun", "moon", "star", "tree",
	"ball", "toy", "book", "car", "bike", "bird",
	"fish", "frog", "apple", "cake", "milk", "juice",
	"happy", "jump", "run", "play", "sing", "dance",
	"red", "blue", "green", "house", "door", "window",
	"mom", "dad", "love", "friend", "park", "school",
	"rain", "snow", "flower", "grass", "hand", "foot",
	"bear", "lion", "bunny", "duck", "horse", "pig"
]


class WordJumbleApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Word Jumble")

		# Make fullscreen
		self.root.attributes('-fullscreen', True)
		self.root.configure(bg='#2c3e50')

		# Create canvas
		self.canvas = tk.Canvas(root, bg='#2c3e50', highlightthickness=0)
		self.canvas.pack(fill=tk.BOTH, expand=True)

		# State variables
		self.current_words = []
		self.is_jumbled = False
		self.word_ids = []

		# Bind spacebar and escape
		self.root.bind('<space>', self.handle_space)
		self.root.bind('<Escape>', lambda e: self.root.destroy())

		# Initial display
		self.display_new_words()

	def get_random_words(self, count=12):
		"""Get random words from the dictionary"""
		return random.sample(WORDS, min(count, len(WORDS)))

	def jumble_word(self, word):
		"""Jumble the letters in a word"""
		if len(word) <= 1:
			return word
		letters = list(word)
		random.shuffle(letters)
		jumbled = ''.join(letters)
		# Make sure it's actually different
		if jumbled == word and len(word) > 1:
			return self.jumble_word(word)
		return jumbled

	def display_new_words(self):
		"""Display a new set of random words"""
		self.canvas.delete('all')
		self.word_ids = []
		self.current_words = self.get_random_words()
		self.is_jumbled = False

		# Get canvas dimensions
		width = self.canvas.winfo_width()
		height = self.canvas.winfo_height()

		if width <= 1:
			width = self.root.winfo_screenwidth()
		if height <= 1:
			height = self.root.winfo_screenheight()

		# Keep track of occupied areas
		occupied_rects = []

		# Display words in random positions without overlap
		for word in self.current_words:
			placed = False
			attempts = 0
			max_attempts = 100

			while not placed and attempts < max_attempts:
				x = random.randint(150, width - 150)
				y = random.randint(150, height - 150)

				# Create temporary text to get bounding box
				temp_id = self.canvas.create_text(
					x, y,
					text=word,
					font=('Helvetica', 96, 'bold'),
					fill='#ecf0f1'
				)

				# Get bounding box with padding
				bbox = self.canvas.bbox(temp_id)
				padding = 30
				new_rect = (
					bbox[0] - padding,
					bbox[1] - padding,
					bbox[2] + padding,
					bbox[3] + padding
				)

				# Check for overlap with existing words
				overlap = False
				for rect in occupied_rects:
					if not (new_rect[2] < rect[0] or  # new is left of existing
					        new_rect[0] > rect[2] or  # new is right of existing
					        new_rect[3] < rect[1] or  # new is above existing
					        new_rect[1] > rect[3]):  # new is below existing
						overlap = True
						break

				if not overlap:
					# Position is good, keep the text
					occupied_rects.append(new_rect)
					self.word_ids.append((temp_id, word))
					placed = True
				else:
					# Position overlaps, delete and try again
					self.canvas.delete(temp_id)

				attempts += 1

			# If we couldn't place the word after max attempts, place it anyway
			if not placed:
				text_id = self.canvas.create_text(
					x, y,
					text=word,
					font=('Helvetica', 96, 'bold'),
					fill='#ecf0f1'
				)
				self.word_ids.append((text_id, word))

	def jumble_current_words(self):
		"""Jumble the currently displayed words"""
		for text_id, original_word in self.word_ids:
			jumbled = self.jumble_word(original_word)
			self.canvas.itemconfig(text_id, text=jumbled)
		self.is_jumbled = True

	def handle_space(self, event):
		"""Handle spacebar press"""
		if self.is_jumbled:
			# If words are jumbled, show new words
			self.display_new_words()
		else:
			# If words are not jumbled, jumble them
			self.jumble_current_words()


if __name__ == '__main__':
	root = tk.Tk()
	app = WordJumbleApp(root)
	root.mainloop()
