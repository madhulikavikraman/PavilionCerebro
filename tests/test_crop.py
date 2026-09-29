from PIL import Image

from cascade.crop import fit_for_model, make_tiles, tile_boxes, upscale_small


def test_small_image_is_single_tile():
    assert tile_boxes(1000, 800) == [(0, 0, 1000, 800)]


def test_tiles_cover_full_extent():
    w, h = 1950, 1581
    boxes = tile_boxes(w, h)
    assert all(0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h for x0, y0, x1, y1 in boxes)
    assert max(b[2] for b in boxes) == w and max(b[3] for b in boxes) == h
    assert min(b[0] for b in boxes) == 0 and min(b[1] for b in boxes) == 0
    assert len(boxes) == 4


def test_make_tiles_names_and_sizes():
    img = Image.new("RGB", (3000, 4000), "gray")
    tiles = make_tiles(img, "img_1")
    assert all(t.name.startswith("img_1/t") for t in tiles)
    assert all(max(t.image.size) <= 1568 for t in tiles)


def test_fit_and_upscale():
    big = Image.new("RGB", (4000, 2000))
    assert max(fit_for_model(big).size) == 1568
    tiny = Image.new("L", (40, 24))
    up = upscale_small(tiny)
    assert min(up.size) >= 224
