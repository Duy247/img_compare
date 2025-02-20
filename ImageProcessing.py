import cv2
import os
from cairosvg import svg2png


class ImageProcessing:
    def convert_svg_to_png(self, svg_path, png_path):
        """
        Convert SVG to PNG using cairosvg
        Dependencies: cairo, pycairo, cairosvg

        Windows: Install GTK Runtime https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/tag/2022-01-04
            pip install cairosvg
        Then set CAIROCFFI_DLL_DIRECTORIES environment variable to the path where you installed Cairo (this is C:\Program Files\GTK3-Runtime Win64\bin with the GTK3 installer, for example)

        
        Mac: brew install pkg-config, cairo
             pip install pycairo cairosvg
        """
        svg2png(url=svg_path, write_to=png_path, output_width=1000, output_height=500, background_color='black')
    
    def compare_two_images(self, image1_path, image2_path, different_image, threshold=5, mesh=5 ):
        """
        Compare two images

        image1_path: The absolute path to image 1 in Unix format with file name extension, e.g., /folder/image1.png

        image2_path: The absolute path to image 2 in Unix format with file name extension, e.g., /folder/image2.png

        different_image: The absolute path to output different image in Unix format with file name extension, e.g., /folder/different_image.png

        mesh: An integer to divide the images into mesh x mesh sub-images - the higher the mesh, the more detailed comparison. Default = 1

        threshold: An integer to determine the difference of two images. Default = 5%

        Assertion cases:

        1. The two images have different size or format, raises assertion error

        2. The difference of two images <= threshold, logs info "These two images are similar."

        3. The difference of two images > threshold, raises assertion error and outputs a different image = image 1 - image 2
        """
        path1 = image1_path.replace('/', os.sep)
        path2 = image2_path.replace('/', os.sep)

        # Check if the extension is SVG, if so, convert to PNG
        if path1.lower().endswith('.svg'):
            png1_path = path1.replace('.svg', '.png')
            self.convert_svg_to_png(path1, png1_path)
            path1 = png1_path
            image1 = cv2.imread(path1)
        else:
            image1 = cv2.imread(path1)
        
        if path2.lower().endswith('.svg'):
            png2_path = path2.replace('.svg', '.png')
            self.convert_svg_to_png(path2, png2_path)
            path2 = png2_path
            image2 = cv2.imread(path2)
        else:
            image2 = cv2.imread(path2)

        # 1. The two images have different size or format, raises assertion error
        if image1.shape != image2.shape:
            raise AssertionError("These two images have different size or format.\nImage 1: %s.\nImage 2: %s." % (image1.shape, image2.shape))

        height, width, _ = image1.shape
        sub_height = height // mesh
        sub_width = width // mesh

        diff_image = image1.copy()
        differences_found = False

        for i in range(mesh):
            for j in range(mesh):
                sub_image1 = image1[i * sub_height:(i + 1) * sub_height, j * sub_width:(j + 1) * sub_width]
                sub_image2 = image2[i * sub_height:(i + 1) * sub_height, j * sub_width:(j + 1) * sub_width]

                count = 0
                area = sub_image1.shape[0] * sub_image1.shape[1]

                for row in range(sub_image1.shape[0]):
                    for col in range(sub_image1.shape[1]):
                        if sub_image1[row][col][0] != sub_image2[row][col][0] \
                        and sub_image1[row][col][1] != sub_image2[row][col][1] \
                        and sub_image1[row][col][2] != sub_image2[row][col][2]:
                            count += 1
                            diff_image[i * sub_height + row, j * sub_width + col] = [0, 0, 255]  # Mark differences in red

                percent = count * 100 / area

                if percent > threshold:
                    cv2.imwrite(different_image, diff_image)
                    print("The difference in sub-image (%d, %d) = %.2f%% is greater than threshold = %s%%." % (i, j, percent, threshold))
                    raise AssertionError("Differences found. See the diff image for details.")
            

if __name__ == '__main__':
    ip = ImageProcessing()
    try:
        ip.compare_two_images('original.svg', 'detail_mod.svg', 'dif_detail.png', threshold=5 , mesh=7)  
    except AssertionError as e:
        print(e)
    try:
        ip.compare_two_images('original.svg', 'color_mod.svg', 'dif_color.png', threshold=5, mesh=2)  
    except AssertionError as e:
        print(e)