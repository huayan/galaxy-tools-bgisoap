"""
soapdenovo2_map.py
A wrapper script for SOAPdenovo2 pregraph module
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
    parser.add_option('', '--contig', dest='contig')
    parser.add_option('', '--contig_index', dest='contig_index')
    parser.add_option('', '--soap_config', dest='soap_config')

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")
    parser.add_option("-p", "--ncpu", dest="ncpu", help="Number of cpu for use")
    parser.add_option("-f", "--output_gap_related_reads", dest="output_gap_related_reads")
    parser.add_option("-k", "--kmer_r2c", dest="kmer_r2c")

    #Outputs
    parser.add_option("", "--pegrads", dest='pegrads')
    parser.add_option("", "--read_on_contig", dest='read_on_contig')
    parser.add_option("", "--read_in_gap", dest='read_in_gap')

    opts, args = parser.parse_args()

    #Need to write inputs to a temporary directory
    dirpath = tempfile.mkdtemp()
    f = open(dirpath + '/soap.config', 'w')
    f.write(opts.soap_config)
    f.close

    f = open(dirpath + '/out.contig', 'w')
    f.write(opts.contig)
    f.close

    f = open(dirpath + '/out.ContigIndex', 'w')
    f.write(opts.contig_index)
    f.close

    #Set up command line call
    #TODO - remove hard coded path
    #Code for adding directory path to other file required as output
    if opts.default_full_settings_type == "default":
        cmd = "/usr/local/bgisoap/soapdenovo2/bin/SOAPdenovo-63mer map -s %s -g %s" % (opts.soap_config, dirpath + "/out")
    elif opts.default_full_settings_type == "full":
        cmd = "/usr/local/bgisoap/soapdenovo2/bin/SOAPdenovo-63mer map -s %s -g %s -f %s -p % -k %s" % (opts.soap_config, dirpath + "/out", opts.output_gap_related_reads, opts.ncpu, opts.kmer_r2c)

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
        raise Exception, 'Problem performing pregraph process ' + str(e)

    #Read soap config file into its output
    pegrads_out = open(opts.pegrads, 'wb')
    file = open(dirpath + "/out.peGrads")
    for line in file:
        pegrads_out.write(line)
    pegrads_out.close()
    file.close()

    #Read soap config file into its output
    read_on_contig_out = open(opts.read_on_contig, 'wb')
    with open(dirpath + "/out.readOnContig.gz", mode='rb') as file: # b is important -> binary
        fileContent = file.read()
        read_on_contig_out.write(fileContent)

    read_on_contig_out.close()
    file.close()

    #Read soap config file into its output
    read_in_gap_out = open(opts.read_in_gap, 'wb')
    with open(dirpath + "/out.readInGap.gz", mode='rb') as file: # b is important -> binary
        fileContent = file.read()
        read_in_gap_out.write(fileContent)

    read_in_gap_out.close()
    file.close()


    # Rename files - this is required by Galaxy to show an unknown number of
    # multiple outputs at runtime after execution of SOAPdenovo2
    #    for filename in sorted(os.listdir(database_tmp_dir)):
    #        if "out" in filename:
    #            print filename
    #            shutil.move( os.path.join( database_tmp_dir, filename ), os.path.join( database_tmp_dir,
    #                'primary_%s_%s_visible_txt' % ( output_id, filename ) ) )

    #Clean up temp files
    cleanup_before_exit(tmp_dir)
    #Check results in output file
    if os.path.getsize(opts.pegrads) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__": main()
