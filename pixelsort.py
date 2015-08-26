from PIL import Image
import random
import colorsys

# between 0 and 256, i think
BLACK_THRESHOLD = 30
WHITE_THRESHOLD = 200

SORT_TO_END = False
SORT_TO_START = False

HLS_LOOKUP = {}

rgb_to_hls = colorsys.rgb_to_hls
def sort_from(im, pix, start, end):
    to_sort = []
    width, height = im.size
    for x in xrange(start, end):
        val = pix[x]
        try:
            hls = HLS_LOOKUP[val]
        except:
            try:
                hls = HLS_LOOKUP[val] = rgb_to_hls(*val)
            except:
                continue
        to_sort.append((hls, val))

    # sort by lightness
    to_sort.sort(key=lambda v: v[0][1])

    putpixel = im.putpixel
    for y, x in enumerate(to_sort):
        putpixel((y + (start % width), (start / width)), x[1])

def pix_sort(filename):
    im = Image.open(filename)
    width, height = im.size
    pix = im.getdata()

    # scan for white or black pixels to sort between
    for i in xrange(height):
        start = None
        end = None

        for j in xrange(width-1):
            px = pix[i * width + j]

            try:
                hls = HLS_LOOKUP[px]
            except:
                try:
                    hls = HLS_LOOKUP[px] = rgb_to_hls(*px)
                except:
                    continue


            tot = hls[1]
            if tot < BLACK_THRESHOLD or tot > WHITE_THRESHOLD:
                if not start:
                    if SORT_TO_START:
                        start = 0
                    else :
                        start = j
                        continue

                end = j

                if start != end:
                    sort_from(im, pix, (i*width) + start, (i*width) + end)
                start = end
                end = None

        if start != end and SORT_TO_END:
            sort_from(im, pix, (i*width) + start, (i*width) + width)





    seeds = []
    im.save("output.JPG")


def main():
    import sys
    if len(sys.argv) < 2:
        print "Usage: %s <image>" % (sys.argv[0])
        sys.exit(0)

    pix_sort(sys.argv[1])

if __name__ == "__main__":
    main()
