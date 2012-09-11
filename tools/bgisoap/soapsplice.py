"""
A wrapper script for SOAPsplice
Copyright Peter Li peter@gigasciencejournal.com

Runs SOAPsplice on paired-end data. Need to ask Ruibang if it works on single-end data
Works with SOAPsplice version 1.9.

usage: soapsplice.py [options]

"""

import optparse, os, shutil, subprocess, sys, tempfile

def get_version():
    sys.stdout.write('SOAPsplice version 1.9')

def stop_err( msg ):
    sys.stderr.write( '%s\n' % msg )
    sys.exit()

def __main__():
    #Parse command line input parameters
    parser = optparse.OptionParser()
    parser.add_option('', '--fileSource', dest='fileSource', help='Source of reference dataset index')
    parser.add_option('', '--ref', dest='ref', help='The reference genome to use or index')
    parser.add_option('', '--dbkey', dest='dbkey', help='Dbkey for reference genome')
    parser.add_option('', '--do_not_build_index', dest='do_not_build_index', action='store_true', help="Don't build index")
    parser.add_option('-1', '--input1', dest='fastq', help='The forward fastq file to use for the mapping')
    parser.add_option('-2', '--input2', dest='rfastq', help='The reverse fastq file to use for mapping if paired-end data')
    parser.add_option('-o', '--output_dir_prefix', dest='output_dir_prefix', help='Prefix of output files, can also include a file directory')
    parser.add_option('-I', '--insert_length', dest='insert_length', help='Insert length of paired-end reads')

    #Individual outputs
    parser.add_option('', '--input1_2segs', dest='input1_2segs', help='Two-segment alignment result for forward reads')
    parser.add_option('', '--input1_out', dest='input1_out', help='One-segment alignment result for forward reads')
    parser.add_option('', '--input2_2segs', dest='input2_2segs', help='Two-segment alignment result for reverse reads')
    parser.add_option('', '--input2_out', dest='input1_out', help='One-segment alignment result for reverse reads')
    parser.add_option('', '--junction', dest='junction', help='Junction file')

    #Inputs continued
    parser.add_option('-t', '--num_threads', dest='num_threads', help='Number of threads to use')
    parser.add_option('-S', '--forward_reverse_both', dest='forward_reverse_both', help='Forward, reverse or both')
    parser.add_option('-m', '--max_mismatch', dest='max_mismatch', help='Maximum mismatch for one-segment alignment')
    parser.add_option('-g', '--max_indel', dest='max_indel', help='Maximum indel for one-segment alignment')
    parser.add_option('-i', '--ignore_tail_length', dest='ignore_tail_length', help='Length of tail that can be ignored in one-segment alignment')
    parser.add_option('-t', '--longest_gap_length', dest='longest_gap_length', help='Longest gap between two segments in two-segment alignment')
    parser.add_option('-a', '--shortest_segment_length', dest='shortest_segment_length', help='Shortest length of a segment in two-segment alignment')
    parser.add_option('-c', '--output_read_and_quality', dest='output_read_and_quality', help='Output read and quality information?')
    parser.add_option('-f', '--output_format', dest='output_format', help='Format of output files')
    parser.add_option('-s', '--set_mapq', dest='set_mapq', help='Set mapping quality value')
    parser.add_option('-q', '--input_quality_type', dest='input_quality_type', help='Input quality type in FASTQ file')
    parser.add_option('-L', '--max_distance_bet_paired_ends', dest='max_distance_bet_paired_ends', help='Maximum distance between paired-end reads')
    parser.add_option('-l', '--min_distance_bet_paired_ends', dest='min_distance_bet_paired_ends', help='Minimum distance between paired-end reads')
    parser.add_option('-j', '--output_junction_info', dest='output_junction_info', help='Output junction information?')

    #Extras
    parser.add_option( '-X', '--do_not_build_index', dest='do_not_build_index', action='store_true', help="Don't build index" )

    options, args = parser.parse_args()

    #Create temporary directory for indices
    tmp_index_dir = tempfile.mkdtemp()
    tmp_dir = tempfile.mkdtemp()
    #Index if necessary
    if options.fileSource == 'history' and not options.do_not_build_index:
        ref_file = tempfile.NamedTemporaryFile(dir=tmp_dir)
        ref_file_name = ref_file.name
        ref_file.close()
        os.symlink(options.ref, ref_file_name)
        #Use 2bwt-builder to create reference index
        #2bwt-builder <FASTA sequence file> <Output index prefix>
        #./2bwt-builder /path/to/human_genome.fa /path/to/index/human_genome.fa
        cmd1 = '2bwt-builder %s %s' % (ref_file_name, tmp_dir + ref_file_name)
        try:
            tmp = tempfile.NamedTemporaryFile(dir=tmp_index_dir).name
            tmp_stderr = open(tmp, 'wb')
            proc = subprocess.Popen(args=cmd1, shell=True, cwd=tmp_index_dir, stderr=tmp_stderr.fileno())
            returncode = proc.wait()
            tmp_stderr.close()
            # get stderr, allowing for case where it's very large
            tmp_stderr = open(tmp, 'rb')
            stderr = ''
            buffsize = 1048576
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
            # clean up temp dirs
            if os.path.exists(tmp_index_dir):
                shutil.rmtree(tmp_index_dir)
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
            stop_err( 'Error indexing reference sequence. ' + str( e ) )
    else:
        ref_file_name = options.ref

    #Set up output files
    tmp_input1_2segs = tempfile.NamedTemporaryFile(dir=tmp_dir)
    tmp_input1_2segs_name = tmp_input1_2segs.name
    tmp_input1_2segs.close()

    tmp_input1_out = tempfile.NamedTemporaryFile(dir=tmp_dir)
    tmp_input1_out_name = tmp_input1_out.name
    tmp_input1_out.close()

    input2_2segs = tempfile.NamedTemporaryFile(dir=tmp_dir)
    input2_2segs_name = input2_2segs.name
    input2_2segs.close()

    input2_out = tempfile.NamedTemporaryFile(dir=tmp_dir)
    input2_out_name = input2_out.name
    input2_out.close()

    junction = tempfile.NamedTemporaryFile(dir=tmp_dir)
    junction_name = junction.name
    junction.close()

    #Prepare actual aligning and generate aligning commands
    #Default: soapsplice -d <2BWT index prefix> -1 <reads_a> -2 <reads_b> -I <insert size> -o <prefix of output files>

    default_cmd = 'soapsplice -d %s -1 %s -2 %s -I %s -o %s' % (ref_file_name, options.fastq, options.rfastq, options.insert_length, options.output_dir_prefix)
    print default_cmd

    full_cmd = 'soapsplice -d %s -1 %s -2 %s -I %s -o %s' % (ref_file_name, options.fastq, options.rfastq, options.insert_length, options.output_dir_prefix)
    print full_cmd

    # perform alignments
    buffsize = 1048576
    try:
        # need to nest try-except in try-finally to handle 2.4
        try:
            # align
            try:
                tmp = tempfile.NamedTemporaryFile(dir=tmp_dir).name
                tmp_stderr = open(tmp, 'wb')
                proc = subprocess.Popen(args=default_cmd, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno())
                returncode = proc.wait()
                tmp_stderr.close()
                # get stderr, allowing for case where it's very large
                tmp_stderr = open(tmp, 'rb')
                stderr = ''
                try:
                    while True:
                        stderr += tmp_stderr.read( buffsize )
                        if not stderr or len( stderr ) % buffsize != 0:
                            break
                except OverflowError:
                    pass
                tmp_stderr.close()
                if returncode != 0:
                    raise Exception, stderr
            except Exception, e:
                raise Exception, 'Error aligning sequence. ' + str( e )
                # and again if paired data
            try:
                if cmd2b:
                    tmp = tempfile.NamedTemporaryFile( dir=tmp_dir ).name
                    tmp_stderr = open( tmp, 'wb' )
                    proc = subprocess.Popen( args=cmd2b, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno() )
                    returncode = proc.wait()
                    tmp_stderr.close()
                    # get stderr, allowing for case where it's very large
                    tmp_stderr = open( tmp, 'rb' )
                    stderr = ''
                    try:
                        while True:
                            stderr += tmp_stderr.read( buffsize )
                            if not stderr or len( stderr ) % buffsize != 0:
                                break
                    except OverflowError:
                        pass
                    tmp_stderr.close()
                    if returncode != 0:
                        raise Exception, stderr
            except Exception, e:
                raise Exception, 'Error aligning second sequence. ' + str( e )
                # generate align
            try:
                tmp = tempfile.NamedTemporaryFile( dir=tmp_dir ).name
                tmp_stderr = open( tmp, 'wb' )
                proc = subprocess.Popen( args=cmd3, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno() )
                returncode = proc.wait()
                tmp_stderr.close()
                # get stderr, allowing for case where it's very large
                tmp_stderr = open( tmp, 'rb' )
                stderr = ''
                try:
                    while True:
                        stderr += tmp_stderr.read( buffsize )
                        if not stderr or len( stderr ) % buffsize != 0:
                            break
                except OverflowError:
                    pass
                tmp_stderr.close()
                if returncode != 0:
                    raise Exception, stderr
            except Exception, e:
                raise Exception, 'Error generating alignments. ' + str( e )
                # remove header if necessary

            # check that there are results in the output file
            if os.path.getsize( options.output ) > 0:
                sys.stdout.write( 'BWA run on %s-end data' % options.genAlignType )
            else:
                raise Exception, 'The output file is empty. You may simply have no matches, or there may be an error with your input file or settings.'
        except Exception, e:
            stop_err( 'The alignment failed.\n' + str( e ) )
    finally:
        # clean up temp dir
        if os.path.exists( tmp_index_dir ):
            shutil.rmtree( tmp_index_dir )
        if os.path.exists( tmp_dir ):
            shutil.rmtree( tmp_dir )

if __name__=="__main__": __main__()
