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
    parser.add_option("", "--filelist", action="append", type="string", dest="inputfile_list", help="Input files")
    parser.add_option("", "--kmer_freq_file", action="append", type="string", dest="kmer_freq_file", help="Kmer frequencies")

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")

    #Custom params
    parser.add_option("-n", "--kmer_freq_with_index", dest="kmer_freq_with_index", help="Are the kmer frequences indexed?")
    parser.add_option("-k", "--kmer_freq_cutoff_start", dest="kmer_freq_cutoff_start", help="Start of kmer frequency cutoff")
    parser.add_option("-e", "--kmer_freq_cutoff_end", dest="kmer_freq_cutoff_end", help="End of kmer frequency cutoff")
    parser.add_option("-d", "--max_error_bases_allowed", dest="max_error_bases_allowed", help="Maximum number of error bases allowed")
    parser.add_option("-s", "--seed_length", dest="seed_length", help="Seed length")
    parser.add_option("-t", "--num_threads", dest="num_threads", help="Number of threads")
    parser.add_option("-f", "--format", dest="format", help="Format of input data?")

    #Outputs
    parser.add_option("", "--corr", dest='corr', help="Corrected short reads")
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
        cmd = "/usr/local/bgisoap/correction/bin/Corrector -i %s -r %s" % (opts.inputfile_list, opts.kmer_freq_file)
    elif opts.default_full_settings_type == "full":
        cmd = "/usr/local/bgisoap/correction/bin/Corrector -i %s -r %s -n %s -k %s -e %s -d %s -s %s -t %s -f %s" % (opts.inputfile_list, opts.kmer_freq_file, opts.kmer_freq_with_index, opts.kmer_freq_cutoff_start, opts.kmer_freq_cutoff_end, opts.max_error_bases_allowed, opts.seed_length, opts.num_threads, opts.format)

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
        raise Exception, 'Problem performing Corrector ' + str(e)

    #Read corr results into outputs
    corr_out = open(opts.corr, 'wb')
    file = open(tmp_dir + '/corr.out')
    for line in file:
        print line
        corr_out.write(line)
    corr_out.close()

    #Clean up temp files
    cleanup_before_exit(tmp_dir)
    cleanup_before_exit(dirpath)
    #Check results in output file
    if os.path.getsize(opts.corr) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__": main()
