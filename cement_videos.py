import cv2
import sys
import argparse
import os

def cement(files):
    """
    Cements together a list of images and returns the file name of the resulting jpg.

    Just a wrapper around the old Bash/Perl cement script.

    Would be much better if the old script was rewritten to be a single file, it's pretty heavy now and relying on old stuff.

    Args: a list of file names of JPGs to be cemented together.
    """
    cement_location = "/home/cayden/programs/cement"
    #load files into cemen.txt
    with open(os.path.join(cement_location, "cement.txt"), "w") as f:
        for file_name in files:
            f.write(file_name)
            f.write(" 1 1 1\n")
    #execute cement trowel
    cmd = "cd {}; perl trowel.pl; convert trowel_out.ppm /tmp/next_cement_frame.jpg".format(cement_location)
    os.system(cmd)
    return "/tmp/next_cement_frame.jpg"

def main(args):
    #setup video capture
    cap = cv2.VideoCapture(args.filename)
    frame_start = int(args.framerate * args.start)
    frame_end = int(args.framerate * args.end)
    window_len = int(args.window * args.framerate)

    #folder to save images temporarily
    tmp_dir = "/tmp/cement_videos_tmp/"
    tmp_dir_output = "/tmp/cement_videos_output_tmp/"
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    if not os.path.exists(tmp_dir_output):
        os.mkdir(tmp_dir_output)

    #loop through specified frames, output them as jpgs in a folder
    for frame_no in range(frame_start, frame_end):
        print("Processing frame_no : {}".format(frame_no), end="\r")
        cap.set(1, frame_no);
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(os.path.join(tmp_dir, "frame{}.jpg".format(frame_no)), frame) # save frame as JPEG file
        else:
            print("Hit end of video, or video corrupt.")
            break
        #if we are passed the first window length seconds, start cementing the last window of frames into a new frame
        if frame_no - frame_start >= window_len:
            file_names = [ os.path.join(tmp_dir, "frame{}.jpg".format(file_no)) for file_no in range(frame_no - window_len, frame_no + 1) ]
            source = cement(file_names)
            destination = os.path.join(tmp_dir_output, "{}_{}_frame_out.jpg".format(frame_no - window_len, frame_no))
            cmd = "cp {} {}".format(source, destination)
            os.system(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Details about the video to be cemented.')
    parser.add_argument('--filename', "-f", required=True, type=str, help='The video file to be edited')
    parser.add_argument('--start', "-s", required=True, type=float, help='The start time in seconds.')
    parser.add_argument('--end', "-e", required=True, type=float, help='The end time in seconds.')
    parser.add_argument('--framerate', "-r", default=30.0, type=float, help='Framerate of the provided video file.')
    parser.add_argument('--window', "-l", default=30.0, required=True, type=float, help='Time (in seconds) of the cement window.')
    args = parser.parse_args()
    main(args)

