import fitz
import os


class CropManager:

    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)

    def crop_question(
        self,
        page_idx,
        start_y,
        end_y,
        column,
        output_path
    ):

        page = self.doc[page_idx]

        page_width = page.rect.width

        if column == "left":

            rect = fitz.Rect(
                0,
                start_y,
                page_width / 2,
                end_y
            )

        else:

            rect = fitz.Rect(
                page_width / 2,
                start_y,
                page_width,
                end_y
            )

        pix = page.get_pixmap(
            matrix=fitz.Matrix(3, 3),
            clip=rect
        )

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        pix.save(output_path)