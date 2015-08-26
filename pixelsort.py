from PIL import Image
import random
import colorsys


# {{{ ARGUMENTS & OPTIONS
# between 0 and 256, i think
BLACK_THRESHOLD = 30
WHITE_THRESHOLD = 200

SORT_TO_END = True
SORT_TO_START = True
RANDOM_SORT = False
REVERSE = False
ROTATE = False
NUM_CHUNK = 0
MAX_CHUNK = 200 # pixels
OUTPUT="output.JPG"


# PARSE OPTIONS
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('IMAGE', type=str)
parser.add_argument('--rotate', dest='rotate', default=ROTATE, action='store_true')
parser.add_argument('--sort-start', dest='sort_to_start', default=SORT_TO_START, action='store_true')
parser.add_argument('--sort-end', dest='sort_to_end', default=SORT_TO_END, action='store_true')
parser.add_argument('--noise', dest='random_sort', default=RANDOM_SORT, action='store_true')
parser.add_argument('--max-chunk', dest='max_chunk', default=MAX_CHUNK, type=int)
parser.add_argument('--num-chunks', dest='num_chunks', default=NUM_CHUNK, type=int)
parser.add_argument('--white-threshold', dest='black_threshold', type=int, default=BLACK_THRESHOLD)
parser.add_argument('--black-threshold', dest='white_threshold', type=int, default=WHITE_THRESHOLD)
parser.add_argument('--output', dest='output', default=OUTPUT, type=str)
args = parser.parse_args()

# }}} OPTIONS & ARGUMENT PARSING


# {{{ LINE SORTING 
HLS_LOOKUP = {}
rgb_to_hls = colorsys.rgb_to_hls
def sort_from(im, pix, big_start, big_end):
    to_sort = []
    width, height = im.size


    if args.num_chunks:
        if big_end - big_start > args.max_chunk:
            delta = big_end - big_start
            chunk_size = (delta / args.num_chunks)

            for i in xrange(delta / chunk_size):
                sort_from(im, pix, big_start + (i * chunk_size), big_start + ((i + 1) * chunk_size))

            return

    start = big_start
    end = big_end

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
    if REVERSE:
        to_sort.sort(key=lambda v: -v[0][1] + ((args.random_sort or 0) and random.randint(-10, 10)))
    else:
        to_sort.sort(key=lambda v: v[0][1] + ((args.random_sort or 0) and random.randint(-10, 10)))
        

    putpixel = im.putpixel
    for y, x in enumerate(to_sort):
        putpixel((y + (start % width), (start / width)), x[1])

# }}}


# {{{ SORT OF FILE LINE BY LINE
def pix_sort(filename):
    im = Image.open(filename)
    if args.rotate:
        im = im.rotate(90)

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
            if tot < args.black_threshold or tot > args.white_threshold:
                if not start:
                    if args.sort_to_end:
                        start = 0
                    else :
                        start = j
                        continue

                end = j

                if start != end:
                    sort_from(im, pix, (i*width) + start, (i*width) + end)
                start = end
                end = None

        if start != end and args.sort_to_end:
            sort_from(im, pix, (i*width) + start, (i*width) + width)





    seeds = []
    if args.rotate:
        im = im.rotate(-90)
    im.save(args.output)

# }}}




# {{{ ENTRY POINT
def main():
    pix_sort(args.IMAGE)

if __name__ == "__main__":
    main()

# }}}
# vim: foldmethod=marker
