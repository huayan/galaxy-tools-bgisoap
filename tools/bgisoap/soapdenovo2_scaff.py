"""
soapdenovo2_scaff.py
A wrapper script for SOAPdenovo2 scaff module
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
    #Inputs
    parser.add_option('', '--arc', dest='arc')
    parser.add_option('', '--pegrads', dest='pegrads')
    parser.add_option('', '--pregraph_basic', dest='pregraph_basic')
    parser.add_option('', '--updated_edge', dest='updated_edge')
    parser.add_option('', '--contig', dest='contig')
    parser.add_option('', '--read_in_gap', dest='read_in_gap')

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")
    parser.add_option("", "--fill_gaps", dest="fill_gaps")
    parser.add_option("", "--compatible_mode", dest="compatible_mode")
    parser.add_option("", "--unmask_contigs", dest="unmask_contigs")
    parser.add_option("", "--keep_contigs_connected", dest="keep_contigs_connected")
    parser.add_option("", "--ass_visual", dest="ass_visual")
    parser.add_option("", "--gap_len_diff", dest="gap_len_diff")
    parser.add_option("", "--min_contig_len", dest="min_contig_len")
    parser.add_option("", "--min_contig_cvg", dest="min_contig_cvg")
    parser.add_option("", "--max_contig_cvg", dest="max_contig_cvg")
    parser.add_option("", "--insert_size_upper_bound", dest="insert_size_upper_bound")
    parser.add_option("", "--bubble_coverage", dest="bubble_coverage")
    parser.add_option("", "--genome_size", dest="genome_size")
    parser.add_option("", "--ncpu", dest="ncpu")

    #Outputs
    parser.add_option("", "--new_contig_index", dest='new_contig_index')
    parser.add_option("", "--links", dest='links')
    parser.add_option("", "--scaf_gap", dest='scaf_gap')
    parser.add_option("", "--scaf", dest='scaf')
    parser.add_option("", "--scaf_seq", dest='scaf_seq')
    parser.add_option("", "--contig_positions_scaff", dest='contig_positions_scaff')
    parser.add_option("", "--bubble_in_scaff", dest='bubble_in_scaff')
    parser.add_option("", "--scaf_stats", dest='scaf_stats')

    opts, args = parser.parse_args()

    #Need to write inputs to a temporary directory
    dirpath = tempfile.mkdtemp()
    f = open(dirpath + '/out.Arc', 'w')
    f.write(opts.arc)
    f.close

    f = open(dirpath + '/out.peGrads', 'w')
    f.write(opts.pegrads)
    f.close

    f = open(dirpath + '/out.preGraphBasic', 'w')
    f.write(opts.pregraph_basic)
    f.close

    f = open(dirpath + '/out.updated.edge', 'w')
    f.write(opts.updated_edge)
    f.close

    f = open(dirpath + '/out.contig', 'w')
    f.write(opts.contig)
    f.close

    f = open(dirpath + '/out.readInGap.gz', 'w')
    f.write(opts.read_in_gap)
    f.close

    #Set up command line call
    #TODO - remove hard coded path
    #Code for adding directory path to other file required as output
    if opts.default_full_settings_type == "default":
        cmd = "/usr/local/bgisoap/soapdenovo2/bin/SOAPdenovo-63mer scaff -g %s -F" % (dirpath + "/out")
    elif opts.default_full_settings_type == "full":
        cmd = "/usr/local/bgisoap/soapdenovo2/bin/SOAPdenovo-63mer scaff -g %s -F %s -z %s -u %s -w %s -v %s -G %s -L %s -c %s -C %s -b %s -B %s -N %s -p %s" % (dirpath + "/out",
            opts.fill_gaps, opts.compatible_mode, opts.unmask_contigs, opts.keep_contigs_connected, opts.ass_visual, opts.gap_len_diff,
            opts.min_contig_len, opts.min_contig_cvg, opts.max_contig_cvg, opts.insert_size_upper_bound, opts.bubble_coverage,
            opts.genome_size, opts.ncpu)
        #Check
        print cmd


    #Perform SOAPdenovo2_config analysis
    buffsize = 1048576
    #Create temp directory for standard error and out
    tmp_dir = tempfile.mkdtemp()
    try:

        tmp_out_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stdout = open(tmp_out_file, 'wb')
        tmp_err_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stderr = open(tmp_err_file, 'wb')

        #Call SOAPdenovo2
        #New additional datasets must be placed in the directory provided by $__new_file_path__
        proc = subprocess.Popen(args=cmd, shell=True, cwd=tmp_dir, stdout=tmp_stdout, stderr=tmp_stderr.fileno())
        returncode = proc.wait()
        #Get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp_err_file, 'rb')
        stderr = ''
        try:
            while True:
                stderr += tmp_stderr.read(buffsize)
                if not stderr or len(stderr) % buffsize != 0:
                    break
        except OverflowError:
            pass
            #Close streams
        tmp_stdout.close()
        tmp_stderr.close()
        if returncode != 0:
            raise Exception, stderr
    except Exception, e:
        raise Exception, 'Problem performing scaff process ' + str(e)

    #Read soap config file into its output
    new_contig_index_out = open(opts.new_contig_index, 'wb')
    file = open(dirpath + "/out.newContigIndex")
    for line in file:
        new_contig_index_out.write(line)
    new_contig_index_out.close()
    file.close()

    links_out = open(opts.links, 'wb')
    file = open(dirpath + "/out.links")
    for line in file:
        links_out.write(line)
    links_out.close()
    file.close()

    scaf_gap_out = open(opts.scaf_gap, 'wb')
    file = open(dirpath + "/out.scaf_gap")
    for line in file:
        scaf_gap_out.write(line)
    scaf_gap_out.close()
    file.close()

    scaf_out = open(opts.scaf, 'wb')
    file = open(dirpath + "/out.scaf")
    for line in file:
        scaf_out.write(line)
    scaf_out.close()
    file.close()

    scaf_seq_out = open(opts.scaf_seq, 'wb')
    file = open(dirpath + "/out.scafSeq")
    for line in file:
        scaf_seq_out.write(line)
    scaf_seq_out.close()
    file.close()

    contig_positions_scaff_out = open(opts.contig_positions_scaff, 'wb')
    file = open(dirpath + "/out.contigPosInscaff")
    for line in file:
        contig_positions_scaff_out.write(line)
    contig_positions_scaff_out.close()
    file.close()

    bubble_in_scaff_out = open(opts.bubble_in_scaff, 'wb')
    file = open(dirpath + "/out.bubbleInScaff")
    for line in file:
        bubble_in_scaff_out.write(line)
    bubble_in_scaff_out.close()
    file.close()

    scaf_stats_out = open(opts.scaf_stats, 'wb')
    file = open(dirpath + "/out.scafStatistics")
    for line in file:
        scaf_stats_out.write(line)
    scaf_stats_out.close()
    file.close()

    #Clean up temp files
    cleanup_before_exit(tmp_dir)
    #Check results in output file
    if os.path.getsize(opts.scaf_stats) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__": main()
