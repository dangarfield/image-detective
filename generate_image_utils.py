import os
import shutil
import fnmatch
import feature_identifier
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

def make_linear_ramp(white):
    ramp = []
    r, g, b = white
    for i in range(255):
        ramp.extend((r * i / 255, g * i / 255, b * i / 255))
    return ramp


def create_color_image(img, palette_tuple):
    sepia = img.copy().convert("L")
    sepia = ImageOps.autocontrast(sepia)
    sepia.putpalette(make_linear_ramp(palette_tuple))
    return sepia.convert("RGB")

def remove_generated_images(basePath, nestedPath):
    if os.path.exists(basePath):
        shutil.rmtree(basePath)
    os.makedirs(basePath)
    os.makedirs(nestedPath)

def generate_image_variants(SRC, GEN, folder, file):

    file_split = os.path.splitext(os.path.basename(file))

    name = folder + file_split[0]
    ext = file_split[1][1:]

    if not os.path.exists(GEN + folder):
        os.makedirs(GEN + folder)

    
    img = Image.open(SRC + name + "." + ext)
    img.save(GEN + name + "." + ext)
    img.resize((128, 128)).save(GEN + name + "-resize-small." + ext)
    img.resize((2560, 2560)).save(GEN + name + "-resize-big." + ext)
    img.resize([int(0.2 * s) for s in img.size]).save(GEN +
                                                      name + "-resize-small-proportional." + ext)
    img.resize([int(1.5 * s) for s in img.size]).save(GEN +
                                                      name + "-resize-big-proportional." + ext)

    if img.width > 200 and img.height > 200:
        img.crop(box=(100, 100, img.width - 100, img.height - 100)
             ).save(GEN + name + "-crop-all-100." + ext)
    if img.width >= 600 and img.height >= 600:
        img.crop(box=(200, 200, 600, 600)
             ).save(GEN + name + "-crop-left-400." + ext)
        img.crop(box=(img.width - 600, img.height - 600, img.width - 200, img.height - 200)
             ).save(GEN + name + "-crop-right-400." + ext)
    img.crop(box=(0, 0, img.width / 2, img.height)
             ).save(GEN + name + "-crop-left-half." + ext)
    img.crop(box=(img.width / 2, 0, img.width, img.height)
             ).save(GEN + name + "-crop-right-half." + ext)
    if img.width > 400 and img.height > 400:
        img.crop(box=((img.width / 2) - 200, (img.height / 2) - 200, (img.width / 2) + 200, (img.height / 2) + 200)
             ).save(GEN + name + "-crop-centre-400." + ext)

    img.rotate(5).save(GEN + name + "-rotate-5." + ext)
    img.rotate(10).save(GEN + name + "-rotate-10." + ext)
    img.rotate(-15).save(GEN + name + "-rotate-15." + ext)
    img.rotate(45).save(GEN + name + "-rotate-45." + ext)

    img.transpose(Image.FLIP_LEFT_RIGHT).save(GEN + name + "-flip-hori." + ext)
    img.transpose(Image.FLIP_TOP_BOTTOM).save(GEN + name + "-flip-vert." + ext)

    img.filter(ImageFilter.BLUR).save(GEN + name + "-filter-blur." + ext)
    img.filter(ImageFilter.DETAIL).save(GEN + name + "-filter-detail." + ext)
    img.filter(ImageFilter.EDGE_ENHANCE).save(
        GEN + name + "-filter-edges." + ext)
    img.filter(ImageFilter.SMOOTH).save(GEN + name + "-filter-smooth." + ext)
    img.filter(ImageFilter.SHARPEN).save(GEN + name + "-filter-sharpen." + ext)

    img.convert('L').save(GEN + name + "-color-grey." + ext)
    create_color_image(img, (255, 240, 192)).save(
        GEN + name + "-color-sepia." + ext)
    ImageOps.colorize(ImageOps.grayscale(img), (255, 255, 255),
                      (255, 0, 0)).save(GEN + name + "-color-red." + ext)

    ImageEnhance.Color(img).enhance(0.9).save(
        GEN + name + "-enhance-color-down." + ext)
    ImageEnhance.Color(img).enhance(0.5).save(
        GEN + name + "-enhance-color-down2." + ext)
    ImageEnhance.Color(img).enhance(1.1).save(
        GEN + name + "-enhance-color-up." + ext)
    ImageEnhance.Color(img).enhance(1.5).save(
        GEN + name + "-enhance-color-up2." + ext)

    ImageEnhance.Contrast(img).enhance(0.9).save(
        GEN + name + "-enhance-contrast-down." + ext)
    ImageEnhance.Contrast(img).enhance(0.5).save(
        GEN + name + "-enhance-contrast-down2." + ext)
    ImageEnhance.Contrast(img).enhance(1.1).save(
        GEN + name + "-enhance-contrast-up." + ext)
    ImageEnhance.Contrast(img).enhance(1.5).save(
        GEN + name + "-enhance-contrast-up2." + ext)

    ImageEnhance.Brightness(img).enhance(0.9).save(
        GEN + name + "-enhance-bright-down." + ext)
    ImageEnhance.Brightness(img).enhance(0.5).save(
        GEN + name + "-enhance-bright-down2." + ext)
    ImageEnhance.Brightness(img).enhance(1.1).save(
        GEN + name + "-enhance-bright-up." + ext)
    ImageEnhance.Brightness(img).enhance(1.5).save(
        GEN + name + "-enhance-bright-up2." + ext)

    img.copy().save(GEN + name + "-format-jpg." + "jpg")
    img.copy().save(GEN + name + "-format-png." + "png")
    img.copy().save(GEN + name + "-format-gif." + "gif")

    # Need to add blends


def generate_detect_image(SRC, QUERY, filename):
    shutil.copy2(SRC+filename, QUERY)