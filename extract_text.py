import os
from pdf2image import convert_from_path
import pytesseract


def pdf_to_images(pdf_path, output_folder, dpi=300):
	"""Convert a PDF into images and save them."""
	images = convert_from_path(pdf_path, dpi=dpi)
	image_paths = []

	for i, image in enumerate(images):
		img_path = os.path.join(output_folder, f"page_{i + 1}.png")
		image.save(img_path, "PNG")
		image_paths.append(img_path)

	return image_paths


def ocr_images(image_paths):
	"""Run Tesseract OCR on a list of image paths and return extracted text."""
	text_output = []
	for img_path in image_paths:
		text = pytesseract.image_to_string(img_path)
		text_output.append(f"--- Page {image_paths.index(img_path) + 1} ---\n{text}\n")

	return "\n".join(text_output)


def main(pdf_path, output_folder):
	os.makedirs(output_folder, exist_ok=True)

	print("Converting PDF to images...")
	image_paths = pdf_to_images(pdf_path, output_folder)

	print("Running OCR on images...")
	extracted_text = ocr_images(image_paths)

	output_txt = os.path.join(output_folder, "output.txt")
	with open(output_txt, "w", encoding="utf-8") as f:
		f.write(extracted_text)

	print(f"OCR complete. Extracted text saved to {output_txt}")


if __name__ == "__main__":
	import sys

	if len(sys.argv) != 3:
		print("Usage: python script.py <pdf_path> <output_folder>")
		sys.exit(1)

	pdf_path = sys.argv[1]
	output_folder = sys.argv[2]
	main(pdf_path, output_folder)
