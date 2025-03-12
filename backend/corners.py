def run(args, image_buffer):
    from preprocessing.scoresheet import Paper_Extraction

    # Perform paper extraction to get corners and warped image
    expected_corners = Paper_Extraction(image_buffer)

    if expected_corners == -1:
        return {"error": "Failed to process image"}

    return expected_corners
