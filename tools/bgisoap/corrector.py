"""
corrector.py
A wrapper script for corrector
Copyright   Peter Li - GigaScience and BGI-HK
"""

import optparse, os, shutil, subprocess, sys, tempfile

def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()


def cleanup_before_exit(tmp_dir):
    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


def main():
    #Parse command line
    parser = optparse.OptionParser()
    #Make list of params
    parser.add_option("", "--inputfile", action="append", type="string", dest="inputfile_list", help="Input files")
    parser.add_option("", "--kmer_freq_file", action="append", type="string", dest="kmer_freq_file", help="Kmer frequencies")

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")

    #Custom params
    parser.add_option("-n", "--kmer_freq_with_index", dest="kmer_freq_with_index", help="Are the kmer frequences indexed?")
    parser.add_option("-k", "--kmer_freq_cutoff_start", dest="kmer_freq_cutoff_start", help="Start of kmer frequency cutoff")
    parser.add_option("-e", "--kmer_freq_cutoff_end", dest="kmer_freq_cutoff_end", help="End of kmer frequency cutoff")
    parser.add_option("-e", "--max_error_bases_allowed", dest="max_error_bases_allowed", help="Maximum number of error bases allowed")
    parser.add_option("-s", "--seed_length", dest="seed_length", help="Seed length")
    parser.add_option("-s", "--num_threads", dest="num_threads", help="Number of threads")
    parser.add_option("-f", "--format", dest="format", help="Format of input data?")

    #Outputs
    parser.add_option("", "--stat", dest='stat', help="Statistical information")
    opts, args = parser.parse_args()

    #Create temp directory for storage
    tmp_dir = tempfile.mkdtemp()
    #Create string for storing paths to saved files
    #Need to save datasets into temp files
    #Then get paths to files into a string
    for index in range(len(opts.inputfile_list)):
        data = open((opts.inputfile_list)[index], 'r')
        #Append
        fileListStr += (dirpath + "/input." + [index] + "\n")
        file = open(dirpath + "/input." + [index], "w")
        for line in data:
            file.write(line)
        data.close()
        file.close()

    #Set up command line call - need to remove hard coded path
    if opts.default_full_settings_type == "default":
        cmd = "/usr/local/bgisoap/correction/bin/KmerFreq -i %s -o %s" % (fileListStr, "kmerfreq.out")
    elif opts.default_full_settings_type == "full":
        cmd = "/usr/local/bgisoap/correction/bin/KmerFreq -i %s -o %s -q %s -s %s -n %s -f %s" % (
            fileListStr, "kmerfreq.out", opts.quality_cutoff, opts.seed_length, opts.output_kmer_index, opts.format)

    #Perform kmer analysis
    buffsize = 1048576

    try:
        #Create file in temporary directory
        tmp = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        #Open a stream to file
        tmp_stderr = open(tmp, 'wb')
        #Call KmerFreq
        proc = subprocess.Popen(args=cmd, shell=True, cwd=dirpath, stderr=tmp_stderr.fileno())
        returncode = proc.wait()
        #Close stream
        tmp_stderr.close()
        #Get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp, 'rb')
        stderr = ''
        try:
            while True:
                stderr += tmp_stderr.read(buffsize)
                if not stderr or len(stderr) % buffsize != 0:
                    break
        except OverflowError:
            pass
        tmp_stderr.close()
        if returncode != 0:
            raise Exception, stderr
    except Exception, e:
        raise Exception, 'Problem performing kmerfreq ' + str(e)

    #Read KmerFreq results into outputs
    stat_out = open(opts.stat, 'wb')
    file = open(tmp_dir + '/kmerfreq.out.stat')
    for line in file:
        print line
        stat_out.write(line)
    stat_out.close()

    freq_out = open(opts.freq, 'wb')
    file = open(tmp_dir + '/kmerfreq.out.freq')
    for line in file:
        print line
        freq_out.write(line)
    freq_out.close()

    filelist_out = open(opts.filelist, 'w')
    filelist_out.write(fileListStr)

    #Clean up temp files
    cleanup_before_exit(tmp_dir)
    cleanup_before_exit(dirpath)
    #Check results in output file
    if os.path.getsize(opts.stat) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__": main()
