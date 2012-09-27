"""
soapdenovo2_contig.py
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
    parser.add_option('', '--pre_graph_basic', dest='pre_graph_basic')
    parser.add_option('', '--vertex', dest='vertex')
    parser.add_option('', '--pre_arc', dest='pre_arc')

    #Outputs
    parser.add_option("", "--contig", dest='contig')
    parser.add_option("", "--arc", dest='arc')
    parser.add_option("", "--updated_edge", dest='updated_edge')
    parser.add_option("", "--contig_index", dest='contig_index')

    opts, args = parser.parse_args()

    #Prepare to run operation
    #soapdenovo2 contig -g graph_prefix -R 1>contig.log 2>contig.err

    #Need to write inputs to a temporary directory
    dirpath = tempfile.mkdtemp()
    f = open(dirpath + '/out.preGraphBasic', 'w')
    f.write(opts.pre_graph_basic)
    f.close

    f = open(dirpath + '/out.vertex', 'w')
    f.write(opts.vertex)
    f.close

    f = open(dirpath + '/out.preArc', 'w')
    f.write(opts.pre_arc)
    f.close

    #Set up command line call
    #TODO - remove hard coded path
    #Code for adding directory path to other file required as output
    cmd = "/usr/local/bgisoap/soapdenovo2/bin/SOAPdenovo-63mer contig -g %s" % (dirpath + "/out")
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
    contig_index_out = open(opts.contig_index, 'wb')
    file = open(dirpath + "/out.ContigIndex")
    for line in file:
        contig_index_out.write(line)
    contig_index_out.close()
    file.close()

    #Read soap config file into its output
    arc_out = open(opts.arc, 'wb')
    file = open(dirpath + "/out.Arc")
    for line in file:
        arc_out.write(line)
    arc_out.close()
    file.close()

    #Read soap config file into its output
    contig_out = open(opts.contig, 'wb')
    file = open(dirpath + "/out.contig")
    for line in file:
        contig_out.write(line)
    contig_out.close()
    file.close()

    #Read soap config file into its output
    edge_out = open(opts.updated_edge, 'wb')
    file = open(dirpath + "/out.updated.edge")
    for line in file:
        edge_out.write(line)
    edge_out.close()
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
    if os.path.getsize(opts.contig_index) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__": main()
