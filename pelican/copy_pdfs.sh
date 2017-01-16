#!/bin/bash

pdf_paths=(
    '../assignments/assignment_one/docs/assignment_one.pdf'
    )

for pdf in ${pdf_paths}; do
    cp $pdf ../public/pdfs/
done

exit 0
