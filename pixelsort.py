from PIL import Image
import random
import colorsys
import sys


# {{{ ARGUMENTS & OPTIONS
# between 0 and 256, i think
BLACK_THRESHOLD = 30
WHITE_THRESHOLD = 200

SORT_TO_END = False
SORT_TO_START = False
RANDOM_SORT = False
REVERSE = False
ROTATE = False
NUM_CHUNK = 0
MAX_CHUNK = 200 # pixels
OUTPUT="out/output_%03i.JPG"

ANIMATE=False
SMOOTH=False
JITTER=0
WIDTH=600


# PARSE OPTIONS
import argparse
parser = argparse.ArgumentParser(description='Primitive pixel sort')
parser.add_argument('IMAGE', type=str)
parser.add_argument('--output', dest='output', default=OUTPUT, type=str, help='Filename for output image')
parser.add_argument('--rotate', dest='rotate', default=ROTATE, action='store_true', help='do a vertical pixel sort')
parser.add_argument('--reverse', dest='reverse', default=REVERSE, action='store_true', help='reverse sort direction')
parser.add_argument('--no-show', dest='no_show', default=False, action='store_true', help='Dont show image after processing')
parser.add_argument('--saturation', dest='saturation', default=False, action='store_true', help='sort by saturation')
parser.add_argument('--sort-start', dest='sort_to_start', default=SORT_TO_START, action='store_true', help='start sort from start of line')
parser.add_argument('--sort-end', dest='sort_to_end', default=SORT_TO_END, action='store_true', help='sort until the end of the line')
parser.add_argument('--noise', dest='random_sort', default=RANDOM_SORT, action='store_true', help='add noise to the sort')
parser.add_argument('--width', dest='width', default=WIDTH, type=int, help='how large to rescale the image')
parser.add_argument('--max-chunk', dest='max_chunk', default=MAX_CHUNK, type=int, help='how many chunks to use with the delay effect')
parser.add_argument('--num-chunks', dest='num_chunks', default=NUM_CHUNK, type=int, help='if sortable area is too large, break into this many chunks')
parser.add_argument('--white-threshold', dest='black_threshold', type=int, default=BLACK_THRESHOLD, help='threshold for a pixel to be considered "black"')
parser.add_argument('--black-threshold', dest='white_threshold', type=int, default=WHITE_THRESHOLD, help='threshold for a pixel to be considered "white"')

# animation args
parser.add_argument('--animate', dest='animate', default=ANIMATE, action='store_true', help='animate')
parser.add_argument('--jitter', dest='jitter', default=JITTER, type=int, help='how much shoudl animation jitter?')
parser.add_argument('--smooth', dest='smooth', default=SMOOTH, action='store_true', help='smooth out animation')
parser.add_argument('--distortions', dest='distortions', default=10, type=int, help='how many distortions to run')
parser.add_argument('--fps', dest='iterations', default=10, type=int, help='how many frames per distortion')
args = parser.parse_args()


# }}} OPTIONS & ARGUMENT PARSING


# {{{ LINE SORTING 
HLS_LOOKUP = {}
rgb_to_hls = colorsys.rgb_to_hls

SORTS=[]
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

    idx = 1
    if args.saturation:
        idx = 2

    if args.reverse:
        to_sort.sort(key=lambda v: -v[0][idx] + ((args.random_sort or 0) and random.randint(-10, 10)))
    else:
        to_sort.sort(key=lambda v: v[0][idx] + ((args.random_sort or 0) and random.randint(-10, 10)))
        

    if big_end - big_start > 5:
        SORTS.append((big_start, big_end, to_sort[0], to_sort[-1]))

    putpixel = im.putpixel
    for y, x in enumerate(to_sort):
        putpixel((y + (start % width), (start / width)), x[1])

# }}}


# {{{ SORT OF FILE LINE BY LINE
def pix_sort(filename):
    im = Image.open(filename)
    width, height = im.size
    new_width, new_height = im.size

    if args.width:
        new_width = args.width
        new_height = int(height * float(new_width) / width)

        im = im.resize((new_width, new_height))

    if args.rotate:
        im = im.rotate(90)

    ratio = float(200) / im.width;

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
                    if args.sort_to_start:
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

    im.save(args.output % 0)
    if not args.animate:
        return


    old_im = Image.open(filename)
    old_im = old_im.resize((new_width, new_height))
    iterations = args.iterations
    new_im = old_im.copy()
    new_im.save(args.output % 0)
    
    if args.rotate:
        old_im = old_im.rotate(90)

    print "0 / 10",
    for i in xrange(1, iterations):

        if args.rotate:
            new_im = new_im.rotate(90)
        sys.stdout.write(".")
        sys.stdout.flush()

        pixels = 0
        for sort in SORTS:
            big_start, big_end, start_val, end_val = sort

            putpixel = new_im.putpixel
            to_sort = []
            start = big_start
            end = big_end - ((big_end - big_start) / iterations) * (iterations - i)
            remaining = big_end - end
            pixels += end - start

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

            for y, x in enumerate(to_sort):
                try:
                    putpixel((y + (start % width), (start / width)), x[1])
                except:
                    pass

        if args.rotate:
            new_im = new_im.rotate(-90)
        new_im.save(args.output % i)

    print ""
    mashed_im = new_im.copy()
    distortions = args.distortions
    for j in xrange(1, distortions):
        pix = old_im.getdata()

        new_im = new_im.copy()
        step_width = width / float(distortions)
        print "%i / %i" % (j, distortions),
        for i in xrange(0, iterations):
            if args.rotate:
                new_im = new_im.rotate(90)
            sys.stdout.write(".")
            sys.stdout.flush()
            pixels = 0
            for sort in SORTS:
                big_start, big_end, start_val, end_val = sort

                putpixel = new_im.putpixel
                to_sort = []
                start = big_start
                end = big_end - ((big_end - big_start) / iterations) * (iterations - i - 1)
                pixels += end - start

                delta = j*step_width + ((i+1) / float(iterations) * step_width) + 1
                if args.jitter:
                    delta = j*args.jitter

                    if j >= distortions / 2:
                        delta = (distortions - j) * args.jitter

                    if j % 2 == 1:
                        delta = -delta




                delta = -delta
                remaining = big_end - end

                for x in xrange(start, end):    
                    if distortions - j > 1 and args.smooth:
                        speed_adj = (hash(str(x)) % (distortions - j)) - (distortions - j) / 2
                        x += speed_adj

                    if x - delta < 0:
                        x += width

                    if args.jitter:
                        if x - delta >= new_im.width:
                            x -= width
                    elif x - delta >= new_im.height:
                        if distortions - j == 1:
                            x -= width
                        else:
                            delta += width

                        
                    val = pix[int(x-delta)]

                    try:
                        hls = HLS_LOOKUP[val]
                    except:
                        try:
                            hls = HLS_LOOKUP[val] = rgb_to_hls(*val)
                        except:
                            continue
                    to_sort.append((hls, val))

                for y, x in enumerate(to_sort):
                    try:
                        putpixel((y + (start % width), (start / width)), x[1])
                    except:
                        pass

            if args.rotate:
                new_im = new_im.rotate(-90)
            new_im.save(args.output % (i + iterations*j))

        print ""


    # now we have to do iterations on the middle IM...


# }}}




# {{{ ENTRY POINT
def main():
    pix_sort(args.IMAGE)

if __name__ == "__main__":
    main()

# }}}
# vim: foldmethod=marker
